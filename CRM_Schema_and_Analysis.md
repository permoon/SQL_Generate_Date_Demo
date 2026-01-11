# CRM 分析倉儲 Schema 與分析應用指南

本文件定義了 CRM 分析倉儲的五大核心表格 Schema，並針對各個表格與欄位說明其分析應用價值。

## 1. 交易明細 (transactions)

這是最核心的事實表 (Fact Table)，紀錄每一筆交易的詳細資訊。

### Schema 設計 (SQLite)

```sql
CREATE TABLE transaction_details (
    transaction_id TEXT NOT NULL,         -- 交易單號 (Primary Key Part 1)
    line_item_id INTEGER NOT NULL,        -- 交易項次 (Primary Key Part 2)
    transaction_date TEXT NOT NULL,       -- 交易時間 (ISO8601: YYYY-MM-DD HH:MM:SS)
    member_id TEXT,                       -- 會員 ID (可為 Null，代表非會員交易)
    product_id TEXT NOT NULL,             -- 產品 ID
    channel_id TEXT NOT NULL,             -- 通路 ID
    quantity INTEGER NOT NULL DEFAULT 1,  -- 數量
    unit_price REAL NOT NULL,             -- 單價 (原價)
    sales_amount REAL NOT NULL,           -- 銷售額 (quantity * unit_price)
    discount_amount REAL DEFAULT 0,       -- 折扣金額
    net_amount REAL NOT NULL,             -- 淨銷額 (sales_amount - discount_amount)
    payment_method TEXT,                  -- 付款方式 (Cash, Credit Card, LinePay...)
    PRIMARY KEY (transaction_id, line_item_id)
);
```

### 📊 可進行的分析應用

1.  **RFM 模型分析**: 利用 `member_id`, `transaction_date`, `net_amount` 計算：
    *   **Recency (R)**: 最近一次消費時間。
    *   **Frequency (F)**: 消費頻率 (一段時間內的交易次數)。
    *   **Monetary (M)**: 消費總金額 (貢獻度)。
2.  **購物籃分析 (Market Basket Analysis)**:
    *   利用 `transaction_id` 與 `product_id` 分析哪些產品常被一起購買 (關聯規則)。
3.  **客單價分析 (AOV - Average Order Value)**:
    *   `SUM(net_amount) / COUNT(DISTINCT transaction_id)`。
4.  **會員 vs 非會員貢獻佔比**:
    *   分析 `member_id` 有值與 Null 的銷售額比例。
5.  **支付方式偏好**:
    *   分析 `payment_method` 的分佈，優化結帳流程或合作優惠。

---

## 2. 會員表 (members)

紀錄會員的靜態屬性與當前狀態。

### Schema 設計 (SQLite)

```sql
CREATE TABLE members (
    member_id TEXT PRIMARY KEY,           -- 會員 ID
    name TEXT,                            -- 姓名
    gender TEXT,                          -- 性別 (M/F/U)
    birthday TEXT,                        -- 生日 (YYYY-MM-DD)
    phone_number TEXT,                    -- 手機
    email TEXT,                           -- Email
    city TEXT,                            -- 居住縣市
    district TEXT,                        -- 居住區域
    register_date TEXT NOT NULL,          -- 註冊日期
    register_channel_id TEXT,             -- 註冊來源通路
    membership_level TEXT,                -- 會員等級 (普卡/銀卡/金卡)
    opt_in_edm INTEGER DEFAULT 0,         -- 是否訂閱 EDM (1=Yes, 0=No)
    opt_in_sms INTEGER DEFAULT 0,         -- 是否訂閱 SMS
    curr_points INTEGER DEFAULT 0         -- 當前點數
);
```

### 📊 可進行的分析應用

1.  **會員輪廓分析 (Demographics)**:
    *   分析會員的性別、年齡 (由 `birthday` 計算)、居住地分佈。
2.  **會員生命週期分析 (Cohort Analysis)**:
    *   利用 `register_date` 將會員分群 (例如：2023 Q1 加入的會員)，觀察其後續的留存率與終身價值 (LTV)。
3.  **會員等級分佈與遷徙**:
    *   監控各等級 (`membership_level`) 人數變化，分析升降級趨勢。
4.  **溝通渠道觸及率**:
    *   統計 `opt_in_edm`, `opt_in_sms` 的比例，評估可觸及的會員池大小。

---

## 3. 產品表 (products)

紀錄產品的階層分類與屬性。

### Schema 設計 (SQLite)

```sql
CREATE TABLE products (
    product_id TEXT PRIMARY KEY,          -- 產品 ID
    product_name TEXT NOT NULL,           -- 產品名稱
    category_l1 TEXT,                     -- 大分類 (e.g. 服飾)
    category_l2 TEXT,                     -- 中分類 (e.g. 上衣)
    category_l3 TEXT,                     -- 小分類 (e.g. T-shirt)
    brand TEXT,                           -- 品牌
    cost REAL,                            -- 成本 (用於計算毛利)
    list_price REAL,                      -- 定價
    launch_date TEXT,                     -- 上市日期
    is_active INTEGER DEFAULT 1           -- 是否上架中
);
```

