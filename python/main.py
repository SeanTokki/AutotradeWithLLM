from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler


app = FastAPI()
scheduler = BackgroundScheduler(daemon=True)


# CORS setting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def isActive():
    global scheduler

    if scheduler.running:
        return "Active"
    else:
        return "Deactive"


def run_autotrade():
    subprocess.Popen(["python", "autotrade.py"])
    # subprocess.Popen(["./.venv/Scripts/python.exe", "./autotrade.py"])

    return


@app.get("/")
def root():
    return {"hello": "world"}


@app.get("/status")
def status():
    return {"status": isActive()}


class StartItem(BaseModel):
    strategy: str = ""


@app.post("/start")
def start(item: StartItem):
    global scheduler

    # item_dict = item.model_dump()
    # print(item_dict)
    # TODO add strategy into DB and apply it to autotrading

    if scheduler.running:
        raise HTTPException(status_code=400, detail="The program is already running.")
    else:
        # start the program
        run_autotrade()
        # schedule to execute program every hour
        scheduler.add_job(run_autotrade, "interval", hours=1, misfire_grace_time=None)
        scheduler.start()

    return {"status": isActive(), "message": "Program started successfully."}


@app.post("/stop")
def stop():
    global scheduler

    # stop the program
    if not scheduler.running:
        raise HTTPException(status_code=400, detail="No running program.")
    else:
        scheduler.remove_all_jobs()
        scheduler.shutdown(wait=False)

    return {"status": isActive(), "message": "Program stopped successfully."}


@app.get("/recommendations")
def recommendations():
    conn = sqlite3.connect("./database/trading_history.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM recommendation ORDER BY id")
        r_list = cursor.fetchall()

    except:
        r_list = []
    finally:
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

    return {"recommendations": recommendations}


@app.get("/profit")
def profit():
    conn = sqlite3.connect("./database/trading_history.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            (SELECT total_asset FROM asset ORDER BY id LIMIT 1)
            UNION ALL
            (SELECT total_asset FROM asset ORDER BY id DESC LIMIT 1)"""
        )
        result = cursor.fetchall()
        initial_asset, current_asset = result[0][0], result[1][0]
    except:
        initial_asset, current_asset = 1, 1
    finally:
        conn.close()
    # cursor.execute("SELECT total_asset FROM asset ORDER BY id LIMIT 1")
    # initial_asset = cursor.fetchone()[0]
    # cursor.execute("SELECT total_asset FROM asset ORDER BY id DESC LIMIT 1")
    # current_asset = cursor.fetchone()[0]

    profit = round((current_asset - initial_asset) / initial_asset * 100, 2)

    return {"profit": profit}


@app.get("/chartData")
def chartData():
    conn = sqlite3.connect("./database/trading_history.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT asset.id, asset.timestamp, decision, ratio, btc_price 
                    FROM recommendation INNER JOIN asset 
                    ON recommendation.timestamp = asset.timestamp"""
        )
        cd_list = cursor.fetchall()
    except:
        cd_list = []
    finally:
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

    return {"data": chart_data}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
