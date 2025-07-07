from flask_login import UserMixin
import pandas


class User(UserMixin):
    is_authenticated = True

    def __init__(self, id: int, login: str, name: str, password: str, is_admin: str, is_moderator: str, is_editor: str):
        print(is_editor)
        self.id = id
        self.login = login
        self.name = name
        self.password = password
        self.role_name = 'admin'
        self.is_admin = is_admin
        self.is_editor = is_editor
        self.is_moderator = is_moderator
        self.org_id = -1
        self.role_id = -1
        self.role_type = -1
        

def is_user_admin(conn, id):
    df_admin = pandas.read_sql(
        '''
        SELECT * FROM admin
        WHERE user_id = :id;
        ''', conn, params={'id': str(id)})
    return len(df_admin) > 0
    
    
def is_user_moderator(conn, id):
    df_moderator = pandas.read_sql(
        '''
        SELECT 
            * 
        FROM 
            moderator, organization_member
        WHERE 
            moderator.member_id = organization_member.member_id
            AND organization_member.user_id = :id;
        ''', conn, params={'id': str(id)})
    return len(df_moderator) > 0


def get_user(conn, login):
    df_users = pandas.read_sql(
        ''' 
        SELECT 
            *
        FROM 
            user
        WHERE 
            user_login = :login
        LIMIT 1;
    ''', conn, params={'login': str(login)})
    
    if len(df_users) > 0:
        return User(df_users.iloc[0]['user_id'],
                    df_users.iloc[0]['user_login'],
                    df_users.iloc[0]['user_name'],
                    df_users.iloc[0]['user_password'],
                    is_user_admin(conn, df_users.iloc[0]['user_id']),
                    is_user_moderator(conn, df_users.iloc[0]['user_id']),
                    df_users.iloc[0]['is_editor'])
    else:
        return None


def get_user_by_id(conn, user_id):
    df_users = pandas.read_sql(
        ''' 
        SELECT 
            *
        FROM 
            user
        WHERE 
            user_id = :user_id
        LIMIT 1;
    ''', conn, params={'user_id': str(user_id)})
    
    if len(df_users) > 0:
        return User(df_users.iloc[0]['user_id'],
                    df_users.iloc[0]['user_login'],
                    df_users.iloc[0]['user_name'],
                    df_users.iloc[0]['user_password'],
                    is_user_admin(conn, df_users.iloc[0]['user_id']),
                    is_user_moderator(conn, df_users.iloc[0]['user_id']),
                    df_users.iloc[0]['is_editor'])
    else:
        return None


def add_user(conn, login, name, password, is_editor):
    cursor = conn.cursor()
    cursor.execute(''' 
                INSERT INTO user(user_login, user_name, user_password, is_editor)
                VALUES (:login, :name, :password, :is_editor);
            ''', {"login": str(login), "name": str(name), "password": str(password), "is_editor": str(is_editor)})
    conn.commit()
