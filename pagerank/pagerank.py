import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    tr = dict()
    numOfPages = len(corpus)

    links = corpus[page]
    
    numOfLinks = len(links)
    if numOfLinks != 0:
        for l in links:
            tr[l] = damping_factor/numOfLinks + (1-damping_factor)/numOfPages
        if len(corpus) != len(tr):
            for page in corpus.keys():  
                if page not in tr.keys():
                    tr[page] = (1-damping_factor)/numOfPages
    else:
        for page in corpus.keys():
            tr[page] = 1/numOfPages
    return tr
    


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    ans = list()
    sampleDict = dict()
    pages = list(corpus.keys())
    page = random.choice(pages)
   
    ans.append(page)
    sampleDict = transition_model(corpus, page , damping_factor)
    prob = sorted(sampleDict.keys())
   
    distribution = list()
    for page in prob:
        distribution.append(sampleDict[page])
    for i in range(n-1):
        x = random.choices(prob,weights = distribution)
        x = x[0]
        ans.append(x)
        sampleDict = transition_model(corpus, x, damping_factor)
        prob = sorted(sampleDict.keys())
        distribution = list()
        for page in prob:
            distribution.append(sampleDict[page])
    tempDict = dict()
    for page in pages:
        tempDict[page] = 0
    for page in pages:
        for p in ans:
            if p == page:
                tempDict[p] +=1
    sampleDict = dict()
    for page in pages:
        sampleDict[page] = tempDict[page]/n
    return sampleDict
                
        
def it(corpus,network ,damping_factor, rank):
        f = False
        t = dict()
        n = len(corpus.keys())
        for page in corpus.keys():
            sum = 0
            for p in network[page]:
                
                sum+= rank[p]/len(corpus[p])
            a = (1-damping_factor)/n + damping_factor*sum
            t[page] = a
        for page in t.keys():
            if abs(rank[page] - t[page]) > 0.001:
                rank[page] = t[page]
                f = True
        if f:
            return it(corpus,network,damping_factor, rank)
        else:
           
            return rank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    network = dict()
    for page in corpus.keys():
        num = set()
        for p in corpus.keys():
            if page == p:
                continue
            for i in corpus[p]:
                if i == page:
                    num.add(p)    
        network[page] = num
 
    iterativeRank = dict()
    for page in network.keys():
        iterativeRank[page] = 1/len(network.keys())

    iterativeRank = it(corpus,network, damping_factor, iterativeRank)

    return iterativeRank

if __name__ == "__main__":
    main()
