from bs4 import BeautifulSoup
import requests
# define a function to scrape a website and return its text content
def scrape_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    else:
        return None
# usage of the function 
if __name__ == "__main__":
    url = "https://www.univ-lille.fr"
    
    content = scrape_website(url)
    if content:
        print(content)
    else:
        print("Failed to retrieve website content.")