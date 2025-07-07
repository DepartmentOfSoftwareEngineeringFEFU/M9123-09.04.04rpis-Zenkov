import pandas
from werkzeug.security import generate_password_hash

pandas.options.mode.chained_assignment = None

def get_user_organizations(conn, user_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            member_id,
            organization.organization_id,
            organization_name
        FROM 
            organization_member, organization
        WHERE
            organization_member.user_id = :user_id
            AND organization_member.organization_id = organization.organization_id
        ORDER BY organization_name ASC
    ''', conn, params={'user_id': str(user_id)})


def get_users(conn):
    df_users = pandas.read_sql(
        ''' 
        SELECT 
            *
        FROM 
            user
        ORDER BY user_id ASC
    ''', conn)
    if len(df_users) < 1:
        return df_users
    df_users["organizations"] = pandas.DataFrame({'member_id', 'organization_id', 'organization_name'})
    for i, user in df_users.iterrows():
        organizations = get_user_organizations(conn, user["user_id"])
        df_users.at[i, "organizations"] = organizations
    return df_users
    
    
def get_guidebooks_all(conn):
    return pandas.read_sql(
        ''' 
        SELECT 
            book_id,
            book_name, 
            subject_name
        FROM 
            guidebook, subject
        WHERE
            guidebook.subject_id = subject.subject_id
        ORDER BY book_name ASC
    ''', conn)
    
    
def get_students_by_user_id(conn, user_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            student_id
        FROM 
            student, organization_member
        WHERE
            student.member_id = organization_member.member_id
            AND organization_member.user_id = :user_id
    ''', conn, params={'user_id': str(user_id)})
    
    
def get_students_by_member_id(conn, member_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            student_id
        FROM 
            student
        WHERE
            student.member_id = :member_id
    ''', conn, params={'member_id': str(member_id)})


def update_user(conn, user_id, user_name, user_is_editor):
    cursor = conn.cursor()
    cursor.execute(''' 
                    UPDATE user
                    SET
                        user_name = :user_name,
                        is_editor = :user_is_editor
                    WHERE
                        user_id = :user_id
                ''', {"user_id": str(user_id), 
                    "user_name": str(user_name),
                    "user_is_editor": str(user_is_editor)
                    })
    conn.commit()


def reset_password(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(''' 
                    UPDATE user
                    SET
                        user_password = :user_password
                    WHERE
                        user_id = :user_id
                ''', {"user_id": str(user_id), "user_password": generate_password_hash("", method='sha256')})
    conn.commit()


def delete_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(''' 
                    DELETE FROM user
                    WHERE user_id = :user_id
                ''', {"user_id": str(user_id)})
    conn.commit()
    

def add_organization(conn, organization_name, organization_address, organization_access):
    cursor = conn.cursor()
    cursor.execute(''' 
                    INSERT INTO organization(organization_name, organization_address, organization_access)
                    VALUES (:organization_name, :organization_address, :organization_access);
                ''', {"organization_name": str(organization_name), 
                    "organization_address": str(organization_address),
                    "organization_access": str(organization_access)
                    })
    conn.commit()
    
    
def update_organization(conn, organization_id, organization_name, organization_address, organization_access):
    cursor = conn.cursor()
    cursor.execute(''' 
                    UPDATE organization
                    SET
                        organization_name = :organization_name,
                        organization_address = :organization_address,
                        organization_access = :organization_access
                    WHERE
                        organization_id = :organization_id
                ''', {"organization_id": str(organization_id), 
                    "organization_name": str(organization_name),
                    "organization_address": str(organization_address),
                    "organization_access": str(organization_access)
                    })
    conn.commit()
    
    
def get_organization_moderators(conn, organization_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            moderator_id,
            user.user_id, 
            user_name,
            user_login
        FROM 
            moderator, user, organization_member
        WHERE
            moderator.member_id = organization_member.member_id
            AND organization_member.user_id = user.user_id
        ORDER BY user_login ASC
    ''', conn)
    
    
def get_organization_members(conn, organization_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            member_id,
            user.user_id,
            user_name,
            user_login
        FROM 
            organization_member, user
        WHERE
            organization_member.user_id = user.user_id
            AND organization_member.organization_id = :organization_id
        ORDER BY user_login ASC
    ''', conn, params={'organization_id': str(organization_id)})
    
    
def get_organizations(conn):
    organizations = pandas.read_sql(
        ''' 
        SELECT 
            organization.organization_id,
            organization_name, 
            organization_address, 
            organization_access
        FROM 
            organization
        ORDER BY organization.organization_id ASC
    ''', conn)
    if len(organizations) < 1:
        return organizations
    organizations["moderators"] = pandas.DataFrame({'moderator_id', 'user_id', 'user_name', 'user_login'})
    organizations["members"] = pandas.DataFrame({'member_id', 'user_id', 'user_name', 'user_login'})
    for i, organization in organizations.iterrows():
        moderators = get_organization_moderators(conn, organization["organization_id"])
        organizations.at[i, "moderators"] = moderators
        members = get_organization_members(conn, organization["organization_id"])
        organizations.at[i, "members"] = members
    return organizations
    
    
def is_moderator(conn, member_id, organization_id):
    df_moderator = pandas.read_sql(
        '''
        SELECT 
            moderator.* 
        FROM 
            moderator, organization_member
        WHERE 
            moderator.member_id = :member_id 
            AND moderator.member_id = organization_member.member_id
            AND organization_member.organization_id = :organization_id;
        ''', conn, params={'member_id': str(member_id), 'organization_id': str(organization_id)})
    return len(df_moderator) > 0
    
    
def add_moderator(conn, member_id, organization_id):
    if is_moderator(conn, member_id, organization_id):
        return False
    else:
        cursor = conn.cursor()
        cursor.execute(''' 
                        INSERT INTO moderator(member_id)
                        VALUES (:member_id);
                    ''', {"member_id": str(member_id)
                        })
        conn.commit()
        return True
        

def is_member(conn, user_id, organization_id):
    df_moderator = pandas.read_sql(
        '''
        SELECT 
            * 
        FROM 
            organization_member
        WHERE 
            user_id = :user_id 
            AND organization_id = :organization_id;
        ''', conn, params={'user_id': str(user_id), 'organization_id': str(organization_id)})
    return len(df_moderator) > 0
        
        
def add_member(conn, user_id, organization_id):
    if is_member(conn, user_id, organization_id):
        return False
    else:
        cursor = conn.cursor()
        cursor.execute(''' 
                        INSERT INTO organization_member(user_id, organization_id)
                        VALUES (:user_id, :organization_id);
                    ''', {"user_id": str(user_id), 
                        "organization_id": str(organization_id)
                        })
        conn.commit()
        return True
    
    
def delete_moderator(conn, moderator_id):
    cursor = conn.cursor()
    cursor.execute(''' 
                    DELETE FROM moderator
                    WHERE moderator_id = :moderator_id
                ''', {"moderator_id": str(moderator_id)})
    conn.commit()
    
    
def delete_member(conn, member_id):
    cursor = conn.cursor()
    cursor.execute(''' 
                    DELETE FROM organization_member
                    WHERE member_id = :member_id
                ''', {"member_id": str(member_id)})
    conn.commit()