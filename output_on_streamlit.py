import streamlit as st
import sqlite3
import pandas as pd
import os

# --- 設定常數 ---
DB_FILE_NAME = "CWA_data.db"
TABLE_NAME = "weather"

def load_data_from_db():
    """連線到 SQLite 資料庫，讀取所有天氣資料，並回傳 DataFrame。"""
    conn = None
    df = pd.DataFrame()
    
    # 檢查資料庫檔案是否存在
    if not os.path.exists(DB_FILE_NAME):
        st.error(f"❌ 錯誤：找不到資料庫檔案 '{DB_FILE_NAME}'。請先執行前一個步驟的 Python 程式來創建它。")
        return df

    try:
        # 建立連線
        conn = sqlite3.connect(DB_FILE_NAME)
        
        # 執行 SQL 查詢，讀取所有資料
        query = f"SELECT location, min_temp, max_temp, description FROM {TABLE_NAME}"
        
        # 使用 pandas 函式直接讀取 SQL 查詢結果到 DataFrame
        df = pd.read_sql_query(query, conn)
        
        # 重新命名欄位，使其更具可讀性
        df.columns = ["地區", "最低溫 (°C)", "最高溫 (°C)", "天氣狀況"]
        
        return df
        
    except sqlite3.Error as e:
        st.error(f"❌ 資料庫讀取錯誤: {e}")
        return df
    finally:
        if conn:
            conn.close()

# --- Streamlit 主介面 ---
def main():
    st.set_page_config(page_title="CWA 天氣預報顯示", layout="wide")
    
    st.title("🇹🇼 中央氣象局天氣預報 (SQLite 資料庫讀取)")
    
    st.markdown("---")
    
    # 載入資料
    weather_df = load_data_from_db()
    
    if not weather_df.empty:
        st.subheader(f"✅ 資料表：{TABLE_NAME} (讀取自 {DB_FILE_NAME})")
        
        # 顯示資料表格
        # 使用 st.dataframe 顯示數據
        st.dataframe(weather_df, use_container_width=True)
        
        st.caption(f"共讀取到 {len(weather_df)} 筆地區的預報資料。")
    else:
        st.warning("資料庫中沒有資料，或資料庫檔案不存在。")

if __name__ == "__main__":
    main()