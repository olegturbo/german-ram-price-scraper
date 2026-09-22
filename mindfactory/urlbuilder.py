from config import URL_MINDFACTORY
from filters.RAM import RAM


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

        if choice in data:
            return data[choice]

        print("Invalid option")


def choice_category():
    return select_option(
        RAM,
        "RAM",
        optional=False
    )


def build_url(category, page):
    category = category.replace("-RAM", "")

    url = f"{URL_MINDFACTORY}/{category}+Module.html"

    if page == 1:
        return url

    return f"{url}/page/{page}"