import pandas
import os
import shutil
from app import app
from models.edit_entry_model import get_entry_type_id_by_name
from flask_login import current_user


def delete_path(local_path):
    path = os.path.join(app.path, local_path)
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
        
        
def get_editors(conn):
    return pandas.read_sql(
        ''' 
        SELECT 
            user.*
        FROM 
            user
        WHERE is_editor = 1;
    ''', conn)
        
        
def add_editor(conn, book_id, user_id):
    cursor = conn.cursor()
    cursor.execute('''
                INSERT INTO editor(book_id, user_id)
                VALUES (:book_id, :user_id);
            ''', {"book_id": str(book_id), "user_id": str(user_id)})
    conn.commit()
    
    
def remove_editor(conn, book_id, user_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        DELETE FROM editor
        WHERE book_id = :book_id AND user_id = user_id
    ''', {"book_id": str(book_id), "user_id": str(user_id)})
    conn.commit()


def add_guidebook(conn, book_name):
    cursor = conn.cursor()
    cursor.execute('''
                INSERT INTO guidebook(book_name)
                VALUES (:book_name);
            ''', {"book_name": str(book_name)})
    book_id = cursor.lastrowid
    conn.commit() 
    return book_id
    
    
def update_guidebook(conn, book_id, book_name, book_visible):
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE guidebook
        SET
            book_name = :book_name,
            book_visible = :book_visible
        WHERE
            book_id = :book_id
    ''', {"book_id": str(book_id), "book_name": str(book_name),
          "book_visible": str(book_visible)})
    conn.commit()
    
    
def update_guidebook_name(conn, book_id, book_name):
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE guidebook
        SET
            book_name = :book_name
        WHERE
            book_id = :book_id
    ''', {"book_id": str(book_id), "book_name": str(book_name)})
    conn.commit()
    

def remove_guidebook(conn, book_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        DELETE FROM guidebook
        WHERE book_id = :book_id
    ''', {"book_id": book_id})
    conn.commit()
    delete_path('templates/guidebooks/' + book_id)
    delete_path('static/guidebooks/' + book_id)
        
        
def get_user_guidebooks(conn, user_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            guidebook.*
        FROM 
            guidebook, editor
        WHERE 
            guidebook.book_id = editor.book_id 
            AND user_id = :user_id
        ORDER BY book_name ASC
    ''', conn, params={"user_id": str(user_id)})
    

def get_book_editors(conn, book_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            editor_id,
            user_login,
            user_name
        FROM 
            editor, user
        WHERE 
            user.user_id = editor.user_id 
            AND book_id = :book_id
        ORDER BY user_name ASC
    ''', conn, params={"book_id": str(book_id)})

    
def get_all_guidebooks(conn):
    df_books = pandas.read_sql(
        ''' 
        SELECT 
            guidebook.book_id,
            book_name,
            book_visible
        FROM 
            guidebook
        ORDER BY book_name ASC
    ''', conn)
    if len(df_books) < 1:
        return df_books
    df_books["editors"] = pandas.DataFrame({'editor_id', 'user_login', 'user_name'})
    for i, book in df_books.iterrows():
        df_books.at[i, "editors"] = get_book_editors(conn, book["book_id"])
    return df_books


def get_book(conn, book_id):
    return pandas.read_sql(
        ''' 
        SELECT * FROM guidebook
        WHERE book_id = :book_id
        LIMIT 1;
    ''', conn, params={"book_id": str(book_id)})
   
   
def is_author(conn, user_id, book_id):
    if current_user.is_admin: return True
    is_author = pandas.read_sql(
        ''' 
        SELECT * FROM editor
        WHERE user_id = :user_id AND book_id = :book_id
        LIMIT 1;
    ''', conn, params={"user_id": str(user_id), "book_id": str(book_id)})   
    return len(is_author) > 0
    
    
def is_true_author(conn, user_id, book_id):
    is_author = pandas.read_sql(
        ''' 
        SELECT * FROM editor
        WHERE user_id = :user_id AND book_id = :book_id
        LIMIT 1;
    ''', conn, params={"user_id": str(user_id), "book_id": str(book_id)})   
    return len(is_author) > 0


def get_lessons(conn, book_id):
    return pandas.read_sql(
        ''' 
        SELECT * FROM lesson
        WHERE book_id = :book_id
        ORDER BY lesson_index
    ''', conn, params={"book_id": str(book_id)})


def add_lesson(conn, book_id, lesson_name, lesson_index):
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO lesson(book_id, lesson_name, lesson_index)
        VALUES (:book_id, :lesson_name, :lesson_index);
    ''', {"book_id": str(book_id), "lesson_name": lesson_name, "lesson_index": lesson_index})
    conn.commit()


def remove_entry(conn, book_id, entry_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        DELETE FROM entry
        WHERE entry_id = :entry_id
    ''', {"entry_id": entry_id})
    conn.commit()
    delete_path('templates/guidebooks/' + book_id + '/entries/' + str(entry_id))
    delete_path('static/guidebooks/' + book_id + '/entries/' + str(entry_id))


def add_entry(conn, lesson_id, entry_name, entry_type_name, entry_index):
    entry_type_id = get_entry_type_id_by_name(conn, entry_type_name)
    if entry_type_id < 1: return False
    cursor = conn.cursor()
    cursor.execute(''' 
                INSERT INTO entry(lesson_id, entry_name, entry_type_id, entry_index)
                VALUES (:lesson_id, :entry_name, :entry_type_id, :entry_index);
            ''', {"lesson_id": str(lesson_id),
                  "entry_name": str(entry_name),
                  "entry_type_id": str(entry_type_id),
                  "entry_index": str(entry_index)})
    entry_id = cursor.lastrowid
    conn.commit()
    return entry_id


