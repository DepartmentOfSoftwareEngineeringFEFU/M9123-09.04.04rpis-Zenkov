import pandas

def has_access(conn, organization_id):
    df_organization = pandas.read_sql(
        '''
        SELECT 
            * 
        FROM 
            organization
        WHERE 
            organization_id = :organization_id
            AND organization_access = 1;
        ''', conn, params={'organization_id': str(organization_id)})
    return len(df_organization) > 0
    

def get_student_groups(conn, user_id):
    return pandas.read_sql(
        '''
        SELECT 
            organization.organization_id,
            organization.organization_name,
            student_id as role_id,
            group_name,
            'student' as role_type
        FROM 
            student, organization_group, organization, organization_member
        WHERE 
            student.member_id = organization_member.member_id
            AND organization_member.user_id = :user_id
            AND organization_group.group_id = student.group_id
            AND organization_group.organization_id = organization.organization_id;
        ''', conn, params={'user_id': str(user_id)})
        
        
def get_teacher_groups(conn, user_id):
    return pandas.read_sql(
        '''
        SELECT 
            organization.organization_id,
            organization.organization_name,
            teacher_id as role_id,
            group_name,
            'teacher' as role_type
        FROM 
            teacher, organization_group, organization, organization_member
        WHERE 
            teacher.member_id = organization_member.member_id
            AND organization_member.user_id = :user_id
            AND organization_group.group_id = teacher.group_id
            AND organization_group.organization_id = organization.organization_id;
        ''', conn, params={'user_id': str(user_id)})
        
    
def get_user_groups(conn, user_id):
    return pandas.concat([get_student_groups(conn, user_id), get_teacher_groups(conn, user_id)], ignore_index=True)
    

def get_all_books(conn):
    return pandas.read_sql(
        ''' 
        SELECT 
            *
        FROM 
            guidebook
        ORDER BY book_name ASC
    ''', conn)
    
def get_available_books(conn):
    return pandas.read_sql(
        ''' 
        SELECT 
            *
        FROM 
            guidebook
        WHERE
            book_visible = 1
        ORDER BY book_name ASC
    ''', conn)
    
    
def get_editor_books(conn, user_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            guidebook.*
        FROM 
            guidebook, editor
        WHERE
            guidebook.book_id = editor.book_id AND user_id = :user_id
        ORDER BY book_name ASC
    ''', conn, params={'user_id': str(user_id)})
    
