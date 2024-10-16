import sqlite3

class Database():
    @staticmethod
    def initConnection():
        conn = sqlite3.connect('./database/trading_history.db')
        cursor = conn.cursor()

        return conn, cursor
    

    @classmethod
    def dropAllTable(cls):
        # open connection
        conn, cursor = cls.initConnection()
        
        # drop asset, recommendation tables
        cursor.execute("DROP TABLE IF EXISTS asset")
        cursor.execute("DROP TABLE IF EXISTS recommendation")
        conn.commit()
        
        # close connection
        conn.close()

        return
    
    @classmethod
    def createTables(cls):
        # open connection
        conn, cursor = cls.initConnection()
        
        # create asset table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            btc_balance REAL,
            btc_avg_price REAL,
            btc_price REAL,
            krw_balance REAL,
            total_asset REAL
            )'''
        )
        # create recommendation table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendation (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            decision TEXT,
            ratio REAL,
            reason TEXT,
            result TEXT,
            FOREIGN KEY(id) REFERENCES asset(id)
            FOREIGN KEY(timestamp) REFERENCES asset(timestamp)
            )'''
        )
        conn.commit()

        # close connection
        conn.close()

        return

    @classmethod
    def insertIntoAsset(cls, asset, price):
        # open connection
        conn, cursor = cls.initConnection()
        
        timestamp = asset.get('current_time')
        btc_balance = asset.get('btc_balance')
        btc_avg_price = asset.get('btc_avg_price')
        btc_price = price
        krw_balance = asset.get('krw_balance')
        total_asset = round(btc_balance * btc_price + krw_balance)

        values = (timestamp, btc_balance, btc_avg_price, btc_price, krw_balance, total_asset)
        
        # insert asset information
        cursor.execute('''
            INSERT INTO asset (timestamp, btc_balance, btc_avg_price, btc_price, krw_balance, total_asset)
            VALUES (?, ?, ?, ?, ?, ?)''', values
        )
        conn.commit()

        # close connection
        conn.close()

        return

    @classmethod
    def insertIntoRecommendation(cls, response):
        # open connection
        conn, cursor = cls.initConnection()
        
        # get latest asset's id and timestamp for synchronization
        cursor.execute("SELECT id, timestamp FROM asset ORDER BY id DESC LIMIT 3")
        id, timestamp = cursor.fetchone()

        values = (id, timestamp, response.get('decision'), response.get('ratio'), response.get('reason'))
        
        # insert AI recommendation information
        cursor.execute('''
            INSERT INTO recommendation (id, timestamp, decision, ratio, reason)
            VALUES (?, ?, ?, ?, ?)''', values
        )
        conn.commit()

        # close connection
        conn.close()

        return

    @classmethod
    def updateRecommendationResult(cls):
        # open connection
        conn, cursor = cls.initConnection()
        
        # check if there is at least two asset information
        cursor.execute("SELECT COUNT(id) FROM asset")
        count = cursor.fetchone()
        if count[0] <= 1: return

        # fetch two latest asset information
        cursor.execute("SELECT id, total_asset FROM asset ORDER BY id DESC LIMIT 3")
        _, current_asset = cursor.fetchone()
        last_id, last_asset = cursor.fetchone()

        # if total asset increased, 'SUCCESS', decreased, 'FAIL'
        if current_asset > last_asset: result = 'SUCCESS'
        else: result = 'FAIL'

        # insert result to second latest recommendation
        cursor.execute('''
            UPDATE recommendation
            SET result = ?
            WHERE id = ?''', (result, last_id)
        )
        conn.commit()

        # close connection
        conn.close()

        return

    @classmethod
    def getLastRecommendation(cls):
        # open connection
        conn, cursor = cls.initConnection()
        
        # fetch last recommendation
        cursor.execute("SELECT * FROM recommendation ORDER BY id DESC LIMIT 3")
        last_recommendation = cursor.fetchone()

        # close connection
        conn.close()

        # raise error message when there is no recommendation
        if last_recommendation is None:
            raise Exception("There is no recommendation in the table")

        return last_recommendation

