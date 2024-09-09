import os, sys, warnings
import lancedb
from lancedb.table import Table
from openai import OpenAI

from retrieval import RetrieveContext
from src.constants import LLM_CLIENT
from src.building_prompt import build_prompt

# ignore some warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

# def build_prompt(query, search_results):
#     prompt_template = PROMPT_TEMPLATE.strip()

#     context = ""
    
#     for doc in search_results:
#         context = context + f"answer: {doc['category']}\nservice: {doc['service']}\ndescription: {doc['description']}\ncloud_provider: {doc['cloud_provider']}\n\n"
    
#     prompt = prompt_template.format(question=query, context=context).strip()
#     return prompt


def ollama_llm(prompt):
    response = LLM_CLIENT.chat.completions.create(
        model='gemma2:2b',
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content



def rag(query):
    search_results = RetrieveContext().get_vector_context(query)[['description', 'category', 'service', 'cloud_provider']].to_dict(orient='records')
    print("**************************************")
    prompt = build_prompt(query, search_results)
    answer = ollama_llm(prompt)
    return answer

if __name__ == "__main__":
    query = "analyze genomic data."
    response = rag(query)
    print(response.strip())
