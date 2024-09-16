# import sys,os
# module_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../src')
# sys.path.append(module_path)
import lancedb
import warnings
import pandas as pd
import pyarrow as pa
from src.constants import LANCEDB_DICT, VECTOR_DB_DICT, ES_CLIENT
from lancedb.rerankers import LinearCombinationReranker
from src.lance_db import lanceDB
from sentence_transformers import SentenceTransformer
from lancedb.embeddings import get_registry

warnings.simplefilter(action="ignore", category=FutureWarning)

class RetrieveContext:
    def __init__(self):
        self.lancedb_connection = lanceDB(LANCEDB_DICT.get('uri'))
        print(self.lancedb_connection)
        self.table = self.lancedb_connection.open_table(VECTOR_DB_DICT.get('TABLE_NAME'))
    
    def get_vector_context(self, query, top_k=5, weight=0.8):
        print("Getting context from the table")
        print(f'table name: {self.table.name}')
        df = self.table.to_pandas()
        print(f'first 5 data: {df.head(5)}')
        reranker = LinearCombinationReranker(
            weight=weight
        )
        print('------------------------------------------')
        print(f'\n\nWorking on query: {query}')
        context_data = self.table.search(
            query,
            query_type='hybrid', 
            vector_column_name=VECTOR_DB_DICT.get('VECTOR_COLUMN'),
        ).rerank(reranker=reranker).limit(top_k).to_pandas()
        return context_data
    def get_fts_and_vector_context(self, query, query_type="fts", top_k=5, weight=0.8):
        print("Getting context from the table")
        print(f'table name: {self.table.name}')
        print(f'Working on query: {query}')
        context_data = self.table.search(query, query_type=query_type).limit(5).to_pandas()
        return context_data
    
    def get_elastic_search_context(query, index_name="asset-categories"):
        search_query = {
            "size": 10,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["description^5", "category^3", "service", "cloud_provider"],
                            "type": "best_fields"
                        }
                    },
                }
            }
        }

        response = ES_CLIENT.search(index=index_name, body=search_query)
        
        result_docs = []
        
        for hit in response['hits']['hits']:
            result_docs.append(hit['_source'])
        
        return result_docs
    
if __name__ == "__main__":
    print("*************** Script started *********************")
    r = RetrieveContext()
    query = "query that makes it easy to analyze data from S3"
    print(r.get_context(query))
