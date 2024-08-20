import os

from processor import db_utils
from processor import dd_brute

def main():
    connection = db_utils.create_connection("localhost", "root", "123456", "test_db")
    if connection:
        db_utils.drop_table_if_exists(connection, "articles_info")
        db_utils.load_excel_to_mysql("./data/data.xlsx", "articles_info", connection)
        db_utils.alter_column_type(connection, "articles_info", "id", "INT", set_primary_key=True)
        db_utils.show_table_structure(connection, "articles_info")
        
        dd_brute.dd_similarity(connection, "title")
        
        db_utils.export_mysql_to_excel("./data/result.xlsx", "articles_info", connection)
        
        connection.close()
        print("Connection closed.")
        
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(script_dir)
    main()
    