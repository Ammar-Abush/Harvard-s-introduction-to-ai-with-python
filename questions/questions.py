import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    fileToText = dict()
    for path in os.listdir(directory):
    	PATH = os.path.join(directory, path)
    	if os.path.isfile(PATH):
    		file = open(PATH, "r")
    		fileToText[path] = file.read()
    		file.close()
    return fileToText
    		
    		
    


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    document = nltk.tokenize.word_tokenize(document.lower())
    l = list()
    for word in document:
    	if word not in string.punctuation and word not in nltk.corpus.stopwords.words("english"):
    		l.append(word)
    
    return l


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = dict()
    num_of_docs = len(documents.keys())
    nonrepeat = set(word for words in documents.values() for word in words)
    for word in nonrepeat:
    	s = 0
    	for d in documents.values():
    		if word in d:
    			s+=1
    	if s !=0:
    		idfs[word] = math.log(num_of_docs/s)
    				
    return  idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    text_idf = dict()
    
    for f in files:
    	stf_idf = 0
    	for w in query:
    		s = 0
    		for words in files[f]:
    			if words == w:
    				s+=1
    		if w in idfs:
    			stf_idf += s*idfs[w]
    	if stf_idf != 0:
    		text_idf[f] = stf_idf
    d = dict(sorted(text_idf.items(), key = lambda x : x[1],reverse = True))
    l = list(d.keys())
    print(l)
    return l[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sen = dict()
    for s in sentences:
    	c = 0
    	numofwords = len(sentences[s])
    	portion = 0
    	for word in query:
    		if word in sentences[s]:
    			c+=idfs[word]
    	for words in sentences[s]:
    		if words in query:
    			portion += 1
    	sen[s] = (c, portion/numofwords)
    d = dict(sorted(sen.items(), key = lambda x : x[1], reverse = True))
    l = list(d.keys())
    
    return l[:n]
    
if __name__ == "__main__":
    main()
