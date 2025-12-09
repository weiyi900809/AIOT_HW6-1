import json
import sqlite3
import os

# --- 1. 定義常數 ---
JSON_FILE_NAME = "cwa_weather_data.json"
DB_FILE_NAME = "CWA_data.db"
TABLE_NAME = "weather"

# SQL 語句：創建資料表
CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    min_temp REAL,
    max_temp REAL,
    description TEXT
);
"""

# SQL 語句：插入資料
# 使用 ? 作為參數的佔位符，防止 SQL 隱碼攻擊，並確保數據類型正確
INSERT_SQL = f"""
INSERT INTO {TABLE_NAME} (location, min_temp, max_temp, description)
VALUES (?, ?, ?, ?);
"""

# --- 2. 載入 JSON 資料 ---
try:
    with open(JSON_FILE_NAME, 'r', encoding='utf-8') as f:
        cwa_data = json.load(f)
    print(f"✅ 成功載入 JSON 檔案: {JSON_FILE_NAME}")

except FileNotFoundError:
    print(f"❌ 錯誤：找不到檔案 {JSON_FILE_NAME}。請確保檔案已存在。")
    raise 

# --- 3. 解析 JSON 資料 (擷取第一天預報) ---
data_list = []
try:
    # 進入到主要預報資料列表的路徑
    locations = cwa_data['cwaopendata']['resources']['resource']['data']['agrWeatherForecasts']['weatherForecasts']['location']
    
    # 遍歷每個地區
    for loc in locations:
        location_name = loc['locationName'] # 取得 locationName (地點名稱)
        
        # 進入天氣元素
        elements = loc['weatherElements']
        
        # 取出第一天的預報（即索引 0）
        first_day_index = 0
        
        # 取得最低溫 (MinT)
        min_temp = elements['MinT']['daily'][first_day_index]['temperature']
        
        # 取得最高溫 (MaxT)
        max_temp = elements['MaxT']['daily'][first_day_index]['temperature']
        
        # 取得天氣描述 (Wx)
        description = elements['Wx']['daily'][first_day_index]['weather']
        
        # 將這筆資料加入清單 (轉換溫度為浮點數 REAL)
        # 數據以元組 (Tuple) 形式儲存，以便於 executemany 批量插入
        data_list.append((
            location_name,
            float(min_temp),
            float(max_temp),
            description
        ))

    print(f"✅ 成功解析 {len(data_list)} 筆資料，準備寫入資料庫。")

except Exception as e:
    print(f"❌ JSON 解析失敗: {e}")
    raise

# --- 4. 建立 SQLite 資料庫連線並存儲資料 ---
conn = None
try:
    # 建立資料庫連線 (如果檔案不存在，會自動創建 CWA_data.db)
    conn = sqlite3.connect(DB_FILE_NAME)
    cursor = conn.cursor()
    
    # 創建資料表
    cursor.execute(CREATE_TABLE_SQL)
    
    # 清空舊資料（可選，但確保資料是即時的）
    cursor.execute(f"DELETE FROM {TABLE_NAME}")

    # 批次插入資料 (使用 executemany 提高效率)
    cursor.executemany(INSERT_SQL, data_list)
    
    # 提交更改，將資料永久寫入檔案
    conn.commit()
    print(f"🎉 成功將 {cursor.rowcount} 筆資料存入 {DB_FILE_NAME} 資料庫。")
    
except sqlite3.Error as e:
    print(f"❌ SQLite 錯誤: {e}")
    if conn:
        conn.rollback() # 出錯時回滾操作
except Exception as e:
    print(f"❌ 發生未知錯誤: {e}")
finally:
    if conn:
        conn.close() # 關閉連線

# 資料庫檔案名稱已輸出給使用者: CWA_data.db