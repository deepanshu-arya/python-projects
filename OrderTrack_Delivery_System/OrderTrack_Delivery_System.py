from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ------------------------------------------------------------
# App Initialization
# ------------------------------------------------------------
app = FastAPI(
    title="OrderTrack Delivery System",
    description="📦 A lightweight API to manage and track customer orders.",
    version="1.1.0"
)

# ------------------------------------------------------------
# Data Models
# ------------------------------------------------------------
class Order(BaseModel):
    id: int = Field(..., description="Unique order ID")
    customer_name: str = Field(..., description="Name of the customer placing the order")
    product_name: str = Field(..., description="Product being ordered")
    quantity: int = Field(..., gt=0, description="Quantity of the product ordered")
    status: str = Field(default="Pending", description="Current order status")
    created_at: datetime = Field(default_factory=datetime.now, description="Order creation time")

class StatusUpdate(BaseModel):
    status: str = Field(..., description="New status for the order (e.g., Shipped, Delivered, Canceled)")

# ------------------------------------------------------------
# In-Memory Database Simulation
# ------------------------------------------------------------
orders_db: List[Order] = []  # Acts like a temporary in-memory table

# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def find_order_by_id(order_id: int) -> Optional[Order]:
    """Finds and returns an order by ID."""
    for order in orders_db:
        if order.id == order_id:
            return order
    return None

# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------

@app.get("/")
def home():
    """API Home Route."""
    return {
        "message": "🚚 Welcome to OrderTrack Delivery System!",
        "usage": "Use /orders endpoint to manage and track your orders."
    }

# ------------------------------------------------------------
# CREATE - Add a New Order
# ------------------------------------------------------------
@app.post("/orders", response_model=Order)
def create_order(order: Order):
    if find_order_by_id(order.id):
        raise HTTPException(status_code=400, detail="⚠️ Order ID already exists. Please use a unique ID.")
    
    orders_db.append(order)
    print(f"[INFO] New order created — ID: {order.id}, Customer: {order.customer_name}")
    return order

# ------------------------------------------------------------
# READ - Get All Orders
# ------------------------------------------------------------
@app.get("/orders", response_model=List[Order])
def get_all_orders():
    if not orders_db:
        return {"message": "No orders found yet. Add your first order using POST /orders."}
    return orders_db

# ------------------------------------------------------------
# READ - Get Single Order
# ------------------------------------------------------------
@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    order = find_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="❌ Order not found. Please check the order ID.")
    return order

# ------------------------------------------------------------
# UPDATE - Modify Order Status
# ------------------------------------------------------------
@app.put("/orders/{order_id}", response_model=Order)
def update_order_status(order_id: int, update: StatusUpdate):
    order = find_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="❌ Cannot update — order not found.")

    valid_statuses = {"Pending", "Processing", "Shipped", "Delivered", "Canceled"}
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from {valid_statuses}.")

    order.status = update.status
    print(f"[UPDATE] Order {order_id} status changed to {update.status}")
    return order

# ------------------------------------------------------------
# DELETE - Remove an Order
# ------------------------------------------------------------
@app.delete("/orders/{order_id}", response_model=dict)
def delete_order(order_id: int):
    order = find_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="❌ Order not found. Deletion failed.")

    orders_db.remove(order)
    print(f"[DELETE] Order {order_id} removed successfully.")
    return {"message": f"✅ Order ID {order_id} deleted successfully."}

# ------------------------------------------------------------
# Developer Note
# ------------------------------------------------------------
# This app uses an in-memory list to store data.
# When restarted, all data resets — ideal for testing or local demos.
# In a real project, replace with a database (e.g., SQLite, PostgreSQL).
