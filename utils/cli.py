import os
import configparser
import argparse
from functools import partial
from processor.db_mysql_utils import DatabaseUtils
from processor.dd_processor import DdProcessor
from pipeline_config import PipelineConfig

def create_connection_workflow(db_config):
    return DatabaseUtils.create_connection(
        db_config['host'], 
        db_config['user'], 
        db_config['password'], 
        db_config['database']
    )

def drop_table_workflow(connection, db_config):
    if connection:
        DatabaseUtils.drop_table_if_exists(connection, db_config['tablename'])

def load_excel_workflow(connection, file_config, db_config):
    if connection:
        DatabaseUtils.load_excel_to_mysql(file_config['input_excel'], "articles_info", connection)
        DatabaseUtils.alter_column_type(connection, db_config['tablename'], "id", "INT", set_primary_key=True)
        DatabaseUtils.show_table_structure(connection, db_config['tablename'])

def process_data_workflow(connection, processor_config):
    if connection:
        processor = DdProcessor(
            threshold=float(processor_config['threshold']), 
            method=processor_config['method']
        )
        processor.dd_similarity(connection, processor_config['process_column'])

def export_excel_workflow(connection, file_config, db_config):
    if connection:
        DatabaseUtils.export_mysql_to_excel(file_config['output_excel'], db_config['tablename'], connection)
        connection.close()
        print("Connection closed.")

def main():
    parser = argparse.ArgumentParser(description="Process some data.")
    parser.add_argument('--config', type=str, required=True, help='Path to the config file')
    parser.add_argument('--skip-drop', action='store_true', help='Skip dropping the table if it exists')
    parser.add_argument('--skip-load', action='store_true', help='Skip loading data from Excel to MySQL')
    
    args = parser.parse_args()
    
    config = configparser.ConfigParser()
    config.read(args.config)
    
    db_config = config['database']
    file_config = config['files']
    processor_config = config['processor']
    
    connection_workflow = partial(create_connection_workflow, db_config)
    connection = connection_workflow()
    
    workflows = []
    if not args.skip_drop:
        workflows.append(partial(drop_table_workflow, connection, db_config))
    if not args.skip_load:
        workflows.append(partial(load_excel_workflow, connection, file_config, db_config))
    workflows.append(partial(process_data_workflow, connection, processor_config))
    workflows.append(partial(export_excel_workflow, connection, file_config, db_config))
    
    pipeline = PipelineConfig(
        root_dir=os.getcwd(),
        input=None,
        reporting=None,
        storage=None,
        cache=None,
        workflows=workflows
    )
    
    pipeline.run()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(script_dir)
    main()