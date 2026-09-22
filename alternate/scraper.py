from curl_cffi import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randrange

from config import PROXY,HEADERS 
from alternate.urlbuilder import build_url

session = requests.Session(impersonate="chrome")
session.headers.update(HEADERS)
session.proxies.update(PROXY)


def get_url(url):
    try:
        response = session.get(url)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response
    except requests.RequestsError as e:
        print(f"[ERROR] failed requests {url} -> {e}")
        return None


def get_html(response):
    return BeautifulSoup(response.text,"lxml")

def last_item(soup):
    navigation = soup.find("div", class_="d-flex justify-content-center align-items-baseline")

    items = navigation.find_all("a",class_="btn m-1 btn-outline-gray-light")

    if not items:
        return 1
    try:
        last = items[-1].text.strip()
        return int(last)
    except (ValueError, IndexError):
        return 1

def get_links(soup):
    div_list = soup.find("div", class_="grid-container")
    url_links = div_list.find_all("a", class_="card")

    for url in url_links :
        link = url.get("href")
        yield link


def get_info(links):
    details = []

    for link in links:
        try:
            response = session.get(link)

            if response.status_code == 429:
                print(f"[429] Too many requests: {link}")
                continue

            response.raise_for_status()
            response.encoding = "utf-8"

            print(response.status_code)
            print(link)

            soup = BeautifulSoup(response.text, "lxml")

            name = soup.find("strong", class_="product-name").text.strip()
            print(name)

            price = soup.find("span", class_="price").text.strip()

            table = soup.find(
                "div",
                class_="d-block details-www mb-2"
            )

            keys = [
                element.text.strip()
                for element in table.find_all("td", class_="c1")
            ]

            values = [
                element.text.strip()
                for element in table.find_all("td", class_="c4")
            ]

            details.append({
                "name":name,
                "price": price,
                "link": link,
                **{
                    key: value
                    for key, value in zip(keys, values)
                    if key
                }
            })

            sleep(randrange(3, 6))

        except requests.RequestsError as e:
            print(f"[ERROR] failed requests {link} -> {e}")
            continue

    return details

def run_alternate(category):
    first_url = build_url(category, 1)

    response = get_url(first_url)

    if response is None:
        return []

    soup = get_html(response)
    last = last_item(soup)

    details = []

    links = get_links(soup)
    details.extend(get_info(links))

    for page in range(2,last + 1): #2,3
        url = build_url(category,page)

        response = get_url(url)
        
        if response is None:
            continue

        soup = get_html(response)
        links = get_links(soup)
        details.extend(get_info(links))

        print(f"Finished page {page}/{last}")

    return details