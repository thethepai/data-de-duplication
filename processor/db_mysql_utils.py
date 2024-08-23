import pandas as pd
import mysql.connector
from mysql.connector import Error

class DatabaseUtils:
    @staticmethod
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
            print("------")
            print("Connection to MySQL DB successful")
        except Error as e:
            print("------")
            print(f"The error '{e}' occurred")
        
        return connection
    
    @staticmethod
    def create_simhash_table(connection, table_name, n=4):
        """
        Creates a table for storing SimHash fingerprints with n parts.

        Parameters:
        connection: A MySQL connection object.
        table_name (str): The name of the table to create.
        n (int): The number of fields to store the hash fingerprint parts (default is 4).

        Returns:
        None
        """
        cursor = connection.cursor()
        
        # Construct the SQL query to create a table with n fields
        fields = ", ".join([f"part{i+1} BIGINT" for i in range(n)])
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {fields}
        );
        """
        
        try:
            cursor.execute(create_table_query)
            connection.commit()
            print("------")
            print(f"Table '{table_name}' created successfully with {n} parts.")
        except Error as e:
            connection.rollback()
            print("------")
            print(f"The error '{e}' occurred while creating the table '{table_name}'")
        finally:
            cursor.close()
            
    @staticmethod
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
        try:
            cursor.execute(create_table_query)
            
            for _, row in df.iterrows():
                insert_query = f"""
                INSERT INTO {table_name} ({', '.join(df.columns)}) 
                VALUES ({', '.join(['%s'] * len(row))})
                """
                cursor.execute(insert_query, tuple(row))
            
            connection.commit()
            print("------")
            print(f"Data from {file_path} has been loaded into {table_name} table.")
        except Error as e:
            connection.rollback()
            print("------")
            print(f"The error '{e}' occurred while loading into table '{table_name}'")
        finally:
            cursor.close()
    
    @staticmethod
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
        try:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, connection)
            
            df.to_excel(file_path, index=False)
            print("------")
            print(f"Data from {table_name} table has been exported to {file_path}")
        except Error as e:
            print("------")
            print(f"The error '{e}' occurred while exporting data from table '{table_name}'")
        
    @staticmethod
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
        
        try:
            cursor.execute(describe_query)
            columns = cursor.fetchall()
            
            fmt = "=== {:45} ==="
            print("------")
            print(f"Structure of table '{table_name}':")
            for column in columns:
                print(fmt.format(f"Column: {column[0]}, Type: {column[1]}"))
        except Error as e:
            print("------")
            print(f"The error '{e}' occurred while showing the structure of table '{table_name}'")
        finally:
            cursor.close()
    
    @staticmethod       
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
            print("------")
            print(f"Column '{column_name}' in table '{table_name}' has been modified to type '{new_type}'.")

            if set_primary_key:
                primary_key_query = f"ALTER TABLE {table_name} ADD PRIMARY KEY ({column_name});"
                cursor.execute(primary_key_query)
                connection.commit()
                print(f"Column '{column_name}' in table '{table_name}' has been set as the primary key.")
        except Exception as e:
            connection.rollback()
            print("------")
            print(f"An error occurred while altering column's type: {e}")
        finally:
            cursor.close()
            
    @staticmethod
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
                print("------")
                print("drop_table_if_exists: true")
                print(f"Table '{table_name}' has been dropped.")
            else:
                print(f"Table '{table_name}' does not exist.")
        except Exception as e:
            connection.rollback()
            print("------")
            print(f"An error occurred when dropping table: {e}")
        finally:
            cursor.close()