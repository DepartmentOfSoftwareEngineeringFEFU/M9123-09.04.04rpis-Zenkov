import json
import os
import codecs
import pandas as pd
import random
import re
import controllers.edit_entry
from app import app
from flask import render_template, request, session, redirect, url_for, flash, jsonify
from models.guidebook_model import *
from models.index_model import has_access
from models.dictionary_model import get_word_by_id, get_book_by_lesson
from models.constructor_model import is_author, delete_path
from utils import *
from flask_login import current_user
from controllers.edit_entry import get_text_data, get_txar_data, get_numb_data, is_json, get_task_data
from controllers.edit_entry import create_directory, create_file
from models.auth_model import get_user_by_id   


def get_points_for_task(book_id, entry_id, student_id):
    points = ''
    path = f'static/guidebooks/{book_id}/answers/{student_id}/{entry_id}'
    if os.path.exists(path):
        filename = 'points.dat'
        f = open(os.path.join(app.path, f'{path}/{filename}'), 'r')
        points = f.readline()
        f.close()
    return points

def set_points_for_task(book_id, entry_id, student_id, points):
    conn = get_db_connection()
    df_entry = get_entry_by_id(conn, entry_id)
    if points == '':
        points = 0
    if len(df_entry) > 0:
        correct_answer_info = get_correct_answer_info(book_id, entry_id)
        task_data = get_task_data(book_id, entry_id)
        if correct_answer_info is not None or task_data is None: return None
        max_points = int(task_data['points'])
        points = str(clamp(int(points), 0, max_points))
    else:
        return None
    path = f'static/guidebooks/{book_id}/answers/{student_id}/{entry_id}'
    if os.path.exists(path):
        filename = 'points.dat'
        create_file(path, filename, '')
        f = open(os.path.join(app.path, f'{path}/{filename}'), 'w')
        f.write(points)
        f.close()


def get_entry_template(book_id, entry_id):
    contents = ""
    path = os.path.join(app.path, 'templates/guidebooks/' + str(book_id) + '/entries/' + str(entry_id))
    if os.path.exists(path) and os.path.exists(path + '/contents.html'):
        f = codecs.open(path + '/contents.html', 'r', 'utf-8-sig')
        contents = f.read()
        f.close()
    return contents


def save_answer_info_for_user(book_id, entry_id, student_id, answer_info):
    path = f'static/guidebooks/{book_id}/answers/{student_id}/{entry_id}'
    filename = 'answer_info.dat'
    # create_directory('static/guidebooks/' + str(book_id) + '/entries/' + str(entry_id) + '/answers')
    create_directory(path)
    create_file(path, filename, '')
    f = open(os.path.join(app.path, f'{path}/{filename}'), 'w')
    json.dump(answer_info, f)
    f.close()


def get_user_speaker_n(book_id, entry_id, student_id):
    speaker_n = None
    answer_info = get_answer_info_by_user(book_id, entry_id, student_id)
    if answer_info is not None and 'speaker' in answer_info:
        speaker_n = answer_info['speaker']
    return speaker_n


def get_user_diag_partner(book_id, entry_id, student_id):
    partner_id = None
    answer_info = get_answer_info_by_user(book_id, entry_id, student_id)
    if answer_info is not None and 'partner' in answer_info.keys():
        partner_id = answer_info['partner']
    return partner_id


def validate_speaker_n(book_id, entry_id, student1_id, student2_id):
    user1_answer_info = get_answer_info_by_user(book_id, entry_id, student1_id)
    user2_answer_info = get_answer_info_by_user(book_id, entry_id, student2_id)
    # if both users sent info for this task
    if user1_answer_info is not None and user2_answer_info is not None:
        if 'speaker' in user1_answer_info and 'speaker' not in user2_answer_info:
            user1_speaker = user1_answer_info['speaker']
            if user1_speaker == '1':
                user2_answer_info['speaker'] = '2'
            else:
                user2_answer_info['speaker'] = '1'
        elif 'speaker' not in user1_answer_info and 'speaker' in user2_answer_info:
            user2_speaker = user2_answer_info['speaker']
            if user2_speaker == '1':
                user1_answer_info['speaker'] = '2'
            else:
                user1_answer_info['speaker'] = '1'
        elif 'speaker' in user1_answer_info and 'speaker' in user2_answer_info:
            user1_speaker = user1_answer_info['speaker']
            user2_speaker = user2_answer_info['speaker']
            if user1_speaker == user2_speaker:
                speakers = [1, 2]
                random.shuffle(speakers)
                user1_answer_info['speaker'] = speakers[0]
                user2_answer_info['speaker'] = speakers[1]
                save_answer_info_for_user(book_id, entry_id, student1_id, user1_answer_info)
                save_answer_info_for_user(book_id, entry_id, student2_id, user2_answer_info)
        else:
            speakers = [1, 2]
            random.shuffle(speakers)
            user1_answer_info['speaker'] = speakers[0]
            user2_answer_info['speaker'] = speakers[1]
            save_answer_info_for_user(book_id, entry_id, student1_id, user1_answer_info)
            save_answer_info_for_user(book_id, entry_id, student2_id, user2_answer_info)


