from base_classes import NLPSystem
import sys
import networkx as nx
import nltk


class Textstar(NLPSystem):
    def __init__(self, stanza_path, ranker=nx.pagerank, trim=80):
        """
        Args:
          stanza_path: Path to the StanzaGraphs folder for importing purpose
        """
        self.ranker = ranker
        self.trim = trim
        self.stanza_path = stanza_path
        sys.path.append(stanza_path)
    
    def __str__(self):
        return "Textstar System at " + self.stanza_path

    def process_text(self, document, summarize=True, key_words=True, sum_len=5, kwds_len=5):
        from textstar.textstar import process_text

        text = document.as_text()
        sentence_len = len(nltk.sent_tokenize(text))
        if sum_len > sentence_len:
            print("The document has only", sentence_len, "sentences. sum_len reduced")
            sum_len = sentence_len

        try:
            sentids, kwds = process_text(
                text,
                self.ranker,
                sum_len,
                kwds_len,
                self.trim,
                False
            )
        except:
            print(sum_len, kwds_len)
            print(document)
            raise

        sents = [s for _,s in sentids]

        return kwds, sents
