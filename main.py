import asyncio

from alternate.scraper import run_alternate
from mindfactory.scraper import run_mindfactory
from caseking.scraper import run_caseking

from alternate.urlbuilder import choice_category as choice_alternate
from caseking.urlbuilder import choice_category as choice_caseking
from mindfactory.urlbuilder import choice_category as choice_mindfactory

from save import save_json
from database import save_products
from config import SAVE_ALTERNATE, SAVE_CASEKING, SAVE_MINDFACTORY


async def process_alternate(category):
    products = await asyncio.to_thread(run_alternate, category)

    if products:
        save_json(products, SAVE_ALTERNATE)
        save_products(products)

    print("Alternate finished and saved")


async def process_caseking(category):
    products = await asyncio.to_thread(run_caseking, category)

    if products:
        save_json(products, SAVE_CASEKING)
        save_products(products)

    print("Caseking finished and saved")


async def process_mindfactory(category):
    products = await asyncio.to_thread(run_mindfactory, category)

    if products:
        save_json(products, SAVE_MINDFACTORY)
        save_products(products)

    print("Mindfactory finished and saved")


async def main():

    alternate_category = choice_alternate()
    caseking_category = choice_caseking()
    mindfactory_category = choice_mindfactory()

    await asyncio.gather(
        process_alternate(alternate_category),
        process_caseking(caseking_category),
        process_mindfactory(mindfactory_category),
    )


if __name__ == "__main__":
    asyncio.run(main())