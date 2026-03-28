# from typing import Dict

# import sqlite3
# import pandas as pd
# import numpy as np
# import os
# import duckdb
# from passlib.context import CryptContext
# from pathlib import Path
# from pydantic import BaseModel
# from fastapi import FastAPI,Depends,HTTPException,UploadFile,File,Form
# from fastapi.security import HTTPBasic,HTTPBasicCredentials
# from fastapi.responses import JSONResponse
# from fastapi import BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# # from langchain_community.embeddings.openai import OpenAIEmbedding
# from langchain_openai import OpenAIEmbeddings
# from langchain_core.documents import Document
# from dotenv import load_dotenv

# load_dotenv()

# from .utils.rag_module import run_indexer,vectorstore,get_rag_chain
# from .utils.query_classifier import detect_query_type_llm
# from .utils.csv_query import ask_csv
# from .utils.rag_chain import ask_rag

# app = FastAPI()
# security = HTTPBasic()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins (for development; restrict in production)
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt_sha256"],
#     deprecated="auto")


# # DUCK DB setup===

# DUCKDB_DIR=Path("statics/data")  # folder in repo contains structured_quiries.duckdb
# DUCKDB_DIR.mkdir(parents=True,exist_ok=True)
# DUCKDB_PATH=DUCKDB_DIR/"structured_quiries.duckdb"

# duckdb_conn=duckdb.connect(str(DUCKDB_PATH))
# print("DuckDB initialized at", DUCKDB_PATH)
# duckdb_conn.execute("SELECT 'Hello DuckDB!' AS greeting").fetchall()
# duckdb_conn.execute("""
#     CREATE TABLE IF NOT EXISTS tables_metadata (
#         table_name TEXT,
#         role TEXT
#     )
# """)

# # SQLITE3 db setup===

# sql_conn=sqlite3.connect("roles.db",check_same_thread=False)
# sql_cursor=sql_conn.cursor()
# sql_cursor.executescript("""
# CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT UNIQUE,
#     password TEXT,
#     role TEXT
# );

# CREATE TABLE IF NOT EXISTS roles (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     role_name TEXT UNIQUE
# );

# CREATE TABLE IF NOT EXISTS documents (
#      id INTEGER PRIMARY KEY AUTOINCREMENT,
#     filename TEXT,
#     role TEXT,
#     filepath TEXT NOT NULL,
#     headers_str TEXT,
#     embedded INTEGER DEFAULT 0
# );
# """)
# sql_conn.commit()

# def create_default_user():
#     sql_conn_local=sqlite3.connect("roles.db")
#     sql_cursor_local=sql_conn_local.cursor()
#     sql_cursor_local.execute("INSERT OR IGNORE INTO roles (role_name) VALUES (?)", ("C-Level",))
#     hashed_password=pwd_context.hash("admin123")
#     try:
#         sql_cursor_local.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", hashed_password, "C-Level"))
#         sql_conn_local.commit()
#         print("Default admin user created.")
#     except sqlite3.IntegrityError:
#         print("Default admin user already exists.")
#     finally:
#         sql_conn_local.close()

# create_default_user()




# # Dummy user database
# # users_db: Dict[str, Dict[str, str]] = {
# #     "Tony": {"password": "password123", "role": "engineering"},
# #     "Bruce": {"password": "securepass", "role": "marketing"},
# #     "Sam": {"password": "financepass", "role": "finance"},
# #     "Peter": {"password": "pete123", "role": "engineering"},
# #     "Sid": {"password": "sidpass123", "role": "marketing"},
# #     "Natasha": {"passwoed": "hrpass123", "role": "hr"}
# # }


# # Authentication dependency
# def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
#     username = credentials.username
#     password = credentials.password
#     sql_cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
#     result = sql_cursor.fetchone()
#     if not result or not pwd_context.verify(password, result[0]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"username": username, "role": result[1]}


# # Models====

# class ChatRequest(BaseModel):
#     question:str

# class CreateUserRequest(BaseModel):
#     username: str
#     password: str
#     role: str

# class CreateRoleRequest(BaseModel):
#     role_name: str

# class LoginRequest(BaseModel):
#     username: str
#     password: str


# # Routes and logics====

# # Login endpoint
# # @app.get("/login")
# # def login(user=Depends(authenticate)):
# #     return {"message": f"Welcome {user['username']}!", "role": user["role"]}

# @app.post("/login")
# def login_json(req: LoginRequest):
#     sql_cursor.execute("SELECT password, role FROM users WHERE username = ?", (req.username,))
#     result = sql_cursor.fetchone()
#     if not result or not pwd_context.verify(req.password, result[0]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"message": f"Welcome {req.username}!", "role": result[1], "username": req.username}

# @app.get("/roles")
# def get_roles(user=Depends(authenticate)):
#     sql_cursor.execute("select role_name from roles")
#     roles=sql_cursor.fetchall()
#     return {"roles":[r[0] for r in roles]}

