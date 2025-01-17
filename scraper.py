import re
import shelve
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.robotparser
from utils import get_urlhash
from collections import Counter
from http.client import InvalidURL
import hashlib

# ********** HELPER FUNCTIONS **********
# The tokenize function runs in linear-time relative to the number of words in the text O(n)
def tokenize(text: str) -> list:
    # Used set instead of list since performing the 'in' operator against a set is about O(1).
    stop_words = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", 
                  "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", 
                  "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", 
                  "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", 
                  "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", 
                  "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", 
                  "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", 
                  "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", 
                  "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", 
                  "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "also", "can", "com", "following", "get", "make", "use", "will"}
    
    pattern = re.compile(r"[a-zA-Z0-9]{3,}(?:'?[a-zA-Z0-9])*(?:-*[a-zA-Z0-9]+)*") # Declaring alphanumeric pattern inlcuding ' and -                                                                     # to check the words in the text file provided 
    text = text.lower().rstrip() # Convert all words in line to lower-case and strip off any white space at end of line
    words = re.findall(pattern, text) # find all words in line that match the aplhanumeric pattern declared above
    
    # Filter the words in text to remove the English stop words.
    result = list(filter(lambda x: x not in stop_words, words))
    return result

# The compute_word_frequencies function runs in linear time relative to the number of tokens in the list O(n)
def compute_word_frequencies(tokens: list) -> defaultdict:
    frequencies = defaultdict(int) # Map of each token and its' number of occurences in the file
    
    for token in tokens: # Iterate through the list of tokens/words and increment the count of each word's occurence
        frequencies[token] += 1
    
    return frequencies

def process_report():
    with shelve.open('frontier.shelve') as shelve_file:
        print(f"1. Number of unique pages found: {len(shelve_file)}")
    with shelve.open('data.shelve') as shelve_file:
        print(f"2. Longest page in terms of the number of words: {shelve_file[max(shelve_file, key=lambda x: len(shelve_file[x][3]))][0]}")

        all_word_freqs = defaultdict(int) # Initializing dictionary which will contain every word and its frequency from all web pages
        # Iterate through all the word:frequency dictionaries corresponding to each webpage
        for tup in shelve_file.values():
            for word, freq in tup[3].items():
                all_word_freqs[word] += freq # Add each word and its frequency to the master dictionary
        all_word_freqs = sorted(all_word_freqs.items(), key=lambda x: x[1], reverse=True) # Sort the master dictionary by word frequency in descending order
        
        # Remove word:frequency pairings from master list that are not present in every webpage 
        for pair in all_word_freqs:
            for tup in shelve_file.values():
                if (pair[0] not in tup[3]):
                    all_word_freqs.remove(pair)
                    break

        top_50 = all_word_freqs[:50] # Cut down the list to only keep the top 50 words with the highest frequencies
        print("3. 50 most common words in entire set of pages crawled:")
        for word, frequency in top_50:
            print(f"{word}: {frequency}")
        
        subdomains = []
        # Iterate through the webpages and check if their domain is ics.uci.edu, if it is, add it to the subdomains list along with that webpage's url count
        for tup in shelve_file.values():
            if (re.match(r"^.+\.ics\.uci\.edu/?$", tup[0])):
                subdomains.append((tup[0], tup[2]))
        subdomains.sort(key=lambda x: x[0]) # Sort the subdomains alphabetically
        print("4. ics.uci.edu subdomains and unique page count:")
        for sub, count in subdomains:
            print(f"{sub}, {count}")

def detect_repeating_path(parsed):
    directories = parsed.path.split('/')
    directory_frequency = Counter(directories).most_common() # Finds how many times a directory appears in the url path.
    repeating_directories = [x for x in directory_frequency if x[0] and x[1] > 1] # Finds the directories that repeat in the url path.
    if repeating_directories: # Checks if there are any repeating directories in the url path.
        return True

def detect_exact_similarity(text_hash):
    with shelve.open('data.shelve') as shelve_file:
        for key in shelve_file:
            if text_hash == shelve_file[key][4]: # Checks if current page has a similar hash to any page already crawled.
                return True
    return False

def detect_near_similarity(token_frequency):
    with shelve.open('data.shelve') as shelve_file:
        for key in shelve_file:
            dict1_keys = token_frequency.keys()
            dict2_keys = shelve_file[key][3].keys()
            dicts_intersection = dict1_keys & dict2_keys
            dicts_union = dict1_keys | dict2_keys
            if dicts_union and len(dicts_intersection)/len(dicts_union) >= 0.9: # Checks if the similarity ratio between pages meets the 90% threshold.
                return True
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

    if not resp or not resp.raw_response:
        return list()
    
    # Checks for valid status code.
    # HTTP Code 301 = Redirected to new page permanetly, code needs to be allowed to index page.
    # HTTP Code 302 = Redirected to new page temporarly, code is not accepted due to potential trap.
    if resp.status not in [200, 301]:
        return list()

    # Checks if the size of the page is greater than the current threshold.
    page_size = len(resp.raw_response.content)
    if page_size > 200000 or page_size < 8000: # 200000 bytes = 0.2 mb, 8000 bytes = 0.008 mb.
        return list()

    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    for element in soup(["script", "style", 'head', 'title', 'meta', '[document]']):
        element.extract()
    text = soup.get_text(" ", strip=True)

    # Handles dead urls.
    if resp.status == 200 and not text:
        return list()

    # Checks if the size of the page's text is sufficient enough to be crawled.
    if len(text) < 500:
        return list()

    # Checks for exact text duplication.
    md5_hash = hashlib.md5(text.encode())
    if detect_exact_similarity(md5_hash.hexdigest()):
        return list()

    # Checks for near text duplication.
    token_frequency = compute_word_frequencies(tokenize(text))
    if detect_near_similarity(token_frequency):
        return list()

    # Iterates through the elements with anchor tag 'a'. soup.find_all('a') returns an iterable that stores the hyperlinks found in the current page. 
    # hyperlink.get('href') returns the hyperlink's destination, which could be a relative/absolute url. absolute_url.split('#')[0] removes fragment from url.
    urls = []
    for hyperlink in soup.find_all('a'):
        absolute_url = urljoin(resp.url, hyperlink.get('href'))
        urls.append(absolute_url.split('#')[0])

    with shelve.open('data.shelve') as shelve_file:
        urlhash = get_urlhash(url)
        shelve_file[urlhash] = (resp.url, resp, len(urls), token_frequency, md5_hash.hexdigest())
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
        
        # Sets up the parser with the url of the domain/robots.txt file and reads the file.
        shelve_file = shelve.open('robots.shelve')
        if parsed.hostname in shelve_file:
            robot_parser = shelve_file[parsed.hostname]
        else:
            robot_parser = urllib.robotparser.RobotFileParser()
            robot_parser.set_url(f"{parsed.scheme}://{parsed.hostname}/robots.txt")
            robot_parser.read()
            shelve_file[parsed.hostname] = robot_parser
            shelve_file.sync()
        shelve_file.close()
        
        # Checks if the current page can be crawled according to its robots.txt.
        if not bool(robot_parser) or not robot_parser.can_fetch("*", url):
            return False

        # Checks if url has repeating directories.
        if detect_repeating_path(parsed):
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
    except InvalidURL:
        print(f"http.client.InvalidURL when setting up robots.txt file for {url}")
        return False


if __name__ == '__main__':
    process_report()