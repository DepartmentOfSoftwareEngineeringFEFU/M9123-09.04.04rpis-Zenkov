import pandas
    
    
def is_moderator(conn, user_id, organization_id):
    df_moderator = pandas.read_sql(
        '''
        SELECT 
            1 
        FROM 
            moderator, organization_member
        WHERE 
            moderator.member_id = organization_member.member_id
            AND organization_member.organization_id = :organization_id
            AND organization_member.user_id = :user_id ;
        ''', conn, params={'user_id': str(user_id), 'organization_id': str(organization_id)})
    return len(df_moderator) > 0    
    
    
def is_group_teacher(conn, member_id, group_id):
    df_teacher = pandas.read_sql(
        '''
        SELECT 
            1
        FROM 
            teacher
        WHERE 
            member_id = :member_id
            AND group_id = :group_id;
        ''', conn, params={'member_id': str(member_id), 'group_id': str(group_id)})
    return len(df_teacher) > 0
    
    
def is_group_student(conn, member_id, group_id):
    df_student = pandas.read_sql(
        '''
        SELECT 
            1
        FROM 
            student
        WHERE 
            member_id = :member_id
            AND group_id = :group_id;
        ''', conn, params={'member_id': str(member_id), 'group_id': str(group_id)})
    return len(df_student) > 0      
    
    
def add_student(conn, member_id, group_id):
    if is_group_student(conn, member_id, group_id) or is_group_teacher(conn, member_id, group_id):
        return None
    cursor = conn.cursor()
    cursor.execute(''' 
                    INSERT INTO student(member_id, group_id)
                    VALUES (:member_id, :group_id);
                ''', {"member_id": str(member_id), 
                    "group_id": str(group_id)
                    })
    student_id = cursor.lastrowid
    conn.commit()
    return student_id
    
    
def add_teacher(conn, member_id, group_id):
    if is_group_student(conn, member_id, group_id) or is_group_teacher(conn, member_id, group_id):
        return False
    cursor = conn.cursor()
    cursor.execute(''' 
                    INSERT INTO teacher(member_id, group_id)
                    VALUES (:member_id, :group_id);
                ''', {"member_id": str(member_id), 
                    "group_id": str(group_id)
                    })
    conn.commit()
    return True
    
    
def delete_student(conn, student_id):
    cursor = conn.cursor()
    cursor.execute(''' 
                    DELETE FROM student
                    WHERE student_id = :student_id
                ''', {"student_id": str(student_id)})
    conn.commit()
    
    
def delete_teacher(conn, teacher_id):
    cursor = conn.cursor()
    cursor.execute(''' 
                    DELETE FROM teacher
                    WHERE teacher_id = :teacher_id
                ''', {"teacher_id": str(teacher_id)})
    conn.commit()    
    
    
def get_group_students(conn, group_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            student_id,
            user_login,
            user_name
        FROM 
            student, organization_member, user
        WHERE 
            student.member_id = organization_member.member_id
            AND organization_member.user_id = user.user_id
            AND group_id = :group_id;
    ''', conn, params={'group_id': str(group_id)})
    
    
def get_group_teachers(conn, group_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            teacher_id,
            user_login,
            user_name
        FROM 
            teacher, organization_member, user
        WHERE 
            teacher.member_id = organization_member.member_id
            AND organization_member.user_id = user.user_id
            AND group_id = :group_id;
    ''', conn, params={'group_id': str(group_id)})
    
    
def get_groups(conn, organization_id):
    df_groups = pandas.read_sql(
        ''' 
        SELECT 
            group_id,
            group_name
        FROM 
            organization_group
        WHERE 
            organization_id = :organization_id;
    ''', conn, params={'organization_id': str(organization_id)})
    if len(df_groups) < 1:
        return df_groups
    df_groups["teachers"] = pandas.DataFrame({'teacher_id', 'user_login', 'user_name'})
    df_groups["students"] = pandas.DataFrame({'student_id', 'user_login', 'user_name'})
    for i, group in df_groups.iterrows():
        df_groups.at[i, "teachers"] = get_group_teachers(conn, group["group_id"])
        df_groups.at[i, "students"] = get_group_students(conn, group["group_id"])
    return df_groups
    
    
def get_group_by_name(conn, group_name, organization_id):
    return pandas.read_sql(
        '''
        SELECT 
            organization_group.*
        FROM 
            organization_group
        WHERE 
            group_name = :group_name
            AND organization_id = :organization_id;
        ''', conn, params={'group_name': str(group_name), 'organization_id': str(organization_id)})
    
    
def add_group(conn, group_name, organization_id):
    if len(get_group_by_name(conn, group_name, organization_id)) > 0:
        return False
    cursor = conn.cursor()
    cursor.execute(''' 
                    INSERT INTO organization_group(group_name, organization_id)
                    VALUES (:group_name, :organization_id);
                ''', {"group_name": str(group_name), 
                    "organization_id": str(organization_id)
                    })
    conn.commit()
    return True
    
    
def delete_group(conn, group_id):
    cursor = conn.cursor()
    cursor.execute(''' 
                    DELETE FROM organization_group
                    WHERE group_id = :group_id
                ''', {"group_id": str(group_id)})
    conn.commit()
    
    
def get_members(conn, organization_id):
    df_members = pandas.read_sql(
        ''' 
        SELECT 
            user.user_login,
            user.user_id,
            user.user_name,
            member_id
        FROM 
            user, organization_member
        WHERE 
            user.user_id = organization_member.user_id
            AND organization_member.organization_id = :organization_id;
    ''', conn, params={'organization_id': str(organization_id)})
    df_members["is_moderator"] = 0
    for i, member in df_members.iterrows():
        df_members.at[i, "is_moderator"] = is_moderator(conn, member["user_id"], organization_id)
    return df_members
    
    
def get_user_organizations(conn, user_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            organization.organization_id,
            organization.organization_name,
            organization.organization_address,
            organization.organization_access
        FROM 
            organization, organization_member
        WHERE 
            organization_member.organization_id = organization.organization_id
            AND organization_member.user_id = :user_id
        LIMIT 1;
    ''', conn, params={'user_id': str(user_id)})
    