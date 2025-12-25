🚀 AI Billing System with Voice & OCR (FastAPI)

An AI-powered billing backend designed for small businesses and shopkeepers.
This system enables voice-based billing, OCR bill uploads, automatic stock deduction, and PDF receipt generation, built using FastAPI and SQLite.

📌 Features

🎙️ Voice Billing

Converts spoken items (English/Hindi) into structured billing data

Parses product name, quantity, and price automatically

🧾 OCR Bill Upload

Upload scanned/offline bills

Extracts text using OCR for digital record keeping

📦 Stock Management

Automatically deducts stock after each transaction

Tracks available product quantities

🧮 Transaction Logging

Saves customer transactions with date & time

Maintains billing history

📄 PDF Receipt Generation

Generates professional PDF invoices

Ready for WhatsApp or email sharing

⚡ FastAPI Backend

Clean REST APIs

Easy integration with mobile or web frontend

🛠️ Tech Stack

Backend: FastAPI (Python)

Database: SQLite + SQLAlchemy

Voice Recognition: Vosk

OCR: Tesseract OCR

PDF Generation: ReportLab

API Testing: Swagger UI (/docs)

📂 Project Structure
AI_Billing_System/
│
├── main.py                # Main FastAPI application
├── database.db            # SQLite database
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── receipts/              # Generated PDF bills
└── uploads/               # Uploaded OCR bills

▶️ How to Run the Project
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Start the server
uvicorn main:app --reload

3️⃣ Open API Docs
http://127.0.0.1:8000/docs

🧪 Example Use Cases

Shopkeeper speaks:
"2 rice, 1 sugar"
→ System creates a bill automatically

Upload a photo of a handwritten bill
→ System extracts text & stores it digitally

🎯 Future Enhancements

WhatsApp Cloud API integration

Sales analytics dashboard

Multi-language voice support

Cloud deployment (AWS / Render)

👨‍💻 Author

Deepanshu Arya
Aspiring AI Backend Developer
Focused on real-world AI solutions for small businesses

GitHub: https://github.com/deepanshu-arya