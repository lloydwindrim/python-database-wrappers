from pydatabase.firebase_interface import FirebaseInterface
import json
from tqdm import tqdm

DESCRIPTION = """

Populates a firebase database with some json data.

Warning: make sure you have configured firebase and have a service key!

"""

if __name__ == "__main__":


    # read data
    with open('../data/product_data.json','r') as f:
        data = json.load(f)

    # initialise db object
    db = FirebaseInterface('path/to/your/service-key.json')

    # mapping between json fields and database fields (json-field : db-field)
    field_map = {"name": "name", "category": "category", "price": "price", "stocked": "stocked"}

    # iteratively populate database
    for item in tqdm(data):
        db.upload_document(document=item, collection='items', id='name', field_map=field_map)

