import re
import shelve
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.robotparser
from utils import get_urlhash
from difflib import SequenceMatcher

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
                  "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", 
                  "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", 
                  "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", 
                  "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", 
                  "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", 
                  "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"}
    
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

def process_report(file_name):
    with shelve.open(file_name) as shelve_file:
        print(f"1. Number of unique pages: {len(shelve_file)}")
        print(f"2. Longest page in terms of the number of words: {shelve_file[max(shelve_file, key=lambda x: len(shelve_file[x][3]))][0]}")

def detect_trap(url):
    # repeated_pattern = re.compile(r".*(.+?)\1+$")
    # mystring = '/community/alumni/index.php/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected//stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/index.ph'
    # print(re.match(r"(/\w+/)(?=.*\1)", mystring))
    # # print(repeated_pattern.match())
    # if repeated_pattern.match(parsed.path):
    #     print(repeated_pattern.match(parsed.path).group(1))
    #     return True
    
    with shelve.open('traps.shelve') as shelve_file:
        parsed = urlparse(url)
        key = parsed.hostname
        if key in shelve_file:
            if shelve_file[key][0] >= 100:
                return True
            
            count = shelve_file[key][0]
            latest_url = shelve_file[key][1]
            parsed_latest_url = urlparse(latest_url)
            sequence1 = parsed_latest_url.params + parsed_latest_url.query
            sequence2 = parsed.params + parsed.query
            if latest_url == url:
                return True
            
            # print(f"COMPARISON: {sequence1} ******************* {sequence2}")
            if sequence1 not in  ["", '/'] and sequence2 not in ["", '/']:
                ratio = SequenceMatcher(None, sequence1, sequence2).ratio()
                if parsed_latest_url.path == parsed.path and ratio > 0.9:
                    count += 1
            shelve_file[key] = (count, url)
            # print("COUNT: ", shelve_file[key][0])
            # print("LATEST PATH: ", shelve_file[key][1])
        else:
            shelve_file[key] = (0, url)
    return False
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

    # Error checks status code.
    if resp.status != 200:
        return list()

    # print(resp.raw_response.headers)
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')

    for element in soup(["script", "style", 'head', 'title', 'meta', '[document]']):
        element.extract()
    text = soup.get_text()

    # Handles dead urls.
    if resp.status == 200 and not text:
        return list()

    # Handles downloaded urls that were flagged as traps
    if detect_trap(url):
        return list()

    urls = []
    # Iterates through the elements with anchor tag 'a'. soup.find_all('a') returns an iterable that stores the hyperlinks found in the current page. 
    # hyperlink.get('href') returns the hyperlink's destination, which could be a relative/absolute url. urljoin handles the case where the hyperlink's destination is a relative url.
    # Appends the absolute url into the urls list. absolute_url.split('#')[0] removes fragment from url.
    for hyperlink in soup.find_all('a'):
        absolute_url = urljoin(resp.url, hyperlink.get('href'))
        urls.append(absolute_url.split('#')[0])

    token_frequency = compute_word_frequencies(tokenize(text))
    with shelve.open('data.shelve') as shelve_file:
        urlhash = get_urlhash(url)
        shelve_file[urlhash] = (resp.url, resp, len(urls), token_frequency)
        shelve_file.sync()

    return urls

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # Checks if domain is in the list of allowed domains.
        if not re.match(r".*\.(ics|cs|informatics|stat)\.uci\.edu", str(parsed.hostname)):
            return False

        # Set up the parser with the url of the domain/robots.txt file and read the file.
        shelve_file = shelve.open('robots.shelve')
        if parsed.hostname in shelve_file:
            robot_parser = shelve_file[parsed.hostname]
        else:
            robot_parser = urllib.robotparser.RobotFileParser()
            robot_parser.set_url(parsed.scheme + "://" + parsed.hostname + "/robots.txt")
            robot_parser.read()
            shelve_file[parsed.hostname] = robot_parser
            shelve_file.sync()
        shelve_file.close()
        
        # Checks if the current page can be crawled according to its robots.txt.
        if not bool(robot_parser) or not robot_parser.can_fetch("*", url):
            return False

        # Handles traps
        if detect_trap(url):
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
    except urllib.error.URLError:
        print(f"urllib.error.URLError when setting up robots.txt file for {url}")
        shelve_file[parsed.hostname] = None
        shelve_file.close()
        return False

if __name__ == '__main__':
    # sequence1 = "/alumni/stayconnected/stayconnected/stayconnected/stayconnected/index.php"
    # sequence2 = "/alumni/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/index.php"
    # if sequence1 not in  ["", '/'] and sequence2 not in ["", '/']:
    #     print(SequenceMatcher(None, sequence1, sequence2).ratio())
    print(is_valid("https://www.ics.uci.edu/community/news/view_news.php?id=1742"))
    # print(is_valid("https://www.ics.uci.edu/community/alumni/index.php/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected//stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/stayconnected/index.php"))
    # process_report('data.shelve')