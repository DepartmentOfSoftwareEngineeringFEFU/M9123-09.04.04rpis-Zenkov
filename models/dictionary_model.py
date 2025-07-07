import pandas


def is_word_in_userbook(conn, word_id, user_id):
    df_word = pandas.read_sql(
        ''' 
        SELECT * FROM user_book_word
        WHERE word_id = :word_id
        AND user_id = :user_id
    ''', conn, params={'word_id': str(word_id), 'user_id': str(user_id)})
    return len(df_word) > 0


def get_book_by_lesson(conn, lesson_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            guidebook.book_id
        FROM 
            guidebook, lesson
        WHERE
            lesson.book_id = guidebook.book_id
            AND lesson_id = :lesson_id
        LIMIT 1;
    ''', conn, params={'lesson_id': str(lesson_id)})
    
    
def get_all_lessons(conn, book_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            *
        FROM 
            lesson
        WHERE
            book_id = :book_id;
    ''', conn, params={'book_id': str(book_id)})


def get_word_from_lesson(conn, word_stemmed, word_speech_tag, lesson_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            word_id,
            reference_word_id
        FROM 
            word, word_speech
        WHERE
            word.word_speech_id = word_speech.word_speech_id
            AND word_speech_tag = :word_speech_tag
            AND word_stemmed = :word_stemmed
            AND lesson_id = :lesson_id
        LIMIT 1;
    ''', conn, params={'word_speech_tag': str(word_speech_tag), 'word_stemmed': str(word_stemmed),
        'lesson_id': str(lesson_id)})
        

def get_word_by_id(conn, word_id):
    return pandas.read_sql(
        ''' 
        SELECT * FROM word
        WHERE word_id = :word_id
        LIMIT 1;
    ''', conn, params={'word_id': str(word_id)})
    
    