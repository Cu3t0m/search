import re
import json
import requests
from urllib.parse import urlencode

wikipediaRegex = re.compile("^([^<>]+)$", re.IGNORECASE)

def search(query):
    match = re.match(wikipediaRegex, query)
    if not match:
        return {}
    wikipedia_query = match.group(1)
    summary_json = requests.get(f'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts|pageimages&exintro&explaintext&redirects=1&exsentences=2&titles={wikipedia_query}').json()
    pages = summary_json['query']['pages']
    page_id = list(pages.keys())[0]
    if page_id == '-1':
        return {}
    article = pages[page_id]
    if article['extract'].endswith(':'):
        return {}
    return {
        'sidebar': {
            'title': article['title'],
            'content': article['extract'],
            'image': article['thumbnail']['source'] if 'thumbnail' in article else None,
            'url': f'https://en.wikipedia.org/wiki/{article["title"].replace(" ", "_")}',
            'weight': 0
        }
    }
