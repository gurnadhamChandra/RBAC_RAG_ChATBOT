from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import uuid4
import os
import json
import shutil
import warnings
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from langchain_community.document_loaders import DirectoryLoader, TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from collections import defaultdict, deque

# store last 5 chats  of user
chat_memory=defaultdict(lambda: deque(maxlen=5))
load_dotenv()
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

class logoutRequest(BaseModel):
    username: str

class ragChatRequest(BaseModel):
    query:str
    role:str
    user_role:str

BASE_DIR =os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..","resources","data")


# HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
app = FastAPI(title="RAG-Powered Role-Based Chatbot API")
DB_FILE = "users.json"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Streamlit origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users():
    with open(DB_FILE, "w") as f:
        json.dump(users_db, f, indent=4)

users_db: Dict[str, Dict] = load_users()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    for user_id, user_data in users_db.items():
        if user_data["username"] == username and user_data["password"] == password:
            return {"id": user_id, "username": username, "role": user_data["role"]}
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        user_id = payload.get("uid")
        if not username or not role or not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload.")
        return {"id": user_id, "username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

@app.post("/register")
def register(request: RegisterRequest):
    if any(u["username"] == request.username for u in users_db.values()):
        # raise HTTPException(status_code=400, detail="Username already exists.")
        return {"message": "Username already exists."}
    
    user_id = str(uuid4())
    users_db[user_id] = {"username": request.username, "password": request.password, "role": request.role}
    save_users()
    return {"message": f"User '{request.username}' registered successfully as '{request.role}'."}

@app.post("/login")
def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        return {"message": "Doesn't exist username or password. Please register."}

    # Mark user as logged in
    users_db[user["id"]]["logged_in"] = True
    save_users()

    token = create_access_token({
        "sub": user["username"],
        "uid": user["id"],
        "role": user["role"]
    })
    return {"access_token": token, "token_type": "bearer", "username": user["username"], "role": user["role"]}

@app.post("/logout")
def logout(request:logoutRequest):
    for user_id, user_data in users_db.items():
        if user_data["username"] == request.username:
            user_data["logged_in"] = False
            save_users()
            return {"message": "Logged out successfully"}
    raise HTTPException(status_code=404, detail="User not found.")


@app.get("/get_user_status")
def get_user_status(username: str):
    for user_data in users_db.values():
        if user_data["username"] == username:
            return {
                "logged_in": user_data.get("logged_in", False),
                "role": user_data["role"]
            }
    raise HTTPException(status_code=404, detail="User not found.")


@app.get("/protected")
def protected(user=Depends(get_current_user)):
    return {"message": f"Hello {user['username']}! You are logged in as {user['role']}.", "user": user}

ATA_DIR = "./resources/data"
VECTOR_DIR = "./faiss_vectors"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)


@app.post("/build_vectors")
def build_vectors():
    print("starting build vector process...")
    logs={}
     # 1. Reset vector storage
    if os.path.exists(VECTOR_DIR):
        print("🧹 Cleaning old vector directory...")
        shutil.rmtree(VECTOR_DIR)
    os.makedirs(VECTOR_DIR, exist_ok=True)
    print(f"📁 Vector directory ready: {VECTOR_DIR}")
    
    all_chunks = []  # Collect all chunks for executive
    
    # 2. Iterate through each role
    for role in os.listdir(DATA_DIR):
        role_path = os.path.join(DATA_DIR, role)
        print(f"<UNK> Role {role} ready: {role_path}")
        if not os.path.isdir(role_path):
            continue

        print(f"\n🔍 Processing role: {role} {role_path}")
        all_docs = []

        # --- Load .md Files ---
        for fname in os.listdir(role_path):
            if fname.endswith(".md"):
                fpath = os.path.join(role_path, fname)
                try:
                    loader = TextLoader(fpath, encoding="utf-8")  # Specify encoding
                    docs = loader.load()
                    all_docs.extend(docs)
                    print(f"📄 Loaded .md file: {fname} ({len(docs)} docs)")
                except Exception as e:
                    print(f"❌ Skipping {fname}: {e}")

        # --- Load .csv Files ---
        for fname in os.listdir(role_path):
            print(fname.endswith)
            if fname.endswith(".csv"):
                fpath = os.path.join(role_path, fname)
                try:
                    loader = CSVLoader(file_path=fpath)
                    docs = loader.load()
                    all_docs.extend(docs)
                    print(f"🧾 Loaded .csv file: {fname} ({len(docs)} rows)")
                except Exception as e:
                    print(f"❌ Skipping CSV {fname}: {e}")

        if not all_docs:
            logs[role] = "⚠️ No valid documents found"
            print(logs[role])
            continue

        #chunks storing
        chunks=splitter.split_documents(all_docs)
        print(f"created{len(chunks)} chunks for role:{role}")
        if not chunks:
            logs[role]="No chunks created"
            continue
        try:
            vectordb=FAISS.from_documents(chunks,embedding_model)
            role_vect_path=os.path.join(VECTOR_DIR,role)
            vectordb.save_local(role_vect_path)
            logs[role] = f"✅ {len(chunks)} chunks stored at {role_vect_path}"
            print(logs[role])
            
            # Add to all_chunks for executive
            all_chunks.extend(chunks)
        except Exception as e:
            logs[role] = f"❌ Vector store creation failed: {e}"
            print(logs[role])

    # Create executive vector store with all data
    if all_chunks:
        try:
            executive_vectordb = FAISS.from_documents(all_chunks, embedding_model)
            executive_vect_path = os.path.join(VECTOR_DIR, "executive")
            executive_vectordb.save_local(executive_vect_path)
            logs["executive"] = f"✅ {len(all_chunks)} chunks stored at {executive_vect_path}"
            print(logs["executive"])
        except Exception as e:
            logs["executive"] = f"❌ Executive vector store creation failed: {e}"
            print(logs["executive"])
    else:
        logs["executive"] = "⚠️ No chunks for executive"

    print("\n✅ Vector building complete.\n")
    return {"status": "completed", "details": logs}

