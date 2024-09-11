import pandas as pd
import pyarrow as pa
import sys,os
module_path = os.path.abspath(os.getcwd() + '/..')
sys.path.append(module_path)
#print(sys.path)
os.getcwd()
from src.constants import LANCEDB_DICT, EMBEDDINGS_DICT
from lancedb.embeddings import get_registry
from lancedb.embeddings.sentence_transformers import SentenceTransformerEmbeddings
from lancedb.pydantic import LanceModel, Vector
from src.lance_db import lanceDB

class Embeddings:
    def __init__(self):
        self.embedding_model = self.embedding_model()
        self.lancedb_connection = self.connect_to_lancedb()

    def embedding_model(self):
        model_name = EMBEDDINGS_DICT.get("model_name")
        device = EMBEDDINGS_DICT.get("device")
        print("Trying to get the model........")
        print("Model name is: ", model_name)
        return self.get_model_registry().create(name=model_name, device=device)

    def connect_to_lancedb(self):
        return lanceDB(uri=LANCEDB_DICT.get('uri'))

    def run_embeddings(self, text):
        embeddings = self.embedding_model.encode(text)
        return embeddings

    def get_model_registry(self):
        model_registry = get_registry().get(EMBEDDINGS_DICT.get("model_registry"))
        return model_registry
    
    def get_model(self):
        return self.embedding_model