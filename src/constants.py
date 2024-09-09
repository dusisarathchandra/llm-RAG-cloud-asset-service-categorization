import os
from openai import OpenAI
from elasticsearch import Elasticsearch
 
EMBEDDINGS_DICT = {
    "model_registry": "sentence-transformers",
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "vector_dims": "384",
    "device": "cpu" # can be 'cpu, 'gpu', 'cuda:0', etc.
}
VECTOR_DB_DICT = {
    "DB_NAME": "cloud_service_knowledge_base",
    "TABLE_NAME": "vector_db",
    "VECTOR_COLUMN": "vector_description",
}
VECTOR_DB_NAME = f'{VECTOR_DB_DICT["DB_NAME"]}/{VECTOR_DB_DICT["TABLE_NAME"]}'

LANCEDB_DICT = {
    "uri": os.environ.get("LANCEDB_URI", VECTOR_DB_NAME),
}
# Elastic Search Client
ES_CLIENT = Elasticsearch('http://localhost:9200')
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/v1/")

# OpenAI Client
LLM_CLIENT = OpenAI(base_url=OLLAMA_URL, api_key='ollama')

os.environ["TOKENIZERS_PARALLELISM"] = "false" # to supress hugging face warning
