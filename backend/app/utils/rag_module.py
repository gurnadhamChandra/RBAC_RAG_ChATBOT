
# from pathlib import Path
# import os
# import pandas as pd
# from collections import defaultdict
# from langchain_core.documents import Document
# import sqlite3
# from langchain_community.document_loaders import UnstructuredMarkdownLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
# from langchain_openai import OpenAIEmbeddings
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_classic.chains.combine_documents import create_stuff_documents_chain
# from langchain_classic.chains import create_retrieval_chain


# langchain_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("Langchain_API_KEY")
# openapi_key = os.getenv("OPENAI_API_KEY") or os.getenv("Open_API_KEY")
# cohere_api_key = os.getenv("COHERE_API_KEY") or os.getenv("Cohere_API_KEY")


# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGCHAIN_PROJECT"] = "RAG"
# if langchain_key is not None:
#     os.environ["LANGCHAIN_API_KEY"] = langchain_key
# if openapi_key is not None:
#     os.environ["OPENAI_API_KEY"] = openapi_key
# if cohere_api_key is not None:
#     os.environ["COHERE_API_KEY"] = cohere_api_key


# # split , loading, embeding and retrival logic for RAG

# openai_embeddings=OpenAIEmbeddings(model="text-embedding-3-small")
# vectorstore=Chroma(
#     collection_name="rag_collections",
#     persist_directory="chroma_db",
#     embedding_function=openai_embeddings
# )


# def embed_docs_to_vectoreStore(docs):
#     text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
#     splitted_docs=text_splitter.split_documents(docs)
#     vectorstore.add_documents(splitted_docs)
#     print("Documents embedded and saved to vectorstore.")
#     print("Total documents:", len(vectorstore.get()["documents"]))

# def load_file(file_path,role):
#     ext=Path(file_path).suffix.lower()
#     try:
#         if ext == ".csv":
#             df1 = pd.read_csv(file_path)
#             documents = []
#             for row in df1.to_dict(orient="records"):
#                 content = "\n".join(f"{k}: {v}" for k, v in row.items())
#                 documents.append(
#                     Document(
#                         page_content=content,
#                         metadata={"role": role.lower(), "source": Path(file_path).name}
#                     )
#                 )
#             return documents
#         elif ext == ".md":
#             with open(file_path , "r" , encoding="utf-8") as f:
#                 md_content = f.read()
#                 return [Document(page_content=md_content,metadata={"role": role.lower(), "source": Path(file_path).name})]
#         else:
#             return None
#     except Exception as e:
#         print(f"Error loading file {file_path}: {e}")
#         return None


# def run_indexer():
#     print("Running indexer..")
#     conn=sqlite3.connect("roles.db")
#     cursor=conn.cursor()
#     cursor.execute("SELECT id, filepath, role FROM documents WHERE embedded = 0")
#     all_docs=[]
#     for doc_id,filepath,role in cursor.fetchall():
#         print(f"Indexing file: {filepath} for role: {role}")
#         docs=load_file(filepath,role)
#         if docs:
#            if isinstance(docs,list):
#               all_docs.extend(docs)
#            else:
#                 all_docs.append(docs)
#                 cursor.execute("UPDATE documents SET embedded =1 where id=?",(doc_id,))

#     if all_docs:
#         embed_docs_to_vectoreStore(all_docs)
#         conn.commit()
#     conn.close()
#     print(f"Indexing completed. Total documents indexed: {len(all_docs)}")
           

# # prompt template==

# system_prompt = (
#     "You are an assistant for summarizing and answering queries from internal company documents.\n"
#     "Always use the retrieved context to answer the query, even if partial.\n"
#     "Do not guess. If data is not found, explain what you searched for.\n"
#     "When responding:\n"
#     "- Add **Source** from document metadata if possible.\n"
#     "- Use headers\n"
#     "- Use bullet points\n"
#     "- For CSV-style data, format in table with two columns\n"
#     "\n{context}"
# )

# chat_prompt=ChatPromptTemplate.from_messages(
#     [
#         ("system", system_prompt),
#         ("human", "{question}")
#     ]
# )

# # Model ==
# # langchain_model
# model=ChatOpenAI(
#      model="gpt-4o",  
#     temperature=0.2
# )
# question_answering_chain=create_stuff_documents_chain(model, chat_prompt)

# # Add reranker

# # def wrap_with_reranker(retriever, cohere_api_key, top_n=4):
# #     #print("[INFO] Using Cohere reranker.")
# #     reranker = CohereRerank(cohere_api_key=cohere_api_key, top_n=top_n)
# #     return ContextualCompressionRetriever(
# #         base_compressor=reranker,
# #         base_retriever=retriever
# #     )

# def get_rag_chain(user_role: str,cohere_api_key: str = None):
#     user_role = user_role.lower()

#     if user_role == "c-level":
#         # C-level sees everything
#         retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

#     elif user_role == "general":
#         # General role sees only general documents
#         retriever = vectorstore.as_retriever(search_kwargs={
#             "k": 4,
#             "filter": {"role": "general"}
#         })

#     else:
#         # All other roles see their docs + general
#         retriever = vectorstore.as_retriever(search_kwargs={
#             "k": 4,
#             "filter": {
#                 "role": {"$in": [user_role, "general"]}
#             }
#         })

#     # # wrap with reranker
#     # if cohere_api_key:
#     #     print("Using cohere reranker")
#     #     retriever = wrap_with_reranker(retriever, cohere_api_key)

#     return create_retrieval_chain(retriever, question_answering_chain)
#     """
#     from langchain_core.runnables import RunnableLambda, RunnableMap

#     extract_input = RunnableLambda(lambda x: x["input"])

#     return RunnableMap({
#         "context": extract_input | retriever,
#         "answer": extract_input | retriever | question_answering_chain
#     })"""


# """
# # ========== MAIN EXECUTION ==========
# if __name__ == "__main__":
#     run_indexer() 
# """
#     # ========== EXAMPLE USAGE ==========
# """
#     user_role = "hr" 
#     rag_chain = get_rag_chain(user_role)

    
#     query = "give me Campaign Highlights from marketing summary."
#     response = rag_chain.invoke({"input": query})

#     print((response["answer"]))
#     for doc in response.get("context", []):
#         print(f"Source: {doc.metadata['source']}, Role: {doc.metadata.get('role')}")

# """