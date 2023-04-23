import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.robotparser

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

    # ERROR CHECK status code
    if resp.status != 200:
        return list()

    urls = []
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    # Iterate through the elements with anchor tag 'a'. soup.find_all('a') returns an iterable that stores the hyperlinks found in the current page.
    for hyperlink in soup.find_all('a'):
        # Append the absolute url into the urls list. hyperlink.get('href') returns the hyperlink's destination, which could be a relative/absolute url. urljoin handles the case
        # where the hyperlink's destination is a relative url.
        urls.append(urljoin(resp.url, hyperlink.get('href')))
    
    return urls


def tokenize(file):
    # The tokenize function runs in polynomial-time relative to the number of lines and number of words in the file O(n*m)
    result = []
    pattern = re.compile(r"[a-zA-Z0-9]+(?:'?[a-zA-Z0-9])*(?:-*[a-zA-Z0-9]+)*") # Declaring alphanumeric pattern inlcuding ' and - used
    try:                                                                       # to check the words in the text file provided 
        for line in open(file, encoding= 'utf-8'): # Iterating through file line by line
            line = line.lower().rstrip() # Convert all words in line to lower-case and strip off any white space at end of line
            words = re.findall(pattern, line) # find all words in line that match the aplhanumeric pattern declared above
            result.extend(words) # Place words matching pattern into result list
        return result
    except FileNotFoundError:
        print(f'File {file} does not exist')
    except OSError:
        print(f'file {file} is an invalid file')
    except UnicodeDecodeError:
        print(f'{file} is not a text file')

    return result

# The compute_word_frequencies function runs in linear time relative to the number of tokens in the list O(n)
def compute_word_frequencies(tokens: list) -> defaultdict:
    frequencies = defaultdict(int) # Map of each token and its' number of occurences in the file
    
    for token in tokens: # Iterate through the list of tokens/words and increment the count of each word's occurence
        frequencies[token] += 1
    
    return frequencies


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
