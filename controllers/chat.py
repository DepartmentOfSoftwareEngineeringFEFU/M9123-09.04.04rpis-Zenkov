import json
import os
import codecs
import re
import time
import pandas
from flask import request, session, redirect, url_for, jsonify
from flask_login import current_user
from app import app
from utils import *
from models.chat_model import *
from models.guidebook_model import get_student_by_id
MESSAGES_TO_LOAD = 15


def is_user_in_group(conn, user, group_id):
    return is_group_student(conn, user.id, group_id) or is_group_teacher(conn, user.id, group_id)


def remove_html_tags(text):
    clean = re.compile('<[^>]+>')
    return re.sub(clean, '', text)
    

def prepare_messages(messages):
    if not isinstance(messages, pandas.DataFrame) or len(messages) < 1:
        return ''
    html = ''
    for i, message in messages.iterrows():
        message_string = f"<div class='chatMessage'>" \
        f"<div class='messageTitle'>" \
        f"<span class='messageTime' time={message['message_datetime']}></span>" \
        f"<br><span class='messageAuthor'>{message['user_name']}</span></div>" \
        f"<span class='messageContent'>{message['message_content']}</span></div>"
        html += message_string
    return html
    
def prepare_comments(comments):
    if not isinstance(comments, pandas.DataFrame) or len(comments) < 1:
        return ''
    html = ''
    for i, comment in comments.iterrows():
        message_string = f"<div class='chatMessage'>" \
        f"<div class='messageTitle'>" \
        f"<span class='messageTime' time={comment['comment_datetime']}></span>" \
        f"<br><span class='messageAuthor'>{comment['user_name']}</span></div>" \
        f"<span class='messageContent'>{comment['comment_content']}</span></div>"
        html += message_string
    return html

@app.route("/chat", methods=['post'])
def chat():

    if request.form.get('send_comment'):
        comment = request.form.get('comment')
        entry_id = request.form.get('entry_id')
        student_id = request.form.get('student_id')
        response = jsonify("")
        if (comment is not None 
            and comment != ''
            and entry_id is not None
            and entry_id != ''
            and student_id is not None
            and student_id != ''):
                conn = get_db_connection()
                df_student = get_student_by_id(conn, student_id)
                if df_student is not None and len(df_student) > 0 and is_user_in_group(conn, current_user, df_student.loc[0, 'group_id']):
                    prepared_comment = remove_html_tags(comment)
                    if prepared_comment != '':
                        add_comment(conn, entry_id, student_id, current_user.id, comment, time.time())
                        response = jsonify("success")
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    if request.form.get('get_comments'):
        entry_id = request.form.get('entry_id')
        student_id = request.form.get('student_id')
        message_time = request.form.get('time')
        get_type = request.form.get('get_type') 
        response = jsonify("err")
        if (entry_id is not None and entry_id != '' and student_id is not None and student_id != ''):
            conn = get_db_connection()
            df_student = get_student_by_id(conn, student_id)
            if df_student is not None and len(df_student) > 0 and is_user_in_group(conn, current_user, df_student.loc[0, 'group_id']):
                comments = ''
                html = ''
                if get_type == 'after':
                    comments = get_comments_after(conn, entry_id, student_id, message_time)
                    html = prepare_comments(comments)
                elif get_type == 'all':
                    comments = get_comments(conn, entry_id, student_id)
                    html = prepare_comments(comments)
                    if html == '':
                        html = '<p>Нет комментариев.</p>'
                response = jsonify(html)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    if request.form.get('send_message'):
        message = request.form.get('message')
        group_id = request.form.get('group_id')
        response = jsonify("")
        if (message is not None 
            and message != ''
            and group_id is not None
            and group_id != ''):
                conn = get_db_connection()
                if is_user_in_group(conn, current_user, group_id):
                    prepared_message = remove_html_tags(message)
                    if prepared_message != '':
                        message_id = add_message(conn, current_user.id, group_id, prepared_message, time.time())
                        df_message = get_message_by_id(conn, message_id)
                        response = jsonify(prepare_messages(df_message))
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    if request.form.get('get_messages'):
        group_id = request.form.get('group_id')
        message_time = request.form.get('time')
        get_type = request.form.get('get_type') # before, after or last
        response = jsonify("err")
        if (group_id is not None and group_id != ''):
            conn = get_db_connection()
            if is_user_in_group(conn, current_user, group_id):
                messages = ''
                if get_type == 'after':
                    messages = get_messages_after(conn, group_id, message_time)
                    html = prepare_messages(messages)
                elif get_type == 'before':
                    messages = get_messages_before(conn, group_id, message_time, MESSAGES_TO_LOAD)
                    html = prepare_messages(messages)
                elif get_type == 'last':
                    messages = get_last_messages(conn, group_id, MESSAGES_TO_LOAD)
                    messages = messages.sort_values(by='message_datetime')
                    html = prepare_messages(messages)
                elif get_type == 'all':
                    messages = get_all_messages(conn, group_id)
                    html = prepare_messages(messages)
                    if html == '':
                        html = '<p>Нет сообщений.</p>'
                response = jsonify(html)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
