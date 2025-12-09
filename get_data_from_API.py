import requests
import json
import os # 引入 os 模組用於檢查檔案路徑等 (非必須，但實用)

# --- 1. 定義 API 請求所需的參數 (與您提供的程式碼相同) ---
CWA_API_KEY = "CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F"
DATASET_ID = "F-A0010-001"
BASE_URL = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/"

# 2. 建構完整的 API 網址
url = f"{BASE_URL}{DATASET_ID}?Authorization={CWA_API_KEY}&downloadType=WEB&format=JSON"

# 3. 發送 GET 請求並處理
cwa_data = None # 初始化變數

try:
    response = requests.get(url)
    response.raise_for_status() # 檢查 HTTP 狀態碼
    cwa_data = response.json()
    
    print("✅ 資料成功獲取並解析為 Python 字典！")

    # --- 4. 儲存資料到本地 JSON 檔案 ---
    
    file_name = "cwa_weather_data.json"
    
    # 使用 'w' (寫入模式) 和 encoding='utf-8' 確保中文字元正確儲存
    with open(file_name, 'w', encoding='utf-8') as f:
        # 使用 json.dump() 寫入檔案。
        # indent=4 讓 JSON 檔案格式化 (易於閱讀)，ensure_ascii=False 確保中文正常顯示。
        json.dump(cwa_data, f, indent=4, ensure_ascii=False)
    
    print(f"🎉 資料已成功儲存至檔案: {file_name}")
    print(f"檔案路徑: {os.path.abspath(file_name)}")


except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP 請求失敗: {e}")
    print("請檢查 API 金鑰或資料集 ID 是否正確。")
except requests.exceptions.RequestException as e:
    print(f"❌ 網路連線錯誤: {e}")
except Exception as e:
    print(f"發生其他錯誤: {e}")