from pydatabase.sqlite_interface import SqliteInterface
import json
from tqdm import tqdm

DESCRIPTION = """

Populates an sqlite database with some json data.

Warning: make sure you have already built the shop.db database

"""

if __name__ == "__main__":


    # read data
    with open('../data/product_data.json','r') as f:
        data = json.load(f)

    # initialise db object
    db = SqliteInterface('../data/shop.db')

    # mapping between json fields and database fields (db-field : json-field)
    field_map = {"name": "name", "category": "category", "price": "price", "stocked": "stocked_integer"}

    # iteratively populate database
    for item in tqdm(data):
        item["stocked_integer"] = int(item["stocked"])
        db.insert_row(entry=item,table="items",field_map=field_map)


    # close connection
    db.close()