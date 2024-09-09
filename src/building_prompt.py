PROMPT_TEMPLATE = """
You're a cloud asset category finder. Answer the DESCRIPTION based on the CONTEXT.
Use only the facts from the CONTEXT when answering the DESCRIPTION. Generate a short answer in JSON format with "category" and "service" as fields.
Your response should **only** include the JSON object itself. Do not include any code blocks, backticks, language tags, or additional formatting like "```json".

DESCRIPTION: {question}

CONTEXT: 
{context}
"""

def build_prompt(query, search_results):
    context = "\n".join(
        f"answer: {doc['category']}\nservice: {doc['service']}\ndescription: {doc['description']}\ncloud_provider: {doc['cloud_provider']}\n"
        for doc in search_results
    )
    
    return PROMPT_TEMPLATE.format(question=query, context=context).strip()

