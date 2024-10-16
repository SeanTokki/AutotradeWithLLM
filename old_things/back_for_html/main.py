from fastapi import FastAPI, Request
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory='./front_html')

# CORS 설정 (필요에 따라 도메인을 제한할 수 있음)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 현재 Autotrading 상태를 저장하는 변수
is_autotrading = False

@app.get("/")
async def main(request: Request):
    global is_autotrading
    
    return templates.TemplateResponse("main.html", {"request": request, "is_autotrading": is_autotrading})

@app.get("/result")
async def result(request: Request):
    conn = sqlite3.connect('./trading_history_old.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendation ORDER BY id")
    data1 = cursor.fetchall()
    cursor.execute("SELECT * FROM asset ORDER BY id")
    data2 = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("result.html", {"request": request, "data1": data1, "data2": data2})

@app.get("/get-state")
async def get_state():
    global is_autotrading

    return {"isAutoTrading": is_autotrading}

@app.get("/toggle-state")
async def toggle_state():
    global is_autotrading
    is_autotrading = not is_autotrading

    return {"message": "State updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)