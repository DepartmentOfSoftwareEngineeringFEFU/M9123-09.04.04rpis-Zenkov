from app import app
from flask import render_template, request, session, redirect, url_for, flash
from models.control_panel_model import *
from models.constructor_model import delete_path
from utils import get_db_connection
from flask_login import current_user


@app.route('/control_panel', methods=['get', 'post'])
def control_panel():

    if not current_user.is_authenticated or current_user.role_name != 'admin':
        return redirect(url_for('index'))

    conn = get_db_connection()

    # "Save" button pressed
    if request.form.get('save'):
        user_id = request.form.get("user_id")
        user_name = request.form.get("user_name")
        user_is_editor = request.form.get("user_is_editor")
        if user_name is None or user_name == "":
            flash('ФИО не может быть пустым', 'error')
            return redirect(url_for('control_panel'))
        update_user(conn, user_id, user_name, user_is_editor)
        flash('Данные пользователя успешно обновлены', 'success')
        return redirect(url_for('control_panel'))

    # "Reset password" button pressed
    if request.form.get('reset'):
        user_id = request.form.get("user_id")
        reset_password(conn, user_id)
        flash('Пароль пользователя успешно сброшен', 'success')
        return redirect(url_for('control_panel'))

    # "Delete" button pressed
    if request.form.get('delete'):
        user_id = request.form.get("user_id")
        df_books = get_guidebooks_all(conn)
        df_students = get_students_by_user_id(conn, user_id)
        for i, book in df_books.iterrows():
            for j, student in df_students.iterrows():
                delete_path('static/guidebooks/' + str(book['book_id']) + '/answers/' + str(student['student_id']))
        delete_user(conn, user_id)
        flash('Пользователь успешно удалён', 'success')
        return redirect(url_for('control_panel'))
        
    # "Add member" button pressed
    if request.form.get('add_member'):
        user_id = request.form.get("user_id")
        organization_id = request.form.get("organization_id")
        if organization_id != None and organization_id != "-1":
            if add_member(conn, user_id, organization_id):
                flash('Пользователь успешно добавлен в организацию', 'success')
            else:
                flash('Ошибка добавления в организацию: пользователь уже является членом данной организации', 'error')
        else:
            flash('Ошибка добавления в организацию: организация не была выбрана', 'error')
        return redirect(url_for('control_panel'))
        
    # "Remove member" button pressed
    if request.form.get('remove_member'):
        member_id = request.form.get("member_id")
        if member_id != None and member_id != "-1":
            df_books = get_guidebooks_all(conn)
            df_students = get_students_by_member_id(conn, member_id)
            for i, book in df_books.iterrows():
                for j, student in df_students.iterrows():
                    delete_path('static/guidebooks/' + str(book['book_id']) + '/answers/' + str(student['student_id']))
            delete_member(conn, member_id)
            flash('Пользователь успешно удален из организации', 'success')
        else:
            flash('Ошибка удаления из организации: организация не была выбрана', 'error')
        return redirect(url_for('control_panel'))

    # "Add organization"
    if request.form.get('add_org'):
        org_name = request.form.get("org_name")
        org_address = request.form.get("org_address")
        org_access = request.form.get("org_access")
        if org_name is not None and org_name != "":
            add_organization(conn, org_name, org_address, org_access)
            flash(f'Организация \"{org_name}\" создана', 'success')
        else:
            flash('Название организации не может быть пустым', 'error')
        return redirect(url_for('control_panel'))

    # "Save organization"
    if request.form.get('save_org'):
        org_id = request.form.get("org_id")
        org_name = request.form.get("org_name")
        org_address = request.form.get("org_address")
        org_access = request.form.get("org_access")
        if org_name is not None and org_name != "":
            update_organization(conn, org_id, org_name, org_address, org_access)
            flash(f'Информация об организации {org_id} обновлена', 'success')
        else:
            flash('Название организации не может быть пустым', 'error')
        return redirect(url_for('control_panel'))
        
    # "Add moderator"    
    if request.form.get('add_moderator'):
        org_id = request.form.get("org_id")
        member_id = request.form.get("member_id")
        if member_id != None and member_id != "-1":
            if add_moderator(conn, member_id, org_id):
                flash(f'Модератор для организации {org_id} успешно добавлен', 'success')
            else:
                flash('Ошибка добавления модератора: пользователь уже является модератором данной организации', 'error')
        else:
            flash('Ошибка добавления модератора: пользователь не был выбран', 'error')
        return redirect(url_for('control_panel'))
        
    # "Remove moderator"    
    if request.form.get('remove_moderator'):
        org_id = request.form.get("org_id")
        moderator_id = request.form.get("moderator_id")
        if moderator_id != None and moderator_id != "-1":
            delete_moderator(conn, moderator_id)
            flash(f'Модератор успешно удален', 'success')
        else:
            flash('Ошибка удаления модератора: пользователь не был выбран', 'error')
        return redirect(url_for('control_panel'))

    # "Delete organization"
    #if request.form.get('delete_org'):
    #    org_id = request.form.get("org_id")
    #    delete_organization(conn, org_id)
    #    flash(f'Организация {org_id} удалена. '
    #          f'Информация о модераторах, группах, студентах и преподавателях данной организации, а также ответах, комментариях и сообщениях чата была удалена', 'success')
    #    return redirect(url_for('control_panel'))

    df_users = get_users(conn)
    df_organizations = get_organizations(conn)
    print(df_organizations)

    html = render_template(
        'control_panel.html',
        users=df_users,
        organizations=df_organizations,
        user=current_user,
        len=len,
        str=str
    )
    return html
