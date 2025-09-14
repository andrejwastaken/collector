from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case
from sqlalchemy.orm import Session
from fastapi import HTTPException as HttpException
from app.db.session import SessionLocal
from app.models import Car, Chat, User
from app.schemas import CarOut, SearchResponse, RetrievedCar, UserCreate, ChatCreate, SearchRequest
from app.auth import hash_password, verify_password
from .embeddings import collection
from ollama import Client as Ollama
from langdetect import detect, LangDetectException, DetectorFactory
DetectorFactory.seed = 0  # For consistent language detection results

app = FastAPI(title="Collector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_client = Ollama()

def is_english(text: str) -> bool:
    try:
        lang = detect(text)
        return lang == "en"
    except LangDetectException:
        # Fallback: assume not English (so it will be translated)
        return False
    
def translate_to_english(text: str) -> str:
    prompt = f"Translate the following text to English:\n\n{text}"
    resp = ollama_client.generate(model="llama3.2:1b", prompt=prompt, stream=False)
    return resp["response"].strip()

def translate_from_english(text: str, target_language: str = "Macedonian") -> str:
    prompt = f"Translate the following English text to {target_language}:\n\n{text}"
    resp = ollama_client.generate(model="llama3.2:1b", prompt=prompt, stream=False)
    return resp["response"].strip()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HttpException(status_code=400, detail="Username already registered")
    new_user = User(username=user.username, hashed_password=hash_password(user.password))
    db.add(new_user) 
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HttpException(status_code=400, detail="Invalid credentials")
    return {"id": db_user.id, "username": db_user.username}

@app.post("/chat")
def save_message(chat: ChatCreate, db: Session = Depends(get_db)):
    new_chat = Chat(user_id=chat.user_id, title=chat.title, message=chat.message)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return {
        "id": new_chat.id,
        "title": new_chat.title,
        "message": new_chat.message,
        "answer": new_chat.answer,
        "timestamp": new_chat.timestamp,
    }

@app.get("/chat/{user_id}")
def get_chats(user_id: int, db: Session = Depends(get_db)):
    chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.timestamp.desc()).all()
    return [
        {
            "id": c.id,
            "title": c.title or (c.message[:30] if c.message else "(No title)"),
            "message": c.message,
            "answer": c.answer,
            "timestamp": c.timestamp,
        }
        for c in chats
    ]

@app.get("/cars", response_model=list[CarOut])
def list_cars(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Car).order_by(Car.price_num.asc().nulls_last()).limit(limit).all()

@app.get("/cars/{car_id}", response_model=CarOut)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HttpException(status_code=404, detail="Car not found")
    return car

@app.post("/search", response_model=SearchResponse)
def semantic_search(req: SearchRequest, db: Session = Depends(get_db)):
    user_query = req.query
    top_k = req.top_k

    english_query = user_query
    translate_answer = False
    if not is_english(user_query):
        english_query = translate_to_english(user_query)  # Only translate if not English
        translate_answer = True

    embed_resp = ollama_client.embed(model="bge-m3", input=english_query)
    query_emb = embed_resp.embeddings[0]

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=50,
        include=["distances", "metadatas"]
    )

    ids = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    items = sorted(zip(ids, distances, metadatas), key=lambda x: x[1])
    sorted_items = items[:top_k]
    sorted_ids = [int(item[0]) for item in sorted_items]

    order_case = case({id_: idx for idx, id_ in enumerate(sorted_ids)}, value=Car.id)
    # cars = db.query(Car).filter(Car.id.in_(sorted_ids)).order_by(order_case).all()

    structured_listings = "\n".join(
        f"{i+1}. {item[2].get('title','N/A')} | {item[2].get('price_num','N/A')} € | "
        f"{item[2].get('mileage_km','N/A')} km | "
        f"{item[2].get('date_posted').strftime('%d.%m.%Y') if item[2].get('date_posted') else 'N/A'} | "
        f"{item[2].get('url','')}"
        for i, item in enumerate(sorted_items)
    )

    # LLM prompt always in English
    prompt = (
        f"The user asked: '{english_query}'\n"
        f"These are the cars we found (use only this data, do NOT make up prices or mileage):\n"
        f"{structured_listings}\n"
        f"Answer concisely in English. Provide a short summary of the best car + the top {top_k} cars with name (link), image (link), price, mileage, and date posted."
    )

    response = ollama_client.generate(model="llama3.2:1b", prompt=prompt, stream=False)
    answer_en = response["response"].strip()

    answer_final = translate_from_english(answer_en, target_language="Macedonian") if translate_answer else answer_en

    if req.user_id:
        title = req.query[:50]
        new_chat = Chat(user_id=req.user_id, title=title, message=req.query, answer=answer_final)
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

    retrieved_listings = [
        RetrievedCar(
            id=int(item[0]),
            distance=item[1],
            metadata={
                "title": item[2].get("title"),
                "url": item[2].get("url"),
                "price": item[2].get("price_num"),
                "mileage": item[2].get("mileage_km"),
                "date_posted": item[2].get("date_posted").strftime("%d.%m.%Y") if item[2].get("date_posted") else None,
                "image_url": item[2].get("image_url"),
            },
        )
        for item in sorted_items
    ]

    return SearchResponse(
        answer=answer_final,
        retrieved_cars=retrieved_listings,
    )
