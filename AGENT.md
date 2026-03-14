# AGENT.md

## 專案定位

此專案是醫美情境用的 Streamlit RAG 展示系統，主要用途是讓使用者輸入顧客問題後，從 Supabase 中找出最相近的 QA 回答，並以適合對外展示的醫美品牌風格呈現結果。

目前正式 repo 是 `nan-rag`，部署入口是 `app.py`，執行環境是 **Python 3.12**。

---

## 目前技術結構

- 前端與查詢流程都集中在 `app.py`
- UI 框架是 `streamlit`
- 向量模型使用 `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- 向量比對結果來自 Supabase RPC：`match_qa`
- 部署目標是 Streamlit Community Cloud

---

## 實際專案結構

```text
nan-rag/
├─ app.py
├─ QA.csv
├─ QA詞向量2.ipynb
├─ requirements.txt
├─ runtime.txt
├─ AGENT.md
└─ .streamlit/
   └─ secrets.toml.example
```

說明：

- `app.py`：正式入口，包含 UI、查詢流程、結果呈現
- `QA.csv`：目前 QA 資料來源之一
- `QA詞向量2.ipynb`：資料整理或向量相關實驗筆記
- `requirements.txt`：部署與本機安裝依賴
- `runtime.txt`：指定 Streamlit Cloud 使用 `python-3.12`
- `.streamlit/secrets.toml.example`：Secrets 格式範例

---

## 已知必要設定

此專案需要以下 secrets 或環境變數才能查詢：

- `SUPABASE_URL`
- `SUPABASE_KEY`

若缺少任一設定，畫面應明確提示缺少哪個項目，而不是直接失敗。

---

## 這次實際踩到的重點

### 1. 正式工作目錄要認 `nan-rag`

- `nan-rag` 才是正式 Git repo
- `nan-rag-main` 只是之前下載下來的副本，後來已刪除
- 之後修改、commit、push、部署都應只在 `nan-rag` 進行

### 2. 對外展示文案要正式

- 此專案會直接展示給廠商看
- 頁面內不應出現過於原型感的字眼，例如 `demo`
- 文案應偏向「展示」「品牌」「顧問」「知識庫」等正式語氣

### 3. 輸入框可讀性很重要

- Streamlit 客製 CSS 後，輸入框文字可能變得太淡或接近白色
- 需要明確指定輸入文字顏色、placeholder 顏色、caret 顏色
- 若前端展示用，請優先檢查輸入框、按鈕、卡片文字是否清楚

### 4. 本機開發環境以 F 槽為主

- 使用者偏好把開發工具集中在 `F:` 管理
- Git 安裝在 `F:\Program Files\Git`
- Python 3.12 安裝在 `F:\Users\beyondsp4\AppData\Local\Programs\Python\Python312`
- 若要建立虛擬環境，優先使用這個 Python 3.12 路徑

### 5. 刪除前要先確認用途

- 使用者偏好先確認資料夾是否還在用，再刪除
- 專案整理時，先分辨正式 repo、下載副本、安裝暫存、快取檔，再做清理
- 保持 workspace 乾淨，但不要在未確認前刪除疑似工作資料

---

## 開發與修改原則

- 優先保持單檔 `app.py` 可維護，不要無必要拆太多檔
- 若新增功能，先評估是否仍適合放在 `app.py`
- 若查詢邏輯或資料處理開始複雜，再考慮拆分模組
- 文案以繁體中文為主，面向廠商或品牌展示時避免工程感措辭
- UI 調整需同時考慮桌面展示與 Streamlit Cloud 實際效果

---

## 常用本機指令

建立虛擬環境：

```powershell
& "F:\Users\beyondsp4\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv
```

啟用虛擬環境：

```powershell
.\.venv\Scripts\Activate.ps1
```

安裝依賴：

```powershell
pip install -r requirements.txt
```

啟動 Streamlit：

```powershell
streamlit run app.py
```

---

## 部署說明

- GitHub repo：`https://github.com/beyondsp44/nan-rag`
- Streamlit Cloud 會從此 repo 的 `main` 分支更新
- 目前 app 為 public，可直接用網址展示

若 UI 已修改但線上未更新，優先檢查：

1. 是否已在 `nan-rag` repo commit 與 push
2. Streamlit Cloud 是否連到正確 repo 與分支
3. secrets 是否仍存在
4. 是否需要手動 `Reboot app` 或 `Redeploy`

---

## 未來擴展方向

此專案很適合逐步擴展成更完整的醫美專有知識庫客服系統，例如：

- 多分類知識庫檢索
- 回答重組與摘要
- 管理端 QA 匯入
- 查詢紀錄與命中品質檢查
- 針對療程、術前、術後、價格、禁忌的分流入口

相關擴展提案請參考 `openspec/changes/`。
