import pandas


def get_comments_after(conn, entry_id, student_id, time):
     return pandas.read_sql(
        ''' 
        SELECT 
            entry_comment.*,
            user_name
        FROM 
            entry_comment,
            user
        WHERE entry_comment.user_id = user.user_id
        AND entry_id = :entry_id
        AND student_id = :student_id
        AND comment_datetime > :time
        ORDER BY comment_datetime ASC;
    ''', conn, params={'entry_id': str(entry_id), 'student_id': str(student_id), 'time': str(time)})


def get_comments(conn, entry_id, student_id):
     return pandas.read_sql(
        ''' 
        SELECT 
            entry_comment.*,
            user_name
        FROM 
            entry_comment, user
        WHERE entry_comment.user_id = user.user_id
        AND entry_id = :entry_id
        AND student_id = :student_id;
    ''', conn, params={'entry_id': str(entry_id), 'student_id': str(student_id)})
    
    
def add_comment(conn, entry_id, student_id, user_id, comment, time):
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO entry_comment(user_id, comment_datetime, comment_content, entry_id, student_id)
        VALUES (:user_id, :comment_datetime, :comment_content, :entry_id, :student_id);
    ''', {"user_id": str(user_id), "comment_datetime": str(time),
        "comment_content": str(comment), "entry_id": str(entry_id), "student_id": str(student_id)})
    conn.commit()


def is_group_student(conn, user_id, group_id):
    df_student = pandas.read_sql(
        ''' 
        SELECT
            1
        FROM 
            student,
            organization_member,
            user
        WHERE user.user_id = :user_id
        AND organization_member.user_id = user.user_id
        AND student.member_id = organization_member.member_id
        AND group_id = :group_id
        LIMIT 1;
    ''', conn, params={'group_id': str(group_id), 'user_id': str(user_id)})
    return len(df_student) > 0
    
    
def is_group_teacher(conn, user_id, group_id):
    df_teacher = pandas.read_sql(
        ''' 
        SELECT
            1
        FROM 
            teacher,
            organization_member,
            user
        WHERE user.user_id = :user_id
        AND organization_member.user_id = user.user_id
        AND teacher.member_id = organization_member.member_id
        AND group_id = :group_id
        LIMIT 1;
    ''', conn, params={'group_id': str(group_id), 'user_id': str(user_id)})
    return len(df_teacher) > 0
    
    
def get_message_by_id(conn, message_id):
     return pandas.read_sql(
        ''' 
        SELECT 
            chat_message.*,
            user_name
        FROM 
            chat_message,
            user
        WHERE chat_message.user_id = user.user_id
        AND message_id = :message_id;
    ''', conn, params={'message_id': str(message_id)})


def add_message(conn, user_id, group_id, message, time):
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO chat_message(user_id, group_id, message_datetime, message_content)
        VALUES (:user_id, :group_id, :time, :message);
    ''', {"user_id": str(user_id), "group_id": str(group_id),
        "time": str(time), "message": str(message)}
        )
    message_id = cursor.lastrowid
    conn.commit()
    return message_id
    
    
def get_messages_after(conn, group_id, time):
     return pandas.read_sql(
        ''' 
        SELECT 
            chat_message.*,
            user_name
        FROM 
            chat_message,
            user
        WHERE chat_message.user_id = user.user_id
        AND group_id = :group_id
        AND message_datetime > :time
        ORDER BY message_datetime ASC;
    ''', conn, params={'group_id': str(group_id), 'time': str(time)})
    
    
def get_messages_before(conn, group_id, time, count):
     return pandas.read_sql(
        ''' 
        SELECT 
            chat_message.*,
            user_name
        FROM 
            chat_message,
            user
        WHERE chat_message.user_id = user.user_id
        AND group_id = :group_id
        AND message_datetime < :time
        ORDER BY message_datetime DESC
        LIMIT :count;
    ''', conn, params={'group_id': str(group_id), 'time': str(time), 'count': str(count)})
    
    
def get_last_messages(conn, group_id, count):
     return pandas.read_sql(
        ''' 
        SELECT 
            chat_message.*,
            user_name
        FROM 
            chat_message,
            user
        WHERE chat_message.user_id = user.user_id
        AND group_id = :group_id
        ORDER BY message_datetime DESC
        LIMIT :count;
    ''', conn, params={'group_id': str(group_id), 'count': str(count)})
    
    
def get_all_messages(conn, group_id):
     return pandas.read_sql(
        ''' 
        SELECT 
            chat_message.*,
            user_name
        FROM 
            chat_message,
            user
        WHERE chat_message.user_id = user.user_id
        AND group_id = :group_id
        ORDER BY message_datetime ASC;
    ''', conn, params={'group_id': str(group_id)})
    
    