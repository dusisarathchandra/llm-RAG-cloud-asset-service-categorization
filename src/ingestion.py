#!/usr/bin/env python

import sys,os
#print(sys.path)
import lancedb
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import os, sys
module_path = sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../'))
sys.path.append(module_path)
#print(sys.path)
from src.lance_db import lanceDB
from src.constants import LANCEDB_DICT, VECTOR_DB_DICT
from src.embeddings import Embeddings
INGESTED_DATA = os.path.abspath(os.getcwd() + '/data/Cloud_Provider_Services.csv')

def generate_data_to_ingest():
    """
    This function is used to generate data to ingest into the lancedb

    Returns:
    --------
    :return list of dictionaries
    """
    # Load data from the source
    df = pd.read_csv(INGESTED_DATA)
    print(df.head())

    # Create list of dictionaries
    data = df.apply(
                lambda row: {
                    "category": row["category"],
                    "cloud_provider": row["cloud_provider"],
                    "service": row["service"],
                    "description": row["description"],
                },
                axis=1,
            ).values.tolist()
    return data

def data_ingestion():
    """
    This function is used to ingest data into the lancedb

    Steps:
    ------
    1. Connect to the lancedb
    2. Load embeddings model & create data model
    3. Load data from the source - residing in the data folder
    4. Create a table in lanceDB
    5. Insert data into the table

    Returns:
    --------
    :return table where the data is added
    """
    # Connect to lanceDB - Use the DB layer to connect to the lancedb
    db = lanceDB(LANCEDB_DICT.get('uri'))

    # Load embeddings model
    model = Embeddings().get_model()
    print(f"Model details: {model}")

    # Create data model for the embeddings & table
    class CloudServiceInestionDataModel(LanceModel):
        description: str = model.SourceField()
        vector_description: Vector(dim=384) = model.VectorField()
        cloud_provider: str
        service: str
        category: str =  model.SourceField()
    
    data = generate_data_to_ingest()

    table = db.create_table(VECTOR_DB_DICT.get('TABLE_NAME'), schema=CloudServiceInestionDataModel, mode="overwrite")
    table.add(data)
    print(f"Table first 5 entries: {table.head(5)}")
    return table

if __name__ == "__main__":
    print('Ingestion Started')
    table = data_ingestion()
    db = lanceDB(LANCEDB_DICT.get('uri'))
    print(f"Table names: {db.table_names()}")
    print(f"Number of entries in the table '{table}': {table.count_rows()}")
    print(f"Table first 5 entries: {table.head(5)}")
    print('Ingestion Ended')
