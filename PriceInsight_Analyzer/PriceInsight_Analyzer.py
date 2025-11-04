from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime

# =============================================================
# App Configuration
# =============================================================
app = FastAPI(
    title="PriceInsight Analyzer",
    version="1.2.0",
    description="An intelligent API that analyzes product price data and provides insights like averages, extremes, and summary."
)

# =============================================================
# Data Models
# =============================================================
class Product(BaseModel):
    """Represents a single product with its name and price."""
    name: str = Field(..., description="Name of the product", example="Laptop")
    price: float = Field(..., gt=0, description="Price of the product (must be greater than 0)", example=49999.99)

    @validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Product name cannot be empty.")
        return v.strip()


class ProductList(BaseModel):
    """Holds a list of products to analyze."""
    products: List[Product] = Field(..., description="List of product objects for price analysis")


# =============================================================
# Helper Function (Logic Layer)
# =============================================================
def analyze_prices(products: List[Product]) -> dict:
    """
    Perform analysis on product prices:
    - Calculates total, average, min, max
    - Identifies cheapest and costliest product
    """
    if not products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No products provided for analysis."
        )

    prices = [p.price for p in products]
    names = [p.name for p in products]

    total = sum(prices)
    avg_price = total / len(prices)
    min_price = min(prices)
    max_price = max(prices)

    cheapest_product = names[prices.index(min_price)]
    costliest_product = names[prices.index(max_price)]

    return {
        "total_products": len(products),
        "average_price": round(avg_price, 2),
        "lowest_price": round(min_price, 2),
        "highest_price": round(max_price, 2),
        "cheapest_product": cheapest_product,
        "costliest_product": costliest_product,
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# =============================================================
# Routes / Endpoints
# =============================================================
@app.get("/", tags=["Home"])
def home():
    """Root endpoint for the PriceInsight API."""
    return {
        "message": "Welcome to PriceInsight Analyzer 💰",
        "usage": "Send a POST request to /analyze with a list of products and their prices.",
        "example_endpoint": "/analyze"
    }


@app.post("/analyze", tags=["Analysis"], status_code=status.HTTP_200_OK)
def analyze_price_data(product_list: ProductList):
    """
    Analyze the given list of products and return price insights.
    Example Request:
    ```json
    {
        "products": [
            {"name": "Laptop", "price": 59999},
            {"name": "Phone", "price": 29999},
            {"name": "Headphones", "price": 1999}
        ]
    }
    ```
    """
    result = analyze_prices(product_list.products)
    return {
        "status": "success",
        "summary": "Price analysis completed successfully.",
        "price_insights": result
    }


@app.get("/sample-data", tags=["Utility"], status_code=status.HTTP_200_OK)
def sample_data():
    """Provides example data for testing the analyzer."""
    sample = {
        "products": [
            {"name": "Laptop", "price": 65000},
            {"name": "Mobile", "price": 25000},
            {"name": "Earphones", "price": 1500},
            {"name": "Monitor", "price": 12000},
            {"name": "Keyboard", "price": 2500}
        ]
    }
    return {
        "message": "Sample dataset ready to test /analyze endpoint.",
        "data": sample
    }


@app.get("/health", tags=["Utility"], status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint for monitoring system status."""
    return {
        "status": "running",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "service": "PriceInsight Analyzer"
    }


# =============================================================
# Developer Notes
# - Cleanly formatted and structured API
# - Includes validation, examples, and helper endpoints
# - Ready to extend with DB or ML-based pricing recommendations
# =============================================================

