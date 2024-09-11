#!/usr/bin/env python

import sys,os
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import os, sys
from sentence_transformers import SentenceTransformer
module_path = sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../'))
sys.path.append(module_path)
from src.lance_db import lanceDB
from src.constants import LANCEDB_DICT, VECTOR_DB_DICT, EMBEDDINGS_DICT
from src.embeddings import Embeddings
INGESTED_DATA = os.path.abspath(os.getcwd() + '/data/Cloud_Provider_Services.csv')
from lancedb.embeddings.sentence_transformers import SentenceTransformerEmbeddings
from typing import Protocol


class SentenceTransformerEmbeddings:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, data):
        if data is None:
            raise ValueError("Input texts cannot be None")

        if not isinstance(data, list):
            raise TypeError("Input texts should be a list of strings")

        # Debugging: Print the input data
        print(f"Input texts: {data}")

        embeddings = self.model.encode(data)
        return embeddings

embedding_generator = SentenceTransformerEmbeddings(EMBEDDINGS_DICT.get('model_name'))

class EmbeddingFunction(Protocol):
    """
    A protocol that represents a function for generating embeddings.

    Parameters
    ----------
    text : List[str]
        A list of strings for which embeddings are to be generated.

    Returns
    -------
    List[List[float]]
        A list of embeddings, where each embedding is represented as
        a list of floats.
    """

    def __call__(self, text: list[str]) -> list[list[float]]: ...

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
    model : SentenceTransformerEmbeddings = (Embeddings().get_model())
    print(f"Model details: {model}")

    # Create data model for the embeddings & table
    class CloudServiceIngestionDataModel(LanceModel):
        description: str = model.SourceField()
        vector_description: Vector(dim=384) = model.VectorField()
        cloud_provider: str
        service: str
        category: str =  model.SourceField()
        class Config:
            arbitrary_types_allowed = True
    
    data = generate_data_to_ingest()
    table = db.create_table(VECTOR_DB_DICT.get('TABLE_NAME'), schema=CloudServiceIngestionDataModel, mode="overwrite")
    print('Table created')
    generated_embeddings = list()
    if data is not None:
        generated_embeddings = embedding_generator.generate_embeddings(data)
    else:
        raise ValueError("Data is None, cannot generate embeddings")
    print('--------------------------------------------------')
    print(f"First 2 Generated embeddings: {generated_embeddings[0:2]}")
    generated_embeddings = [embedding.tolist() for embedding in generated_embeddings]
    # Assuming data is a list of dictionaries with keys matching the schema
    entries = []
    for i, chunk in enumerate(generated_embeddings):
        entry = {
            "description": data[i]['description'],
            "vector_description": chunk,
            "cloud_provider": data[i]['cloud_provider'],
            "service": data[i]['service'],
            "category": data[i]['category']
        }
        entries.append(entry)
    table.add(entries)
    return table

if __name__ == "__main__":
    print('******************** Manual Ingestion Started ***********************')
    table = data_ingestion()
    db = lanceDB(LANCEDB_DICT.get('uri'))
    print(f"Table names: {db.table_names()}")
    print(f"Number of entries in the table: {table}")
    print(f"Total rows: {table.count_rows()}")
    print("\n\n################################################")
    print(f"Table first 5 entries: {table.head(5)}")
    print("################################################\n\n")
    print('********************* Manual Ingestion Ended ************************')
