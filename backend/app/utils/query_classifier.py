# from openai import OpenAI
# import os

# client =OpenAI(api_key=os.getenv("Open_API_KEY"))

# def detect_query_type_llm(query:str)->str:
#      prompt = f"""
# You are a classifier that decides if a user's question should be handled by structured SQL query logic or by unstructured document search (RAG).

# If the question contains terms related to **structured data analysis** (e.g., "average", "sum", "total", "count", "how many", "filter", "greater than", "less than", "top 5", "group by", "details of employee" etc.), classify it as:

# → "SQL"

# If the question is more about general understanding, summarization, definitions, or cannot be answered from structured tabular data, classify it as:
# If question is about summary of a document, process etc classify it as
# → "RAG"

# Respond with only one word: either **SQL** or **RAG**.

# Here is the question:
# "{query}"

# Answer:
#     """
     
#      response =client.chat.completions.create(
#           model="llama-3.3-70b-versatile",
#           messages=[{"role": "system", "content": prompt}],
#           temperature=0.0,
#      )
#      return response.choices[0].message.content.strip().upper()