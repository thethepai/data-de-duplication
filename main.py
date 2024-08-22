import os
import configparser
from processor.db_utils import DatabaseUtils
from processor.dd_processor import DdProcessor

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    db_config = config['database']
    file_config = config['files']
    processor_config = config['processor']
    
    # create connection
    connection = DatabaseUtils.create_connection(
        db_config['host'], 
        db_config['user'], 
        db_config['password'], 
        db_config['database']
    )
    
    if connection:
        # load excel and database
        DatabaseUtils.drop_table_if_exists(connection, db_config['tablename'])
        DatabaseUtils.load_excel_to_mysql(file_config['input_excel'], "articles_info", connection)
        DatabaseUtils.alter_column_type(connection, db_config['tablename'], "id", "INT", set_primary_key=True)
        DatabaseUtils.show_table_structure(connection, db_config['tablename'])
        
        # process data
        processor = DdProcessor(
            threshold = float(processor_config['threshold']), 
            method=processor_config['method']
        )
        processor.dd_similarity(connection, processor_config['process_column'])
        
        # export to excel
        DatabaseUtils.export_mysql_to_excel(file_config['output_excel'], db_config['tablename'], connection)
        
        connection.close()
        print("Connection closed.")
        
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(script_dir)
    main()