import os
import time
from flask import Flask, render_template, request, make_response, jsonify
from flask_socketio import SocketIO, emit
import random, string, collections
from fastcore.utils import *
from urllib.parse import urlparse
import google.generativeai as genai
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
socketio = SocketIO(app)
sid2student, student2color, class2students = dict(), dict(), collections.defaultdict(lambda: set())
class2slides = {}
class2questions = collections.defaultdict(list)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-2m-latest",
    generation_config=generation_config,
)

@app.route('/')
def root(): 
    return render_template('howto.html', url=f'https://{urlparse(request.base_url).hostname}')

@app.route('/<class_id>')
def student_interface(class_id):
    student_id = request.cookies.get('student_id') or ''.join(random.choices(string.ascii_letters, k=12))
    class2students[class_id].add(student_id)
    response = make_response(render_template('student.html', timestamp=time.time(), class_id=class_id))
    response.set_cookie('student_id', student_id)
    return response

@app.route('/<class_id>/teacher')
def teacher_interface(class_id):
    return render_template('teacher.html', student_count=student_count(class_id),
        active_student_count=active_student_count(class_id), color2frac=color_fraction(class_id))

@app.route('/<class_id>/upload_slides', methods=['POST'])
def upload_slides(class_id):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        uploaded_file = upload_to_gemini(file_path, mime_type="application/pdf")
        wait_for_files_active([uploaded_file])
        class2slides[class_id] = uploaded_file
        return jsonify({"message": "File uploaded successfully"}), 200
    else:
        return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400

@socketio.on('register_student')
def register_student(timestamp, class_id):
    student_id = request.cookies.get('student_id')
    emit('deactivate_old_tabs', 
            {'student_id':  student_id, 'timestamp': timestamp}, broadcast=True, namespace='/')
    student2color[student_id] = 'inactive'
    sid2student[request.sid] = student_id
    for cls in class2students:
        class2students[cls].discard(student_id)
    class2students[class_id].add(student_id)

@socketio.on('color_change')
def handle_color_change(new_color): 
    student2color[request.cookies['student_id']] = new_color

@socketio.on('disconnect')
def handle_disconnect():
    student = sid2student.pop(request.sid, None)

@socketio.on('submit_question')
def handle_question(class_id, question):
    if class_id in class2slides:
        chat_session = model.start_chat(history=[{"role": "user", "parts": [class2slides[class_id]]}])
        response = chat_session.send_message(question)
        class2questions[class_id].append({
            "question": question,
            "answer": response.text,
            "status": "pending"
        })
        emit('new_question', {"question": question, "answer": response.text}, room=class_id)
    else:
        class2questions[class_id].append({
            "question": question,
            "answer": None,
            "status": "pending"
        })
        emit('new_question', {"question": question, "answer": None}, room=class_id)

@socketio.on('mark_question_solved')
def mark_question_solved(class_id, question_index):
    if 0 <= question_index < len(class2questions[class_id]):
        class2questions[class_id][question_index]['status'] = 'solved'
        emit('question_status_update', {"index": question_index, "status": "solved"}, room=class_id)

@socketio.on('submit_to_speaker')
def submit_to_speaker(class_id, question_index):
    if 0 <= question_index < len(class2questions[class_id]):
        class2questions[class_id][question_index]['status'] = 'submitted'
        emit('question_status_update', {"index": question_index, "status": "submitted"}, room=class_id)

def student_count(class_id): 
    return L(sid2student.values()).filter(lambda s: s in class2students[class_id]).count()

def connected_student2color(class_id):
    return {k: v for k, v in student2color.items() if (k in class2students[class_id]) and (k in sid2student.values())}

def active_student_count(class_id):
    return L(connected_student2color(class_id).values()).filter(lambda c: c != 'inactive').count()

def color_fraction(class_id):
    return {color: L(connected_student2color(class_id).values()).map(eq(color)).sum()/(active_student_count(class_id) or 1)
            for color in ['green', 'yellow', 'red']}

@patch
def count(self:L): return len(self)

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
