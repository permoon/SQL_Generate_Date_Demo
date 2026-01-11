# CRM Data Warehouse Project

本專案旨在演示如何利用 AI 協作，從無到有建立一個 CRM 分析用的資料倉儲 (SQLite)，包含 Schema 設計、假資料生成、以及自動化分析報告。

## 📂 檔案清單說明

以下是本專案資料夾 (`c:\My_Repo\SQL_TEST\`) 內的檔案用途說明：

### 📘 文件與指南 (Documentation)

*   **`AI_CRM_Collaboration_Guide.md`**
    *   **用途**：操作指南的原始 Markdown 文件。
    *   **內容**：同上，適合在編輯器中查看或修改。

*   **`CRM_Schema_and_Analysis.md`**
    *   **用途**：資料庫架構定義與分析字典。
    *   **內容**：定義 5 張核心表格 (會員、交易、行銷等) 的 Schema，以及相關的商業分析指標 (如 RFM、LTV)。

### 💾 資料庫與生成工具 (Data & Scripts)

*   **`crm_data.db`**
    *   **用途**：SQLite 資料庫檔案 (最終產出物)。
    *   **內容**：包含 10,000 筆會員、數萬筆交易紀錄、以及細緻的行銷活動發送紀錄。

*   **`generate_crm_data.py`**
    *   **用途**：產生測試資料的 Python 腳本。
    *   **邏輯**：使用 Gamma 分配模擬交易頻率，並設定了特定的產品熱銷權重與季節性，以確保資料具有分析價值 (非均勻分佈)。

### 📊 分析報告 (EDA)

*   **`crm_eda_report.html`**
    *   **用途**：自動生成的探索性資料分析報告。
    *   **內容**：包含各資料表的欄位統計 (缺失值、分佈) 以及視覺化圖表 (Histogram, Bar Chart)。

*   **`generate_eda_report.py`**
    *   **用途**：產出 EDA 報告的 Python 腳本。
    *   **技術**：讀取 SQLite 資料，並生成嵌入 Chart.js 的 HTML 檔案。

### 🛠️ 輔助工具 (Utilities)

*   **`convert_md_to_html.py`**
    *   **用途**：Markdown 轉 HTML 工具。
    *   **說明**：可以將 `.md` 文件編譯成帶有樣式的 `.html` 文件。需要安裝 python `markdown` 套件。

---

## 🚀 快速開始

1.  **檢視資料**：使用 DB Browser for SQLite 打開 `crm_data.db`。
2.  **檢視報告**：直接用瀏覽器打開 `crm_eda_report.html` 了解資料分佈。
3.  **閱讀指南**：打開 `AI_CRM_Collaboration_Guide.html` 學習如何複製此工作流。
