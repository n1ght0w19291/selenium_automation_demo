# lesson_skip_script

## 簡介
此專案是一個用於掛網課的自動化腳本。透過設置環境變數與簡單配置，您可以快速啟動並使用此腳本。

---

## 環境變數
使用此腳本前，請先設置一個 `.env` 檔案，內容如下：

```dotenv
PASSWORD=ABC123  # 登入密碼
ACCOUNT=U11116000  # 使用者帳號
COURSE_URL=https://tms.utaipei.edu.tw/course/329  # 課程頁面的 URL
```

請根據您的實際資訊修改上述變數內容。

---

## 使用方法
1. **安裝依賴：**
   如果是 Python 腳本，請確保已安裝必要的套件。您可以使用以下命令安裝：
   ```bash
   pip install selenium
   pip install python-dotenv
   ```

2. **設定環境變數：**
   確保 `.env` 文件存在於專案根目錄，並填寫正確資訊。

3. **執行腳本：**
   使用以下命令啟動腳本：
   ```bash
   python ./src/main.py
   ```

---

## 注意事項
- 確認您的帳號、密碼與課程 URL 是否正確。
- 此腳本僅供學術用途，請勿用於未經授權的活動。