# medical-aesthetics-rag Specification

## Purpose

定義此醫美 RAG 專案目前已完成的查詢流程、對外展示 UI、必要設定與部署行為，作為後續維護、驗證與擴展的正式規格基準。

## Requirements

### Requirement: Streamlit vendor-facing experience

The system SHALL provide a Streamlit-based vendor-facing interface with a warm medical-aesthetics visual style.

#### Scenario: 首頁呈現醫美展示風格

- GIVEN 使用者開啟首頁
- WHEN 頁面完成載入
- THEN 系統應顯示醫美品牌感的主視覺區塊
- AND 畫面應包含暖色系背景、說明文字與查詢入口
- AND 文案應適合對外展示，不應出現過於原型感的 `demo` 字樣

#### Scenario: 輸入框維持清楚可讀

- GIVEN 使用者聚焦在查詢輸入框
- WHEN 使用者輸入問題
- THEN 輸入中的文字應保持深色且清晰可讀
- AND placeholder 應與實際輸入文字有足夠辨識差異

### Requirement: Secrets-based Supabase connectivity

The system SHALL read Supabase connection settings from Streamlit Secrets or environment variables.

#### Scenario: 以 Streamlit Secrets 取得設定

- GIVEN `st.secrets` 中存在 `SUPABASE_URL` 與 `SUPABASE_KEY`
- WHEN 系統建立 Supabase client
- THEN 系統應使用這兩個值完成連線

#### Scenario: 以環境變數取得設定

- GIVEN `st.secrets` 中未提供設定
- AND 系統環境變數存在 `SUPABASE_URL` 與 `SUPABASE_KEY`
- WHEN 系統建立 Supabase client
- THEN 系統應改用環境變數完成連線

#### Scenario: 缺少必要設定時提示錯誤

- GIVEN `SUPABASE_URL` 或 `SUPABASE_KEY` 缺失
- WHEN 使用者執行查詢
- THEN 系統應顯示缺少哪個設定項目的錯誤訊息

### Requirement: Embedding-based QA retrieval

The system SHALL encode the user query with a multilingual sentence-transformer model and retrieve similar QA entries from Supabase RPC `match_qa`.

#### Scenario: 建立查詢向量

- GIVEN 使用者輸入一段醫美問題
- WHEN 系統準備執行檢索
- THEN 系統應使用 `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- AND 系統應將問題轉成 embedding 向量

#### Scenario: 呼叫 Supabase RPC 查詢

- GIVEN 系統已取得查詢向量
- WHEN 系統執行檢索
- THEN 系統應呼叫 Supabase RPC `match_qa`
- AND 應傳入 `query_embedding`
- AND 應傳入 `match_count`

### Requirement: Adjustable result count

The system SHALL allow the operator to choose how many top matches to show.

#### Scenario: 以側欄調整結果筆數

- GIVEN 使用者位於首頁
- WHEN 使用者調整側欄 slider
- THEN 系統應允許在 `1` 到 `5` 筆之間選擇結果數量
- AND 該值應作為 `match_count` 傳入檢索流程

### Requirement: Search workflow and result presentation

The system SHALL provide a form-based query workflow and show retrieved QA results as styled cards.

#### Scenario: 查詢前的空狀態

- GIVEN 使用者尚未送出查詢
- WHEN 頁面進入查詢區
- THEN 系統應顯示引導性空狀態文案

#### Scenario: 空白查詢不應送出

- GIVEN 使用者未輸入任何內容
- WHEN 使用者按下查詢按鈕
- THEN 系統應顯示請先輸入問題的提示
- AND 系統不應執行 Supabase 查詢

#### Scenario: 顯示查詢結果卡片

- GIVEN 系統成功查到相近 QA
- WHEN 檢索完成
- THEN 系統應顯示成功訊息與結果筆數
- AND 每筆結果應以卡片形式呈現
- AND 卡片應包含問題文字與回答文字

#### Scenario: 顯示相似度資訊

- GIVEN 查詢結果包含 `similarity`
- WHEN 系統渲染結果卡片
- THEN 卡片中應顯示相似度數值

#### Scenario: 查無結果時提示

- GIVEN 系統未找到任何相符資料
- WHEN 檢索完成
- THEN 系統應顯示目前未找到相符結果的提示

### Requirement: Safe text rendering

The system SHALL escape question and answer text before injecting them into HTML-rendered result cards.

#### Scenario: 結果內容含有特殊字元

- GIVEN 問題或答案文字中包含 HTML 特殊字元
- WHEN 系統渲染結果卡片
- THEN 系統應先將文字做 escape
- AND 頁面不應因資料內容破壞排版或插入非預期 HTML

### Requirement: Streamlit Community Cloud deployment compatibility

The system SHALL remain deployable on Streamlit Community Cloud with Python 3.12 and the repository entry point `app.py`.

#### Scenario: 雲端依指定版本建置

- GIVEN Streamlit Community Cloud 讀取此 repo
- WHEN 平台依專案設定建置
- THEN 應使用 `runtime.txt` 指定的 `python-3.12`
- AND 應安裝 `requirements.txt` 中的依賴

#### Scenario: 以 app.py 作為入口

- GIVEN Streamlit Community Cloud 完成建置
- WHEN 應用啟動
- THEN 系統應以 `app.py` 作為入口頁面
- AND 使用者應可直接從公開網址看到查詢介面
