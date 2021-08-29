import pymongo
from bson.objectid import ObjectId
import sys

class MongoInterface:
    def __init__(self,database,connection_str=None):
        '''

        If running locally, make sure you have an active mongo db server running.

        The connection string is only required if your database is on the cloud (Atlas) or if it is local and the
        connection settings (host and port) are non-default. Use db.serverCmdLineOpts() in your mongo shell to check.

        :param database: (str) name of database to work with
        :param connection_str: (str) use if your db server has non-default connection settings or is on the cloud (Atlas)
        '''

        if connection_str:
            self.client = pymongo.MongoClient(connection_str, serverSelectionTimeoutMS=5000)
        else:
            # uses default host (local) and port
            self.client = pymongo.MongoClient()

        self.database = database
        self.db = self.client[str(database)]


    def switch_databases(self,database):
        '''
        Change the current database. If the new database does not exist, then it will be created when the first insert
        occurs.

        Example usage:
        - switch to a new database
            db.switch_databases(database='users')

        :param database: (str) new database
        '''

        self.database = database
        self.db = self.client[str(database)]


    def clear_collection(self,collection):
        '''
        Delete all documents in a collection, leaving it empty.

        :param collection: (str) name
        '''

        self.db[collection].delete_many({})



    def delete_collection(self,collection):
        '''
        Deletes an entire collection from the database.

        Example usage:
            db.delete_collection(collection='users')

        :param collection: (str)
        :return:
        '''

        self.db[collection].drop()

    def delete_documents_by_query(self,collection,query_dict):
        '''
        Deletes documents that match an MQL query.

        Example usage:
        - delete all documents in "user" collection that have an age greater than 29
            db.update_fields_by_query(collection='users',query_dict={"age":{"$gt":29}})

        :param collection: (str)
        :param query_dict: (dict) a valid mongoDB query document e.g. {"age":{"$gt":29}}
        :return:
        '''

        self.db[collection].delete_many(query_dict)

    def delete_documents_by_id(self,collection,doc_ids,convertObjectId=True):
        '''
        Deletes documents that match an input list of id's (primary keys).

        Example usage:
            db.delete_documents_by_id(collection='user',doc_ids=["6129b7e3774460dccb16f7ff"],convertObjectId=True)

        :param collection: (str)
        :param doc_ids: List(str) ids of documents to delete. Can be either strings or ObjectId's, but must be consistent.
        :param convertObjectId: (bool) - True if doc_ids are strings which need to be converted to ObjectId's, False otherwise
        '''

        for id in doc_ids:

            if convertObjectId:
                self.db[collection].delete_one({"_id":ObjectId(id)})
            else:
                self.db[collection].delete_one({"_id":id})


    def upload_collection(self,data,collection,field_map=None,use_index_as_id=True):
        '''
        Upload multiple documents to a database collection (existing or non-existing).
        If the collection does not exist, it will be created.

        If use_index_as_id is True, than the primary index will be the dictionary key or list index of the document.
        Alternatively, if use_index_as_id is set to False, if one of the db-fields in the field_map is _id, then that
        json-field will be the primary index. If _id is not assigned to any of the json-fields in this scenario, then
        the primary index will be automatically generated (an ObjectId).

        Example usage:
        - Upload a dictionary of dictionaries to a collection called "items", using key as primary index
            db.upload_collection( data, collection='items' )
        - Only upload name and price fields for each document, and map name in the input data to item name in the db.
            db.upload_collection( data, collection='items' , {"name":"item_name","price":"price"} )
        - Upload a dictionary of dictionaries, using the field _id in the documents as primary index
             db.upload_collection( data, collection='items',use_index_as_id=False )

        :param data: list of json's (one per document)
        :param field_map: e.g. {'a':'a','b':'c'}. json-field:db-field
        :param use_index_as_id: (bool) what to set as the primary index
        :return:
        '''

        if type(data).__name__ == 'dict':
            for key,entry in data.items():
                if use_index_as_id:
                    if field_map:
                        field_map["_id"] = "_id"
                    entry["_id"] = key
                self.upload_document(entry,collection,field_map)
        elif type(data).__name__ == 'list':
            for i,entry in enumerate(data):
                if use_index_as_id:
                    if field_map:
                        field_map["_id"] = "_id"
                    entry["_id"] = i
                self.upload_document(entry,collection,field_map)



    def upload_document(self,document,collection,field_map=None):
        '''
        Upload a single document to a database collection (existing or non-existing).
        If the collection does not exist, it will be created.

        If one of the db-fields in the field_map is _id, then that json-field will be the primary index. If _id is not
        assigned to any of the json-fields, then the primary index will be automatically generated (an ObjectId).

        The field map can be used to re-map field names within the document to new field names in the db and also to ignore
        certain fields. If None (default), the fields and values in the document are mirrored exactly in the db.

        Example usage:
        - upload a document with the name and price of an item to a collection called "items", with an auto-generated primary index
            db.upload_document( {"name":"ball","price",5}, collection='items' )
        - upload using a custom primary index
            db.upload_document( {"_id":20,"name":"ball","price",5}, collection='items' )
        - map the field "name" to "item_name", and drop the "price" field
            db.upload_document( {"name":"ball","price",5}, collection='items', field_map={"name":"item_name"} )

        :param document: (json)
        :param collection: (str)
        :param field_map: e.g. {'a':'a','b':'c'}. json-field:db-field. Default None uses preserves all key-value pairs in the document
        :return:
        '''

        if field_map is None:
            doc = document
        else:
            doc = {}
            for (json_field, db_field) in field_map.items():
                if json_field in document.keys():
                    doc[db_field] = document[json_field]
                else:
                    sys.stderr.write(f'key: {json_field} not in document.')

        self.db[collection].insert_one(doc)

    def download_documents_by_id(self,collection,doc_ids,convertObjectId=True):
        '''
        Queries documents with a list of id's (primary indexes). All fields within document are returned.

        Example usage:
        - download documents using string indexes which need to be converted to ObjectId's
            docs = db.download_documents_by_id('user', ["6129b5ff77","6129b7e377"], convertObjectId=True)
        - download documents using ObjectId's
            docs = db.download_documents_by_id('user', [ObjectId("6129b5ff77"),ObjectId("6129b7e377")], convertObjectId=False)

        :param collection: (str)
        :param doc_ids: List(str) ids of documents to download. Can be either strings or ObjectId's, but must be consistent.
        :param convertObjectId: bool - True if doc_ids are strings which need to be converted to ObjectId's, False otherwise
        :return: dictionary
        '''

        docs = {}
        for id in doc_ids:

            if convertObjectId:
                docs[id] = self.db[collection].find_one({"_id":ObjectId(id)})
            else:
                docs[id] = self.db[collection].find_one({"_id":id})

        return docs


    def download_collection(self,collection,display_fields=None,sort_field=None,ascend=True,num_results=None,
                            output_dict=True,convertObjectId=True):
        '''
        Reads all documents within a collection.

        Example usage:
        - download entire collection as dictionary
            docs = db.download_collection(collection='items')
        - only download the names and prices from a collection
            docs = db.download_collection(collection='items',display_fields=['name','price'] )
        - sort by increasing price and download as list
            docs = db.download_collection(collection='items',sort_by=['price'],output_dict=False)

        :param collection: (str)
        :param display_fields: List(str) names of fields to return (if available)
        :param sort_field: (str) field to sort by (default None will not sort)
        :param ascend: (bool) only relevant if sort_field is not None - True: ascend, False: descend
        :param num_results: (int) limits the number of documents returned (default None returns all documents)
        :param output_dict: (bool) True: returns documents as dict values with _id as key, False: returns documents as list
        :param convertObjectId: (bool) True: only relevant if output_dict is True - keys are converted from ObjectId's to strings
        :return: dict or list of documents
        '''

        return self.query(collection,{},display_fields,sort_field,ascend,num_results,output_dict,convertObjectId)



    def query(self,collection,query_dict,display_fields=None,sort_field=None,ascend=True,num_results=None,
              output_dict=True,convertObjectId=True):
        '''
        Returns documents within a collection that match an MQL query.

        Example usage:
        - read all users who's age is greater than 29, and display their name and age
            db.query(collection='user',query_dict= {"age": {"$gt": 29}},display_fields=['name','age'])
        - sort by decreasing age
            db.query(collection='user',query_dict= {"age": {"$gt": 29}},display_fields=['name','age'],sort_field='age',ascend=False)
        - return as a list instead of a dictionary
            db.query(collection='user',query_dict= {"age": {"$gt": 29}},display_fields=['name','age'],output_dict=False)

         :param collection: (str)
         :param query_dict: (dict) a valid mongoDB query document e.g. {"age":{"$gt":29}}
         :param display_fields: List(str) names of fields to return (if available)
         :param sort_field: (str) field to sort by (default None will not sort)
         :param ascend: (bool) only relevant if sort_field is not None - True: ascend, False: descend
         :param num_results: (int) limits the number of documents read and returned (default None returns all documents matching the query)
         :param output_dict: (bool) True: returns documents as dict values with _id as key, False: returns documents as list
         :param convertObjectId: (bool) True: only relevant if output_dict is True - keys are converted from ObjectId's to strings
         :return: dict or list of documents
         '''

        results = self.db[collection].find(query_dict)

        if sort_field:
            if ascend:
                direction = 1
            else:
                direction = -1
            results = results.sort(sort_field,direction)

        if num_results:
            results = results.limit(num_results)

        if output_dict:
            docs = {}
        else:
            docs = []
        for result in results:
            if display_fields:
                doc = {}
                for field in display_fields:
                    if field in result.keys():
                        doc[field] = result[field]
                filtered_result = doc
            else:
                filtered_result = result

            if output_dict:
                if convertObjectId:
                    if type(result["_id"]).__name__ == 'ObjectId':
                        key = str(result["_id"])
                    else:
                        key = result["_id"]
                else:
                    key = result["_id"]
                docs[key] = filtered_result
            else:
                docs.append(filtered_result)

        return docs


    def update_fields_by_query(self,collection,query_dict,update_dict):
        '''
        Updates the fields of documents that match a query.
        If a field doesn't exist within the document then it will be created.

        Example usage:
        - set the employed status of users aged over 29 to be True
            db.update_fields_by_query(collection='user',query_dict={"age":{"$gt":29}}, update_dict={"$set":{"employed":True}})

        :param collection: (str)
        :param query_dict: (dict) a valid mongoDB query document e.g. {"age":{"$gt":29}}
        :param update_dict: (dict) a valid mongoDB update document e.g. {"$set":{"status":True}}
        :return:
        '''

        self.db[collection].update_many(query_dict,update_dict)

    def update_fields_by_id(self,collection,doc_ids,update_dict,convertObjectId=True):
        '''
        Updates the fields of documents that match an input list of id's (primary keys).
        If a field doesn't exist within the document then it will be created.

        Example usage:
            db.update_fields_by_id(collection='user',doc_ids=["61274b65","612752"],update_dict={"$set":{"employed":True}},convertObjectId=True)

        :param collection: (str)
        :param doc_ids: List(str) ids of documents to update. Can be either strings or ObjectId's, but must be consistent.
        :param update_dict: (dict) a valid mongoDB update document e.g. {"$set":{"status":True}}
        :param convertObjectId: (bool) - True if doc_ids are strings which need to be converted to ObjectId's, False otherwise
        '''

        for id in doc_ids:

            if convertObjectId:
                self.db[collection].update_one({"_id":ObjectId(id)},update_dict)
            else:
                self.db[collection].update_one({"_id":id},update_dict)





