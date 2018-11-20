import spacy
from spacy.tokens import Doc
from multiprocessing import cpu_count
import random
from collections import Counter
import itertools

def stop_words_pipe(doc):
    tokens = [token.text for token in doc if token.is_stop is False]
    return Doc(doc.vocab, words=tokens)
    
def get_nlp():
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "ner"])    
    nlp.add_pipe(stop_words_pipe, name="stop_words", first=True)
    return nlp

class CondenseStoryTransforms:
    @staticmethod
    def first_sentences(data, n, offset = 0):
        nlp = get_nlp()
        out = []
        for doc in nlp.pipe(data, batch_size=10, n_threads=cpu_count()):
            sentences = list(doc.sents)
            sentences = sentences[offset:offset+n+1]
            out.append(sentences)
        return out

    @staticmethod
    def last_sentences(data, n, offset = 0):
        nlp = get_nlp()
        out = []
        for doc in nlp.pipe(data, batch_size=10, n_threads=cpu_count()):
            sentences = list(doc.sents)
            if offset > 0:
                out.append(sentences[-n:-offset])
            else:
                out.append(sentences[-n:])

        return out
    
    @staticmethod
    def random_sentences(data, n):
        nlp = get_nlp()
        out = []
        for doc in nlp.pipe(data, batch_size=10, n_threads=cpu_count()):
            sentences = list(doc.sents)
            
            random_indices = random.sample(range(len(sentences)), n)
            randomized = [sentences[i] for i in random_indices]
            
            out.append(randomized)
        
        return out
    
    @staticmethod
    def random_words(data, n):
        nlp = get_nlp()
        out = []
        for doc in nlp.pipe(data, batch_size=10, n_threads=cpu_count()):
            tokens = [token.text for token in doc]
            
            random_indices = random.sample(range(len(tokens)), n)
            randomized = [tokens[i] for i in random_indices]
            
            out.append(randomized)
        return out
    
    @staticmethod
    def most_common_words(data, n):
        nlp = get_nlp()
        out = []
        for doc in nlp.pipe(data, batch_size=10, n_threads=cpu_count()):
            tokens = [token.text for token in doc]
            
            word_freq = Counter(tokens)
            common = word_frew.most_common(n)
            common = [pair[0] for pair in common]
            
            out.append(common)
        return out
    
    @staticmethod
    def least_common_words(data, n):
        nlp = get_nlp()
        out = []
        for doc in nlp.pipe(data, batch_size=10, n_threads=cpu_count()):
            tokens = [token.text for token in doc]
            
            word_freq = Counter(tokens)
            common = word_frew.most_common()
            common = [pair[0] for pair in common]
            
            least_common = common[-n:]
            out.append(least_common)
        return out

class VocabularyTransforms:
    @staticmethod
    def to_indices(data):
        pass
    
    @staticmethod
    def from_indices(data, vocab):
        pass
    
class TextTransforms:    
    @staticmethod
    def tokenize(data):
        nlp = get_nlp()
        tokenized = []
        for doc in nlp.pipe(data, batch_size=10, n_threads=cpu_count()):
            tokens = [token.text for token in doc]
            tokenized.append(tokens)
        
        return tokenized
    
    @staticmethod
    def to_strings(spans):
        sentences = []
        for span in spans:
            sentence = [token.text for token in span]
            sentence = " ".join(sentence)
            sentences.append(sentence)
        return sentences
    
    @staticmethod
    def to_categorical(data):
        pass

class SeriesTransforms:
    @staticmethod
    def values(data):
        return data.values