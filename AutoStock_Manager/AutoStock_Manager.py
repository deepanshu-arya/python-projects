from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ------------------------------------------------------------
# App Initialization
# ------------------------------------------------------------
app = FastAPI(
    title="AutoStock Manager",
    description="📦 A smart and lightweight inventory management API for tracking stock levels in real-time.",
    version="1.1.0"
)

# ------------------------------------------------------------
# Data Models
# ------------------------------------------------------------
class Product(BaseModel):
    id: int = Field(..., description="Unique product ID")
    name: str = Field(..., description="Product name")
    quantity: int = Field(..., ge=0, description="Quantity of product available in stock")
    added_at: datetime = Field(default_factory=datetime.now, description="Timestamp when product was added")

class StockUpdate(BaseModel):
    quantity: int = Field(..., ge=0, description="New quantity for the product")

# ------------------------------------------------------------
# In-Memory "Database"
# ------------------------------------------------------------
inventory: List[Product] = []  # Simulates a database table for demo purposes

# ------------------------------------------------------------
# Helper Function
# ------------------------------------------------------------
def find_product(product_id: int) -> Optional[Product]:
    """Helper function to find a product by ID."""
    for product in inventory:
        if product.id == product_id:
            return product
    return None

# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------

@app.get("/")
def home():
    """Root endpoint - API welcome message."""
    return {
        "message": "🏪 Welcome to AutoStock Manager!",
        "hint": "Use /products to add, view, update, or delete items."
    }

# ------------------------------------------------------------
# CREATE - Add a new product
# ------------------------------------------------------------
@app.post("/products", response_model=Product)
def add_product(product: Product):
    if find_product(product.id):
        raise HTTPException(status_code=400, detail="⚠️ Product ID already exists. Please use a unique ID.")
    
    inventory.append(product)
    print(f"[INFO] New product added — ID: {product.id}, Name: {product.name}, Quantity: {product.quantity}")
    return product

# ------------------------------------------------------------
# READ - View all products
# ------------------------------------------------------------
@app.get("/products", response_model=List[Product])
def get_all_products():
    if not inventory:
        return {"message": "📭 No products available in inventory. Add some using POST /products."}
    return inventory

# ------------------------------------------------------------
# READ - Get a product by ID
# ------------------------------------------------------------
@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="❌ Product not found in inventory.")
    return product

# ------------------------------------------------------------
# UPDATE - Update stock quantity
# ------------------------------------------------------------
@app.put("/products/{product_id}", response_model=Product)
def update_stock(product_id: int, update: StockUpdate):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="❌ Product not found.")
    
    old_qty = product.quantity
    product.quantity = update.quantity
    print(f"[UPDATE] Product {product.name}: Quantity updated from {old_qty} → {update.quantity}")
    return product

# ------------------------------------------------------------
# SELL - Automatically reduce stock after sale
# ------------------------------------------------------------
@app.post("/products/{product_id}/sell")
def sell_product(product_id: int, quantity: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="❌ Product not found.")
    
    if product.quantity < quantity:
        raise HTTPException(status_code=400, detail="⚠️ Not enough stock available to complete the sale.")
    
    product.quantity -= quantity
    print(f"[SALE] Sold {quantity} units of {product.name}. Remaining: {product.quantity}")
    return {
        "message": f"✅ Sold {quantity} units of '{product.name}'. Remaining stock: {product.quantity}"
    }

# ------------------------------------------------------------
# DELETE - Remove a product
# ------------------------------------------------------------
@app.delete("/products/{product_id}", response_model=dict)
def delete_product(product_id: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="❌ Product not found.")
    
    inventory.remove(product)
    print(f"[DELETE] Product '{product.name}' removed from inventory.")
    return {"message": f"🗑️ Product '{product.name}' deleted successfully."}

# ------------------------------------------------------------
# Developer Note
# ------------------------------------------------------------
# 💡 This app uses an in-memory list for simplicity.
# In production, connect it to a real database (SQLite, PostgreSQL, etc.)
# via SQLAlchemy or another ORM.
