import sqlite3


class SqliteInterface:
    def __init__(self,db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        self._get_fields()

    def _get_fields(self):

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        info = self.cursor.fetchall()
        self.tables = []
        for e in info:
            self.tables.append(e[0])

        self.field_info = {}
        self.fields = {}
        self.primary_key = {}
        for table in self.tables:
            self.cursor.execute(f"pragma table_info([{table}])")
            info = self.cursor.fetchall()

            self.field_info[table] = {}
            self.fields[table] = []
            for e in info:
                self.fields[table].append(e[1])
                self.field_info[table][e[1]] = {'idx':e[0],'type':e[2],'not_null':e[3]}
                if e[5] == 1:
                    self.primary_key[table] = e[1]


    def close(self):
        '''
        Disconnect safely from the database.

        :return:
        '''

        self.cursor.close()
        self.connection.close()

    def insert_row(self,entry,table,field_map):
        '''
        Insert a single row (via json) into the database.

        If field from database is not in entry, it will not assign anything to it (and it will get the default or null
        value from database, or trigger an error if the field has a NOT NULL constraint)

        Example usage:
            db.insert_row(entry={"name":ball,"cost":20.0},table="items",field_map={"name":"name","price":"cost"})

        :param entry: json where keys should be in json-field.
        :param table: name of the table to insert into.
        :param field_map: e.g. {'a':'a','b':'c'}. db-field:json-field
        :return:
        '''

        record = ''
        available_fields = []
        for field in self.fields[table]:
            if field_map[field] in entry.keys():
                f = entry[field_map[field]]
                if type(f) == str:
                    record = record + f'\"{f}\",'
                else:
                    record = record + f'{f},'
                available_fields.append(field)
        record = record.rsplit(',',1)[0]

        self.cursor.execute(f"insert into {table} ({','.join(available_fields)}) values({record});")
        self.connection.commit()


    def query(self,table,display_fields=None,query=None,output_json=False):
        '''
        Query a database table with an expression and return selective fields for each query.

        If using a string in query string, make sure to use double quotations within single quotations (or vice-versa).

        Example usage:
        - display all item names in db:
            queries = db.query(table='items',display_fields=('name',) )
        - display all item names and prices with price less than 50
            queries = db.query(table='items',display_fields=('name','price'),query='price<50')
        - display items with a matching category
            queries = db.query(table='items',display_fields=('name','category'),query='category="Sporting Goods"')
        - display items with a double criteria for query
            queries = db.query(table='items',display_fields=('name','category'),query='(category="Sporting Goods")&(price>30)')
        - display all data in the database
            queries = db.query(table='items')


        :param table: (str) name of table
        :param display_fields: tuple(str) column names to output for each returned query e.g. ('name','place'). If None, returns all columns.
        :param query: (str) query expression to perform e.g. 'height<5'
        :param output_json: (bool) True: returns a dictionary of dictionaries (primary key as key) instead of a list of tuples.
        :return: list of tuples
        '''
        if display_fields:
            display_str = ','.join(display_fields)
        else:
            display_str = '*'

        if query is None:
            self.cursor.execute( f"select {display_str} from {table};" )
        else:
            self.cursor.execute(f"select {display_str} from {table} where {query};")


        data = self.cursor.fetchall()

        if output_json:
            if not display_fields:
                display_fields = self.fields[table]
            data_dict = {}
            key_idx = display_fields.index(self.primary_key[table])
            for row in data:
                data_dict[row[key_idx]] = {}
                for i,field in enumerate(display_fields):
                    data_dict[row[key_idx]][field] = row[i]

            data = data_dict

        return data


    def sql_command(self,command,modify_db=False):
        '''
        Perform sqlite commands on the database.

        Example usage:
            queries = db.sql_command("select HEIGHT from TABLE group by HEIGHT;")
            db.sql_command("delete from TABLE where HEIGHT>5;",modify_db=True)

        :param command: (str) Sqlite command
        :param modify_db: (bool) False if reading, True to mutate the database.
        :return: list of tuples
        '''

        self.cursor.execute(command)

        if modify_db:
            self.connection.commit()
        else:
            return self.cursor.fetchall()

    def delete_rows(self,table,query):
        '''
        Delete rows which satisfy the condition in query.

        Example usage:
        - delete all sporting goods
            db.delete_rows(table='items',query='categories="Sporting Goods"')

        :param table: (str) name of table
        :param query: (str) query expression to perform e.g. 'height<5'
        :return: 0
        '''

        self.cursor.execute(f"delete from {table} where {query};")
        self.connection.commit()

    def delete_table(self,table):
        '''
        Delete an entire table from the database.

        Example usage:
            db.delete_table(table='items')

        :param table: (str) table to detele
        :return: 0
        '''

        self.cursor.execute(f"drop table {table};")
        self.connection.commit()

    def clear_table(self,table):
        '''
        Clears all rows from table, leaving it empty.

        Example usage:
            db.clear_table(table="items")

        :param table: (str) name of table
        :return: 0
        '''

        self.cursor.execute(f"delete from {table};")
        self.connection.commit()

    def get_distinct_values(self,table,field):
        '''
        Return unique values for a given field.

        Example usage:
        - find all types of categories
            queries = db.get_distinct_values(table='items', field='categories')

        :param table: (str)
        :param field: (str)
        :return: list(str)
        '''

        self.cursor.execute(f"select distinct {field} from {table};")
        return self.cursor.fetchall()



    def update_fields(self,table,update,query):
        '''
        Update specific fields for a row.

        Example usage:
        - update the price and stocked status of the basketball item
            update = {"price": 5.0, "stocked": 1}
            db.update_fields(table="items", update=update, query='(name="Basketball")')

        :param table: (str)
        :param update: (dict) keys = field names, values = updated values for those fields
        :param query: (str) query expression to perform e.g. 'height<5'
        :return: 0
        '''
        update_str = ''
        for key, value in update.items():
            update_str = update_str + key + '='
            if type(value) == str:
                update_str = update_str + f'\"{value}\",'
            else:
                update_str = update_str + f'{value},'
        update_str = update_str.rsplit(',',1)[0]

        self.cursor.execute(f"update {table} set {update_str} where {query};")
        self.connection.commit()


    def export_fields_to_csv(self):

        pass

