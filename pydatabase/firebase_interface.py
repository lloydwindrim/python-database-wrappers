import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import sys


def _delete_collection(coll_ref, batch_size):

    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return _delete_collection(coll_ref, batch_size)


class FirebaseInterface:
    def __init__(self,service_key):
        '''
        :param service_key: (str)
        '''

        # Use a service account
        cred = credentials.Certificate(service_key)
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()


    def delete_collection(self,collection,batch_size=10):
        '''
        Deletes an entire collection from the database.

        Example usage:
            db.delete_collection(collection='items')

        :param collection: (str)
        :param batch_size: (int) number of documents to delete at a time.
        :return:
        '''

        coll_ref = self.db.collection(collection)
        _delete_collection(coll_ref,batch_size)


    def delete_documents_by_id(self,collection,doc_ids):
        '''
        Deletes documents that match an input list of id's (primary keys).

        Example usage:
            db.delete_documents_by_id(collection='items',doc_ids=['Baseball','Basketball'])

        :param collection: (str)
        :param doc_ids: List(str) ids of documents to delete.
        :return:
        '''

        for doc_id in doc_ids:
            self.db.collection(collection).document(doc_id).delete()

    def delete_fields_all_docs(self,collection,fields):
        '''
        Deletes specified fields for all documents in a collection.

        Example usage:
            db.delete_fields_all_docs(collection='places',fields=['price','category'])

        :param collection: string e.g. 'products'
        :param fields: List of strings e.g. ['price','category']
        :return:
        '''

        docs = self.db.collection(collection).stream()

        # dictionary used in doc update to delete fields
        delete_dict = {}
        for field in fields:
                delete_dict[field] = firestore.DELETE_FIELD

        # delete fields for all docs
        for doc in docs:
            doc.reference.update(delete_dict)



    def upload_collection(self,data,collection,id=None,field_map=None):
        '''
        Upload multiple documents to a database collection (existing or non-existing). Accepts either a dictionary of
        documents or a list of documents. If the collection does not exist, it will be created.

        For the dictionary, if id is None, then the primary index will be the dictionary key. For the list, if id is
        None, then the primary index will be the index of the document in the list. If id is not None, it should be a
        field that exists within all input documents (doesn't matter what name it gets mapped to in field_map).

        The field map can be used to re-map field names within the document to new field names in the db and also to ignore
        certain fields. If None (default), the fields and values in the document are mirrored exactly in the db.

        Example usage:
        - Upload a dictionary of dictionaries, using the keys as the index
            db.upload_collection( data, collection='items'  )
        - Upload a list or dictionary, using the contents of the "name" field for each document as its index
            db.upload_collection( data, collection='items', id='name'  )
        - Only upload name and price fields for each document, and map name in the input data to item name in the db.
            db.upload_collection( data, collection='items', id='name' , {"name":"item_name","price":"price"} )

        :param data: dictionary or list of documents
        :param collection: (str)
        :param id: what to use as the primary index of each document. Default is None.
        :param field_map: e.g. {'a':'a','b':'c'}. json-field:db-field
        '''
        if type(data).__name__ == 'dict':
            for key,entry in data.items():
                if id:
                    id_ = id
                    id_is_field = True
                else:
                    id_ = key
                    id_is_field = False
                self.upload_document(entry, collection, id_, field_map, id_is_field)
        elif type(data).__name__ == 'list':
            for i,entry in enumerate(data):
                if id:
                    id_ = id
                    id_is_field = True
                else:
                    id_ = i
                    id_is_field = False
                self.upload_document(entry,collection,id_,field_map, id_is_field)


    def upload_document(self,document,collection,id,field_map=None,id_is_field=True):
        '''
        Upload a single document to a database collection (existing or non-existing).
        If the collection does not exist, it will be created.

        The field map can be used to re-map field names within the document to new field names in the db and also to ignore
        certain fields. If None (default), the fields and values in the document are mirrored exactly in the db.

        Example usage:
        - upload a document with the name and price of an item to a collection called "items", using "ball" as the index
            db.upload_document( {"name":"ball","price",5}, collection='items', id='name' )
        - upload using the number 20 as the index
            db.upload_document( {"name":"ball","price",5}, collection='items', id=20, id_is_field=False )
        - map the field "name" to "item_name", and drop the "price" field
            db.upload_document( {"name":"ball","price",5}, collection='items', id='name', field_map={"name":"item_name"} )

        :param document: (dict)
        :param collection: (str)
        :param id: what to use as the primary index of each document.
        :param field_map: e.g. {'a':'a','b':'c'}. json-field:db-field. Default None uses preserves all key-value pairs in the document
        :param id_is_field: (bool) whether the id is the literal primary key or whether it is the field that should be
                            used to get the primary key from within the document.
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
        if id_is_field:
            id_ = document[id]
        else:
            id_ = id
        doc_ref = self.db.collection(collection).document(id_)
        doc_ref.set(doc)

    def download_documents_by_id(self,collection,doc_ids,extractFields=True):
        '''
        Queries documents with a list of id's (primary indexes). All fields within document are returned.

        Example usage:
            docs = db.download_documents_by_id(collection='items',doc_ids=['Baseball','Basketball'])

        :param collection: (str)
        :param doc_ids: list(str) names of documents to download
        :return: if extractField is True, returns all field data for the specified document, else returns DocumentSnapshot.
        '''

        docs = {}
        for document in doc_ids:
            doc_ref = self.db.collection(collection).document(document)
            doc_snapshot = doc_ref.get()
            if extractFields==True:
                docs[doc_ref.id] =  doc_snapshot.to_dict()
            else:
                docs[document.id] = doc_snapshot

        return docs


    def download_collection(self,collection,extractFields=True):
        '''
        Reads all documents within a collection.

        Example usage:
            docs = db.download_collection(collection='items')

        :param collection: (str)
        :param extractFields: if False, returns the raw snapshot. if True, returns snapshot._data
        :return:
        '''

        docs = self.db.collection(collection).stream()

        doc_snapshots = {}
        for doc in docs:

            if extractFields:
                data = doc.to_dict()
            else:
                data = doc
            doc_snapshots[doc.id] = data

        return doc_snapshots


    def query(self,collection,query_tuple,display_fields=None,output_dict=True):
        '''
        Returns documents within a collection that match a valid firebase query tuple.

        Example usage:
        - read all documents with a rating greater than 3.9
            docs = db.query(collection='items', query=('rating','>',3.9))
        - read names only of all documents with a rating greater than 3.9
            docs = db.query(collection='items', query=('rating','>',3.9), display_fields=['name']
        - output as a list instead of a dictionary
            docs = db.query(collection='items', query=('rating','>',3.9), output_dict=False)

        :param collection: (str)
        :param query_tuple: (tuple) (field,opstring,value) e.g. ('rating','>',3.9)
        :param display_fields: List(str) fields to return. Default None returns all.
        :param output_dict: (bool) True: returns documents as dict values with _id as key, False: returns documents as list
        :return:
        '''

        results = self.db.collection(collection).where(query_tuple[0], query_tuple[1], query_tuple[2]).stream()
        if output_dict:
            docs = {}
        else:
            docs = []
        for result in results:
            result_dict = result.to_dict()
            if display_fields:
                doc = {}
                for field in display_fields:
                    if field in result_dict.keys():
                        doc[field] = result_dict[field]
                filtered_result = doc
            else:
                filtered_result = result_dict

            if output_dict:
                docs[result.id] =  filtered_result
            else:
                docs.append(filtered_result)
        return docs


    def delete_fields_by_query(self,collection,fields,query_tuple):
        '''
        Delete specified fields for all documents that match a valid firebase query tuple.

        Example usage:
        - delete the rating and price fields from all documents that have the category "sports"
            db.delete_fields_by_query(collection='items', fields=['rating','price'], query_tuple=('category','==','Sporting Goods'))

        :param collection: (str)
        :param fields: List(str) fields to delete.
        :param query_tuple: (tuple) (field,opstring,value) e.g. ('rating','>',3.9)
        :return:
        '''

        docs = self.db.collection(collection).where(query_tuple[0], query_tuple[1], query_tuple[2]).stream()

        # dictionary used in doc update to delete fields
        delete_dict = {}
        for field in fields:
                delete_dict[field] = firestore.DELETE_FIELD

        # delete fields for all docs
        for doc in docs:
            doc.reference.update(delete_dict)

    def delete_documents_by_query(self,collection,query_tuple):
        '''
        Deletes documents that match a firebase query tuple.

        Example usage:
        - delete all documents that have the category "sports"
            db.delete_fields_by_query(collection='items', query_tuple=('category','==','Sporting Goods'))

        :param collection: (str)
        :param query_tuple: (tuple) (field,opstring,value) e.g. ('rating','>',3.9)
        :return:
        '''

        docs = self.db.collection(collection).where(query_tuple[0], query_tuple[1], query_tuple[2]).stream()

        for doc in docs:
            doc.reference.delete()


    def update_fields_by_query(self,collection,query_tuple,update_dict):
        '''
        Update specific fields for documents that match a firebase query tuple.

        Example usage:
        - update the stock and price fields of all documents that have the category "Sporting Goods"
            db.update_fields_by_query(collection='items',query_tuple=('category','==','Sporting Goods'),
                    update_dict={'stock':False,'price':5.0})

        :param collection: (str)
        :param query_tuple: (tuple) (field,opstring,value) e.g. ('rating','>',3.9)
        :param update_dict: (dict) dictionary containing fields to update and new values e.g {'stock':False,'tagline':"coming soon"}
        :return:
        '''

        docs = self.db.collection(collection).where(query_tuple[0], query_tuple[1], query_tuple[2]).stream()

        # update fields for all docs
        for doc in docs:

            doc.reference.update(update_dict)

    def update_fields_by_id(self,collection,doc_ids,update_dict):
        '''
        Update specific fields for documents from the list of document id's.

        Example usage:
        - update the price of basketball's and baseballs to be $7
            db.update_fields_by_id(collection='items', doc_ids=['basketball','baseball'],update_dict={'price': 7})

        :param collection: (str)
        :param doc_ids: List(str)
        :param update_dict: (dict) dictionary containing fields to update and new values e.g {'stock':False,'tagline':"coming soon"}
        :return:
        '''

        for document in doc_ids:
            doc_ref = self.db.collection(collection).document(document)
            doc_ref.update(update_dict)









