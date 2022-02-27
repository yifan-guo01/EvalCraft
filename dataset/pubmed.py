from pathlib import Path
import json
import random
from base_classes import Dataset, Document


class Pubmed(Dataset):
    has_sums = True
    has_kwds = False

    def __init__(self, path="dataset/pubmed-dataset/", count=None,
                 order=Dataset.SORTED, dataset="test"):
        self.path = path
        self.txt_path = path + dataset + ".txt"
        self.order = order

        file_count = sum(1 for line in open(self.txt_path))
        if count is None:
            self.count = file_count
        else:
            self.count = min(count, file_count)

    def __str__(self):
        return "Pubmed-dataset at " + self.txt_path
    
    def __iter__(self):
        assert self.order == Dataset.SORTED, "Random order is not supported for Pubmed dataset"
        
        with open(self.txt_path, 'r') as f:
            for i, line in zip(range(self.count), f):
                yield PubmedDoc(
                    line
                )


class PubmedDoc(Document):
    has_summary = True
    has_key_words = False
    
    def __init__(self, line):
        self.json = json.loads(line)

        self.name = self.json['article_id']
        self.fname = self.name + ".txt"
    
    def __str__(self) -> str:
        return "Pubmed document (id: %s)" % self.name
    
    def as_text(self):
        return " ".join(self.json['article_text'])
    
    def summary(self):
        return " ".join(self.json['abstract_text'])
    
    def key_words(self):
        pass