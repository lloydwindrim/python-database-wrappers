from pydatabase.mongo_interface import MongoInterface
import json
from tqdm import tqdm

DESCRIPTION = """

Populates a mongodb database with some json data.

Warning: make sure you have an active mongodb server!

"""

if __name__ == "__main__":


    # read data
    with open('../data/product_data.json','r') as f:
        data = json.load(f)

    # initialise db object
    db = MongoInterface('shopdb')

    # mapping between json fields and database fields (json-field : db-field)
    field_map = {"name": "id_","category": "category", "price": "price", "stocked": "stocked"}

    # iteratively populate database
    for item in tqdm(data):
        db.upload_document(document=item, collection='items', field_map=field_map)