def is_diag_connection_set(book_id, entry_id, student_id):
    answer_info = get_answer_info_by_user(book_id, entry_id, student_id)
    if answer_info is not None and 'partner' in answer_info.keys():
        partner_id = answer_info['partner']
        partner_answer_info = get_answer_info_by_user(book_id, entry_id, partner_id)
        if partner_answer_info is not None and 'partner' in partner_answer_info:
            partner_partner_id = partner_answer_info['partner']
            if str(partner_partner_id) == str(student_id):
                return True
    return False


def is_partner_valid(book_id, entry_id, student_id, partner_id):
    partner_answer_info = get_answer_info_by_user(book_id, entry_id, partner_id)
    if partner_answer_info is not None:
        # partner chose partner and it's user
        if 'partner' in partner_answer_info and str(partner_answer_info['partner']) == str(student_id):
            return True
        # partner chose partner and it's NOT user
        elif 'partner' in partner_answer_info and str(partner_answer_info['partner']) != str(student_id):
            return False
        # partner didn't choose partner
        else:
            return True
    # partner didn't send anything for this task yet
    else:
        return True


def get_df_rule_info(book_id, df_lesson_entries):
    df_rule_info = pd.DataFrame(
        columns=['lesson_id', 'entry_id', 'entry_name', 'header_align', 'header_size', 'in_contents_main'])
    for i, row in df_lesson_entries.iterrows():
        entry_id = row['entry_id']
        lesson_id = row['lesson_id']
        entry_type = row['entry_type_name']
        entry_name = row['entry_name']
        if entry_type == 'rule' or entry_type == 'rule_nic':
            task_data = get_task_data(book_id, entry_id)
            if task_data is not None:
                header_align = controllers.edit_entry.DEFAULT_HEADER_ALIGN
                header_size = controllers.edit_entry.DEFAULT_HEADER_SIZE
                in_contents_main = 'False'
                if 'header_align' in task_data.keys():
                    header_align = task_data['header_align']
                if 'header_size' in task_data.keys():
                    header_size = task_data['header_size']
                if 'in_contents_main' in task_data.keys():
                    in_contents_main = task_data['in_contents_main']
                new_row = [lesson_id, entry_id, entry_name, header_align, header_size, in_contents_main]
                df_rule_info.loc[len(df_rule_info)] = new_row
    return df_rule_info.drop_duplicates(subset="entry_id")


def is_task_autocheck_old(book_id, entry_id):
    check = False
    path = os.path.join(app.path, 'static/guidebooks/' + str(book_id) + '/entries/' + str(entry_id))
    if os.path.exists(path) and os.path.exists(path + '/info.dat'):
        if is_json(path + '/info.dat'):
            f = codecs.open(path + '/info.dat', 'r', 'utf-8-sig')
            task_data = json.load(f)
            if 'check' in task_data:
                check = task_data['check']
            f.close()
    return check
    
    
# if has correct answers then task is autocheck
def is_task_autocheck(book_id, entry_id):
    path = os.path.join(app.path, 'static/guidebooks/' + str(book_id) + '/answers/0/' + str(entry_id))
    if os.path.exists(path) and os.path.exists(path + '/answer_info.dat'):
        return True
    return False


def get_answer_info_by_user(book_id, entry_id, user_id):
    answer_info = None
    if user_id is not None:
        path = os.path.join(app.path, f'static/guidebooks/{book_id}/answers/{user_id}/{entry_id}/answer_info.dat')
        if os.path.exists(path):
            f = open(path, 'r')
            answer_info = json.load(f)
            f.close()
    return answer_info


def get_answer_info(book_id, entry_id):
    answer_info = None
    user_id = None
    conn = get_db_connection()
    if current_user.is_authenticated and 'role_type' in session and session['role_type'] == 'student':
        user_id = session['role_id']
    elif current_user.is_authenticated and 'role_type' in session and session['role_type'] == 'teacher' \
            and 'student_id' in session and session['student_id'] != '-1':
        user_id = session['student_id']
    elif current_user.is_authenticated and current_user.is_editor and is_author(conn, current_user.id, book_id):
        user_id = 0
    if user_id is not None:
        path = os.path.join(app.path, f'static/guidebooks/{book_id}/answers/{user_id}/{entry_id}/answer_info.dat')
        if os.path.exists(path):
            f = open(path, 'r')
            answer_info = json.load(f)
            f.close()
    return answer_info


def get_correct_answer_info(book_id, entry_id):
    answer_info = None
    user_id = 0  # answer is saved with user_id 0
    path = os.path.join(app.path, f'static/guidebooks/{book_id}/answers/{user_id}/{entry_id}/answer_info.dat')
    if os.path.exists(path):
        f = open(path, 'r')
        answer_info = json.load(f)
        f.close()
    return answer_info


