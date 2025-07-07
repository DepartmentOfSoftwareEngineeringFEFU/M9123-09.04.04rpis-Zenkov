import codecs
import os
from flask import render_template, request, session, redirect, url_for, flash
from flask_login import current_user
from app import app
from utils import get_db_connection
from controllers.edit_entry import get_all_images, get_all_videos, get_all_audios
from controllers.dictionary import get_part_of_speech, stem_text, get_prepared_text
from models.edit_word_model import *
from models.constructor_model import get_book, is_author
from models.edit_dictionary_model import get_lesson, remove_word, get_word_speech_by_name


def update_contents(book_id, word_id, word_contents):
    path = os.path.join(app.path, 'templates/guidebooks/' + str(book_id) + '/dictionary/' + str(word_id))
    if os.path.exists(path) and os.path.exists(path + '/contents.html'):
        f = codecs.open(path + '/contents.html', 'w', 'utf-8-sig')
        f.write(word_contents)
        f.close()


@app.route('/edit_word', methods=['GET', 'POST'])
def edit_word():

    if not current_user.is_authenticated or not current_user.is_editor:
        return redirect(url_for('index'))

    conn = get_db_connection()
    book_id = request.args.get('b')
    lesson_id = request.args.get('l')
    word_id = request.args.get('w')
    
    if book_id == None or len(get_book(conn, book_id)) < 1\
    or lesson_id == None or len(get_lesson(conn, lesson_id)) < 1\
    or word_id == None or len(get_word(conn, word_id)) < 1:
        return redirect(url_for('constructor'))
    
    if not is_author(conn, current_user.id, book_id):
        return redirect(url_for('constructor'))
        
    if not os.path.isfile('templates/guidebooks/' + str(book_id) + '/dictionary/' + str(word_id) + '/contents.html'):
        return redirect(url_for('edit_dictionary') + '?b=' + str(book_id) + '&l=' + str(lesson_id))
        
    df_word = get_word(conn, word_id)
    df_synonyms = get_synonyms(conn, word_id)

    # "Save" button pressed
    if request.form.get('save'):
        word_id = request.form.get("word_id")
        word_contents = request.form.get("entry_contents")
        update_contents(book_id, word_id, word_contents)
        return redirect(url_for('edit_word') + '?b=' + str(book_id) + '&l=' + str(lesson_id) + '&w=' + str(word_id))

    # "Delete image" button pressed
    if request.form.get('delete_image') or request.form.get('delete_video'):
        filename = request.form.get("file")
        if filename is not None:
            os.remove(os.path.join(app.path, 'static/guidebooks/' + book_id + '/files/' + filename))
            flash('Файл успешно удалён', 'success')
            return redirect(url_for('edit_word') + '?b=' + str(book_id) + '&l=' + str(lesson_id) + '&w=' + str(word_id))
        else:
            flash('Файл для удаления не был выбран', 'error')
            return redirect(url_for('edit_word') + '?b=' + str(book_id) + '&l=' + str(lesson_id) + '&w=' + str(word_id))

    # "Add synonym" button pressed
    if request.form.get('add_synonym'):
        print('add synonym')
        reference_word_id = request.form.get("reference_word_id")
        lesson_id = request.form.get("lesson_id")
        word = request.form.get("word")
        if word == None or word == "":
            flash('Слово не было введено', 'error')
            return redirect(url_for('edit_word') + '?b=' + str(book_id) + '&l=' + str(lesson_id) + '&w=' + str(word_id))
        word = get_prepared_text(word)
        word_speech_tag = get_part_of_speech(word)
        conn = get_db_connection()
        df_word_speech = get_word_speech_by_name(conn, word_speech_tag)
        if len(df_word_speech) < 1:
            flash('Произошла ошибка при добавлении слова', 'error')
            return redirect(url_for('edit_word') + '?b=' + str(book_id) + '&l=' + str(lesson_id) + '&w=' + str(word_id))
        word_speech_id = str(df_word_speech.loc[0, 'word_speech_id'])
        word_stemmed = stem_text(word)
        if len(get_word_by_name_and_speech(conn, word_stemmed, word_speech_id, lesson_id)) > 0:
            flash('Слово уже существует в словаре данного урока', 'error')
            return redirect(url_for('edit_word') + '?b=' + str(book_id) + '&l=' + str(lesson_id) + '&w=' + str(word_id))
        synonym_id = add_synonym(conn, lesson_id, word_stemmed, word, word_speech_id, reference_word_id)
        flash('Слово успешно добавлено в словарь', 'success')
        return redirect(url_for('edit_word') + '?b=' + str(book_id) + '&l=' + str(lesson_id) + '&w=' + str(word_id))

    # "Delete synonym" button pressed
    if request.form.get('remove_synonym'):
        word_id = request.form.get("word_id")
        remove_word(conn, word_id)
        flash('Слово успешно удалено', 'success')
        return redirect(url_for('edit_dictionary') + '?b=' + str(book_id) + '&l=' + str(lesson_id))

    images = get_all_images(book_id)
    videos = get_all_videos(book_id)
    audios = get_all_audios(book_id)
    images.sort()
    videos.sort()
    audios.sort()

    html = render_template(
        'edit_word.html',
        book_id=book_id,
        lesson_id=lesson_id,
        word_id=word_id,
        word=df_word,
        synonyms=df_synonyms,
        user=current_user,
        images=images,
        videos=videos,
        audios=audios,
        len=len,
        str=str
    )
    return html