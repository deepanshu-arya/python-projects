# ---------------------------------------------------------------------
# Project: SmartShop AI Assistant (Shop Management Backend)
# Description: Manage products, customers, and transactions.
# Author: Deepanshu
# ---------------------------------------------------------------------

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from datetime import datetime

# ------------------------------------------------------------
# App metadata
# ------------------------------------------------------------
app = FastAPI(
    title="SmartShop AI Assistant",
    version="1.2.0",
    description="A simple shop management backend for products, customers, and transactions (demo/in-memory)."
)

# ------------------------------------------------------------
# In-memory "database" (demo)
# ------------------------------------------------------------
_products: Dict[int, "Product"] = {}
_customers: Dict[int, "Customer"] = {}
_transactions: List[Dict] = []


# ------------------------------------------------------------
# Data Models
# ------------------------------------------------------------
class Product(BaseModel):
    id: int = Field(..., description="Unique product ID")
    name: str = Field(..., min_length=1, description="Product name")
    price: float = Field(..., gt=0, description="Product price (must be > 0)")
    stock: int = Field(..., ge=0, description="Available stock (>= 0)")

    @validator("name")
    def strip_name(cls, v: str) -> str:
        return v.strip()


class Customer(BaseModel):
    id: int = Field(..., description="Unique customer ID")
    name: str = Field(..., min_length=1, description="Customer full name")
    phone: str = Field(..., min_length=6, description="Customer phone number")

    @validator("name", "phone", pre=True)
    def strip_strings(cls, v: str) -> str:
        return v.strip()


class Transaction(BaseModel):
    customer_id: int = Field(..., description="ID of the customer making the purchase")
    product_id: int = Field(..., description="ID of the product sold")
    quantity: int = Field(..., gt=0, description="Quantity sold (must be > 0)")
    timestamp: Optional[str] = Field(None, description="ISO timestamp when transaction was recorded")


# ------------------------------------------------------------
# Utility / Helper functions
# ------------------------------------------------------------
def log_action(message: str) -> None:
    """Simple timestamped console logger for development and auditing."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def get_product_or_404(product_id: int) -> Product:
    """Return product or raise 404 if not found."""
    product = _products.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
    return product


def get_customer_or_404(customer_id: int) -> Customer:
    """Return customer or raise 404 if not found."""
    customer = _customers.get(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found."
        )
    return customer


def reduce_stock(product_id: int, quantity: int) -> None:
    """
    Deduct quantity from product stock.
    Raises HTTPException on insufficient stock.
    """
    product = get_product_or_404(product_id)
    if product.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock}"
        )
    product.stock -= quantity
    log_action(f"Stock updated for product ID {product_id}: new stock = {product.stock}")


# ------------------------------------------------------------
# Routes / Endpoints
# ------------------------------------------------------------
@app.get("/", tags=["Root"])
def home():
    """API root with quick information."""
    return {
        "message": "Welcome to SmartShop AI Assistant Backend 🛍️",
        "note": "This is a demo using in-memory storage. Data resets when server restarts."
    }


# -------------------------
# Product Management
# -------------------------
@app.post("/products/add", status_code=status.HTTP_201_CREATED, tags=["Products"])
def add_product(product: Product):
    """Add a new product to the inventory."""
    if product.id in _products:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product ID {product.id} already exists."
        )
    _products[product.id] = product
    log_action(f"Added product: {product.id} - {product.name}")
    return {"status": "success", "message": "Product added successfully", "product": product}


@app.get("/products", tags=["Products"])
def list_products():
    """List all products in inventory."""
    return {"products": list(_products.values())}


@app.put("/products/update/{product_id}", tags=["Products"])
def update_product(product_id: int, updated_data: Product):
    """Update product details (replace existing)."""
    if product_id not in _products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
    _products[product_id] = updated_data
    log_action(f"Updated product: {product_id}")
    return {"status": "success", "message": "Product updated successfully", "product": updated_data}


@app.delete("/products/delete/{product_id}", tags=["Products"])
def delete_product(product_id: int):
    """Remove a product from inventory."""
    if product_id not in _products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
    removed = _products.pop(product_id)
    log_action(f"Deleted product: {product_id} - {removed.name}")
    return {"status": "success", "message": "Product deleted successfully", "product_id": product_id}


# -------------------------
# Customer Management
# -------------------------
@app.post("/customers/add", status_code=status.HTTP_201_CREATED, tags=["Customers"])
def add_customer(customer: Customer):
    """Register a new customer."""
    if customer.id in _customers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Customer ID {customer.id} already exists."
        )
    _customers[customer.id] = customer
    log_action(f"Added customer: {customer.id} - {customer.name}")
    return {"status": "success", "message": "Customer added successfully", "customer": customer}


@app.get("/customers", tags=["Customers"])
def list_customers():
    """List all registered customers."""
    return {"customers": list(_customers.values())}


# -------------------------
# Transaction Management
# -------------------------
@app.post("/transactions/add", status_code=status.HTTP_201_CREATED, tags=["Transactions"])
def add_transaction(transaction: Transaction):
    """Record a sale transaction, update stock, and store transaction history."""
    # Verify customer and product exist
    get_customer_or_404(transaction.customer_id)
    get_product_or_404(transaction.product_id)

    # Update stock (will raise HTTPException if insufficient)
    reduce_stock(transaction.product_id, transaction.quantity)

    # Record transaction with timestamp
    transaction.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tx_record = transaction.dict()
    _transactions.append(tx_record)

    log_action(f"Recorded transaction: customer={transaction.customer_id}, product={transaction.product_id}, qty={transaction.quantity}")
    return {"status": "success", "message": "Transaction recorded successfully", "transaction": tx_record}


@app.get("/transactions", tags=["Transactions"])
def list_transactions():
    """Return recorded transactions (history)."""
    return {"transactions": _transactions}


# -------------------------
# Sales Summary
# -------------------------
@app.get("/summary/sales", tags=["Summary"])
def sales_summary():
    """
    Compute a simple sales summary:
    - total_transactions
    - total_items_sold
    - total_sales_amount
    """
    total_sales = 0.0
    total_items_sold = 0

    for t in _transactions:
        prod = _products.get(t["product_id"])
        if prod:
            total_sales += prod.price * t["quantity"]
            total_items_sold += t["quantity"]

    return {
        "total_transactions": len(_transactions),
        "total_items_sold": total_items_sold,
        "total_sales_amount": round(total_sales, 2)
    }


# ------------------------------------------------------------
# Developer Notes
# - This backend uses in-memory dictionaries for demo purposes.
# - For production: migrate to a database (SQLite / PostgreSQL), add authentication,
#   input validation with unique constraints, and background tasks for reporting.
# ------------------------------------------------------------
