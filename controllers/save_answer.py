import os
import json
import math
import os
import shutil
from app import app
from utils import *
from flask import render_template, request, session, redirect, url_for, flash
from flask_login import current_user
from controllers.constructor import create_directory, create_file
from controllers.guidebook import is_partner_valid, validate_speaker_n, get_answer_info_by_user, is_diag_connection_set, get_answer_info_by_user, is_task_autocheck, get_correct_answer_info
from controllers.edit_entry import get_task_data
from models.constructor_model import is_author, delete_path
from models.guidebook_model import get_entry_by_id, get_all_students


def clear_student_answers(book_id, entry_id):
    conn = get_db_connection()
    df_students = get_all_students(conn)
    if len(df_students) < 1: return None
    for i, student in df_students.iterrows():
        student_id = student['student_id']
        path = f'static/guidebooks/{book_id}/answers/{student_id}/{entry_id}'
        delete_path(path)


def calculate_points(book_id, entry_id, student_id, answer_info):
    points = ""
    conn = get_db_connection()
    df_entry = get_entry_by_id(conn, entry_id)
    if len(df_entry) > 0:
        entry_type = df_entry.loc[0, "entry_type_name"]
        correct_answer_info = get_correct_answer_info(book_id, entry_id)
        task_data = get_task_data(book_id, entry_id)
        if correct_answer_info is None or task_data is None or 'points' not in task_data: return ''
        max_points = int(task_data['points'])
        match entry_type:
            # task types where each answer gives points
            case 'task_text' | 'task_txar' | 'task_chbx' | 'task_numb' | 'task_ordr':
                points = 0
                answer_amount = len(correct_answer_info)
                points_per_answer = math.ceil(max_points / answer_amount)
                for answer_num, correct_answer in correct_answer_info.items():
                    num = int(answer_num)
                    if num in answer_info and answer_info[num] == correct_answer:
                        points += points_per_answer
                points = str(clamp(points, 0, max_points))
            # radio button task can only be 0 or MAX_POINTS
            case 'task_radi':
                points = str(max_points)
                # if at least one answer is incorrect set points to 0
                for answer_num, correct_answer in correct_answer_info.items():
                    num = int(answer_num)
                    if num not in answer_info or answer_info[num] != correct_answer:
                        points = '0'
                        break
    return points


def save_answer_info(book_id, entry_id, answer_info):
    user_id = -1
    conn = get_db_connection()
    if current_user.is_editor and is_author(conn, current_user.id, book_id):
        user_id = 0
    elif 'role_id' in session and 'role_type' in session and session['role_type'] == 'student':
        user_id = session['role_id']
    if user_id == -1:
        return None
    path = f'static/guidebooks/{book_id}/answers/{user_id}/{entry_id}'
    filename = 'answer_info.dat'
    create_directory('static/guidebooks/' + str(book_id) + '/answers')
    create_directory('static/guidebooks/' + str(book_id) + '/answers/' + str(user_id))
    create_directory(path)
    create_file(path, filename, '')
    f = open(os.path.join(app.path, f'{path}/{filename}'), 'w')
    json.dump(answer_info, f)
    f.close()
    # automatically calculate points if user is student
    if user_id != 0:
        create_file(path, 'points.dat', '')
        f = open(os.path.join(app.path, f'{path}/points.dat'), 'w')
        points = calculate_points(book_id, entry_id, user_id, answer_info)
        f.write(points)
        f.close()
    # changing correct answer resets student answers
    else:
        clear_student_answers(book_id, entry_id)
        

@app.route('/save_answer', methods=['get', 'post'])
def save_answer():

    # "Update" button in dialog task pressed
    if request.form.get('form_update'):
        return_url = request.form.get("return_url")
        if return_url is not None:
            return redirect(return_url)
        return redirect(url_for('index'))
    # student chose speaker
    if current_user.is_authenticated and request.form.get('form_choose_speaker'):
        book_id = request.form.get("book_id")
        entry_id = request.form.get("entry_id")
        partner_id = request.form.get("partner")
        speaker_n = request.form.get("speaker_n")
        return_url = request.form.get("return_url")
        if 'role_id' in session and is_partner_valid(book_id, entry_id, session['role_id'], partner_id) and not is_diag_connection_set(book_id, entry_id, session['role_id']):
            answer_info = get_answer_info_by_user(book_id, entry_id, session['student_id'])
            if answer_info is None:
                answer_info = {}
            answer_info['speaker'] = str(speaker_n)
            answer_info['partner'] = str(partner_id)
            save_answer_info(book_id, entry_id, answer_info)
            validate_speaker_n(book_id, entry_id, session['role_id'], partner_id)
            flash("Собеседник выбран. Если ниже не появились области для ответа, значит собеседник ещё не выбрал вас. "
                  "Подождите, пока он/она вас выберет, и перезагрузите страницу при помощи кнопки 'Обновить'. "
                  "Или выберите другого собеседника.", 'success')
        elif is_diag_connection_set(book_id, entry_id, session['role_id']):
            flash('Вы не можете поменять собеседника и/или номер. Собеседник, которого вы выбрали ранее, уже выбрал вас.', 'error')
        else:
            flash('Данный студент уже выбрал собеседника.', 'error')
        return redirect(return_url)

    if request.form.get('entry_id') and current_user.is_authenticated:
        conn = get_db_connection()
        entry_id = request.form.get('entry_id')
        book_id = request.form.get('book_id')
        entry_type = request.form.get('entry_type')
        return_url = request.form.get('return_url')
        if not (
            'role_id' in session and 'role_type' in session and session['role_type'] == 'student' 
            and get_answer_info_by_user(book_id, entry_id, session['role_id']) is None
            or current_user.is_editor and is_author(conn, current_user.id, book_id)):
            if return_url is not None:
                return redirect(return_url)
        
        if entry_type == 'task_audi' or entry_type == 'task_diag':
            if return_url is not None:
                return redirect(return_url)
            else:
                return return_url(url_for('index'))
        answer_count = request.form.get('answer_count')
        if entry_type == 'task_radi':
            answer_count = 1
        answers = {}
        for i in range(int(answer_count)):
            answers[i] = request.form.get(f"answer_{i}")

        match entry_type:
            case 'task_text' | 'task_txar' | 'task_numb' | 'task_radi':
                for key, value in answers.items():
                    if value is None:
                        answers[key] = ''
                    else:
                        answers[key] = answers[key].strip()
            case 'task_chbx':
                for key, value in answers.items():
                    if value is None:
                        answers[key] = ''
                    else:
                        answers[key] = 'checked'
            case _:
                pass
        # saving answers
        save_answer_info(book_id, entry_id, answers)
        if return_url is not None:
            return redirect(return_url)
    return redirect(url_for('index'))

