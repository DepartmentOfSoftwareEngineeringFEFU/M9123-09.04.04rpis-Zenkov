import os
from app import app
from flask import render_template, request, session, redirect, url_for, flash
from models.edit_dictionary_model import *
from models.constructor_model import get_book, is_author, delete_path
from controllers.constructor import create_empty_file, create_directory
from controllers.dictionary import stem_text, get_part_of_speech, get_prepared_text
from utils import get_db_connection
from flask_login import current_user


@app.route('/edit_dictionary', methods=['get', 'post'])
def edit_dictionary():

    if not current_user.is_authenticated or not current_user.is_editor:
        return redirect(url_for('index'))

    conn = get_db_connection()
    book_id = request.args.get('b')
    lesson_id = request.args.get('l')
    
    if book_id == None or len(get_book(conn, book_id)) < 1\
    or lesson_id == None or len(get_lesson(conn, lesson_id)) < 1:
        if book_id == None:
            book_id = ""
        return redirect(url_for('constructor') + '?b=' + str(book_id))
    
    if not is_author(conn, current_user.id, book_id):
        return redirect(url_for('constructor'))
    
    df_words = get_words(conn, lesson_id)
    df_pos = get_parts_of_speech(conn)


    # "Add word" button pressed
    if request.form.get('add_word'):
        lesson_id = request.form.get("lesson_id")
        # word_speech_id = request.form.get("word_speech_id")
        word = request.form.get("word")
        if word == None or word == "":
            flash('Слово не было введено', 'error')
            return redirect(url_for('edit_dictionary') + '?b=' + str(book_id) + '&l=' + str(lesson_id))
        word = get_prepared_text(word)
        word_speech_tag = get_part_of_speech(word)
        conn = get_db_connection()
        df_word_speech = get_word_speech_by_name(conn, word_speech_tag)
        if len(df_word_speech) < 1:
            flash('Произошла ошибка при добавлении слова', 'error')
            return redirect(url_for('edit_dictionary') + '?b=' + str(book_id) + '&l=' + str(lesson_id))
        word_speech_id = str(df_word_speech.loc[0, 'word_speech_id'])
        word_stemmed = stem_text(word)
        if len(get_word(conn, word_stemmed, word_speech_id, lesson_id)) > 0:
            flash('Слово уже существует в словаре данного урока', 'error')
            return redirect(url_for('edit_dictionary') + '?b=' + str(book_id) + '&l=' + str(lesson_id))
        word_id = add_word(conn, lesson_id, word_stemmed, word, word_speech_id)
        create_directory('templates/guidebooks/' + str(book_id) + '/dictionary/')
        create_directory('templates/guidebooks/' + str(book_id) + '/dictionary/' + str(word_id))
        create_empty_file('templates/guidebooks/' + str(book_id) + '/dictionary/' + str(word_id), 'contents.html')
        flash('Слово успешно добавлено в словарь', 'success')
        return redirect(url_for('edit_dictionary') + '?b=' + str(book_id) + '&l=' + str(lesson_id))

    # "Delete word" button pressed
    if request.form.get('remove_word'):
        word_id = request.form.get("word_id")
        remove_word(conn, word_id)
        delete_path('templates/guidebooks/' + book_id + '/dictionary/' + str(word_id))
        flash('Слово успешно удалено', 'success')
        return redirect(url_for('edit_dictionary') + '?b=' + str(book_id) + '&l=' + str(lesson_id))

    html = render_template(
        'edit_dictionary.html',
        book_id=book_id,
        lesson_id=lesson_id,
        dict_words=df_words,
        parts_of_speech=df_pos,
        user=current_user,
        len=len,
        str=str
    )
    return html
