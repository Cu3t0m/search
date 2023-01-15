
import requests
from bs4 import BeautifulSoup
from operator import itemgetter
from itertools import chain
import libs.plugins.wikipedia as wiki


def request_neeva(query):
    url = f'https://neeva.com/search?q={query}'
    # neeva makes us do a redirect if we don't save the cookies thx bailey for reminding me
    session = requests.session()
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    result_items = soup.select('.result-container__wrapper-38pV8')
    results = []
    weight = 0
    for result_item in result_items:
        title = result_item.select_one('a.lib-doc-title__link-1b9rC[href]')
        href = result_item.select_one('a.lib-doc-title__link-1b9rC[href]')
        content = result_item.select_one('.lib-doc-snippet__component-3ewW6')
        suggestion = result_item.select_one(
            'a.result-group-layout__queryCorrectedText-2Uw3R[href]')
        results.append({
            'title': title['href'] if title else None,
            'href': href['href'] if href else None,
            'content': content.text if content else None,
            'suggestion': suggestion['href'] if suggestion else None,
            'source': 'neeva',
            'weight': weight
        })
        weight += 0.3
    return results


def request_bing(query):
    url = f'https://www.bing.com/search?q={query}'
    resp = requests.get(url)
    html = resp.text
    soup = BeautifulSoup(html, 'html.parser')
    result_items = soup.select('#b_results > li.b_algo')
    results = []
    weight = 0
    for result_item in result_items:
        title = result_item.select_one('.b_algo > h2 > a')
        href = result_item.select_one('cite')
        content = result_item.select_one('.b_caption > p')
        suggestion = result_item.select_one(
            'li.b_ans > #sp_requery > a[href] > strong')
        results.append({
            'title': title.text if title else None,
            'href': href.text if href else None,
            'content': content.text if content else None,
            'suggestion': suggestion.text if suggestion else None,
            'source': 'bing',
            'weight': weight
        })
        weight += 0.2
    return results


def request_brave(query):
    url = f'https://search.brave.com/search?q={query}'
    resp = requests.get(url)
    html = resp.text
    soup = BeautifulSoup(html, 'html.parser')
    result_items = soup.select('#results > .fdb')
    results = []
    weight = 0
    for result_item in result_items:
        title = result_item.select_one('.snippet-title')
        href = result_item.select_one('.result-header')
        content = result_item.select_one('.snippet-description')
        suggestion = result_item.select_one('.altered-query > .h6 > a')
        results.append({
            'title': title.text if title else None,
            'href': href.text if href else None,
            'content': content.text if content else None,
            'suggestion': suggestion.text if suggestion else None,
            'source': 'brave',
            'weight': weight
        })
        weight += 0.1
    return results


def auto_suggest(query):
    query = query.strip()
    if not query:
        return []
    url = f'https://search.brave.com/api/suggest?q={query}'
    resp = requests.get(url)
    data = resp.json()
    return data[1]


"""
def request_google(query):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    url = f'https://www.google.com/search?nfpr=1&q={query}'
    resp = requests.get(url, headers=headers)
    html = resp.text
    soup = BeautifulSoup(html, 'html.parser')
    result_items = soup.select('div.g')
    results = []
    for result_item in result_items:
        title = result_item.select_one('h3.LC20lb')
        href = result_item.select('div.yuRUbf > a[href], h3.H1u2de > a[href]')
        content = result_item.select_one('div.IsZvec')
        featured_snippet = result_item.select_one('.c2xzTb')
        featured_snippet_content = featured_snippet.select(
            '.hgKElcm, .X5LH0c, .LGOjhe, .iKJnec')
        featured_snippet_title = featured_snippet.select_one(
            '.g > div > div a > h3')
        featured_snippet_href = featured_snippet.select_one('.g > div > div a')
        suggestion = result_item.select_one('a.gL9Hy')
        results.append({
            'title':
            title.text if title else None,
            'href':
            href[0]['href'] if href else None,
            'content':
            content.text if content else None,
            'featured_snippet':
            featured_snippet.text if featured_snippet else None,
            'featured_snippet_content':
            featured_snippet_content.text
            if featured_snippet_content else None,
            'featured_snippet_title':
            featured_snippet_title.text if featured_snippet_title else None,
            'featured_snippet_href':
            featured_snippet_href['href'] if featured_snippet_href else None,
            'suggestion':
            suggestion.text if suggestion else None
        })
    return results
"""


def request_google(query, page=1, headers=None, params=None):
    _headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    if headers != None:
        _headers = headers
    _params = {
        "q": query,
        "start": (page - 1) * 10,
        "hl": "en",
    }
    if params != None:
        _params = params
    # Make a GET request to the Google search page
    r = requests.get("https://www.google.com/search?",
                     headers=_headers,
                     params=_params)
    print(f"Response: {r.status_code}")
    print(f"URL: {r.url}")
    # Parse the HTML of the page
    soup = BeautifulSoup(r.text, "html.parser")
    # Extract the search results
    results = soup.find_all("div", class_="MjjYud")
    print("results: " + str(results))
    res = []
    for result in results:
        try:
            title = result.find("h3", class_="LC20lb MBeuO DKV0Md").text
            link = result.find("a", href=True)["href"]
            try:
                description = result.find(
                    "div",
                    class_="VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf").text
            except:
                description = "N/A"

            res.append({
                "title": title,
                "link": link,
                "description": description
            })
        except:
            continue
    return res


def request(source, query):
    if source == "google":
        #return "Temporarily disabled"
        return request_google(query)
    elif source == "neeva":
        return request_neeva(query)
    elif source == "bing":
        return request_bing(query)
    elif source == "brave":
        return request_brave(query)
    elif source == "all":
        return search_all(query)
    else:
        raise ValueError(
            f"Invalid source: {source}. Valid sources are: google, bing, brave, all"
        )
        return f"Invalid source: {source}. Valid sources are: google, bing, brave"


def search_all(query):
    results = list(
        chain(request_bing(query), request_neeva(query), request_brave(query)))

    sort = sorted(results, key=lambda x: x['weight'])
    filtered_results = list(filter(lambda x: x["href"] is not None, sort))
    return filtered_results


def sidebar(query):
    return wiki.search(query)


def autocomplete(query):
    return auto_suggest(query)
