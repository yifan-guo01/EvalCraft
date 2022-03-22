from pydoc import doc
import sys
from base_classes import NLPSystem
import os

class DocTalk(NLPSystem):
    def __init__(self, doctalk_path):
        """
        Args:
          doctalk_path: Path to the outer DocTalk folder for importing purpose
        """
        self.doctalk_path = doctalk_path
        sys.path.append(doctalk_path)
        
    
    def __str__(self):
        return "DocTalk System at " + self.doctalk_path
    
    def process_text(self, document, summarize=True, key_words=True, sum_len=5, kwds_len=5):
        text = document.as_text()

        this_dir = os.getcwd()
        os.chdir(self.doctalk_path)

        from doctalk.talk import Talker, nice
        from doctalk.params import talk_params
        
        params = talk_params()
        # params.top_sum = sum_len
        # params.top_keys = kwds_len
        talker = Talker(from_text=text, params=params)
        
        summary = [nice(x[2]) for x in talker.get_summary()]
        key_words = list(talker.get_keys())

        os.chdir(this_dir)

        return key_words, summary