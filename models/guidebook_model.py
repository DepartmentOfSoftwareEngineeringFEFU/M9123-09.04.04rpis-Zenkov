import pandas


def is_book_available(conn, book_id):
    df_book = pandas.read_sql(
        ''' 
        SELECT
            1
        FROM
            guidebook
        WHERE
            book_id = :book_id
            AND book_visible = 1;
    ''', conn, params={'book_id': str(book_id)})     
    return len(df_book) > 0


def get_all_students(conn):
    return pandas.read_sql(
        ''' 
        SELECT
            student.*
        FROM
            student;
    ''', conn)   


def get_student_by_id(conn, student_id):
    return pandas.read_sql(
        ''' 
        SELECT
            student.*,
            user_name
        FROM
            student, user, organization_member
        WHERE student.student_id = :student_id
        AND student.member_id = organization_member.member_id
        AND user.user_id = organization_member.user_id
        LIMIT 1;
    ''', conn, params={'student_id': str(student_id)})   


def get_book_id_by_entry(conn, entry_id):
    return pandas.read_sql(
        ''' 
        SELECT
            book_id
        FROM
            entry, lesson
        WHERE entry.entry_id = :entry_id
        AND entry.lesson_id = lesson.lesson_id
        LIMIT 1;
    ''', conn, params={'entry_id': str(entry_id)})


def delete_userbook_entry(conn, user_id, entry_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        DELETE FROM user_book_entry
        WHERE user_id = :user_id AND entry_id = :entry_id;
    ''', {"user_id": str(user_id), "entry_id": entry_id})
    conn.commit()
    
    
def delete_userbook_word(conn, user_id, word_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        DELETE FROM user_book_word
        WHERE user_id = :user_id AND word_id = :word_id;
    ''', {"user_id": str(user_id), "word_id": word_id})
    conn.commit()


def add_userbook_entry(conn, user_id, entry_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO user_book_entry(user_id, entry_id)
        VALUES (:user_id, :entry_id);
    ''', {"user_id": str(user_id), "entry_id": entry_id})
    conn.commit()
    
    
def add_userbook_word(conn, user_id, word_id):
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO user_book_word(user_id, word_id)
        VALUES (:user_id, :word_id);
    ''', {"user_id": str(user_id), "word_id": word_id})
    conn.commit()


def is_entry_in_userbook(conn, entry_id, user_id):
    df_entry = pandas.read_sql(
        ''' 
        SELECT * FROM user_book_entry
        WHERE entry_id = :entry_id
        AND user_id = :user_id
    ''', conn, params={'entry_id': str(entry_id), 'user_id': str(user_id)})
    return len(df_entry) > 0


def get_userbook_entries(conn, user_id, book_id):
    return pandas.read_sql(
        ''' 
        SELECT
            entry.entry_id,
            entry.entry_name
        FROM
            user_book_entry, entry, lesson
        WHERE user_book_entry.entry_id = entry.entry_id
        AND entry.lesson_id = lesson.lesson_id
        AND book_id = :book_id
        AND user_id = :user_id
        ORDER BY entry.entry_name
    ''', conn, params={'book_id': str(book_id), 'user_id': str(user_id)})
    
    
def get_userbook_words(conn, user_id, book_id):
    return pandas.read_sql(
        ''' 
        SELECT
            word.word_id,
            word.word_normal
        FROM
            user_book_word, word, lesson
        WHERE user_book_word.word_id = word.word_id
        AND word.lesson_id = lesson.lesson_id
        AND book_id = :book_id
        AND user_id = :user_id
        ORDER BY word.word_normal
    ''', conn, params={'book_id': str(book_id), 'user_id': str(user_id)})
    
    