def get_prepared_task_contents(book_id, entry_id, entry_type, conn):
    is_editing = False
    if current_user.is_authenticated and current_user.is_editor and is_author(conn, current_user.id, book_id):
        is_editing = True
    disabled = 'readonly'
    answer_info = get_answer_info(book_id, entry_id)
    correct_answer_info = get_correct_answer_info(book_id, entry_id)
    if (current_user.is_authenticated and 'role_type' in session and session['role_type'] == 'student' and answer_info is None
        or is_editing):
        disabled = ''
    contents = get_entry_template(book_id, entry_id)
    answer_count = contents.count('{answer_field}')
    notice_count = contents.count('{notice_button}')
    string_ans_count = f"<input type='hidden' form='form_save_{entry_id}' name='answer_count' value={answer_count}>"
    # replacing notice
    for i in range(notice_count):
        contents = contents.replace('{notice_button}',
                                    f"<button class='button-notice' id='buttonNotice_{entry_id}_{i}' "
                                    f"onclick='openNotice({entry_id}, {i})'>Развернуть</button>", 1)
        contents = contents.replace('{notice_body}',
                                    f"<div class='notice-div' id='divNotice_{entry_id}_{i}' style='display: none;'>", 1)
        contents = contents.replace('{/notice_body}',
                                    f"</div>", 1)
    # replacing answer fields
    match entry_type:
        case 'task_text':
            for i in range(contents.count('{answer_field}')):
                text_size = get_text_data(book_id, entry_id, 'size')
                text_maxlength = get_text_data(book_id, entry_id, 'maxlength')
                if is_editing:
                    text_maxlength = 999

                answer = ''
                answer_correct = None
                if answer_info is not None:
                    answer = answer_info[str(i)]
                if correct_answer_info is not None:
                    answer_correct = correct_answer_info[str(i)]

                color_red = "style='font-weight: bold; color: red; background-color: lightpink'"
                color_green = "style='font-weight: bold; color: green; background-color: lightgreen'"
                color = ''
                if answer_correct is not None and is_task_autocheck(book_id, entry_id) and current_user.is_authenticated \
                        and 'role_type' in session \
                        and (session['role_type'] == 'student' or session['role_type'] == 'teacher') \
                        and answer_info is not None:
                    if answer.strip().lower() == answer_correct.strip().lower():
                        color = color_green
                    else:
                        color = color_red
                        
                replaced_string = f"<input class='{'editorTextInput' if is_editing else ''}' type='text' form='form_save_{entry_id}' size={text_size} " \
                                  f"maxlength={text_maxlength} name='answer_{i}' {disabled} value='{answer}' {color} autocomplete='off'>"
                if i == answer_count - 1:
                    replaced_string += string_ans_count
                contents = contents.replace('{answer_field}', replaced_string, 1)

        case 'task_txar':
            for i in range(answer_count):
                txar_rows = get_txar_data(book_id, entry_id)

                answer = ''
                answer_correct = None
                if answer_info is not None:
                    answer = answer_info[str(i)]
                if correct_answer_info is not None:
                    answer_correct = correct_answer_info[str(i)]

                color_red = "style='font-weight: bold; color: red; background-color: lightpink'"
                color_green = "style='font-weight: bold; color: green; background-color: lightgreen'"
                color = ''
                if answer_correct is not None and is_task_autocheck(book_id, entry_id) and current_user.is_authenticated \
                        and 'role_type' in session \
                        and (session['role_type'] == 'student' or session['role_type'] == 'teacher') \
                        and answer_info is not None:
                    if answer.strip().lower() == answer_correct.strip().lower():
                        color = color_green
                    else:
                        color = color_red

                replaced_string = f"<textarea class='fullwidth resize-none' form='form_save_{entry_id}' rows={txar_rows} " \
                                  f"name='answer_{i}' {disabled} {color}>{answer}</textarea>"
                if i == answer_count - 1:
                    replaced_string += string_ans_count
                contents = contents.replace('{answer_field}', replaced_string, 1)

        case 'task_numb':
            for i in range(answer_count):
                numb_min = get_numb_data(book_id, entry_id, 'min')
                numb_max = get_numb_data(book_id, entry_id, 'max')

                answer = ''
                answer_correct = None
                if answer_info is not None:
                    answer = answer_info[str(i)]
                if correct_answer_info is not None:
                    answer_correct = correct_answer_info[str(i)]

                color_red = "style='font-weight: bold; color: red; background-color: lightpink'"
                color_green = "style='font-weight: bold; color: green; background-color: lightgreen'"
                color = ''
                if answer_correct is not None and is_task_autocheck(book_id, entry_id) and current_user.is_authenticated \
                        and 'role_type' in session \
                        and (session['role_type'] == 'student' or session['role_type'] == 'teacher') \
                        and answer_info is not None:
                    if answer.strip().lower() == answer_correct.strip().lower():
                        color = color_green
                    else:
                        color = color_red

                replaced_string = f"<input type='number' form='form_save_{entry_id}' min={numb_min} " \
                                  f"max={numb_max} size=2 name='answer_{i}' {disabled} value='{answer}' {color} autocomplete='off'>"
                if i == answer_count - 1:
                    replaced_string += string_ans_count
                contents = contents.replace('{answer_field}', replaced_string, 1)

        case 'task_chbx':
            disabled = 'disabled'
            if current_user.is_authenticated and \
            ('role_type' in session and session['role_type'] == 'student' and answer_info is None \
            or is_editing):
                disabled = ''
            for i in range(answer_count):

                answer = ''
                checked = ''
                answer_correct = None
                if answer_info is not None:
                    answer = answer_info[str(i)]
                if correct_answer_info is not None:
                    answer_correct = correct_answer_info[str(i)]
                if answer == 'on':
                    checked = 'checked'

                color_red = "style='font-weight: bold; color: red;'"
                color_green = "style='font-weight: bold; color: limegreen;'"
                color = ''
                if is_task_autocheck(book_id, entry_id) and current_user.is_authenticated \
                        and 'role_type' in session \
                        and (session['role_type'] == 'student' or session['role_type'] == 'teacher') \
                        and answer_info is not None:
                    if answer == answer_correct:
                        color = color_green
                    elif answer != answer_correct:
                        color = color_red
                        
                replaced_string = f"<input type='checkbox' form='form_save_{entry_id}' id='{entry_id}_answer_{i}' " \
                                  f" name='answer_{i}' {disabled} {checked}><label for='{entry_id}_answer_{i}' {color} autocomplete='off'>"
                if i == answer_count - 1:
                    replaced_string += string_ans_count
                contents = contents.replace('{answer_field}', replaced_string, 1)

        case 'task_radi':
            disabled = 'disabled'
            if current_user.is_authenticated \
            and ('role_type' in session and session['role_type'] == 'student' and answer_info is None \
                or is_editing):
                disabled = ''

            answer = ''
            answer_correct = None
            if answer_info is not None:
                answer = answer_info["0"]
            if correct_answer_info is not None:
                answer_correct = correct_answer_info["0"]

            color_red = "style='font-weight: bold; color: red;'"
            color_green = "style='font-weight: bold; color: limegreen;'"
            for i in range(answer_count):

                color = ''
                if is_task_autocheck(book_id, entry_id) and current_user.is_authenticated \
                        and 'role_type' in session \
                        and (session['role_type'] == 'student' or session['role_type'] == 'teacher') \
                        and answer_info is not None:
                    if answer == answer_correct and str(i) == answer:
                        color = color_green
                    elif answer != answer_correct and str(i) == answer:
                        color = color_red

                replaced_string = f"<input type='radio' form='form_save_{entry_id}' id='{entry_id}_answer_{i}'" \
                                  f" name='answer_0' value='{i}' {disabled} {'checked' if str(i) == answer else ''} autocomplete='off'>" \
                                  f"<label for='{entry_id}_answer_{i}' {color}>"
                if i == answer_count - 1:
                    replaced_string += string_ans_count
                contents = contents.replace('{answer_field}', replaced_string, 1)

        case 'task_ordr':
            disabled = 'disabled'
            if current_user.is_authenticated \
            and ('role_type' in session and session['role_type'] == 'student' and answer_info is None \
                or is_editing):
                disabled = ''

            CLEAN_SPAN = re.compile('<span.*?>')
            CLEAN_SPAN_CLOSE = re.compile('</span.*?>')
            contents = re.sub(CLEAN_SPAN, '', contents)
            contents = re.sub(CLEAN_SPAN_CLOSE, '', contents)
            new_contents = string_ans_count
            if answer_count > 0:
                new_contents += "<table class='table-ordr'><tbody>"
            for i in range(answer_count):
                default_statement = re.search('{answer_field}(.+?)<', contents).group(1)
                answer = ''
                answer_correct = None
                if answer_info is not None:
                    answer = answer_info[str(i)]
                if correct_answer_info is not None:
                    answer_correct = correct_answer_info[str(i)]
                if answer == '':
                    answer = default_statement

                color_red = "style='font-weight: bold; color: red; background-color: lightpink'"
                color_green = "style='font-weight: bold; color: green; background-color: lightgreen'"
                color = ''
                if answer_correct is not None and is_task_autocheck(book_id, entry_id) and current_user.is_authenticated \
                        and 'role_type' in session \
                        and (session['role_type'] == 'student' or session['role_type'] == 'teacher') \
                        and answer_info is not None:
                    if answer.strip().lower() == answer_correct.strip().lower():
                        color = color_green
                    else:
                        color = color_red
                
                # move buttons
                new_contents += f"<tr id='row_{entry_id}_{i}' {color}><td><input class='button-ordr' type='button' onclick='moveUp({entry_id}, {i})' {disabled} value='/\\'><br>" \
                                f"<input class='button-ordr' type='button' onclick='moveDown({entry_id}, {i})' {disabled} value='\\/'></td>"

                # statement (default or answer) and input
                new_contents += f"<td><p id='ordr_value_{entry_id}_{i}'>{answer}</p>" \
                                f"<input form='form_save_{entry_id}' type='hidden' id='answer_{entry_id}_{i}' name='answer_{i}' value='{answer}'></td></tr>"
                contents = contents.replace('{answer_field}', "", 1)
            contents = new_contents + "</tbody></table>"

        case 'task_audi':
            disabled = 'disabled'
            if current_user.is_authenticated and 'role_type' in session and session['role_type'] == 'student' and answer_info is None:
                disabled = ''

            for i in range(contents.count('{answer_field}')):
                answer = ''
                if answer_info and str(i) in answer_info is not None:
                    answer = answer_info[str(i)]
                replaced_string = f"<div class='answer-audio'>" \
                                  f"<audio class='audio-player' controls src='{answer}' id='audio_{entry_id}_{i}'" \
                                  f"></audio>"
                if disabled == '':
                    replaced_string += f"<br><input type='file' accept='audio/*' id='fileAnswer_{entry_id}_{i}' capture " \
                                       f"onchange='updateAudioTag({entry_id}, {i})' {disabled}/>" \
                                       f"<input type='button' id='buttonSave_{entry_id}_{i}' value='Отправить'" \
                                       f"onclick='saveAudio({book_id}, {entry_id}, {i})' {disabled}>" \
                                       f"</div>"

                if i == answer_count - 1:
                    replaced_string += string_ans_count
                contents = contents.replace('{answer_field}', replaced_string, 1)

        case 'task_diag':
            task_data = get_task_data(book_id, entry_id)
            diag_replies = controllers.edit_entry.DEFAULT_DIAG_REPLIES
            if task_data is not None and 'replies' in task_data.keys():
                diag_replies = task_data['replies']
            replaced_string = ''
            user_id = None
            partner_fio = 'Нет'
            cur_speaker_n = 'Не выбран'
            if current_user.is_authenticated and 'role_id' in session and 'role_type' in session and session['role_type'] == 'student':
                user_id = session['role_id']
            elif current_user.is_authenticated and 'role_type' in session and session['role_type'] == 'teacher' and 'student_id' in session:
                user_id = session['student_id']
            if user_id is not None:
                partner_id = get_user_diag_partner(book_id, entry_id, user_id)
                user_speaker_n = get_user_speaker_n(book_id, entry_id, user_id)
                if user_speaker_n is not None:
                    cur_speaker_n = f"№{user_speaker_n}"
                if partner_id is not None:
                    partner = get_user_by_id(conn, partner_id)
                    if partner is not None:
                        partner_fio = partner.name
            if current_user.is_authenticated and 'role_type' in session and (session['role_type'] == 'student' or session['role_type'] == 'teacher'):
                replaced_string += f"Собеседник: {partner_fio}<br>" \
                                   f"Номер: {cur_speaker_n}<br>"
            if current_user.is_authenticated and 'role_id' in session and 'role_type' in session and session['role_type'] == 'student' and not is_diag_connection_set(
                    book_id, entry_id, session['role_id']):
                df_students = get_other_students(conn, session['role_id'])
                replaced_string += f"Выберите собеседника: <select form='form_choose_partner_{entry_id}' name='partner'>" \
                                   f"<option value='' selected disabled>Выберите собеседника</option>"
                for i, partner in df_students.iterrows():
                    partner_answer_info = get_answer_info_by_user(book_id, entry_id, partner['user_id'])
                    if partner['user_id'] != session['role_id'] and (partner_answer_info is None
                                                                  or 'partner' in partner_answer_info.keys() and
                                                                  partner_answer_info['partner'] == str(session['role_id'])):
                        replaced_string += f"<option value='{partner['student_id']}'>{partner['user_name']}</option>"
                replaced_string += f"</select><br>Выберите желаемый номер:<select form='form_choose_partner_{entry_id}' name='speaker_n'>" \
                                   f"<option value='1'>№1</option>" \
                                   f"<option value='2'>№2</option>" \
                                   f"</select><br>" \
                                   f"<input form='form_choose_partner_{entry_id}' type='submit' value='Выбрать'>" \
                                   f"<input form='form_update_{entry_id}' type='submit' value='Обновить'><br><br>"

            else:
                if user_id is not None and answer_info is not None:
                    partner_id = get_user_diag_partner(book_id, entry_id, user_id)
                    # validate_speaker_n(entry_id, user_id, partner_id)
                    partner_answer_info = get_answer_info_by_user(book_id, entry_id, partner_id)
                    replaced_string += f"<input form='form_update_{entry_id}' type='submit' value='Обновить'><div></div>"
                    for i in range(int(diag_replies)):
                        answer = ""
                        disabled = 'disabled'
                        user_speaker_n = int(get_user_speaker_n(book_id, entry_id, user_id))
                        speaker = '2'
                        if (i % 2) == 0:
                            speaker = '1'
                        # user is speaker 1, even answers (0, 2, ...)
                        if (user_speaker_n % 2) == 0:
                            # and current answer is even so it is answer_field for the user
                            if (i % 2) != 0:
                                u = user_id
                                # if user did not submit audio for this answer
                                if answer_info is not None and f'{i}' not in answer_info.keys() \
                                        and 'role_type' in session and session['role_type'] == 'student':
                                    disabled = ''
                                # if user DID submit audio
                                elif answer_info is not None and f'{i}' in answer_info.keys():
                                    answer = answer_info[f'{i}']
                            # current answer is odd so it is answer_field for the partner
                            else:
                                u = partner_id
                                if partner_answer_info is not None and f'{i}' in partner_answer_info.keys():
                                    answer = partner_answer_info[f'{i}']
                        # user is speaker 2, odd answers (1, 3, ...)
                        else:
                            # and current answer is odd so it is answer_field for the user
                            if (i % 2) == 0:
                                u = user_id
                                # if user did not submit audio for this answer
                                if answer_info is not None and f'{i}' not in answer_info.keys() \
                                        and 'role_type' in session and session['role_type'] == 'student':
                                    disabled = ''
                                # if user DID submit audio
                                elif answer_info is not None and f'{i}' in answer_info.keys():
                                    answer = answer_info[f'{i}']
                            # current answer is even so it is answer_field for the partner
                            else:
                                u = partner_id
                                if partner_answer_info is not None and f'{i}' in partner_answer_info.keys():
                                    answer = partner_answer_info[f'{i}']
                        replaced_string += f"<label>Студент №{speaker}:</label>" \
                                           f"<p id='diag_message_{entry_id}_{i}'>Пожалуйста, подождите</p>" \
                                           f"<div id='answer_audio_{entry_id}_{i}' class='answer-audio' style='display: none;'>" \
                                           f"<audio class='audio-player-dialog' controls src='{answer}' id='audio_{entry_id}_{i}'" \
                                           f" u='{u}'></audio>"
                        # if not disabled add "Attach" and "Send" buttons
                        if disabled == '':
                            replaced_string += f"<br><input type='file' accept='audio/*' id='fileAnswer_{entry_id}_{i}' capture " \
                                               f"onchange='updateAudioTag({entry_id}, {i})' {disabled}/>" \
                                               f"<input type='button' id='buttonSave_{entry_id}_{i}' value='Отправить'" \
                                               f"onclick='saveAudio({book_id}, {entry_id}, {i})'></div><br><br>"
                        else:
                            replaced_string += "</div><br><br>"

            contents = contents.replace('{answer_field}', replaced_string, 1)
            contents = contents.replace('{answer_field}', '')
            
    # showing points
    task_data = get_task_data(book_id, entry_id)
    if task_data != None and 'points' in task_data and 'role_id' in session and 'role_type' in session and answer_info is not None:
        message = ''
        if session['role_type'] == 'student':
            points = get_points_for_task(book_id, entry_id, session['role_id'])
            # task without autocheck and not checked by teacher
            if points == '':
                message = f"<p><b>Баллы:</b> задание ожидает проверки преподавателем.</p>"
            # task with autocheck or checked by teacher
            else:
                max_points = int(task_data['points'])
                message = f"<p><b>Баллы:</b> {points}/{max_points}</p>"
        elif session['role_type'] == 'teacher' and 'student_id' in session and session['student_id'] != '-1':
            points = get_points_for_task(book_id, entry_id, session['student_id'])
            if points == '':
                points = 0
            max_points = int(task_data['points'])
            # getting lesson id for return url
            lesson_id = ''
            df_entry = get_entry_by_id(conn, entry_id)
            if len(df_entry) > 0:
                lesson_id = df_entry.loc[0, 'lesson_id']
            # teacher can change points for tasks without autocheck at any time
            if not is_task_autocheck(book_id, entry_id):
                message = f"<form id='form_points_{entry_id}' action='{url_for('teacher')}' method='post'>" \
                        f"<input type='hidden' name='set_points' value='1'>" \
                        f"<input type='hidden' name='entry_id' value='{entry_id}'>" \
                        f"<input type='hidden' name='book_id' value='{book_id}'>" \
                        f"<input type='hidden' name='return_url' value='{url_for('guidebook')}?b={str(book_id)}&l={str(lesson_id)}#{str(entry_id)}'>" \
                        f"</form>"
                message += f"<p><b>Баллы:</b> " \
                    f"<input type='number' form='form_points_{entry_id}' min=0 max={max_points} name='points' value={points}>" \
                    f"/{max_points}</p>" \
                    f"<input form='form_points_{entry_id}' type='submit' value='Сохранить баллы'><br><br>"
            # if task autocheck show points (teacher can't edit points)
            else:
                message = f"<p><b>Баллы:</b> {points}/{max_points}</p>"
            message += f"<form id='form_reset_{entry_id}' action='{url_for('teacher')}' method='post'>" \
                f"<input type='hidden' name='reset_answer' value='1'>" \
                f"<input type='hidden' name='entry_id' value='{entry_id}'>" \
                f"<input type='hidden' name='book_id' value='{book_id}'>" \
                f"<input type='submit' value='Сбросить ответ'>" \
                f"<input type='hidden' name='return_url' value='{url_for('guidebook')}?b={str(book_id)}&l={str(lesson_id)}#{str(entry_id)}'></form>"
        contents += message
    return contents


