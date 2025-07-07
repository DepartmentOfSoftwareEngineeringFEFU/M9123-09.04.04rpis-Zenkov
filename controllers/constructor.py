from app import app
from flask import render_template, request, session, redirect, url_for, flash
from models.constructor_model import *
from utils import get_db_connection
import os
from flask_login import current_user


def create_directory(local_path):
    path = os.path.join(app.path, local_path)
    if not os.path.exists(path):
        os.mkdir(path)


def create_empty_file(local_path, filename):
    path = os.path.join(app.path, local_path)
    if os.path.exists(path):
        if not os.path.exists(path + '/files'):
            create_directory(local_path + '/files')
        if not os.path.exists(path + '/' + filename):
            f = open(path + '/' + filename, 'w+')
            f.write('')
            f.close()


def create_file(local_path, filename, contents):
    path = os.path.join(app.path, local_path)
    if os.path.exists(path):
        if os.path.exists(path + '/' + filename):
            os.remove(path + '/' + filename)
        f = open(path + '/' + filename, 'w+')
        f.write(contents)
        f.close()


@app.route('/constructor', methods=['get', 'post'])
def constructor():

    if not current_user.is_authenticated or (not current_user.is_editor and not current_user.is_admin):
        return redirect(url_for('index'))

    conn = get_db_connection()
    
    # "Add guidebook" button pressed
    if request.form.get('add_guidebook') and current_user.is_editor:
        book_name = request.form.get("book_name")
        if book_name is None or book_name == '':
            flash('Название пособия не может быть пустым', 'error')
        else:
            book_id = add_guidebook(conn, book_name)
            add_editor(conn, book_id, current_user.id)
            create_directory('templates/guidebooks/')
            create_directory('templates/guidebooks/' + str(book_id))
            create_directory('static/guidebooks/')
            create_directory('static/guidebooks/' + str(book_id))
            create_directory('static/guidebooks/' + str(book_id) + '/files')
            create_directory('static/guidebooks/' + str(book_id) + '/answers')
            create_directory('static/guidebooks/' + str(book_id) + '/entries/')
            create_directory('static/guidebooks/' + str(book_id) + '/dictionary')
            flash('Новое пособие успешно создано', 'success')
        return redirect(url_for('constructor'))
    
    # "Save guidebook" button pressed (for admin)
    if request.form.get('update_guidebook') and current_user.is_admin:
        book_id = request.form.get("book_id")
        book_name = request.form.get("book_name")
        book_visible = request.form.get("book_visible")
        if (book_name is None or book_name == '' or book_visible is None or book_visible == ''
            or book_id is None or book_id == ''):
            flash('Ошибка сохранения пособия', 'error')
        else:
            update_guidebook(conn, book_id, book_name, book_visible)
            flash('Изменения сохранены', 'success')
        return redirect(url_for('constructor'))
        
    # "Save guidebook" button pressed (for editor)
    if request.form.get('update_guidebook') and not current_user.is_admin:
        book_id = request.form.get("book_id")
        book_name = request.form.get("book_name")
        if book_id is None or book_id == '' or book_name is None or book_name == '':
            flash('Ошибка сохранения пособия', 'error')
        else:
            update_guidebook_name(conn, book_id, book_name)
            flash('Изменения сохранены', 'success')
        return redirect(url_for('constructor'))
        
    # "Remove guidebook" button pressed
    if request.form.get('remove_guidebook'):
        book_id = request.form.get("book_id")
        if book_id is not None and book_id != '':
            remove_guidebook(conn, book_id)
            flash('Пособие успешно удалено', 'success')
        return redirect(url_for('constructor'))
        
    # "Add editor" button pressed
    if request.form.get('add_editor') and current_user.is_admin:
        book_id = request.form.get("book_id")
        user_id = request.form.get("user_id")
        if (book_id is not None and book_id != ''
            and user_id is not None and user_id != '' and user_id != '-1'):
            if is_true_author(conn, user_id, book_id):
                flash('Пользователь уже является редактором пособия', 'error')
            else:
                add_editor(conn, book_id, user_id)
                flash('Редактор успешно добавлен', 'success')
        else:
            flash('Ошибка добавления редактора: пользователь не был выбран', 'error')
        return redirect(url_for('constructor'))
        
    # "Remove editor" button pressed
    if request.form.get('remove_editor') and current_user.is_admin:
        print('REMOVE EDITOR')
        book_id = request.form.get("book_id")
        editor_id = request.form.get("editor_id")
        if (book_id is not None and book_id != ''
            and editor_id is not None and editor_id != ''):
                remove_editor(conn, book_id, editor_id)
                flash('Редактор успешно удален', 'success')
        else:
            flash('Произошла ошибка при удалении редактора', 'error')
        return redirect(url_for('constructor'))
        
    book_id = request.args.get('b')
    if book_id == None or len(get_book(conn, book_id)) < 1:
        book_id = None
        user_books = None
        editors = get_editors(conn)
        if current_user.is_admin:
            user_books = get_all_guidebooks(conn)
        else:
            user_books = get_user_guidebooks(conn, current_user.id)
        return render_template(
            'constructor.html',
            user=current_user,
            book_id=book_id,
            books=user_books,
            editors=editors,
            len=len,
            str=str
        )
    
    if not is_author(conn, current_user.id, book_id):
        flash('Нет доступа на редактирование пособия', 'error')
        book_id = None
        user_books = None
        if current_user.is_admin:
            user_books = get_all_guidebooks(conn)
        else:
            user_books = get_user_guidebooks(conn, current_user.id)
        return render_template(
            'constructor.html',
            user=current_user,
            book_id=book_id,
            books=user_books,
            len=len,
            str=str
        )
    
    df_lessons = get_lessons(conn, book_id)
    df_lesson_entries = get_lesson_entries(conn, book_id)

    # "Save" button pressed
    if request.form.get('save'):
        for i, lesson in df_lessons.iterrows():
            lesson_id = lesson["lesson_id"]
            lesson_name = request.form.get("name_l_{}".format(lesson_id))
            lesson_index = request.form.get("index_l_{}".format(lesson_id))
            update_lesson(conn, lesson_id, lesson_name, lesson_index)
        for i, lesson_entry in df_lesson_entries.iterrows():
            lesson_id = lesson_entry["lesson_id"]
            entry_id = lesson_entry["entry_id"]
            lesson_entry_index = request.form.get("index_e_{}".format(entry_id))
            update_entry_index(conn, lesson_id, entry_id, lesson_entry_index)
        flash('Изменения успешно сохранены', 'success')
        return redirect(url_for('constructor') + '?b=' + str(book_id))

    # "Add lesson" button pressed
    if request.form.get('add_lesson'):
        lesson_index = request.form.get("lesson_index")
        add_lesson(conn, book_id, "Новый урок", lesson_index)
        flash('Новый урок успешно добавлен', 'success')
        return redirect(url_for('constructor') + '?b=' + str(book_id))

    # "Delete lesson" button pressed
    if request.form.get('remove_lesson'):
        lesson_id = request.form.get("lesson_id")
        remove_lesson(conn, book_id, lesson_id)
        flash('Урок успешно удалён', 'success')
        return redirect(url_for('constructor') + '?b=' + str(book_id))

    # "Delete entry" button pressed
    if request.form.get('remove_entry'):
        entry_id = request.form.get("entry_id")
        remove_lesson_entry_eid(conn, book_id, entry_id)
        flash('Запись успешно удалена', 'success')
        return redirect(url_for('constructor') + '?b=' + str(book_id))

    # "Add entry" button pressed
    if request.form.get('add_entry'):
        lesson_id = request.form.get("lesson_id")
        lesson_entry_index = request.form.get("lesson_entry_index")
        entry_id = add_entry(conn, lesson_id, "Новая запись", "none", lesson_entry_index)
        create_directory('static/guidebooks/' + str(book_id))
        create_directory('static/guidebooks/' + str(book_id) + '/files')
        create_directory('static/guidebooks/' + str(book_id) + '/answers')
        create_directory('static/guidebooks/' + str(book_id) + '/entries/')
        create_directory('static/guidebooks/' + str(book_id) + '/dictionary')
        create_directory('static/guidebooks/' + str(book_id) + '/entries/' + str(entry_id))
        create_directory('templates/guidebooks/' + str(book_id))
        create_directory('templates/guidebooks/' + str(book_id) + '/entries/')
        create_directory('templates/guidebooks/' + str(book_id) + '/entries/' + str(entry_id))
        create_empty_file('templates/guidebooks/' + str(book_id) + '/entries/' + str(entry_id), 'contents.html')
        flash('Новая запись успешно создана', 'success')
        return redirect(url_for('constructor') + '?b=' + str(book_id))

    html = render_template(
        'constructor.html',
        book_id=book_id,
        lessons=df_lessons,
        lesson_entries=df_lesson_entries,
        user=current_user,
        len=len,
        str=str
    )
    return html
