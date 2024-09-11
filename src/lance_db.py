import lancedb

class lanceDB:
    def __init__(self, uri):
        self.uri = uri
        self.db = lancedb.connect(uri)

    def create_table(self, table_name, schema=None, mode="overwrite"):
        print(f"Creating table: {table_name}")
        print(f"mode is {mode}")
        print(f"schema is {schema}")
        return self.db.create_table(table_name, schema=schema, mode=mode)

    def open_table(self, table_name):
        return self.db.open_table(table_name)

    def insert(self, table_name, data):
        self.db.add(table_name, data)

    def query(self, query):
        return self.db.query(query)

    def close(self):
        self.db.close()
        self.async_db.close()
    
    def table_names(self):
        return self.db.table_names()