import pandas


def get_entry(conn, entry_id):
    return pandas.read_sql(
        ''' 
        SELECT 
            entry.*, entry_type_name 
        FROM 
            entry, entry_type 
        WHERE 
            entry.entry_type_id = entry_type.entry_type_id
            AND entry_id = :entry_id
    ''', conn, params={'entry_id': str(entry_id)})


def get_entry_type_name(conn, entry_id):
    return pandas.read_sql(
        ''' 
        SELECT entry_type_name
        FROM entry, entry_type
        WHERE
            entry_id = :entry_id 
            AND entry.entry_type_id = entry_type.entry_type_id
    ''', conn, params={'entry_id': str(entry_id)})
    
def get_entry_type_id_by_name(conn, entry_type_name):
    df_type = pandas.read_sql(
        ''' 
        SELECT entry_type_id
        FROM entry_type
        WHERE
            entry_type_name = :entry_type_name 
        LIMIT 1
    ''', conn, params={'entry_type_name': str(entry_type_name)})
    if len(df_type) > 0:
        return df_type.iloc[0]['entry_type_id']
    return -1


def update_entry(conn, entry_id, entry_name, entry_type_name):
    entry_type_id = get_entry_type_id_by_name(conn, entry_type_name)
    if entry_type_id < 1: return False
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE entry
        SET
            entry_name = :entry_name,
            entry_type_id = :entry_type_id
        WHERE
            entry_id = :entry_id
    ''', {"entry_name": entry_name, "entry_type_id": str(entry_type_id),
          "entry_id": entry_id})
    conn.commit()