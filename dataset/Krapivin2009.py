from pathlib import Path
import glob
from base_classes import Dataset, Document


class Karpivin2009(Dataset):
    has_sums = True
    has_kwds = True

    def __init__(self, docs, sums, kwds, include_abs=False, order=Dataset.SORTED):
        self.docs_path = docs
        self.sums_path = sums
        self.kwds_path = kwds
        self.include_abs = include_abs
        self.order = order

    def __str__(self):
        return "CNN Big Dataset at " + self.text_path
    
    def __iter__(self):
        doc_files = sorted(glob.glob(self.docs_path))
        sum_files = sorted(glob.glob(self.sums_path))
        kwd_files = sorted(glob.glob(self.kwds_path))

        if self.order == Dataset.RANDOM:
            #TODO: randomize...
            pass

        for doc_path, sum_path, kwd_path in zip(doc_files, sum_files, kwd_files):
            yield Krapivin2009Doc(
                doc_path,
                sum_path,
                kwd_path,
                include_abs=self.include_abs
            )


class Krapivin2009Doc(Document):
    def __init__(self, doc_path, sum_path, kwd_path, include_abs=False):
        self.doc_path = doc_path
        self.sum_path = sum_path
        self.kwd_path = kwd_path
        self.name = Path(doc_path).stem
    
    def __str__(self) -> str:
        return "Krapivin2009 Document at " + self.doc_path
    
    def as_text(self):
        #TODO: Check include_abs
        with open(self.doc_path,'r', encoding='utf8') as f:
            s = f.read()
        return s.replace('-',' ')
    
    def summary(self):
        with open(self.sum_path, 'r') as f:
            summary = f.read()
        return summary
    
    def key_words(self):
        #TODO: Check include_abs
        with open(self.kwd_path, 'r') as f:
            kwds = f.read()
        return kwds.strip().split("\n")
    
    def summary_count(self):
        pass

    def key_word_count(self):
        return len(self.key_words())