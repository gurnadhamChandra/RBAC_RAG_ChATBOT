# from .rag_module import get_rag_chain

# async def ask_rag(query:str,role:str,chore_api_key:str=None)->dict:
#     rag_chain = get_rag_chain(user_role=role,chore_api_key= chore_api_key)
#     result =  rag_chain.invoke({"question": query})
#     return {"answer": result["answer"]}

#     """
#       # result now includes: {"context": [...], "answer": "..."}
#     return {
#         "answer": result["answer"],
#         "context": result["context"]
#     }"""