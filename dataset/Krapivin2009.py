from pathlib import Path
import glob
import random
from base_classes import Dataset, Document


class Karpivin2009(Dataset):
    has_sums = True
    has_kwds = True

    def __init__(self, path="dataset/Krapivin2009/", include_abs=False,
                 count=None, order=Dataset.SORTED, direct=False):
        self.path = path
        self.docs_path = path + "docsutf8/*.txt"
        self.sums_path = path + "abs/docsutf8/*.txt"
        self.kwds_path = path + "keys/docsutf8/*.key"
        self.include_abs = include_abs
        self.order = order
        self.direct = direct

        fileCount = len(glob.glob(self.docs_path))
        if count is None:
            self.count = fileCount
        else:
            self.count = min(count, fileCount)
        
        assert not direct or include_abs, "If direct=True, include_abs must be True"

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
                include_abs=self.include_abs,
                direct=self.direct
            )


class Krapivin2009Doc(Document):
    has_summary = True
    has_key_words = True
    
    def __init__(self, doc_path, sum_path, kwd_path, include_abs=False, direct=False):
        self.doc_path = doc_path
        self.sum_path = sum_path
        self.kwd_path = kwd_path
        self.include_abs = include_abs
        self.direct = direct

        self.name = Path(doc_path).stem
        self.fname = Path(doc_path).name
    
    def __str__(self) -> str:
        if self.include_abs:
            return "Krapivin2009 document (with abstract) at " + self.doc_path
        else:
            return "Krapivin2009 document (without abstract) at " + self.doc_path
    
    @staticmethod
    def disect_doc(text) :
        title_start = text.find('--T') + 3
        abstract_start = text.find('--A', title_start) + 3
        body_start = text.find('--B', abstract_start) + 3
        body_end = text.find('--R')
        
        return {
            'TITLE': text[title_start:abstract_start-3].strip(),
            'ABSTRACT': text[abstract_start:body_start-3].strip(),
            'BODY': text[body_start:body_end].strip()
        }
    
    def as_text(self):
        with open(self.doc_path, 'r', encoding='utf8') as f:
            s = f.read()

        if self.direct:
            return s.replace('-',' ')
        else:
            parts = self.disect_doc(s)

            if self.include_abs:
                return parts['TITLE'] + ' ' + parts['ABSTRACT'] + ' ' + parts['BODY']
            else:
                return parts['TITLE'] + ' ' + parts['BODY']
    
    def summary(self):
        with open(self.sum_path, 'r', encoding='utf8') as f:
            summary = f.read()
        return summary.replace('-', ' ')
    
    def key_words(self):
        with open(self.kwd_path, 'r', encoding='utf8') as f:
            kwds = f.read()
        return kwds.replace('-', ' ')