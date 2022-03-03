from pathlib import Path
import glob
import random
from base_classes import Dataset, Document


class NUS(Dataset):
    has_sums = True
    has_kwds = True

    def __init__(self, path="dataset/NUS/", include_abs=False,
                 count=None, order=Dataset.SORTED):
        self.path= path
        self.docs_path = path + ("docsutf8_full/*.txt" if include_abs else "docsutf8_noAbstract/*.txt")
        self.sums_path = path + "abs/docsutf8/*.txt"
        self.kwds_path = path + "keys/docsutf8/*.key"
        self.include_abs = include_abs
        self.order = order

        fileCount = len(glob.glob(self.docs_path))
        if count is None:
            self.count = fileCount
        else:
            self.count = min(count, fileCount)

    def __str__(self):
        if self.include_abs:
            return "NUS (with abstracts) at " + self.docs_path
        else:
            return "NUS (without abstracts) at " + self.docs_path
    
    def __iter__(self):
        doc_files = sorted(glob.glob(self.docs_path))
        sum_files = sorted(glob.glob(self.sums_path))
        kwd_files = sorted(glob.glob(self.kwds_path))

        assert len(doc_files) == len(sum_files) == len(kwd_files)
        
        if self.order == Dataset.RANDOM:
            temp = list(zip(doc_files, sum_files, kwd_files))
            random.shuffle(temp)
            doc_files, sum_files, kwd_files = zip(*temp)
        
        for i, doc_path, sum_path, kwd_path in zip(range(self.count), doc_files, sum_files, kwd_files):
            yield NUSDoc(
                doc_path,
                sum_path,
                kwd_path
            )


class NUSDoc(Document):
    has_summary = True
    has_key_words = True
    
    def __init__(self, doc_path, sum_path, kwd_path):
        self.doc_path = doc_path
        self.sum_path = sum_path
        self.kwd_path = kwd_path

        self.name = Path(doc_path).stem
        self.fname = Path(doc_path).name
    
    def __str__(self) -> str:
        return "NUS document at " + self.doc_path
    
    def as_text(self):
        with open(self.doc_path, 'r', encoding='utf8') as f:
            s = f.read()

        return s.replace('-',' ')
        # return s
        
    def summary(self):
        with open(self.sum_path, 'r', encoding='utf8') as f:
            summary = f.read()
        return summary.replace('-', ' ')
    
    def key_words(self):
        with open(self.kwd_path, 'r', encoding='utf8') as f:
            kwds = f.read()
        return kwds.replace('-', ' ')