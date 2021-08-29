from pydatabase.mongo_interface import MongoInterface
from pydatabase.sqlite_interface import SqliteInterface
import json
from tqdm import tqdm

DESCRIPTION = """

Populates a mongodb database with data from an sqlite database.

Warning: make sure you have an active mongodb server and an sqlite server setup with data in it!

"""

if __name__ == "__main__":

    # initialise db object's
    db_mongo = MongoInterface('shopdb')
    db_sqlite = SqliteInterface('../data/shop.db')

    # read data from sqlite database
    data = db_sqlite.query(table='items',output_json=True)

    # upload as collection to mongo database
    db_mongo.upload_collection(data, collection='items2', use_index_as_id=False)

