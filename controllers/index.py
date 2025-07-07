import pandas
from flask import render_template, request, session, redirect, url_for, flash
from flask_login import current_user
from app import app
from models.index_model import *
from utils import get_db_connection


@app.route('/', methods=['get', 'post'])
def index():
    if not current_user.is_authenticated:
        return render_template('login.html', user=current_user, len=len, str=str)
        
    conn = get_db_connection()
    user_groups = get_user_groups(conn, current_user.id)
    books = None
    if current_user.is_admin:
        books = get_all_books(conn)
    elif current_user.is_editor:
        available_books = get_available_books(conn)
        editor_books = get_editor_books(conn, current_user.id)
        books = pandas.concat([available_books, editor_books], axis=0).drop_duplicates().reset_index()
    else:
        books = get_available_books(conn)
    
    current_access = False
    if session.get('org_id') != None:
        current_access = has_access(conn, session.get('org_id'))
    
    # Group selected
    if request.form.get('group_selected'):
        group_info = request.form.get("group_info")
        if group_info != None and group_info != "-1":
            organization_id, role_id, role_type = request.form.get("group_info").split(',')
            if has_access(conn, organization_id):
                current_access = True
                session['org_id'] = organization_id
                session['role_id'] = role_id
                session['role_type'] = role_type
                session['student_id'] = None
            else:
                current_access = False
                session['org_id'] = None
                session['role_id'] = None
                session['role_type'] = None
                session['student_id'] = None
                flash('Ошибка входа: у организации нет доступа к системе', 'error')
        else:
            current_access = False
            session['org_id'] = None
            session['role_id'] = None
            session['role_type'] = None
            session['student_id'] = None
        return redirect(url_for('index')) 
        
    if current_user.is_admin or current_user.is_editor:
        current_access = True
        
    html = render_template(
        'index.html',
        user=current_user,
        groups=user_groups,
        books=books,
        has_access=current_access,
        org_id=session.get('org_id'),
        role_id=session.get('role_id'),
        role_type=session.get('role_type'),
        len=len,
        str=str
    )
    return html
