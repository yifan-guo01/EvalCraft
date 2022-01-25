import abc

class BaseSystem(abc.ABC):
    @abc.abstractmethod
    def process_text(self, text, summarize=True, key_words=True, sum_len=5, kwds_len=5):
        """
        Note: You must overwrite this method in your subclass!
        
        Args:
          text: text string to process
          summarize: generate summary?
          key_words: extract key words?
          sum_len: max number of summary sentances
          kwds_len: max number of key words/phrases
        
        Returns:
          summary: The generated summary, or None
          key_words: The generated key words, or None
        """
        pass

    def process_file(self, path, **kwargs):
        """
        Process a file with your program:
          path: path to file
          summarize: generate summary?
          key_words: extract key words?
          sum_len: max number of summary sentances
          kwds_len: max number of key words/phrases
        
        Returns:
          summary: The generated summary, or None
          key_words: The generated key words, or None
        
        Note: If not overwritten, this just calls process_text
        """
        with open(path, 'r') as f:
            return self.process_text(f.read(), **kwargs)
    
    def answer(self, question):
        raise NotImplemented("Q&A is not implemented yet")