### 📊 可進行的分析應用

1.  **產品銷售排行與帕累托分析 (80/20 法則)**:
    *   識別貢獻 80% 營收的前 20% 關鍵產品 (`SKU`)。
2.  **品類滲透率**:
    *   分析不同 `category_l1` / `category_l2` 在會員中的購買比例。
3.  **毛利率分析**:
    *   結合交易表的 `net_amount` 與此表的 `cost` 計算各產品或品類的真實獲利能力。
4.  **新品表現追蹤**:
    *   利用 `launch_date` 追蹤新品上市後 30/60/90 天的銷售曲線。

---

## 4. 通路表 (channels)

紀錄銷售渠道資訊，區分線上與線下。

### Schema 設計 (SQLite)

```sql
CREATE TABLE channels (
    channel_id TEXT PRIMARY KEY,          -- 通路 ID
    channel_name TEXT NOT NULL,           -- 通路名稱
    channel_type TEXT,                    -- 通路類型 (官網/APP/門市/Outlet)
    region TEXT,                          -- 區域 (北/中/南)
    store_area REAL,                      -- 坪數 (用於坪效分析)
    open_date TEXT,                       -- 開店日
    close_date TEXT                       -- 關店日 (Null 代表營業中)
);
```

### 📊 可進行的分析應用

1.  **通路績效分析**:
    *   比較不同 `channel_type` (線上 vs 線下) 的業績佔比與成長率。
2.  **O2O (Online-to-Offline) 分析**:
    *   結合交易表，分析是否有會員在 `官網` 註冊但在 `門市` 消費 (跨通路行為)。
3.  **單店坪效分析**:
    *   利用 `store_area` 計算實體門市的單位面積產值 (Sales per Area)。
4.  **區域銷售熱圖**:
    *   依據 `region` 分析地理區域的銷售強弱趨勢。

---

## 5. 行銷活動發送紀錄 (campaign_logs) & 活動主檔 (campaigns)

為了支援更細緻的會員級別分析，我们将行銷成效拆分為「活動主檔」與「發送紀錄明細」。

### Schema 設計 (SQLite)

**5-A. 活動主檔 (campaigns)**
```sql
CREATE TABLE campaigns (
    campaign_id TEXT PRIMARY KEY,         -- 活動 ID
    campaign_name TEXT NOT NULL,          -- 活動名稱
    channel_type TEXT NOT NULL,           -- 渠道 (EDM/SMS/LINE)
    start_date TEXT,                      -- 活動開始/發送日
    end_date TEXT,                        -- 活動結束日 (若有)
    cost_per_send REAL                    -- 單次發送成本
);
```

**5-B. 發送紀錄 (campaign_logs)**
*這張表是核心，每位會員針對每個活動會有一筆紀錄*
```sql
CREATE TABLE campaign_logs (
    log_id TEXT PRIMARY KEY,              -- 流水號
    campaign_id TEXT NOT NULL,            -- 關聯活動
    member_id TEXT NOT NULL,              -- 關聯會員
    send_time TEXT NOT NULL,              -- 發送時間
    is_opened INTEGER DEFAULT 0,          -- 是否開啟 (0/1)
    is_clicked INTEGER DEFAULT 0,         -- 是否點擊 (0/1)
    is_converted INTEGER DEFAULT 0,       -- 是否轉換 (0/1)
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);
```

### 📊 可進行的分析應用

1.  **個人化行銷反應分析**:
    *   分析特定會員 (`member_id`) 對哪種通路 (`channel_type`) 的開信率 (`is_opened`) 最高，以決定未來的溝通渠道。
2.  **精準名單成效追蹤**:
    *   分析某次活動的「點擊會員」後來是否有實際消費 (需與 `transaction_details` join)。
3.  **溝通疲勞度分析**:
    *   計算每位會員每月收到的訊息量 (`COUNT(log_id)`)，觀察發送頻率是否過高導致開信率下降。
4.  **歸因模型 (Attribution)**:
    *   利用 `send_time` 與交易時間的比對，計算更精確的轉換率 (e.g. 收到簡訊後 24 小時內的購買)。

---

## 總結：跨表綜合分析 (Advanced)

將上述表格關聯 (Join) 後，可回答更深度的商業問題：

*   **高價值會員偏好**: 篩選 RFM 最高的 5% 會員，分析他們最愛買哪些品類 (`products`)？最常去哪些通路 (`channels`)？
*   **非活躍會員喚醒**: 找出 R (Recency) > 180 天的沉睡會員，分析他們過去是否對 SMS (`campaign_performance`) 反應較好？
*   **新品推廣策略**: 分析曾購買同類競品的會員，針對該群體發送 LINE 推播，並追蹤轉換成效。
