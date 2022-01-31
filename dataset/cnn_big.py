import os
import glob
from base_classes import Dataset


class CnnBig(Dataset):
    def __init__(self, path, include_abs=False, sums='../abs/docsutf8', kwds='../keys/docsutf8'):
        self.text_path = os.path.join(path, '*.txt')
        self.sum_path = os.path.join(path, sums, '*.txt')
        self.kwd_path = os.path.join(path, kwds, '*.key')

    def __str__(self):
        return "CNN Big Dataset at " + self.text_path
    
    def __iter__(self):
        print(self.text_path, self.sum_path, self.kwd_path)
        text_files = glob.glob(self.text_path)
        sum_files = glob.glob(self.sum_path)
        kwd_files = glob.glob(self.kwd_path)
        for text, sums, kwds in zip(text_files, sum_files, kwd_files):
            yield text, sums, kwds
