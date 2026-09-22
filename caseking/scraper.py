from curl_cffi import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randrange
from urllib.parse import urljoin

from config import PROXY,HEADERS,URL_CASEKING
from caseking.urlbuilder import build_url

session = requests.Session(impersonate="chrome")
session.proxies.update(PROXY)
session.headers.update(HEADERS)


def get_url(url):
    try:
        response = session.get(url)
        response.raise_for_status()
        response.encoding = "utf-8"
        print(response.status_code)
        return response
    except requests.RequestsError as e:
        print(f"[ERROR] Request failed {e}")
        return None


def parse_html(response):
    return BeautifulSoup(response.text,"lxml")

def last_item(soup):
    navigation = soup.find("ul",class_="pagination")

    if navigation is None:
        return 1

    items = navigation.find_all("a",class_="page-link")
    if items:
        last = items[-2].text.strip()
        return int(last)

    return 1
    

def get_links(soup):
    div = soup.find("div", class_="product-grid")
    links = div.find_all("a", class_="link")

    for link in links:
        url = link.get("href")
        full_url = urljoin("https://www.caseking.de/",url)
        print(full_url)
        yield full_url

def get_info(links):
    products = []

    for link in links:
        try:    
            response = session.get(link)
            response.raise_for_status()
            response.encoding = "utf-8"

            if response is None:
                return None
            soup = BeautifulSoup(response.text,"lxml")

            name = soup.find("h1",class_="product-name").text.strip()
            price = soup.find("span",class_="js-unit-price").text.strip()
            ean = soup.find_all("span", class_="product-attributes-value")[1].text.strip()

            table = soup.find("table",class_="table")
            rows = table.find_all("tr")

            specs = {}

            for row in rows:
                cells = row.find_all("td")

                if len(cells) == 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()

                    specs[key] = value
            
            product = {
                    "name": name,
                    "ean": ean,
                    "price": price,
                    "link": link,
                    "specs": specs
                }

            products.append(product)
            # print(products)

            sleep(randrange(2,3))
        except requests.RequestsError as e:
            print(f"[ERROR] Request failed -> {e}")
            return None

    return products

def run_caseking(category):
    first_url = build_url(category,1)

    response = get_url(first_url)

    if response is None:
        return []

    soup = parse_html(response)
    last = last_item(soup)

    details = []
    links = get_links(soup)
    details.extend(get_info(links))

    if last == 1:
        return details

    for page in range(2,last + 1): #2,3
        url = build_url(category,page)

        response = get_url(url)
        
        if response is None:
            continue

        soup = parse_html(response)
        links = get_links(soup)
        details.extend(get_info(links))

        print(f"Finished page {page}/{last}")

    return details