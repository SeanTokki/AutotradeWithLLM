from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
import subprocess

app = FastAPI()
process = None

# CORS 설정 (필요에 따라 도메인을 제한할 수 있음)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def toStatus(p):
    if p is not None:
        return "Active"
    else:
        return "Deactive"


@app.get("/")
def root():
    return {"hello": "world"}


@app.get("/status")
def status():
    global process

    return {'status': toStatus(process)}


class StartItem(BaseModel):
    strategy: str = ""


@app.post("/start")
def start(item: StartItem):
    global process

    item_dict = item.model_dump()
    print(item_dict)
    # TODO add strategy into DB and apply it to autotrading
    
    # start the program with item_dict.strategy
    if process is not None and process.poll() is None:
        raise HTTPException(status_code=400, detail="The program is already running.")
    process = subprocess.Popen(["python", "../autotrade/autotrade.py"])
    
    return {'status': toStatus(process), "message": "Program started successfully."}


@app.post("/stop")
def stop():
    global process
    
    # stop the program
    if process is None or process.poll() is not None:
        raise HTTPException(status_code=400, detail="No running program.")
    process.terminate()
    process.wait()
    process = None

    return {'status': toStatus(process)}


@app.get("/recommendations")
def recommendations():
    conn = sqlite3.connect('../autotrade/database/trading_history_old.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendation ORDER BY id LIMIT 30") # limit for test
    r_list = cursor.fetchall()
    conn.close()

    recommendations = []
    for item in r_list:
        r_json = {
            "id": item[0],
            "timestamp": item[1],
            "decision": item[2],
            "ratio": item[3],
            "reason": item[4],
            "result": item[5],
        }
        recommendations.append(r_json)

    return {'recommendations': recommendations}


@app.get("/profit")
def profit():
    conn = sqlite3.connect('../autotrade/database/trading_history_old.db')
    cursor = conn.cursor()
    cursor.execute("SELECT total_asset FROM asset ORDER BY id LIMIT 1")
    initial_asset = cursor.fetchone()[0]
    cursor.execute("SELECT total_asset FROM asset ORDER BY id DESC LIMIT 1")
    current_asset = cursor.fetchone()[0]
    conn.close()

    profit = round((current_asset - initial_asset) / initial_asset * 100, 2)

    return {'profit': profit}


@app.get("/chartData")
def chartData():
    conn = sqlite3.connect('../autotrade/database/trading_history_old.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT asset.id, asset.timestamp, decision, ratio, btc_price 
                   FROM recommendation INNER JOIN asset 
                   ON recommendation.timestamp = asset.timestamp LIMIT 30''')
    cd_list = cursor.fetchall()
    conn.close()

    chart_data = []
    for item in cd_list:
        cd_json = {
            "id": item[0],
            "timestamp": item[1],
            "decision": item[2],
            "ratio": item[3],
            "btc_price": item[4],
        }
        chart_data.append(cd_json)
    
    return {'data': chart_data}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)