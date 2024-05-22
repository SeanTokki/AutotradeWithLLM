from fastapi import FastAPI, Request
import sqlite3
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory='/home/ec2-user/AutotradeWithLLM/front_html')

@app.get("/")
def root(request: Request):
    conn = sqlite3.connect('/home/ec2-user/AutotradeWithLLM/trading_history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendation ORDER BY id")
    data1 = cursor.fetchall()
    cursor.execute("SELECT * FROM asset ORDER BY id")
    data2 = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse("index.html", {"request": request, "data1": data1, "data2": data2})


@app.get("/main")
def main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)