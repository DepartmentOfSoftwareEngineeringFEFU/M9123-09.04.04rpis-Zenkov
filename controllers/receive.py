import json
from app import app
from utils import get_db_connection
from flask import request, session, redirect, url_for, jsonify
from flask_login import current_user
from controllers.constructor import create_directory, create_file
from controllers.save_answer import save_answer_info
from controllers.edit_entry import is_audio_file_allowed
from controllers.guidebook import get_answer_info_by_user
from models.guidebook_model import get_book_id_by_entry
import os


def get_answer_info(book_id, entry_id):
    answer_info = None
    user_id = None
    if current_user.is_authenticated and 'role_id' in session and 'role_type' in session and session['role_type'] == 'student':
        user_id = session['role_id']
    elif current_user.is_authenticated and 'role_type' in session and session['role_type'] == 'teacher' \
            and session['student_id'] is not None and session['student_id'] != '-1':
        user_id = session['student_id']
    if user_id is not None:
        path = os.path.join(app.path, f'static/guidebooks/{book_id}/answers/{user_id}/{entry_id}/answer_info.dat')
        if os.path.exists(path):
            f = open(path, 'r')
            answer_info = json.load(f)
            f.close()
    return answer_info


def update_answer_info_audi(book_id, entry_id, answer_n, path_to_audio):
    answer_info = get_answer_info(book_id, entry_id)
    if answer_info is None:
        answer_info = {}
    answer_info[answer_n] = path_to_audio
    save_answer_info(book_id, entry_id, answer_info)


@app.route("/receive", methods=['post'])
def form():
    if request.form.get('get_audio_data'):
        entry_id = request.form.get('entry_id')
        answer_n = request.form.get('answer_n')
        user_id = request.form.get('user_id')
        response = jsonify("No file.")
        if entry_id is not None and answer_n is not None and user_id is not None:
            conn = get_db_connection()
            df_entry = get_book_id_by_entry(conn, entry_id)
            if len(df_entry) > 0:
                book_id = df_entry.loc[0, 'book_id']
                answer_info = get_answer_info_by_user(book_id, entry_id, user_id)
                if answer_info is not None and f"{answer_n}" in answer_info:
                    src = answer_info[f"{answer_n}"]
                    response = jsonify(src)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    if request.method == 'POST':
        files = request.files
        file = files.get('file')
        book_id = request.form.get('book_id')
        entry_id = request.form.get('entry_id')
        answer_n = request.form.get('answer_n')
        if 'role_id' in session and 'role_type' in session and session['role_type'] == 'student' and book_id is not None and entry_id is not None and answer_n is not None and file is not None:
            if is_audio_file_allowed(file.filename):
                path = f'static/guidebooks/{book_id}/answers/{session["role_id"]}/{entry_id}'
                filename = f"{answer_n}{os.path.splitext(file.filename)[1]}"
                create_directory(f'static/guidebooks/{book_id}/answers/{session["role_id"]}')
                create_directory(path)
                create_file(path, filename, '')
                file.save(f'{path}/{filename}')
                update_answer_info_audi(book_id, entry_id, answer_n,
                                        f'../static/guidebooks/{book_id}/answers/{session["role_id"]}/{entry_id}/{filename}')
                response = jsonify("File received and saved.")
            else:
                response = jsonify("File not allowed.")
        else:
            response = jsonify("File, entry ID or answer number is missing.")
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    return redirect(url_for('index'))
