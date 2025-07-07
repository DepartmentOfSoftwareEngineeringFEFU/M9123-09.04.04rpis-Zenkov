import pandas
from app import app

def add_synonym(conn, lesson_id, word_stemmed, word_normal, word_speech_id, reference_word_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO word(lesson_id, word_stemmed, word_normal, word_speech_id, reference_word_id)
        VALUES (:lesson_id, :word_stemmed, :word_normal, :word_speech_id, :reference_word_id);
    ''', {"lesson_id": str(lesson_id), "word_stemmed": word_stemmed, 
        "word_normal": word_normal, "word_speech_id": str(word_speech_id), "reference_word_id": str(reference_word_id)})
    word_id = cursor.lastrowid
    conn.commit()
    return word_id
        
def get_synonyms(conn, reference_word_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            word_id,
            word_stemmed,
            word_normal,
            word_speech.word_speech_id,
            word_speech.word_speech_name,
            reference_word_id
        FROM 
            word, word_speech
        WHERE 
            word.word_speech_id = word_speech.word_speech_id 
            AND reference_word_id = :reference_word_id
        ORDER BY word_normal ASC;
    ''', conn, params={'reference_word_id': str(reference_word_id)})        
        
def get_word(conn, word_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            word_id,
            word_stemmed,
            word_normal,
            word.word_speech_id,
            word_speech_name
        FROM 
            word, word_speech
        WHERE 
            word_id = :word_id 
            AND word.word_speech_id = word_speech.word_speech_id
        LIMIT 1;
    ''', conn, params={'word_id': str(word_id)})
    
def get_word_by_name_and_speech(conn, word_stemmed, word_speech_id, lesson_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            word_id,
            word_stemmed,
            word_normal,
            word.word_speech_id,
            word_speech_name,
            lesson_id
        FROM 
            word, word_speech
        WHERE 
            word_stemmed = :word_stemmed 
            AND word.word_speech_id = :word_speech_id
            AND word.word_speech_id = word_speech.word_speech_id
            AND lesson_id = :lesson_id
        LIMIT 1;
    ''', conn, params={'word_stemmed': str(word_stemmed), 'word_speech_id': str(word_speech_id), 'lesson_id': str(lesson_id)})
    