def get_prepared_rule_contents(book_id, entry_id, conn):
    contents = get_entry_template(book_id, entry_id)
    if 'role_type' not in session or session['role_type'] != 'student':
        return contents
    button = ""
    button_type = ''
    button_text = ''
    if is_entry_in_userbook(conn, entry_id, current_user.id):
        button_type = 'remove'
        button_text = 'Удалить из картотеки'
    else:
        button_type = 'add'
        button_text = 'Добавить в картотеку'
    button = f"<input type='button' class='rule_button_{entry_id}' button_type='{button_type}' onclick='UpdateUserbook(0, {entry_id})' value='{button_text}'>"
    contents = button + '<br>' + contents
    return contents

def get_entry_contents_dict(book_id, lesson_entries, conn):
    entry_dict = {}
    if lesson_entries is not None:
        for i, row in lesson_entries.iterrows():
            contents = ""
            if row['entry_type_name'] == 'task_text' \
                    or row['entry_type_name'] == 'task_txar' \
                    or row['entry_type_name'] == 'task_numb' \
                    or row['entry_type_name'] == 'task_chbx' \
                    or row['entry_type_name'] == 'task_radi' \
                    or row['entry_type_name'] == 'task_audi' \
                    or row['entry_type_name'] == 'task_diag'\
                    or row['entry_type_name'] == 'task_ordr':
                contents = get_prepared_task_contents(book_id, row['entry_id'], row['entry_type_name'], conn)
            elif row['entry_type_name'] == 'rule':
                contents = get_prepared_rule_contents(book_id, row['entry_id'], conn)
            else:
                contents = get_entry_template(book_id, row['entry_id'])
            entry_dict[row['entry_id']] = get_prepared_html(contents)
        return entry_dict


