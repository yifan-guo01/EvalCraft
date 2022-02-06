from pathlib import Path
import glob
import random
from base_classes import Dataset, Document


class Karpivin2009(Dataset):
    has_sums = True
    has_kwds = True

    def __init__(self, docs, sums, kwds, include_abs=False, count=None, order=Dataset.SORTED):
        self.docs_path = docs
        self.sums_path = sums
        self.kwds_path = kwds
        self.include_abs = include_abs
        self.order = order

        fileCount = len(glob.glob(self.docs_path))
        if count is None:
            self.count = fileCount
        else:
            self.count = min(count, fileCount)

    def __str__(self):
        if self.include_abs:
            return "Krapivin2009 (with abstracts) at " + self.docs_path
        else:
            return "Krapivin2009 (without abstracts) at " + self.docs_path
    
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
        self.include_abs = include_abs

        self.name = Path(doc_path).stem
        self.fname = Path(doc_path).name
    
    def __str__(self) -> str:
        if self.include_abs:
            return "Krapivin2009 Document (with abstract) at " + self.doc_path
        else:
            return "Krapivin2009 Document (without abstract) at " + self.doc_path
    
    def as_text(self):
        #TODO: Check include_abs
        with open(self.doc_path, 'r', encoding='utf8') as f:
            s = f.read()
        return s.replace('-',' ')
    
    def summary(self):
        with open(self.sum_path, 'r', encoding='utf8') as f:
            summary = f.read()
        return summary.replace('-', ' ')
    
    def key_words(self):
        #TODO: Check include_abs
        with open(self.kwd_path, 'r', encoding='utf8') as f:
            kwds = f.read()
        return kwds.replace('-', ' ')
    
    def summary_count(self):
        raise NotImplementedError()

    def key_word_count(self):
        return len(self.key_words())