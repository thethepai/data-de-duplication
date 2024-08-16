import pandas as pd
import mysql.connector
from mysql.connector import Error
import os

def create_connection(host_name, user_name, user_password, db_name):
    """
    Establishes a connection to a MySQL database.

    Parameters:
    host_name (str): The hostname of the MySQL server.
    user_name (str): The username to use for authentication.
    user_password (str): The password to use for authentication.
    db_name (str): The name of the database to connect to.

    Returns:
    connection: A MySQL connection object if the connection is successful, None otherwise.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    
    return connection

def load_excel_to_mysql(file_path, table_name, connection):
    """
    Loads data from an Excel file into a MySQL table.

    Parameters:
    file_path (str): The path to the Excel file.
    table_name (str): The name of the table to create and insert data into.
    connection: A MySQL connection object.

    Returns:
    None
    """
    df = pd.read_excel(file_path)

    cursor = connection.cursor()
    
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join([f'{col} TEXT' for col in df.columns])}
    );
    """
    cursor.execute(create_table_query)
    
    for _, row in df.iterrows():
        insert_query = f"""
        INSERT INTO {table_name} ({', '.join(df.columns)}) 
        VALUES ({', '.join(['%s'] * len(row))})
        """
        cursor.execute(insert_query, tuple(row))
    
    connection.commit()
    cursor.close()
    print(f"Data from {file_path} has been loaded into {table_name} table.")
    
def export_mysql_to_excel(file_path, table_name, connection):
    """
    Exports data from a MySQL table to an Excel file.

    Parameters:
    table_name (str): The name of the table to export data from.
    file_path (str): The path to the Excel file to create.
    connection: A MySQL connection object.

    Returns:
    None
    """
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, connection)
    
    df.to_excel(file_path, index=False)
    print(f"Data from {table_name} table has been exported to {file_path}")

def show_table_structure(connection, table_name):
    """
    Displays the structure of a specified table in the database.

    Parameters:
    connection: A MySQL connection object.
    table_name (str): The name of the table whose structure is to be displayed.

    Returns:
    None
    """
    cursor = connection.cursor()
    describe_query = f"DESCRIBE {table_name};"
    cursor.execute(describe_query)
    columns = cursor.fetchall()
    
    print(f"Structure of table '{table_name}':")
    for column in columns:
        print(f"Column: {column[0]}, Type: {column[1]}")
        
def alter_column_type(connection, table_name, column_name, new_type, set_primary_key=False):
    """
    Modifies the type of a specified column in a table and optionally sets it as the primary key.

    Parameters:
    connection: A MySQL connection object.
    table_name (str): The name of the table containing the column to be modified.
    column_name (str): The name of the column to be modified.
    new_type (str): The new data type for the column.
    set_primary_key (bool): Whether to set the column as the primary key. Default is False.

    Returns:
    None
    """
    cursor = connection.cursor()
    alter_query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {new_type};"
    try:
        cursor.execute(alter_query)
        connection.commit()
        print(f"Column '{column_name}' in table '{table_name}' has been modified to type '{new_type}'.")

        if set_primary_key:
            primary_key_query = f"ALTER TABLE {table_name} ADD PRIMARY KEY ({column_name});"
            cursor.execute(primary_key_query)
            connection.commit()
            print(f"Column '{column_name}' in table '{table_name}' has been set as the primary key.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def drop_table_if_exists(connection, table_name):
    """
    Drops a specified table if it exists in the database.

    Parameters:
    connection: A MySQL connection object.
    table_name (str): The name of the table to be dropped.

    Returns:
    None
    """
    cursor = connection.cursor()
    check_query = f"SHOW TABLES LIKE '{table_name}';"
    try:
        cursor.execute(check_query)
        result = cursor.fetchone()
        if result:
            drop_query = f"DROP TABLE {table_name};"
            cursor.execute(drop_query)
            connection.commit()
            print(f"Table '{table_name}' has been dropped.")
        else:
            print(f"Table '{table_name}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(script_dir)
    
    connection = create_connection("localhost", "root", "123456", "test_db")
    if connection:
        drop_table_if_exists(connection, "articles_info")
        load_excel_to_mysql("../data/data.xlsx", "articles_info", connection)
        alter_column_type(connection, "articles_info", "id", "INT", set_primary_key=True)
        show_table_structure(connection, "articles_info")
        connection.close()