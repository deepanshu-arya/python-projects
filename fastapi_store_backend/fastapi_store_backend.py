from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime

# ============================================================
# 🗃️ Database Configuration
# ============================================================
DATABASE_URL = "sqlite:///./store.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================
# 📦 Database Model
# ============================================================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Float)
    quantity = Column(Integer)

Base.metadata.create_all(bind=engine)

# ============================================================
# 🧩 Pydantic Schemas
# ============================================================
class ProductCreate(BaseModel):
    name: str = Field(..., example="Laptop", min_length=2, max_length=50)
    price: float = Field(..., gt=0, example=55000.00)
    quantity: int = Field(..., ge=0, example=10)

class ProductUpdate(BaseModel):
    name: str | None = Field(None, example="Mouse")
    price: float | None = Field(None, gt=0)
    quantity: int | None = Field(None, ge=0)

# ============================================================
# 🧠 Utility: Database Dependency
# ============================================================
def get_db():
    """Database session generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# 🚀 FastAPI App Initialization
# ============================================================
app = FastAPI(
    title="FastAPI Store Backend",
    description="A simple and efficient inventory management API built with FastAPI.",
    version="1.1.0"
)

# ============================================================
# 🧩 Helper Functions
# ============================================================
def log_action(action: str):
    """Log timestamped actions in console for better debugging."""
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{time}] - {action}")

def get_product_or_404(product_id: int, db: Session):
    """Reusable helper to fetch product or raise 404."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product

# ============================================================
# 🏠 Root Route
# ============================================================
@app.get("/", tags=["Home"])
def home():
    log_action("Home route accessed")
    return {"message": "Welcome to FastAPI Store Backend API!"}

# ============================================================
# ➕ Create Product
# ============================================================
@app.post("/products/", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Add a new product to the store."""
    existing = db.query(Product).filter(Product.name == product.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product '{product.name}' already exists in the store."
        )

    new_product = Product(name=product.name, price=product.price, quantity=product.quantity)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    log_action(f"Added new product: {new_product.name}")
    return {"message": "✅ Product added successfully", "product_id": new_product.id}

# ============================================================
# 📜 Get All Products
# ============================================================
@app.get("/products/", response_model=list[dict], tags=["Products"])
def get_all_products(db: Session = Depends(get_db)):
    """Retrieve a list of all products."""
    products = db.query(Product).all()
    log_action("Fetched all products")
    return [
        {"id": p.id, "name": p.name, "price": p.price, "quantity": p.quantity}
        for p in products
    ]

# ============================================================
# 🔍 Get Single Product
# ============================================================
@app.get("/products/{product_id}", response_model=dict, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product details by ID."""
    product = get_product_or_404(product_id, db)
    log_action(f"Fetched product details for ID: {product_id}")
    return {"id": product.id, "name": product.name, "price": product.price, "quantity": product.quantity}

# ============================================================
# ✏️ Update Product
# ============================================================
@app.put("/products/{product_id}", response_model=dict, tags=["Products"])
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """Update product details."""
    product = get_product_or_404(product_id, db)

    if product_update.name is not None:
        product.name = product_update.name
    if product_update.price is not None:
        product.price = product_update.price
    if product_update.quantity is not None:
        product.quantity = product_update.quantity

    db.commit()
    db.refresh(product)
    log_action(f"Updated product ID: {product_id}")

    return {
        "message": "✅ Product updated successfully",
        "product": {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity
        }
    }

# ============================================================
# ❌ Delete Product
# ============================================================
@app.delete("/products/{product_id}", response_model=dict, status_code=status.HTTP_200_OK, tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product from the store."""
    product = get_product_or_404(product_id, db)
    db.delete(product)
    db.commit()

    log_action(f"Deleted product ID: {product_id}")
    return {"message": f"🗑️ Product ID {product_id} deleted successfully"}
