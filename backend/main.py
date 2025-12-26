from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from fastapi import UploadFile, File
import shutil
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import re
import uuid

from fastapi.middleware.cors import CORSMiddleware


# ---------------- DATABASE SETUP ----------------
DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ---------------- DATABASE MODELS ----------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    price = Column(Float)
    stock = Column(Integer)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    phone = Column(String)
    items = Column(String)
    total = Column(Float)
    created_at = Column(String, default=str(datetime.now()))

class TransactionRequest(BaseModel):
    customer_name: str
    phone: str
    items_text: str   # example: "2 rice and 1 milk"


Base.metadata.create_all(bind=engine)

# ---------------- FASTAPI APP ----------------
app = FastAPI(title="AI Billing System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DEPENDENCY ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- SCHEMAS ----------------
class TransactionInput(BaseModel):
    audio_text: str
    customer_name: str
    phone: str

def generate_pdf(transaction_id, customer, phone, items, total):
    file_path = f"bill_{transaction_id}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 14)
    c.drawString(50, height - 50, "AI Billing System")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 90, f"Customer: {customer}")
    c.drawString(50, height - 110, f"Phone: {phone}")
    c.drawString(50, height - 130, f"Items: {items}")
    c.drawString(50, height - 150, f"Total: ₹{total}")

    c.drawString(50, height - 180, "Thank you for your purchase!")

    c.save()
    return file_path

def parse_items(text: str):
    pattern = r"(\d+)\s*(\w+)"
    matches = re.findall(pattern, text.lower())

    items = []
    for qty, name in matches:
        items.append({
            "name": name,
            "quantity": int(qty)
        })

    return items

# ---------------- ROUTES ----------------
@app.get("/")
def home():
    return {"message": "AI Billing System running successfully"}

@app.post("/transaction")
def create_transaction(data: TransactionInput, db: Session = Depends(get_db)):
    from services.whatsapp import send_whatsapp_message
    # SIMPLE PRICE LOGIC (for demo)
    total = len(data.audio_text.split()) * 10  

    tx = Transaction(
        customer_name=data.customer_name,
        phone=data.phone,
        items=data.audio_text,
        total=total
    )

    db.add(tx)
    db.commit()
    db.refresh(tx)

    pdf_path = generate_pdf(
    tx.id,
    data.customer_name,
    data.phone,
    data.audio_text,
    total,
)
    
    send_whatsapp_message(data.phone, pdf_path)

    return {
        "message": "Transaction created",
        "transaction_id": tx.id,
        "total": total,
        "bill_pdf": pdf_path,
        "whatsapp": "sent (mock)"
}

@app.post("/ocr/upload")
async def upload_bill(file: UploadFile = File(...)):
    from services.ocr import read_image_text, read_pdf_text
    file_path = f"ocr_uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.lower().endswith(".pdf"):
        text = read_pdf_text(file_path)
    else:
        text = read_image_text(file_path)

    return {
        "filename": file.filename,
        "extracted_text": text
    }

@app.post("/voice/upload")
async def upload_voice(file: UploadFile = File(...)):
    from services.voice import speech_to_text
    if not file.filename.lower().endswith((".wav", ".flac", ".ogg")):
        raise HTTPException(
            status_code=400,
            detail="Only audio files are allowed (wav, flac, ogg)"
        )
    
    audio_path = f"voice_{file.filename}"

    with open(audio_path, "wb") as buffer:
        buffer.write(await file.read())

    text = speech_to_text(audio_path)

    return {
        "filename": file.filename,
        "recognized_text": text
    }

@app.post("/ai/parse")
async def parse_text(text: str):
    from services.ai import parse_items
    items = parse_items(text)
    return {
        "input_text": text,
        "parsed_items": items
    }

@app.post("/populate-sample")
def populate_sample(db=Depends(get_db)):
    products = [
        Product(name="rice", price=50, stock=100),
        Product(name="milk", price=30, stock=50),
        Product(name="oil", price=120, stock=40),
    ]

    for p in products:
        exists = db.query(Product).filter(Product.name == p.name).first()
        if not exists:
            db.add(p)

    db.commit()
    return {"status": "sample products added"}

@app.post("/create-transaction")
def create_transaction(data: TransactionRequest, db=Depends(get_db)):

    items = parse_items(data.items_text)
    total = 0
    summary = []

    for item in items:
        product = db.query(Product).filter(Product.name == item["name"]).first()

        if not product:
            return {"error": f"{item['name']} not found"}

        if product.stock < item["quantity"]:
            return {"error": f"Not enough stock for {item['name']}"}

        cost = product.price * item["quantity"]
        total += cost
        product.stock -= item["quantity"]

        summary.append(f"{item['quantity']} {item['name']}")

    transaction = Transaction(
        customer_name=data.customer_name,
        phone=data.phone,
        items=", ".join(summary),
        total=total
    )

    db.add(transaction)
    db.commit()

    return {
        "message": "Transaction successful",
        "items": summary,
        "total": total
    }





