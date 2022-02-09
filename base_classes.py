import abc
import nltk

class NLPSystem(abc.ABC):
    @abc.abstractmethod
    def __str__(self):
        pass
    
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
        Process a file with your program. If not overwriten, just calls process_text.

        Args:
          path: path to file
          The rest are the same as process_text
        
        Returns:
          key_words: The generated key words, or None
          summary: The generated summary, or None
        
        Note: If not overwritten, this just calls process_text
        """
        with open(path, 'r') as f:
            return self.process_text(f.read(), **kwargs)
    
    def process_files(self, files, **kwargs):
        """
        Runs process_file on each file.

        Args:
          files: (iterator) paths to files
          The rest are the same as process_text
        
        Yields (for each file):
          key_words: The generated key words, or None
          summary: The generated summary, or None
        
        Note: If not overwritten, this just calls process_file
        """
        for f in files:
          yield self.process_file(f, **kwargs)
    
    def answer(self, question):
        raise NotImplemented("Q&A is not implemented yet")


class Dataset(abc.ABC):
    SORTED = 'sorted'
    RANDOM = 'random'

    has_sums = False
    has_kwds = False


    @abc.abstractmethod
    def __str__(self):
        pass
    
    @abc.abstractmethod
    def __iter__(self):
        """
        Note: You must overwrite this method in your subclass!
        
        Yields:
            Document: a subclass of Document with text, summary, and key word info
        """
        pass
    
    def read_files(self):
        for file in self:
            yield self.to_text(file)


class Document(abc.ABC):
    @abc.abstractmethod
    def __str__(self):
        pass
    
    @abc.abstractmethod
    def as_text(self):
        pass

    @abc.abstractmethod
    def summary(self):
        pass
    
    @abc.abstractmethod
    def key_words(self):
        pass
    
    def summary_count(self):
        return len(nltk.sent_tokenize(self.summary()))

    def key_word_count(self):
        return len(self.key_words().splitlines())


class Metric(abc.ABC):
    @abc.abstractmethod
    def __str__(self):
        pass
    
    @abc.abstractmethod
    def compare_sum(self, guess, correct):
        """
        Note: You must overwrite this method in your subclass!
        Compare the generated summary with the "correct" summary
        
        Args:
          guess: the generated summary
          correct: the "correct" summary
        
        Returns:
          score: How close are they?
        """
        pass

    
    @abc.abstractmethod
    def compare_kwds(self, guess, correct):
        """
        Note: You must overwrite this method in your subclass!
        Compare generated key words with the "correct" key words
        
        Args:
          guess: the generated key words
          correct: the "correct" key words
        
        Returns:
          score: How close are they?
        """
        pass