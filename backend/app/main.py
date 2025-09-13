from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case
from sqlalchemy.orm import Session
from fastapi import HTTPException as HttpException
from app.db.session import SessionLocal
from app.models import Car, Chat, User
from app.schemas import CarOut, SearchResponse, RetrievedCar, UserCreate, MessageCreate, SearchRequest
from app.auth import hash_password, verify_password
from .embeddings import collection
from ollama import Client as Ollama

app = FastAPI(title="Collector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_client = Ollama()

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
def save_message(message: MessageCreate, db: Session = Depends(get_db)):
    new_msg = Chat(user_id=message.user_id, message=message.message)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return {"id": new_msg.id, "message": new_msg.message, "timestamp": new_msg.timestamp}

@app.get("/chat/{user_id}")
def get_chats(user_id: int, db: Session = Depends(get_db)):
    chats = db.query(Chat).filter(Chat.user_id == user_id).all()
    return [{"id": c.id, "message": c.message, "timestamp": c.timestamp} for c in chats]

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
    # 1. Embed query
    query = req.query
    top_k = req.top_k
    embed_resp = ollama_client.embed(model="bge-m3", input=query)
    query_emb = embed_resp.embeddings[0]

    # 2. Query Chroma
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=50,
        include=["distances", "metadatas", "documents"]
    )

    ids = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    documents = results["documents"][0]

    # 3. Sort by distance
    items = sorted(zip(ids, distances, metadatas, documents), key=lambda x: x[1])
    sorted_items = items[:top_k]
    sorted_ids = [int(item[0]) for item in sorted_items]

    # 4. Query PostgreSQL
    order_case = case({id_: index for index, id_ in enumerate(sorted_ids)}, value=Car.id)
    cars = db.query(Car).filter(Car.id.in_(sorted_ids)).order_by(order_case).all()

    # 5. Prepare structured context for LLM
    structured_context = [
        {
            "title": item[2].get("title"),
            "make": item[2].get("make"),
            "model": item[2].get("model"),
            "year": item[2].get("year"),
            "price": item[2].get("price_num"),
            "city": item[2].get("city"),
            "mileage": item[2].get("mileage_km")
        }
        for item in sorted_items
    ]

    prompt = (
        f"Корисникот праша: '{query}'\n"
        f"Ова се автомобилите што ги најдовме (користи само овие податоци, НЕ измислувај никакви цени или километражи):\n"
        f"{structured_context}\n"
        f"Одговори јасно на македонски, кратко и корисно, користејќи вистински валути и информации од податоците."
    )

    # 6. Generate answer with LLM
    response = ollama_client.generate(
        model="llama3.2:1b",
        prompt=prompt,
        stream=False
    )
    answer_text = response["response"]

    return SearchResponse(
        answer=answer_text.strip(),
        retrieved_cars=[
            RetrievedCar(
                id=int(item[0]),
                distance=item[1],
                metadata=item[2],
                document=item[3],
            )
            for item in sorted_items
        ],
        cars=cars
    )
