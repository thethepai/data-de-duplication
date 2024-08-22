import os

from processor.db_utils import DatabaseUtils
from processor.dd_processor import DdProcessor

def main():
    connection = DatabaseUtils.create_connection("localhost", "root", "123456", "test_db")
    if connection:
        DatabaseUtils.drop_table_if_exists(connection, "articles_info")
        DatabaseUtils.load_excel_to_mysql("./data/data.xlsx", "articles_info", connection)
        DatabaseUtils.alter_column_type(connection, "articles_info", "id", "INT", set_primary_key=True)
        DatabaseUtils.show_table_structure(connection, "articles_info")
        
        processor = DdProcessor(threshold=0.7, method='tfidf')
        processor.dd_similarity(connection, "title")
        
        DatabaseUtils.export_mysql_to_excel("./data/result.xlsx", "articles_info", connection)
        
        connection.close()
        print("Connection closed.")
        
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(script_dir)
    main()
    