import pandas


def update_password(conn, user_id, password):
    cursor = conn.cursor()
    cursor.execute(''' 
                    UPDATE user
                    SET
                        user_password = :password
                    WHERE
                        user_id = :user_id
                ''', {"user_id": str(user_id), "password": str(password)})
    conn.commit()
