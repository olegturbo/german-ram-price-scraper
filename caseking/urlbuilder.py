from urllib.parse import urlencode

from filters.RAM import RAM
from config import URL_CASEKING


def select_option(data, title, optional=False):
    print("\n" + "-" * 30)
    print(title)
    print("-" * 30)

    for key, value in data.items():
        print(f"{key}. {value}")

    if optional:
        print("0. Exit")

    while True:
        choice = input("\nSelect: ").strip()

        if optional and choice == "0":
            return None

        if choice == "3":
            print("DDR3 is not available on Caseking.")
            continue

        if choice in data:
            return data[choice]

        print("Invalid option")
        
def choice_category():
    while True:
        category = select_option(
            RAM,
            "RAM",
            optional=False
        )

        if category == "DDR3-RAM":
            print("DDR3 is not available on Caseking.")
            continue

        return category


def build_url(category,page):
    category = category.lower().replace("-ram", "")

    params = {
        "page":page
    }

    query = urlencode(params)

    url = f"{URL_CASEKING}/{category}?{query}"

    return url