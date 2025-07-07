import string
import json
import nltk
import pymorphy3
import os
import codecs
import pandas
from flask import request, session, redirect, url_for, jsonify
from flask_login import current_user
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from app import app
from utils import *
from models.dictionary_model import *
nltk.download('punkt')
morph = pymorphy3.MorphAnalyzer()


def prepare_dict_text(text):
    prepared_text = ''
    words = word_tokenize(text)
    for word in words:
        prepared_text += morph.parse(word)[0].normal_form + ' '
    return prepared_text


def get_prepared_text(text):
    result = text.strip()
    for char in string.punctuation:
        result = result.replace(char, '')
    return prepare_dict_text(result)
    
    
def get_part_of_speech(text):
    words = word_tokenize(text)
    if len(words) > 1:
        return "PHRASE"
    parsed = morph.parse(words[0])
    if len(parsed) > 0:
        tag = str(parsed[0].tag)
        # getting the POS and replacing INFN verbs to VERB
        return tag.split(",", 1)[0].replace('INFN', 'VERB')
    return ""


def stem_text(text):
    stemmer = SnowballStemmer("russian")
    words = word_tokenize(text)
    stemmed_words = [stemmer.stem(word) for word in words]
    return " ".join(stemmed_words)
    

def get_word_html(book_id, word_id):
    contents = ""
    path = os.path.join(app.path, 'templates/guidebooks/' + str(book_id) + '/dictionary/' + str(word_id))
    if os.path.exists(path) and os.path.exists(path + '/contents.html'):
        f = codecs.open(path + '/contents.html', 'r', 'utf-8-sig')
        contents = f.read()
        f.close()
    return contents
    
    
def get_prepared_word_contents(contents, word_id, conn):
    if session['role_type'] != 'student' or contents == '':
        return contents
    button = ""
    button_type = ''
    button_text = ''
    if is_word_in_userbook(conn, word_id, current_user.id):
        button_type = 'remove'
        button_text = 'Удалить из картотеки'
    else:
        button_type = 'add'
        button_text = 'Добавить в картотеку'
    button = f"<input type='button' class='word_button_{word_id}' button_type='{button_type}' onclick='UpdateUserbook(1, {word_id})' value='{button_text}'>"
    contents = button + '<br>' + contents
    return contents
    
    
def get_word_contents(conn, stemmed_word, part_of_speech, lesson_id):
    contents = ""
    book = get_book_by_lesson(conn, lesson_id)
    book_id = -1
    word_id = -1
    if len(book) > 0:
        book_id = book.iloc[0]['book_id']
    else:
        return contents
    word_dict = get_word_from_lesson(conn, stemmed_word, part_of_speech, lesson_id)
    if len(word_dict) > 0:
        if not pandas.isnull(word_dict.iloc[0]['reference_word_id']):
            word_id = word_dict.iloc[0]['reference_word_id']
        else:
            word_id = word_dict.iloc[0]['word_id']
        contents = get_word_html(book_id, word_id)
    else:
        lessons = get_all_lessons(conn, book_id)
        for i, lesson in lessons.iterrows():
            word_dict = get_word_from_lesson(conn, stemmed_word, part_of_speech, lesson["lesson_id"])
            if len(word_dict) > 0:
                if not pandas.isnull(word_dict.iloc[0]['reference_word_id']):
                    word_id = word_dict.iloc[0]['reference_word_id']
                else:
                    word_id = word_dict.iloc[0]['word_id']
                contents = get_word_html(book_id, word_id)   
                break
    return get_prepared_word_contents(get_prepared_html(contents), word_id, conn)
    
def get_word_contents_by_id(conn, word_id, lesson_id):
    contents = ""
    book = get_book_by_lesson(conn, lesson_id)
    if len(book) > 0:
        book_id = book.iloc[0]['book_id']
        df_word = get_word_by_id(conn, word_id)
        if len(df_word) > 0:
            if not pandas.isnull(df_word.iloc[0]['reference_word_id']):
                word_id = df_word.iloc[0]['reference_word_id']
            else:
                word_id = df_word.iloc[0]['word_id']
            contents = get_word_html(book_id, word_id)
    return get_prepared_word_contents(get_prepared_html(contents), word_id, conn)  

        

@app.route("/dict", methods=['post'])
def dict():
    if request.form.get('get_word_def'):
        selected = request.form.get('selected')
        lesson_id = request.form.get('lesson_id')
        response = jsonify("")
        if selected is not None:
            if selected != "":
                prepared_text = get_prepared_text(selected)
                conn = get_db_connection()
                stemmed = stem_text(prepared_text)
                part_of_speech = get_part_of_speech(prepared_text)
                response = jsonify(get_word_contents(conn, stemmed, part_of_speech, lesson_id))
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    if request.form.get('get_word_def_id'):
        word_id = request.form.get('word_id')
        lesson_id = request.form.get('lesson_id')
        response = jsonify("")
        if word_id is not None:
            if word_id != "":
                conn = get_db_connection()
                response = jsonify(get_word_contents_by_id(conn, word_id, lesson_id))
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
