# python database wrappers

Light python wrapper classes for some popular databases. 
They provide a simple interface for building, reading, deleting and updating databases.
Currently, supported databases are `sqlite3`, `firebase` and `mongodb`.


## Installation
From root of this directory:
```
pip install .
```
will install `pydatabase` package and its dependency packages: `firebase_admin` and `pymongo[srv]`

The example scripts also use `tqdm`, so you will need to install it in order to run them.

## Requirements for each database

- **SQLite3**: 
You must have an existing sqlite3 database (it can be empty).

- **Firebase**:
You must have a firebase account and database setup, as well as a service key json that links to it. The database can have zero collections in it.

- **MongoDB**:
You will need to have a mongodb server running, either on Atlas or your local machine. 
If Atlas, you will require the connection string.

## Comparison

| Database | Type | Multi-field queries | Host | Mobile-friendly |
| ----------- | ----------- | ----------- | ----------- | ----------- | 
| SQLite3 | relational | :heavy_check_mark: | local + cloud | |
| MongoDB | document |:heavy_check_mark: | local + cloud | |
| Firebase | document | | cloud only | :heavy_check_mark: |

## Example Contents
1. [SQLite3 examples](#SQLite3-examples)
   1. [sqlite: inserting a new row](#sqlite:-inserting-a-new-row)
    2. [sqlite: querying](#sqlite:-querying)
    3. [sqlite: deleting](#sqlite:-deleting)
    4. [sqlite: updating](#sqlite:-updating)
2. [Firebase examples](#firebase-examples)
    1. [fb: uploading](#fb:-uploading)
    2. [fb: querying](#fb:-querying)
    3. [fb: deleting](#fb:-deleting)
    4. [fb: updating](#fb:-updating)
3. [MongoDB examples](#mongodb-examples)
    1. [mongo: uploading](#mongo:-uploading)
    2. [mongo: querying](#mongo:-querying)
    3. [mongo: deleting](#mongo:-deleting)
    4. [mongo: updating](#mongo:-updating)
4. [Populate a MongoDB database from an SQLite3 database](#populate-a-mongodb-database-from-an-sqlite3-database)

## SQLite3 examples

Import the library and initialise the db object:
```
from pydatabase.sqlite_interface import SqliteInterface
db = SqliteInterface('../data/shop.db')
```

### sqlite: inserting a new row
```
db.insert_row(entry={"name":ball,"cost":20.0},table="items",field_map={"name":"name","price":"cost"})
```

### sqlite: querying

Display all item names in db:
```
queries = db.query(table='items',display_fields=('name',) )
```
Display all item names and prices with price less than 50:
```
queries = db.query(table='items',display_fields=('name','price'),query='price<50')
```
Display items with a matching category:
```
queries = db.query(table='items',display_fields=('name','category'),query='category="Sporting Goods"')
```
Display items with a double criteria for query:
```
queries = db.query(table='items',display_fields=('name','category'),query='(category="Sporting Goods")&(price>30)')
```
Display all data in the database:
```
queries = db.query(table='items')
```
Display unique categories:
```
queries = db.get_distinct_values(table='items', field='categories')
```
List fields in the `items` table:
```
db.fields['items']
```
Return the primary key for the `items` table:
```
db.primary_key['items']
```

### sqlite: deleting
delete all sporting goods:
```
db.delete_rows(table='items',query='categories="Sporting Goods"')
```
Clear all rows from a table:
```
db.clear_table(table="items")
```

Delete a table from the db:
```
db.clear_table(table="items")
```
### sqlite: updating
Update the price and stocked status of the `basketball` item:
```
update = {"price": 5.0, "stocked": 1}
db.update_fields(table="items", update=update, query='(name="Basketball")')
```

## Firebase examples

Import the library and initialise the db object:
```
from pydatabase.firebase_interface import FirebaseInterface
db = FirebaseInterface('path/to/your/service-key.json')
```

### fb: uploading
A collection will be created after the first new document is added.

Assume a toy dataset:
```
[{"category": "Sporting Goods", "price": 49.99, "stocked": true, "name": "Football"}, {"category": "Sporting Goods", "price": 9.99, "stocked": true, "name": "Baseball"}, {"category": "Sporting Goods", "price": 29.99, "stocked": false, "name": "Basketball"}, {"category": "Electronics", "price": 99.99, "stocked": true, "name": "iPod Touch"}, {"category": "Electronics", "price": 399.99, "stocked": false, "name": "iPhone 5"}, {"category": "Electronics", "price": 199.99, "stocked": true, "name": "Nexus 7"}]
```

Upload a collection from a json:
```
db.upload_collection( data, collection='items'  )
```


Upload a collection, using the contents of the `name` field as the document id:
```
db.upload_collection( data, collection='items', id='name'  )
```
Only upload name and price fields for each document, and map the field `name` in the input data to `item_name` in the db:
```
db.upload_collection( data, collection='items', id='name' , {"name":"item_name","price":"price"} )
```
Upload a single document using the `name` "ball" as the index:
```
db.upload_document( {"name":"ball","price",5}, collection='items', id='name' )
```
Upload a single document, dropping the `price` field:
```
db.upload_document( {"name":"ball","price",5}, collection='items', id='name', field_map={"name":"name"} )
```

### fb: querying
Download an entire collection:
```
docs = db.download_collection(collection='items')
```

Download documents by id:
```
docs = db.download_documents_by_id(collection='items',doc_ids=['Baseball','Basketball'])
```
Read all documents with a rating greater than 3.9:
```
docs = db.query(collection='items', query=('rating','>',3.9))
```
Read names only of all documents with a rating greater than 3.9:
```
docs = db.query(collection='items', query=('rating','>',3.9), display_fields=['name'])
```
Output queries as a list instead of a dictionary:
```
docs = db.query(collection='items', query=('rating','>',3.9), output_dict=False)
```
### fb: deleting
Delete the `items` collection:
```
db.delete_collection(collection='items')
```

Delete all documents that have the `category` "Sporting Goods":
```
db.delete_fields_by_query(collection='items', query_tuple=('category','==','Sporting Goods'))
```
Delete the documents with id 'Baseball' and 'Basketball':
```
db.delete_documents_by_id(collection='items',doc_ids=['Baseball','Basketball'])
```

Delete the `rating` and `price` fields (keep the documents) from all documents that have the category "Sporting Goods":
```
db.delete_fields_by_query(collection='items', fields=['rating','price'], query_tuple=('category','==','Sporting Goods'))
```
Delete the `price` and `category` fields from all documents (keep the documents):
```
db.delete_fields_all_docs(collection='places',fields=['price','category'])
```
### fb: updating
Update the `stock` and `price` fields of all documents that have the `category` "Sporting Goods":
```
db.update_fields_by_query(collection='items',query_tuple=('category','==','Sporting Goods'),update_dict={'stock':False,'price':5.0})
```
Update the price of specific id's, e.g. basketball's and baseball's, to be $7:
```
db.update_fields_by_id(collection='items', doc_ids=['basketball','baseball'],update_dict={'price': 7})
```

## MongoDB examples
Import the library and initialise the db object:
```
from pydatabase.mongo_interface import MongoInterface
db = MongoInterface('shopdb')
```

### mongo: uploading
A collection will be created after the first new document is added.

Upload a collection from a json, using position in list or dictionary key as primary index:
```
db.upload_collection( data, collection='items' )
```
Only upload `name` and `price` fields for each document, and map `name` in the input data to `item_name` in the db:
```
db.upload_collection( data, collection='items' , {"name":"item_name","price":"price"} )
```
Use autogenerated `ObjectId`'s or `_id` keys in the json as the primary index:
```
db.upload_collection( data, collection='items',use_index_as_id=False )
```
Upload a single document (with auto-generate `ObjectId` as primary index):
```
db.upload_document( {"name":"ball","price",5}, collection='items' )
```
Upload a single document with a custom primary index (e.g. `20`):
```
db.upload_document( {"_id":20,"name":"ball","price",5}, collection='items' )
```
Map the field `name` to `item_name`, and drop the `price` field:
```
db.upload_document( {"name":"ball","price",5}, collection='items', field_map={"name":"item_name"} )
```

### mongo: querying
Download a collection:
```
docs = db.download_collection(collection='items')
```
Download the `names` and `prices` only from a collection:
```
docs = db.download_collection(collection='items',display_fields=['name','price'] )
```
Sort by increasing `price` and download as list:
```
docs = db.download_collection(collection='items',sort_by=['price'],output_dict=False)
```
Download documents that have `ObjectId`'s as primary index, using strings:
```
docs = db.download_documents_by_id('user', ["6129b5ff77","6129b7e377"], convertObjectId=True)
```

Download documents by `ObjectId`:
```
from bson.objectid import ObjectId
docs = db.download_documents_by_id('user', [ObjectId("6129b5ff77"),ObjectId("6129b7e377")], convertObjectId=False)
```
Download all users who's `age` is greater than 29, and display their `name` and `age`:
```
db.query(collection='user',query_dict= {"age": {"$gt": 29}},display_fields=['name','age'])
```
Sort by decreasing age:
```
db.query(collection='user',query_dict= {"age": {"$gt": 29}},display_fields=['name','age'],sort_field='age',ascend=False)
```
### mongo: deleting
Delete collection:
```
db.delete_collection(collection='users')
```
Delete all documents in "user" collection that have an `age` greater than 29:
```
db.update_fields_by_query(collection='users',query_dict={"age":{"$gt":29}})
```
Delete documents by their id (i.e. primary index):
```
db.delete_documents_by_id(collection='user',doc_ids=["6129b7e3774460dccb16f7ff"],convertObjectId=True)
```

### mongo: updating

Update the employed status of a user document by id:
```
db.update_fields_by_id(collection='user',doc_ids=["61274b65","612752"],update_dict={"$set":{"employed":True}},convertObjectId=True)
```

Update the `employed` status of users aged over 29 to be True:
```
db.update_fields_by_query(collection='user',query_dict={"age":{"$gt":29}}, update_dict={"$set":{"employed":True}})
```

## Populate a MongoDB database from an SQLite3 database:

```
# import libraries for mongo and sqlite
from pydatabase.mongo_interface import MongoInterface
from pydatabase.sqlite_interface import SqliteInterface

# initialise db object's
db_mongo = MongoInterface('shopdb')
db_sqlite = SqliteInterface('../data/shop.db')

# read data from sqlite database
data = db_sqlite.query(table='items',output_json=True)

# upload as collection to mongo database
db_mongo.upload_collection(data, collection='items2', use_index_as_id=False)

```