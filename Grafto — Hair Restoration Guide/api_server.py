#!/usr/bin/env python3
"""Grafto lead form API — stores submissions in SQLite."""
import sqlite3
import json
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

DB_PATH = "/home/user/workspace/grafto-site/leads.db"

def get_db():
    db = sqlite3.connect(DB_PATH, check_same_thread=False)
    db.execute("""CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        procedure_interest TEXT,
        norwood_stage TEXT,
        message TEXT,
        language TEXT DEFAULT 'en',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    db.commit()
    return db

db = get_db()

@asynccontextmanager
async def lifespan(app):
    yield
    db.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class LeadForm(BaseModel):
    name: str
    email: str
    phone: str = ""
    procedure_interest: str = ""
    norwood_stage: str = ""
    message: str = ""
    language: str = "en"

@app.post("/api/leads", status_code=201)
def create_lead(lead: LeadForm):
    cur = db.execute(
        "INSERT INTO leads (name, email, phone, procedure_interest, norwood_stage, message, language) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [lead.name, lead.email, lead.phone, lead.procedure_interest, lead.norwood_stage, lead.message, lead.language]
    )
    db.commit()
    return {"id": cur.lastrowid, "status": "success"}

@app.get("/api/leads")
def list_leads():
    rows = db.execute("SELECT id, name, email, phone, procedure_interest, norwood_stage, message, language, created_at FROM leads ORDER BY id DESC").fetchall()
    return [{"id": r[0], "name": r[1], "email": r[2], "phone": r[3], "procedure_interest": r[4], "norwood_stage": r[5], "message": r[6], "language": r[7], "created_at": r[8]} for r in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