def update_entry_index(conn, lesson_id, entry_id, entry_index):
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE entry
        SET
            entry_index = :entry_index
        WHERE
            lesson_id = :lesson_id AND entry_id = :entry_id
    ''', {"entry_id": str(entry_id), "entry_index": str(entry_index),
          "lesson_id": str(lesson_id)})
    conn.commit()


# lower entries indexes by 1 in a lesson after entry with entry_id.
# used when removing entry with entry_id
def update_lesson_entry_indexes_after(conn, lesson_id, entry_id):
    # getting current lesson_entry index
    df_lesson_entry = pandas.read_sql(
        ''' 
        SELECT 
            entry_index
        FROM 
            entry
        WHERE
            entry_id = :entry_id AND lesson_id = :lesson_id
    ''', conn, params={"entry_id": str(entry_id), "lesson_id": str(lesson_id)})

    # getting lesson_entries after the removed one
    df_lessons_after = pandas.read_sql(
        ''' 
        SELECT 
            * 
        FROM 
            entry
        WHERE
            lesson_id = :lesson_id AND
            entry_index > :entry_index
    ''', conn, params={"entry_index": str(df_lesson_entry.iloc[0]['entry_index']),
                       "lesson_id": str(lesson_id)})

    # updating indexes for lesson_entries after the removed one
    for i, lesson_after in df_lessons_after.iterrows():
        update_entry_index(conn, lesson_after["lesson_id"], lesson_after["entry_id"],
                                  int(lesson_after["entry_index"]) - 1)


# remove all entries for lesson
def remove_lesson_entry_lid(conn, book_id, lesson_id):
    df_lesson_entries = pandas.read_sql(
        ''' 
        SELECT 
            entry_id 
        FROM 
            entry 
        WHERE
            lesson_id = :lesson_id
    ''', conn, params={"lesson_id": lesson_id})

    for i, lesson_entry in df_lesson_entries.iterrows():
        remove_entry(conn, book_id, lesson_entry['entry_id'])

    # cursor = conn.cursor()
    # cursor.execute(''' 
    #     DELETE FROM entry
    #     WHERE lesson_id = :lesson_id
    # ''', {"lesson_id": lesson_id})
    # conn.commit()


# remove entry from lesson and update indexes
def remove_lesson_entry_eid(conn, book_id, entry_id):
    # getting current lesson_entry lesson_id
    df_lesson_id = pandas.read_sql(
        ''' 
        SELECT 
            lesson_id
        FROM 
            entry
        WHERE
            entry_id = :entry_id
    ''', conn, params={"entry_id": entry_id})
    update_lesson_entry_indexes_after(conn, df_lesson_id.iloc[0]['lesson_id'], entry_id)

    cursor = conn.cursor()
    cursor.execute(''' 
        DELETE FROM entry
        WHERE entry_id = :entry_id
    ''', {"entry_id": entry_id})
    conn.commit()
    remove_entry(conn, book_id, entry_id)


# remove lesson and update indexes
def remove_lesson(conn, book_id, lesson_id):
    # getting current entry index
    df_lesson = pandas.read_sql(
        ''' 
        SELECT 
            lesson_index
        FROM 
            lesson
        WHERE
            lesson_id = :lesson_id
    ''', conn, params={"lesson_id": str(lesson_id)})

    # getting lessons after the removed one
    df_lessons_after = pandas.read_sql(
        ''' 
        SELECT 
            * 
        FROM 
            lesson
        WHERE
            lesson_index > :lesson_index
    ''', conn, params={"lesson_index": str(df_lesson.iloc[0]['lesson_index'])})

    # updating indexes for lessons after the removed one
    for i, lesson_after in df_lessons_after.iterrows():
        update_lesson_index(conn, lesson_after["lesson_id"], int(lesson_after["lesson_index"]) - 1)

    # removing lesson
    cursor = conn.cursor()
    cursor.execute(''' 
        DELETE FROM lesson
        WHERE lesson_id = :lesson_id
    ''', {"lesson_id": lesson_id})
    conn.commit()
    remove_lesson_entry_lid(conn, book_id, lesson_id)


def update_lesson_index(conn, lesson_id, lesson_index):
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE lesson
        SET
            lesson_index = :lesson_index
        WHERE
            lesson_id = :lesson_id
    ''', {"lesson_index": str(lesson_index),
          "lesson_id": str(lesson_id)})
    conn.commit()


# update lesson index
def update_lesson(conn, lesson_id, lesson_name, lesson_index):
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE lesson
        SET
            lesson_index = :lesson_index,
            lesson_name = :lesson_name
        WHERE
            lesson_id = :lesson_id
    ''', {"lesson_index": str(lesson_index), "lesson_name": str(lesson_name),
          "lesson_id": str(lesson_id)})
    conn.commit()


def get_lesson_entries(conn, book_id):
    return pandas.read_sql(
        ''' 
        SELECT entry_id, entry_name, entry.lesson_id, entry_index, entry.entry_type_id, entry_type_name
        FROM entry, entry_type, lesson
        WHERE entry.entry_type_id = entry_type.entry_type_id
            AND lesson.lesson_id = entry.lesson_id
            AND lesson.book_id = :book_id
        ORDER BY entry_index
    ''', conn, params={"book_id": str(book_id)})
