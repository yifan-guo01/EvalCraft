from pathlib import Path
import json
import random
from base_classes import Dataset, Document


class KP20K(Dataset):
    has_sums = False
    has_kwds = True

    def __init__(self, path="dataset/kp20k/", count=None,
                 order=Dataset.SORTED, dataset="test"):
        self.path = path
        self.txt_path = path + dataset + ".json"
        self.order = order

        file_count = sum(1 for line in open(self.txt_path))
        if count is None:
            self.count = file_count
        else:
            self.count = min(count, file_count)

    def __str__(self):
        return "KP20K at " + self.txt_path
    
    def __iter__(self):
        assert self.order == Dataset.SORTED, "Random order is not supported for KP20K dataset"
        
        with open(self.txt_path, 'r') as f:
            for i, line in zip(range(self.count), f):
                yield KP20KDoc(
                    line
                )

def fileNameFromTitle(title):
    return "".join(c for c in title[:20] if c.isalnum())


class KP20KDoc(Document):
    has_summary = False
    has_key_words = True
    
    def __init__(self, line):
        self.json = json.loads(line)

        self.title = self.json['title']
        self.name = fileNameFromTitle(self.title)
        self.fname = self.name + ".txt"
    
    def __str__(self) -> str:
        return "KP20K document (%s)" % self.title
    
    def as_text(self):
        return self.json['abstract']
    
    def summary(self):
        pass
    
    def key_words(self):
        kwds = [w.strip() for w in self.json['keyword'].split(';')]
        return "\n".join(kwds)