def get_task_can_submit_dict(book_id, lesson_entries):
    conn = get_db_connection()
    task_dict = {}
    if lesson_entries is not None:
        for i, row in lesson_entries.iterrows():
            if row['entry_type_name'] == 'task_text' \
                    or row['entry_type_name'] == 'task_txar' \
                    or row['entry_type_name'] == 'task_numb' \
                    or row['entry_type_name'] == 'task_chbx' \
                    or row['entry_type_name'] == 'task_radi' \
                    or row['entry_type_name'] == 'task_audi' \
                    or row['entry_type_name'] == 'task_diag'\
                    or row['entry_type_name'] == 'task_ordr':
                can_submit = False
                if (get_answer_info(book_id, row['entry_id']) is None
                    or current_user.is_editor and is_author(conn, current_user.id, book_id)):
                    can_submit = True
                task_dict[row['entry_id']] = can_submit
        return task_dict

def prepare_lesson_entries(book_id, lesson_entries):
    lesson_entries['is_autocheck'] = None
    for i, entry in lesson_entries.iterrows():
        lesson_entries.loc[i, 'is_autocheck'] = is_task_autocheck(book_id, entry['entry_id'])
    return lesson_entries

@app.route("/userbook", methods=['post'])
def userbook():
    if request.form.get('get_entry_contents'):
        entry_id = request.form.get('entry_id')
        lesson_id = request.form.get('lesson_id')
        response = jsonify("")
        if entry_id is not None:
            if entry_id != "":
                conn = get_db_connection()
                book = get_book_by_lesson(conn, lesson_id)
                if len(book) > 0:
                    book_id = book.iloc[0]['book_id']
                    response = jsonify(get_prepared_rule_contents(book_id, entry_id, conn))
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    if request.form.get('update_userbook_add'):
        userbook_entry_type = request.form.get('update_userbook_add')
        element_id = request.form.get('element_id')
        lesson_id  = request.form.get('lesson_id')
        response = jsonify("")
        if element_id is not None:
            if element_id != "":
                conn = get_db_connection()
                if userbook_entry_type == '0':
                    add_userbook_entry(conn, current_user.id, element_id)
                    df_entry = get_entry_by_id(conn, element_id)
                    if len(df_entry) > 0:
                        entry_name = df_entry.iloc[0]['entry_name']
                        response = jsonify(entry_name)
                else:
                    add_userbook_word(conn, current_user.id, element_id)
                    df_word = get_word_by_id(conn, element_id)
                    if len(df_word) > 0:
                        word_normal = df_word.iloc[0]['word_normal']
                        response = jsonify(word_normal)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    if request.form.get('update_userbook_remove'):
        userbook_entry_type = request.form.get('update_userbook_remove')
        element_id = element_id = request.form.get('element_id')
        response = jsonify("")
        if element_id is not None:
            if element_id != "":
                conn = get_db_connection()
                if userbook_entry_type == '0':
                    delete_userbook_entry(conn, current_user.id, element_id)
                else:
                    delete_userbook_word(conn, current_user.id, element_id)
                response = jsonify('success')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/teacher', methods=['post'])
