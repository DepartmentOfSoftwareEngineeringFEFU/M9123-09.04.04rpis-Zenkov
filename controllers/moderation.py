from app import app
from flask import render_template, request, session, redirect, url_for, flash
from models.moderation_model import *
from models.control_panel_model import get_guidebooks_all
from models.constructor_model import delete_path
from utils import get_db_connection
from flask_login import current_user


@app.route('/moderation', methods=['get', 'post'])
def moderation():

    if not current_user.is_authenticated or not current_user.is_moderator:
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    df_organizations = get_user_organizations(conn, current_user.id)
        
    # checking if organization ID is provided 
    # and user is a moderator of this organization
    organization_id = request.args.get('o')
    if organization_id == None or not is_moderator(conn, current_user.id, organization_id):
        organization_id = None
        return render_template(
            'moderation.html',
            user=current_user,
            organization_id=organization_id,
            organizations=df_organizations,
            len=len,
            str=str
        )
        
    # "Remove group" button pressed
    if request.form.get('remove_group'):
        group_id = request.form.get("group_id")
        df_books = get_guidebooks_all(conn)
        df_students = get_group_students(conn, group_id)
        for i, book in df_books.iterrows():
            for j, student in df_students.iterrows():
                delete_path('static/guidebooks/' + str(book['book_id']) + '/answers/' + str(student['student_id']))
        delete_group(conn, group_id)
        flash('Группа успешно удалена', 'success')
        return redirect(url_for('moderation')+f'?o={organization_id}')
        
    # "Add group" button pressed
    if request.form.get('add_group'):
        group_name = request.form.get("group_name")
        organization_id = request.form.get("organization_id")
        if group_name != None and group_name != "":
            if add_group(conn, group_name, organization_id):
                flash('Группа успешно создана', 'success')
            else:
                flash('Ошибка создания группы: группа с введённым номером уже существует', 'error')
        else:
            flash('Ошибка создания группы: номер группы не может быть пустым', 'error')
        return redirect(url_for('moderation')+f'?o={organization_id}')    
        
    # "Add teacher" button pressed
    if request.form.get('add_teacher'):
        group_id = request.form.get("group_id")
        member_id = request.form.get("member_id")
        if member_id != None and member_id != "-1":
            if add_teacher(conn, member_id, group_id):
                flash('Преподаватель успешно добавлен в группу', 'success')
            else:
                flash('Ошибка добавления преподавателя: пользователь уже является преподавателем или студентом в данной группе', 'error')
        else:
            flash('Ошибка добавления преподавателя: пользователь не выбран', 'error')
        return redirect(url_for('moderation')+f'?o={organization_id}')   
        
    # "Add student" button pressed
    if request.form.get('add_student'):
        group_id = request.form.get("group_id")
        member_id = request.form.get("member_id")
        if member_id != None and member_id != "-1":
            student_id = add_student(conn, member_id, group_id)
            if student_id != None:
                flash('Студент успешно добавлен в группу', 'success')
            else:
                flash('Ошибка добавления студента: пользователь уже является преподавателем или студентом в данной группе', 'error')
        else:
            flash('Ошибка добавления студента: пользователь не выбран', 'error')
        return redirect(url_for('moderation')+f'?o={organization_id}')
        
    # "Remove teacher" button pressed
    if request.form.get('remove_teacher'):
        teacher_id = request.form.get("teacher_id")
        if teacher_id != None and teacher_id != "-1":
            delete_teacher(conn, teacher_id)
            flash('Преподаватель успешно исключён из группы', 'success')
        else:
            flash('Ошибка исключения преподавателя: пользователь не выбран', 'error')
        return redirect(url_for('moderation')+f'?o={organization_id}')
        
    # "Remove student" button pressed
    if request.form.get('remove_student'):
        student_id = request.form.get("student_id")
        if student_id != None and student_id != "-1":
            delete_student(conn, student_id)
            flash('Студент успешно исключён из группы', 'success')
        else:
            flash('Ошибка исключения студента: пользователь не выбран', 'error')
        return redirect(url_for('moderation')+f'?o={organization_id}')

    df_members = get_members(conn, organization_id)
    df_groups = get_groups(conn, organization_id)
    print('LENLENLEN')
    print(df_groups)

    html = render_template(
        'moderation.html',
        members=df_members,
        organization_id=organization_id,
        organizations=df_organizations,
        groups=df_groups,
        user=current_user,
        len=len,
        str=str
    )
    return html
