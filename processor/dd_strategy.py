# similarity_strategy.py
from abc import ABC, abstractmethod

class SimilarityStrategy(ABC):
    @abstractmethod
    def find_similar_pairs(self, articles, column_name, threshold, sub_string = True):
        pass