import sqlite3

def drop_all_table(cursor, conn):
  cursor.execute("DROP TABLE IF EXISTS asset")
  cursor.execute("DROP TABLE IF EXISTS recommendation")
  conn.commit()

  return

def create_tables(cursor, conn):
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

  return

def insert_into_asset(cursor, conn, asset, price):
  timestamp = asset.get('current_time')
  btc_balance = asset.get('btc_balance')
  btc_avg_price = asset.get('btc_avg_price')
  btc_price = price
  krw_balance = asset.get('krw_balance')
  total_asset = round(btc_balance * btc_price + krw_balance)

  values = (timestamp, btc_balance, btc_avg_price, btc_price, krw_balance, total_asset)

  cursor.execute('''
    INSERT INTO asset (timestamp, btc_balance, btc_avg_price, btc_price, krw_balance, total_asset)
    VALUES (?, ?, ?, ?, ?, ?)''', values
  )
  conn.commit()

  return

def insert_into_recommendation(cursor, conn, response):
  cursor.execute("SELECT id, timestamp FROM asset ORDER BY id DESC LIMIT 3")
  id, timestamp = cursor.fetchone()

  values = (id, timestamp, response.get('decision'), response.get('ratio'), response.get('reason'))
  cursor.execute('''
    INSERT INTO recommendation (id, timestamp, decision, ratio, reason)
    VALUES (?, ?, ?, ?, ?)''', values
  )
  conn.commit()

  return

def update_recommendation_result(cursor, conn):
  # check if there is at least two asset information
  cursor.execute("SELECT COUNT(id) FROM asset")
  count = cursor.fetchone()
  if count[0] <= 1: return

  cursor.execute("SELECT id, total_asset FROM asset ORDER BY id DESC LIMIT 3")
  _, current_asset = cursor.fetchone()
  last_id, last_asset = cursor.fetchone()

  # if total asset increased, 'SUCCESS', decreased, 'FAIL'
  if current_asset > last_asset: result = 'SUCCESS'
  else: result = 'FAIL'

  cursor.execute('''
    UPDATE recommendation
    SET result = ?
    WHERE id = ?''', (result, last_id)
  )
  conn.commit()

  return

def get_last_recommendation(cursor):
  cursor.execute("SELECT * FROM recommendation ORDER BY id DESC LIMIT 3")
  last_recommendation = cursor.fetchone()
  if last_recommendation:
    return last_recommendation
  else:
    print("There is no recommendation in the table")
    return None