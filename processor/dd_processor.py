import time
import logging
from typing import Literal
from .dd_algorithm import TfidfSimilarity, SimhashSimilarity, MinHashSimilarity

class DdProcessor:
    def __init__(self, threshold: float = 0.7, method: Literal['tfidf', 'simhash', 'minhash'] = 'minhash'):
        self.THRESHOLD = threshold
        self.METHOD = method

    def dd_similarity(self, connection, column_name):
        start_time = time.time()
        deletion_time = None
        deleted_count = 0
        
        logging.basicConfig(
            filename=f'{start_time}_log_.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        print("processing...")

        try:
            with connection.cursor(dictionary=True) as cursor:
                
                select_query = f"SELECT id, {column_name} FROM articles_info"
                cursor.execute(select_query)
                articles = cursor.fetchall()
                
                if self.METHOD == 'tfidf':
                    strategy = TfidfSimilarity()
                elif self.METHOD == 'simhash':
                    strategy = SimhashSimilarity()
                elif self.METHOD == 'minhash':
                    strategy = MinHashSimilarity()
                else:
                    raise ValueError("Unknown method")
                print(f"Using {self.METHOD} method.")
            
                similar_pairs = strategy.find_similar_pairs(articles, column_name, self.THRESHOLD)
                
                logging.info(f"Found {len(similar_pairs)} similar records.")
                
                record = 1
                for pair in similar_pairs:
                    logging.info(f"pair NO.{record}")
                    logging.info(f"Similarity: {pair['id1']} and {pair['id2']}")
                    # logging.info(f"Text 1: {pair['text1']}")
                    # logging.info(f"Text 2: {pair['text2']}")
                    logging.info("------")
                    record += 1
                
                # delete similar records
                for pair in similar_pairs:
                    delete_query = f"DELETE FROM articles_info WHERE id = {pair['id2']}"
                    cursor.execute(delete_query)
                    deleted_count += cursor.rowcount
                
                deletion_time = time.time() - start_time
                
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")
            connection.rollback()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Deletion time: {deletion_time} seconds")
        print(f"Total records deleted: {deleted_count}")
        print(f"Total time taken: {total_time} seconds")