@app.post("/rag_chat")
def rag_chat(request:ragChatRequest):
    print(f"\n🟦 Received RAG Chat Request")
    print(f"📝 Query: {request.query}")
    print(f"👤 Role: {request.role}")
    role = request.role.lower().strip()
    role_vector_path = os.path.join(VECTOR_DIR, role)
    
    if not os.path.exists(role_vector_path):
        msg = f"❌ No vector store found for role '{role}'"
        print(msg)
        raise HTTPException(status_code=404, detail=msg)
    
    try:
        print(f"loading vector from local vector:{role_vector_path}")
        vectordb=FAISS.load_local(
            folder_path=role_vector_path,
            embeddings=embedding_model,
            allow_dangerous_deserialization=True
        )
        retriver=vectordb.as_retriever(
            # max marginal relevence
            search_type="mmr", 
            search_kwargs={
                 "k": 10,  # Increase to give the model more context to work with
                "lambda_mult": 0.5  # 0.5 balances relevance (0.0) and diversity (1.0)
            }
        )
        docs = retriver.invoke(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Retrieval error: {e}")
    
    if not docs:
        return {"response": "No relevant information found."}

    context = "\n\n".join(doc.page_content for doc in docs)

    # 🔁 Get chat history
    history = chat_memory[role]
    formatted_history = ""
    for i, (q, a) in enumerate(history):
        formatted_history += f"\nUser: {q}\nFinBot: {a}"

    llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY
    )

    prompt = PromptTemplate.from_template("""
    You are FinBot — a professional, intelligent assistant designed to assist users in finance with crisp, engaging, and secure replies. Your core directive is to **strictly adhere to financial topics and the provided context**.

    ---

    User Role: {user_role}
    User Question: {query}

    Conversation History:
    {history}

    ---

    **Instructions for FinBot:**

    1.  🎯 **Greeting Handling**:
        this needs to be executed only when user uses greeting
        If the user input is **ONLY** a greeting (e.g., "Hi", "Hello", "Hey FinBot"), respond **ONLY** with:
        "Hi, I’m FinBot. How can I assist you with your {role} data today?"
        Keep it simple and friendly — do not add extra info or answer anything else.

    2.  🚫 **Strict Scope Enforcement (Critical!)**:
        - **NEVER** answer general knowledge questions or queries unrelated to finance.
        - **NEVER** answer questions where the information is not **explicitly and directly** present within the <context>.
        - **Always** choose one of the "Concise Redirection" responses (Rule 4) for any question that falls outside the defined scope (general, non-financial, or not found in context).
        - Do not guess, assume, or pull from external knowledge. Your sole source of truth is the provided <context>.

    3.  ✅ **If you CAN answer (Financial & In-Context)**:
        - Give a short, well-written answer in full sentences.
        - Be confident, informative, and clear. Do not hallucinate.
        - Ensure the response contains **only** the answer to the question, no introductory phrases (like "Here's your answer," "Based on context," etc.), and do not repeat the user's question.

     4. Role-Based Access Denial for Out-of-Scope Queries ( if questions answer is not present in the context then)
        - If the user role is not "executive" and a user asks a question outside their assigned role, the system must not provide any information and should redirect with a firm but polite denial.
            
        - Use one of the following predefined role-based denial messages (insert the user's actual role in {user_role}):
            
        - "Access denied. This information is restricted outside your {user_role} access."
            
        - "Sorry, you're not authorized to view data beyond your {user_role} permissions."
            
        - "This topic isn't available for your role. Please ask something related to {user_role}."
            
        - "Your current access level only permits questions related to {user_role}."
            
        - Do not explain why access is denied or reference internal system rules.
            
        - For executive role, allow access to all topics as they have full access.

    5.  💬 **General Style & Conciseness**:
        - Be helpful and professional, like an AI advisor.
        - Keep things human-readable, short, brief, and clear. Use bullet points if needed for lists.
        - Avoid any conversational fillers or unnecessary preambles.
        
    Provide the answer directly don't include anything else like the answer to your question, then showing the same question again in response etc.
    - Only give the answer to the question don't add anything else.
    ---

    <context>
    {context}
    </context>
    """)

   # 🔥 NEW CHAIN (LCEL)

    chain = prompt | llm

    try:
        response = chain.invoke({
            "context": context,
            "query": request.query,
            "role": role,
            "history": formatted_history,
            "user_role": request.user_role
        })
        answer =response.content
        print(f"✅ LLM Response: {answer[:300]}...\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ LLM error: {e}")

    # 📝 Save current interaction in memory
    chat_memory[role].append((request.query, answer))

    return {"response": answer}