# @app.post("/create-user")
# def create_user(req: CreateUserRequest, user=Depends(authenticate)):
#     if user["role"] != "C-Level":
#         raise HTTPException(status_code=403, detail="Only C-Level users can create new users.")
#     sql_cursor.execute("SELECT 1 FROM roles WHERE role_name=?",(req.role,))
#     if not sql_cursor.fetchone():
#         raise HTTPException(status_code=400, detail="Invalid role specified.")
#     hashed_password=pwd_context.hash(req.password)
#     try:
#         sql_cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (req.username, hashed_password, req.role))
#         sql_conn.commit()
#         return {"message": f"User '{req.username}' created successfully with role '{req.role}'."}
#     except sqlite3.IntegrityError:
#         raise HTTPException(status_code=400, detail="Username already exists.")
    
# @app.post("/create-role")
# def create_role(req: CreateRoleRequest, user=Depends(authenticate)):
#     if user["role"] != "C-Level":
#         raise HTTPException(status_code=403, detail="Only C-Level users can create new roles.")
#     try:
#         sql_cursor.execute("INSERT INTO roles (role_name) VALUES (?)", (req.role_name,))
#         sql_conn.commit()
#         return {"message": f"Role '{req.role_name}' created successfully."}
#     except sqlite3.IntegrityError:
#         raise HTTPException(status_code=400, detail="Role already exists.")
    

# UPLOAD_DIR="statics/uploads"

# @app.post("/upload")
# async def upload_files(file:UploadFile=File(...),role:str=Form(...)):
#     try:
#         filename=file.filename
#         extension=Path(filename).suffix.lower()

#         # storage==
#         role_dir=os.path.join(UPLOAD_DIR,role)
#         os.makedirs(role_dir,exist_ok=True)
#         file_path=os.path.join(role_dir,filename)

#         # contnet reading==
#         data = await file.read()
#         with open(file_path, "wb") as f:
#             f.write(data)   # saving file for next use
#         if extension==".csv":
#             from io import BytesIO
#             df=pd.read_csv(BytesIO(data))
#             content=df.to_string(index=False)

#             # load into duckdb==
#             df1=pd.read_csv(file_path)
#             table_name=Path(file_path).stem.replace("-","_").lower()

#             # save data to duckdb
#             headers =df1.columns.tolist()
#             headers_str=",".join(headers)
#             duckdb_conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * from df1")

#             # save to table_metadata
#             duckdb_conn.execute("INSERT INTO tables_metadata (table_name, role) VALUES (?, ?)", (table_name, role))

#         elif extension == ".md":
#             content=data.decode("utf-8")
#             headers_str=None
#         else:
#             raise HTTPException(status_code=400, detail="Unsupported file type. Only CSV and MD files are allowed.")
        
#         # save metadata to sqlite
#         conn=sqlite3.connect("roles.db")
#         cursor=conn.cursor()
#         cursor.execute("INSERT INTO documents (filename, role, filepath, headers_str) VALUES (?, ?, ?, ?)", (filename, role, file_path, headers_str))
#         conn.commit()
#         conn.close()

#         run_indexer()
#         print(f"File '{filename}' uploaded and processed successfully for role '{role}'.")
#         return JSONResponse(content={"message": f"{filename} uploaded successfully for role '{role}'."})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"File upload failed: {e}")
    

# @app.post("/chat")
# async def chat(request:ChatRequest,user=Depends(authenticate)):
#     role=user["role"]
#     query=request.question
#     username=user["username"]

#     # 1. Detect mode: SQL or RAG
#     mode = detect_query_type_llm(query)
#     print(f"Detected mode: {mode}")

#     result = {}
#     fallback_used = False

#     # route to appropriate logic based on mode
#     if mode == "SQL":
#         try:
#             result =await ask_csv(query,role,username,return_sql=True)
#             if result.get("error") or not result.get("answer", "").strip():
#                 raise ValueError("SQL query blocked or failed")
#         except Exception as e:
#             print(f"[SQL Fallback Triggered] Error: {e}")
#             result = await ask_rag(query, role)
#             fallback_used = True
#             mode = "SQL → fallback to RAG"
#     else:
#         result = await ask_rag(query, role)

#     return {
#         "mode": mode,
#         "user": username,
#         "role": role,
#         "fallback": fallback_used,
#         "answer": result["answer"],
#         **({"sql": result["sql"]} if "sql" in result else {})
#     }


# # Protected test endpoint
# @app.get("/test")
# def test(user=Depends(authenticate)):
#     return {"message": f"Hello {user['username']}! You can now chat.", "role": user["role"]}



# @app.get("/db-health")
# def db_health():
#     try:
#         result = duckdb_conn.execute("SELECT 1 AS status").fetchone()
#         return {"duckdb": "ok", "status": int(result[0])}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"DuckDB health check failed: {e}")


# @app.get("/users-check")
# def users_check():
#     try:
#         sql_cursor_check = sql_conn.cursor()
#         sql_cursor_check.execute("SELECT username, role FROM users")
#         users_list = sql_cursor_check.fetchall()
#         return {"users_count": len(users_list), "users": [{"username": u[0], "role": u[1]} for u in users_list]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Users check failed: {e}")