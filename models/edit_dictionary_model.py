import pandas
import os
import shutil
from app import app


def get_word_speech_by_name(conn, word_speech_tag):
    return pandas.read_sql(
        ''' 
        SELECT 
            word_speech_id,
            word_speech_tag,
            word_speech_name
        FROM 
            word_speech
        WHERE 
            word_speech_tag = :word_speech_tag
        LIMIT 1;
    ''', conn, params={'word_speech_tag': str(word_speech_tag)})
        
        
def get_words(conn, lesson_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            word_id,
            word_stemmed,
            word_normal,
            word_speech.word_speech_id,
            word_speech.word_speech_name
        FROM 
            word, word_speech
        WHERE 
            word.word_speech_id = word_speech.word_speech_id 
            AND lesson_id = :lesson_id
            AND reference_word_id is NULL
        ORDER BY word_normal ASC;
    ''', conn, params={'lesson_id': str(lesson_id)})
    

def get_parts_of_speech(conn):
    return pandas.read_sql(
        ''' 
        SELECT 
            word_speech_id,
            word_speech_tag,
            word_speech_name
        FROM 
            word_speech;
    ''', conn)
    
    
def get_word(conn, word_stemmed, word_speech_id, lesson_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            word_id,
            word_stemmed,
            word_normal,
            word_speech.word_speech_id,
            word_speech.word_speech_name
        FROM 
            word, word_speech
        WHERE 
            word.word_speech_id = word_speech.word_speech_id 
            AND word_stemmed = :word_stemmed
            AND word_speech.word_speech_id = :word_speech_id
            AND lesson_id = :lesson_id
        ORDER BY word_normal ASC;
    ''', conn, params={'word_stemmed': str(word_stemmed), 'word_speech_id': str(word_speech_id), 'lesson_id': str(lesson_id)})   


def add_word(conn, lesson_id, word_stemmed, word_normal, word_speech_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO word(lesson_id, word_stemmed, word_normal, word_speech_id)
        VALUES (:lesson_id, :word_stemmed, :word_normal, :word_speech_id);
    ''', {"lesson_id": str(lesson_id), "word_stemmed": word_stemmed, 
        "word_normal": word_normal, "word_speech_id": str(word_speech_id)})
    word_id = cursor.lastrowid
    conn.commit()
    return word_id


def remove_word(conn, word_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        DELETE FROM word
        WHERE word_id = :word_id
    ''', {"word_id": word_id})
    conn.commit()
    
    
def get_lesson(conn, lesson_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            lesson_id
        FROM 
            lesson
        WHERE 
            lesson_id = :lesson_id
        LIMIT 1;
    ''', conn, params={'lesson_id': str(lesson_id)})     
    

