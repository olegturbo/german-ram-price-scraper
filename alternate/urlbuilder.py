from urllib.parse import urlencode

from filters.RAM import RAM
from config import URL_ALTERNATE


def select_option(data,title,optional=False):
    print("\n" + "-" * 30)
    print(title)
    print("-" * 30)

    for key,value in data.items():
        print(f"{key}. {value}")

    if optional:
        print("0. Exit")

    while True:
        choice = input("\nSelect: ").strip()
        if optional and choice == "0":
            return None

        if choice in data:
            return data[choice]

        print("Invalid option")

def choice_category():
    category = select_option(
        RAM,
        "RAM",
        optional=False
    )
    return category


def build_url(category,page):
    params = {
        "page":page
    }

    query = urlencode(params)

    url = f"{URL_ALTERNATE}/{category}?{query}"

    return url