def teacher():
    if not current_user.is_authenticated or 'role_type' not in session or session['role_type'] != 'teacher':
        return render_template('login.html', user=current_user, len=len, str=str)
        
    # "Save points" button pressed
    if request.form.get('set_points'):
        book_id = request.form.get("book_id")
        entry_id = request.form.get("entry_id")
        points = request.form.get("points")
        return_url = request.form.get("return_url")
        if book_id != None and entry_id != None and points != None and 'student_id' in session and session['student_id'] != '':
            set_points_for_task(book_id, entry_id, session['student_id'], points)
        if return_url != None:
            return redirect(return_url)
        else:
            return redirect(url_for('index'))
            
    # "Reset answer" button pressed
    if request.form.get('reset_answer'):
        book_id = request.form.get("book_id")
        entry_id = request.form.get("entry_id")
        return_url = request.form.get("return_url")
        if book_id != None and entry_id != None and 'student_id' in session and session['student_id'] != '':
            delete_path(f"static/guidebooks/{book_id}/answers/{session['student_id']}/{entry_id}")
        if return_url != None:
            return redirect(return_url)
        else:
            return redirect(url_for('index'))


@app.route('/guidebook', methods=['get', 'post'])
def guidebook():
    if not current_user.is_authenticated:
        return render_template('login.html', user=current_user, len=len, str=str)
        
    conn = get_db_connection()
        
    if (session.get('org_id') == None or not has_access(conn, session.get('org_id')))\
    and not current_user.is_admin and not current_user.is_editor:
        return redirect(url_for('index'))
        
    book_id = 0
    if request.values.get('b'):
        book_id = request.values.get('b')
    else:
        return redirect(url_for('index'))
        
    if not is_book_available(conn, book_id) and not is_author(conn, current_user.id, book_id):
        return redirect(url_for('index'))

    df_lessons = get_lessons(conn, book_id)
    df_rules = get_rules(conn, book_id)
    df_lesson_entries = None
    df_students = None
    df_groups = None
    df_words = None
    student = None
    df_comment_sections = None
    df_ubook_rules = get_userbook_entries(conn, current_user.id, book_id)
    df_ubook_words = get_userbook_words(conn, current_user.id, book_id)
    
    if len(df_lessons) < 1:
        return redirect(url_for('index'))

    lesson_id = 0
    if request.values.get('l'):
        lesson_id = request.values.get('l')
    else:
        if df_lessons.size > 0:
            lesson_id = df_lessons.iloc[0]['lesson_id']
            
    if 'role_type' in session and session['role_type'] == 'teacher':
        df_groups = get_teacher_groups(conn, session['org_id'], current_user.id)
    elif 'role_type' in session and session['role_type'] == 'student':
        df_groups = get_student_groups(conn, session['org_id'], current_user.id)

    # "Load answers" button pressed
    if request.form.get('form_choose'):
        student_id = request.form.get("student_id")
        session['student_id'] = student_id
        return redirect(url_for('guidebook') + f'?b={book_id}&l={lesson_id}')
    elif (current_user.is_authenticated 
        and 'role_type' in session and session['role_type'] == 'teacher'
        and 'org_id' in session):
        if 'student_id' not in session or session['student_id'] == '':
            session['student_id'] = None
        df_students = get_students_by_teacher_id(conn, session['org_id'])
        if 'student_id' in session and session['student_id'] != '-1':
            student = get_student_by_id(conn, session['student_id'])

    if int(lesson_id) > 0:
        df_lesson_entries = get_lesson_entries(conn, lesson_id)
        df_lesson_entries = prepare_lesson_entries(book_id, df_lesson_entries)
        df_words = get_words(conn, lesson_id)

    entry_contents_dict = get_entry_contents_dict(book_id, df_lesson_entries, conn)
    task_can_submit = get_task_can_submit_dict(book_id, df_lesson_entries)
    df_rule_info = get_df_rule_info(book_id, get_all_lessons_entries(conn, book_id))
    df_book = get_guidebook(conn, book_id)
    book_name = None
    if len(df_book) > 0:
        book_name = df_book.iloc[0]['book_name']
        
    is_editing_answers = False
    if current_user.is_editor and is_author(conn, current_user.id, book_id):
        is_editing_answers = True

    html = render_template(
        'guidebook.html',
        book_id=book_id,
        book_name=book_name,
        lesson_id=lesson_id,
        lessons=df_lessons,
        rules=df_rules,
        lesson_entries=df_lesson_entries,
        entry_contents=entry_contents_dict,
        task_can_submit=task_can_submit,
        students=df_students,
        groups=df_groups,
        student=student,
        rule_info=df_rule_info,
        user=current_user,
        role_type=session.get('role_type'),
        role_id=session.get('role_id'),
        words=df_words,
        ubook_rules=df_ubook_rules,
        ubook_words=df_ubook_words,
        is_editing_answers=is_editing_answers,
        len=len,
        str=str
    )
    return html