def get_entry_by_id(conn, entry_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            entry.*,
            entry_type_name
        FROM 
            entry, 
            entry_type
        WHERE entry_id = :entry_id
        AND entry.entry_type_id = entry_type.entry_type_id
    ''', conn, params={'entry_id': str(entry_id)})


def get_words(conn, lesson_id):
    return pandas.read_sql(
        ''' 
        SELECT * FROM word
        WHERE lesson_id = :lesson_id
        ORDER BY word_normal
    ''', conn, params={'lesson_id': str(lesson_id)})


def get_guidebook(conn, book_id):
    return pandas.read_sql(
        ''' 
        SELECT * FROM guidebook
        WHERE book_id = :book_id
    ''', conn, params={'book_id': str(book_id)})
    
    
def get_teacher_by_id(conn, teacher_id):
    return pandas.read_sql(
        ''' 
        SELECT * FROM teacher
        WHERE teacher_id = :teacher_id
    ''', conn, params={'teacher_id': str(teacher_id)})    


def get_students_by_teacher_id(conn, teacher_id):
    df_teacher = get_teacher_by_id(conn, teacher_id)
    if len(df_teacher) < 1: return pandas.DataFrame()
    return pandas.read_sql(
        ''' 
        SELECT 
            user.user_id,
            user_name,
            student_id,
            student.group_id
        FROM 
            user,
            student,
            organization_member
        WHERE
            user.user_id = organization_member.user_id
            AND organization_member.member_id = student.member_id
            AND group_id = :group_id
        ORDER BY user_name
    ''', conn, params={'group_id': str(df_teacher.loc[0, 'group_id'])})
    
    
def get_teacher_groups(conn, organization_id, user_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            teacher.group_id,
            group_name
        FROM 
            user,
            organization_member,
            teacher,
            organization_group
        WHERE
            user.user_id = :user_id
            AND user.user_id = organization_member.user_id
            AND organization_member.member_id = teacher.member_id
            AND teacher.group_id = organization_group.group_id
            AND organization_group.organization_id = :organization_id
        ORDER BY user_name
    ''', conn, params={'user_id': str(user_id), 'organization_id': str(organization_id)})
    
    
def get_student_groups(conn, organization_id, user_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            student.group_id,
            group_name
        FROM 
            user,
            organization_member,
            student,
            organization_group
        WHERE
            user.user_id = :user_id
            AND user.user_id = organization_member.user_id
            AND organization_member.member_id = student.member_id
            AND student.group_id = organization_group.group_id
            AND organization_group.organization_id = :organization_id
        ORDER BY user_name
    ''', conn, params={'user_id': str(user_id), 'organization_id': str(organization_id)})


def get_student_group(conn, student_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            organization_group.*
        FROM 
            student,
            organization_group
        WHERE
            organization_group.group_id = student.group_id
            AND student.student_id = :student_id
    ''', conn, params={'student_id': str(student_id)}) 


def get_other_students(conn, student_id):
    df_group = get_student_group(conn, student_id)
    if len(df_group) < 1: return pandas.DataFrame()
    return pandas.read_sql(
        ''' 
        SELECT 
            user.user_id,
            student_id,
            user_name
        FROM 
            user,
            student,
            organization_member
        WHERE
            user.user_id = organization_member.user_id
            AND organization_member.member_id = student.member_id
            AND student.group_id = :group_id
            AND student.student_id != :student_id
        ORDER BY user_name
    ''', conn, params={'student_id': str(student_id), 'group_id': str(df_group.loc[0,"group_id"])})


def get_groups(conn):
    return pandas.read_sql(
        ''' 
        SELECT * FROM group
    ''', conn)


def get_lessons(conn, book_id):
    return pandas.read_sql(
        ''' 
        SELECT * FROM lesson 
        WHERE lesson.book_id = :book_id
        ORDER BY lesson_index
    ''', conn, params={'book_id': str(book_id)})


def get_rules(conn, book_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            entry_id,
            entry.lesson_id,
            entry_index,
            entry_name
        FROM 
            entry,
            entry_type,
            lesson
        WHERE 
            entry.lesson_id = lesson.lesson_id
            AND lesson.book_id = :book_id
            AND entry.entry_type_id = entry_type.entry_type_id
            AND entry_type_name = 'rule'
        ORDER BY lesson_index, entry_index
    ''', conn, params={'book_id': str(book_id)})


def get_lesson_entries(conn, lesson_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            entry.lesson_id, 
            entry_id, 
            entry_index, 
            entry_name,
            entry_type_name
        FROM 
            entry,
            entry_type
        WHERE 
            entry.entry_type_id = entry_type.entry_type_id
            AND lesson_id = :lesson_id
        ORDER BY entry_index
    ''', conn, params={'lesson_id': str(lesson_id)})


def get_all_lessons_entries(conn, book_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            lesson.lesson_id, 
            lesson.lesson_index,
            entry.entry_id, 
            entry_index, 
            entry_name,
            entry_type_name
        FROM 
            lesson, 
            entry,
            entry_type
        WHERE 
            lesson.lesson_id = entry.lesson_id
            AND lesson.book_id = :book_id
            AND entry.entry_type_id = entry_type.entry_type_id
        ORDER BY lesson_index, entry_index
    ''', conn, params={'book_id': str(book_id)})
