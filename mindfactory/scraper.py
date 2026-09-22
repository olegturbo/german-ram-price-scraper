from patchright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)
from bs4 import BeautifulSoup
from time import sleep
from random import randrange
from tornet import change_ip

from config import PROXY
from mindfactory.urlbuilder import build_url


LAST_LINK_FILE = "last_link.txt"
COMPLETED_FILE = "completed.txt"


def save_last_link(link):
    with open(LAST_LINK_FILE, "w", encoding="utf-8") as f:
        f.write(link)


def load_last_link():
    try:
        with open(LAST_LINK_FILE, "r", encoding="utf-8") as f:
            link = f.read().strip()
            return link or None
    except FileNotFoundError:
        return None


def mark_completed():
    with open(COMPLETED_FILE, "w", encoding="utf-8") as f:
        f.write("completed")


def is_completed():
    try:
        with open(COMPLETED_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() == "completed"
    except FileNotFoundError:
        return False


def reset_progress():
    with open(LAST_LINK_FILE, "w", encoding="utf-8") as f:
        f.write("")

    with open(COMPLETED_FILE, "w", encoding="utf-8") as f:
        f.write("")


def handle_security_check(page, max_wait=30):
    security = page.locator(".security-content").first

    if not security.is_visible():
        return

    print("Security check detected. Waiting...")

    page.wait_for_timeout(3000)

    btn = page.locator(".btn-submit")

    if btn.is_visible():
        btn.click()
        print("Clicked. Waiting for challenge to clear...")

    try:
        page.wait_for_selector(
            ".security-content",
            state="hidden",
            timeout=max_wait * 1000
        )

        print("Challenge cleared.")

    except PlaywrightTimeoutError:
        print(
            f"Challenge not cleared after {max_wait}s."
        )

        raise RuntimeError(
            "Security check not resolved"
        )


def get_url(p, first_url):
    attempt = 0

    while True:
        attempt += 1
        browser = None

        try:
            print(f"Connection attempt: {attempt}")

            browser = p.chromium.launch(
                headless=False,
                proxy=PROXY
            )

            context = browser.new_context()
            page = context.new_page()

            # Homepage
            page.goto(
                "https://www.mindfactory.de/",
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(12000)

            # Security check homepage
            handle_security_check(page)

            page.wait_for_timeout(6000)

            # Cookie settings
            a = page.locator(
                'xpath=//*[@id="cookie-settings-ic"]/div[1]/a[1]'
            )

            if a.is_visible():
                a.click()

            page.wait_for_timeout(3000)

            # Target URL
            page.goto(
                first_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(1500)

            # Security check AGAIN after target URL
            handle_security_check(page)

            return page, context, browser

        except Exception as e:
            print(f"Browser error: {e}")

            if browser:
                try:
                    browser.close()
                except Exception:
                    pass

            try:
                print("Switch IP Tor...")
                print("IP new:", change_ip())

            except Exception as e:
                print(f"change_ip error: {e}")

            print("Await 5 sec...")
            sleep(5)

            print("Reconnect...")


def parse_html(page):
    return BeautifulSoup(
        page.content(),
        "lxml"
    )


def get_links(soup):
    for link in soup.find_all(
        "a",
        class_="phover-complete-link"
    ):
        url = link.get("href")

        if url:
            yield url


def get_links_from_pages(
    page,
    context,
    browser,
    category,
    p
):
    all_links = []
    seen_links = set()
    page_number = 1

    while True:
        url = build_url(
            category,
            page_number
        )

        while True:
            try:
                print(
                    f"Opening category page "
                    f"{page_number}"
                )

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                page.wait_for_timeout(1500)

                # Security check AGAIN
                handle_security_check(page)

                soup = parse_html(page)

                links = list(
                    get_links(soup)
                )

                print(
                    f"Found: {len(links)} products"
                )

                break

            except Exception as e:
                print(
                    f"Error category page "
                    f"{page_number}"
                )

                print(e)

                if not is_connection_error(e):
                    raise

                print("Connection error.")

                try:
                    browser.close()
                except Exception:
                    pass

                print("Switch IP Tor...")

                sleep(5)

                print("Reconnect...")

                page, context, browser = get_url(
                    p,
                    url
                )

        if not links:
            print(
                "No products found. Stop."
            )
            break

        new_links = [
            link
            for link in links
            if link not in seen_links
        ]

        if not new_links:
            print(
                "Page already seen. "
                "Last page reached."
            )
            break

        all_links.extend(new_links)

        seen_links.update(new_links)

        page_number += 1

    return (
        all_links,
        page,
        context,
        browser
    )


def parse_price(price_element):
    price = price_element.get_text(
        "",
        strip=True
    )

    price = (
        price
        .replace("nur", "")
        .replace("€", "")
        .replace("*", "")
        .replace(" ", "")
    )

    if price.endswith(",-"):
        price = price[:-2] + ".00"

    else:
        price = price.replace(",", ".")

    return price


def is_connection_error(error):
    text = str(error).lower()

    connection_errors = [
        "connection",
        "timeout",
        "timed out",
        "net::err",
        "network",
        "proxy",
        "socket",
        "econn",
        "connectionreset",
        "connection refused",
    ]

    return any(
        x in text
        for x in connection_errors
    )


def get_info(
    links,
    page,
    context,
    browser,
    p
):
    products = []

    links = list(links)

    if is_completed():
        print(
            "Previous run completed."
        )

        print(
            "Starting from the beginning."
        )

        reset_progress()

    last_link = load_last_link()

    if last_link and last_link in links:
        index = links.index(last_link)

        print(
            f"Resume de la index "
            f"{index + 1}: {last_link}"
        )

        links = links[index + 1:]

    for link in links:

        retry_count = 0

        while True:
            try:
                print(
                    f"Opening: {link}"
                )

                page.goto(
                    link,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                page.wait_for_timeout(1500)

                # Security check AGAIN
                handle_security_check(page)

                soup = BeautifulSoup(
                    page.content(),
                    "lxml"
                )

                # -------------------------
                # NAME
                # -------------------------

                title = soup.find(
                    "h1",
                    class_="hidden-xs hidden-sm"
                )

                if not title:
                    raise RuntimeError(
                        "Product title not found"
                    )

                name = title.get_text(
                    strip=True
                )

                # -------------------------
                # PRICE
                # -------------------------

                price_element = soup.find(
                    "div",
                    class_="pprice"
                )

                if not price_element:
                    raise RuntimeError(
                        "Price not found"
                    )

                price = parse_price(
                    price_element
                )

                # -------------------------
                # SPECS
                # -------------------------

                table = soup.find(
                    "table",
                    class_="table"
                )

                if not table:
                    raise RuntimeError(
                        "Specs table not found"
                    )

                rows = table.find_all(
                    "tr"
                )

                specs = {}

                for row in rows:

                    cells = row.find_all(
                        "td"
                    )

                    if len(cells) < 2:
                        continue

                    key = cells[0].get_text(
                        strip=True
                    )

                    value = cells[1].get_text(
                        strip=True
                    )

                    specs[key] = value

                # -------------------------
                # SAVE PRODUCT
                # -------------------------

                products.append({
                    "name": name,
                    "price": price,
                    "url": link,
                    "specs": specs
                })

                # Save progress AFTER
                # successful product parsing
                save_last_link(link)

                print(
                    f"Saved: {name}"
                )

                break

            except Exception as e:

                print(
                    f"Error: {link}"
                )

                print(e)

                # Security check failed
                if (
                    "Security check not resolved"
                    in str(e)
                ):
                    print(
                        "Security check failed."
                    )

                    print(
                        "Creating new browser..."
                    )

                    try:
                        browser.close()
                    except Exception:
                        pass

                    sleep(5)

                    page, context, browser = (
                        get_url(
                            p,
                            link
                        )
                    )

                    retry_count += 1

                    print(
                        f"Retry {retry_count}"
                    )

                    continue

                # Normal connection error
                if not is_connection_error(e):
                    print(
                        "Non-network error. "
                        "Next product."
                    )
                    break

                retry_count += 1

                print(
                    f"Connection error. "
                    f"Retry {retry_count}"
                )

                # Close old browser
                try:
                    browser.close()
                except Exception:
                    pass

                print(
                    "Starting new browser..."
                )

                sleep(10)

                # New browser + new IP
                page, context, browser = (
                    get_url(
                        p,
                        link
                    )
                )

        sleep(
            randrange(5, 10)
        )

    mark_completed()

    print(
        "All products processed."
    )

    return (
        products,
        page,
        context,
        browser
    )


def run_mindfactory(category):
    browser = None
    context = None

    with sync_playwright() as p:

        try:
            first_url = build_url(
                category,
                1
            )

            page, context, browser = (
                get_url(
                    p,
                    first_url
                )
            )

            links, page, context, browser = (
                get_links_from_pages(
                    page,
                    context,
                    browser,
                    category,
                    p
                )
            )

            print(
                f"TOTAL LINKS: {len(links)}"
            )

            data, page, context, browser = (
                get_info(
                    links,
                    page,
                    context,
                    browser,
                    p
                )
            )

            return data

        finally:

            if browser:
                browser.close()