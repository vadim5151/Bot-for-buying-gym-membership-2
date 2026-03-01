import requests

from bs4 import BeautifulSoup as bs 


def parse_expertise_article():
    url_expertise = "https://afitness.ru/fitness-magazine/expertise/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url_expertise, headers=headers)
    response.raise_for_status()

    soup = bs(response.text, 'html.parser')

    all_article = []

    articles = soup.find_all('div', class_='art-group')

    for article in articles:
        url_article = article.find('a')['href']

        all_article.append({
        'title': article.find('h5').text,
        'text': article.find('p').text,    
        'url_article':'https://afitness.ru/'+url_article
        })

    return all_article


