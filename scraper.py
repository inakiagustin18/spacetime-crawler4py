import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.robotparser

# ********** HELPER FUNCTIONS **********
# The tokenize function runs in linear-time relative to the number of words in the text O(n)
def tokenize(text: str) -> list:
    result = []
    # Used set instead of list since performing the 'in' operator against a set is about O(1).
    stop_words = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because",
                  "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", 
                  "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", 
                  "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", 
                  "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", 
                  "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours"}
    
    pattern = re.compile(r"[a-zA-Z0-9]+(?:'?[a-zA-Z0-9])*(?:-*[a-zA-Z0-9]+)*") # Declaring alphanumeric pattern inlcuding ' and -                                                                     # to check the words in the text file provided 
    text = text.lower().rstrip() # Convert all words in line to lower-case and strip off any white space at end of line
    words = re.findall(pattern, text) # find all words in line that match the aplhanumeric pattern declared above
    
    # Iterate through the words in text and remove the English stop words
    for word in words:
        if word in stop_words:
            words.remove(word)
    
    result.extend(words) # Place words matching pattern into result list
    return result

# The compute_word_frequencies function runs in linear time relative to the number of tokens in the list O(n)
def compute_word_frequencies(tokens: list) -> defaultdict:
    frequencies = defaultdict(int) # Map of each token and its' number of occurences in the file
    
    for token in tokens: # Iterate through the list of tokens/words and increment the count of each word's occurence
        frequencies[token] += 1
    
    return frequencies
# **************************************


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # Errors check status code
    if resp.status != 200:
        return list()

    # If redirected, resp.raw_response.content is the redirected content.
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    
    urls = []
    # Iterates through the elements with anchor tag 'a'. soup.find_all('a') returns an iterable that stores the hyperlinks found in the current page.
    for hyperlink in soup.find_all('a'):
        # Appends the absolute url into the urls list. hyperlink.get('href') returns the hyperlink's destination, which could be a relative/absolute url. urljoin handles the case
        # where the hyperlink's destination is a relative url. absolute_url.split('#')[0] removes fragment from url.
        absolute_url = urljoin(resp.url, hyperlink.get('href'))
        urls.append(absolute_url.split('#')[0])
    
    text = soup.get_text()
    tokens = tokenize(text)
    token_frequency = compute_word_frequencies(tokens)
    with open("data.txt", 'w') as data:
        data.write(f"resp.raw_response.url: {resp.raw_response.url}\n")
        data.write(f"resp.raw_response.content: {resp.raw_response.content}\n")
        data.write(f"number of urls: {len(urls)}\n")
        for token, count in token_frequency.items():
            data.write(f"{token}: {count}\n")

    return urls

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        currentURL = urllib.robotparser.RobotFileParser()
        parsed = urlparse(url)
        currentURL.set_url(parsed.hostname + "/robots.txt")
        currentURL.read()
    except:
        print("error setting up robots.txt file on")

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

# find # unique pages. check uniqueness by url similarities w/o fragments.
# longest page w num of words
# 50 most common words in the entire set of pages crawled under these domains
# how many subdomains did you find in the ics.uci.edu domain? Submit the list of subdomains ordered alphabetically and the number of unique pages detected in each subdomain
#finish robots.txt parser in is_valid function
#Detect and avoid infinite traps
#Detect and avoid crawling very large files
#Avoid pages with no data 