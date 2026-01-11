import sqlite3
import random
import datetime
import math
import os
import uuid

# Configuration
DB_PATH = 'c:/My_Repo/SQL_TEST/crm_data.db'
NUM_MEMBERS = 10000
NUM_PRODUCTS = 50
NUM_CHANNELS = 12  # 1 EC, 11 Retail
MIN_ORDERS = 1
MAX_ORDERS = 12

# Delete existing db if exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ---------------------------------------------------------
# 1. Create Tables
# ---------------------------------------------------------
ddl_script = """
CREATE TABLE transaction_details (
    transaction_id TEXT NOT NULL,
    line_item_id INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    member_id TEXT,
    product_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price REAL NOT NULL,
    sales_amount REAL NOT NULL,
    discount_amount REAL DEFAULT 0,
    net_amount REAL NOT NULL,
    payment_method TEXT,
    PRIMARY KEY (transaction_id, line_item_id)
);

CREATE TABLE members (
    member_id TEXT PRIMARY KEY,
    name TEXT,
    gender TEXT,
    birthday TEXT,
    phone_number TEXT,
    email TEXT,
    city TEXT,
    district TEXT,
    register_date TEXT NOT NULL,
    register_channel_id TEXT,
    membership_level TEXT,
    opt_in_edm INTEGER DEFAULT 0,
    opt_in_sms INTEGER DEFAULT 0,
    curr_points INTEGER DEFAULT 0
);

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category_l1 TEXT,
    category_l2 TEXT,
    category_l3 TEXT,
    brand TEXT,
    cost REAL,
    list_price REAL,
    launch_date TEXT,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE channels (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT NOT NULL,
    channel_type TEXT,
    region TEXT,
    store_area REAL,
    open_date TEXT,
    close_date TEXT
);

CREATE TABLE campaigns (
    campaign_id TEXT PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    channel_type TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    cost_per_send REAL
);

CREATE TABLE campaign_logs (
    log_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    member_id TEXT NOT NULL,
    send_time TEXT NOT NULL,
    is_opened INTEGER DEFAULT 0,
    is_clicked INTEGER DEFAULT 0,
    is_converted INTEGER DEFAULT 0,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);
"""
cursor.executescript(ddl_script)
conn.commit()
print("Tables created.")

# ---------------------------------------------------------
# 2. Helpers
# ---------------------------------------------------------
def random_date(start, end):
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())))

start_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2023, 12, 31)
today = datetime.datetime.now()

# ---------------------------------------------------------
# 3. Generate Channels
# ---------------------------------------------------------
# 1 EC, 11 Retail
channels = []
# EC
channels.append({
    'id': 'CH_WEB', 'name': 'Official Website', 'type': 'Online', 'region': 'Online', 'area': 0
})
# Retail
regions = ['North'] * 5 + ['Central'] * 3 + ['South'] * 3
for i, reg in enumerate(regions):
    channels.append({
        'id': f'CH_S{i+1:03d}', 
        'name': f'Store {reg} {i+1}', 
        'type': 'Offline', 
        'region': reg, 
        'area': random.randint(30, 150)
    })

for c in channels:
    cursor.execute("INSERT INTO channels VALUES (?,?,?,?,?,?,?)", 
                   (c['id'], c['name'], c['type'], c['region'], c['area'], '2020-01-01', None))
conn.commit()
print("Channels generated.")

# ---------------------------------------------------------
# 4. Generate Products
# ---------------------------------------------------------
# 5 Categories
categories = {
    'Apparel': ['T-Shirt', 'Jeans', 'Jacket', 'Shirt'],
    'Footwear': ['Sneakers', 'Boots', 'Sandals'],
    'Accessories': ['Bag', 'Hat', 'Watch', 'Belt'],
    'Home': ['Towel', 'Cushion', 'Mug'],
    'Sports': ['Yoga Mat', 'Dumbbell', 'Water Bottle']
}
products = []
p_counter = 1
for cat, subcats in categories.items():
    for sub in subcats:
        # Generate 3-5 products per subcat
        for _ in range(random.randint(3, 5)):
            if len(products) >= NUM_PRODUCTS and cat=='Sports': break # Cap roughly
            
            price_base = random.randint(50, 500) * 10
            cost = price_base * random.uniform(0.3, 0.6)
            products.append({
                'id': f'P{p_counter:04d}',
                'name': f'{sub} {chr(random.randint(65,90))}{random.randint(100,999)}',
                'cat1': cat,
                'cat2': sub,
                'cat3': 'Standard',
                'brand': 'MyBrand',
                'cost': int(cost),
                'price': price_base,
                'launch': random_date(datetime.datetime(2022,1,1), datetime.datetime(2023,6,1)).strftime('%Y-%m-%d')
            })
            p_counter += 1
            
# Fill up if short
while len(products) < NUM_PRODUCTS:
    products.append({
        'id': f'P{p_counter:04d}',
        'name': f'Generic Item {p_counter}',
        'cat1': 'Others',
        'cat2': 'General',
        'cat3': 'Standard',
        'brand': 'MyBrand',
        'cost': 100,
        'price': 200,
        'launch': '2023-01-01'
    })
    p_counter += 1

for p in products:
    cursor.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?)", 
                   (p['id'], p['name'], p['cat1'], p['cat2'], p['cat3'], p['brand'], p['cost'], p['price'], p['launch'], 1))
conn.commit()
print(f"Products generated: {len(products)}")

# ---------------------------------------------------------
# 5. Generate Members
# ---------------------------------------------------------
# Non-uniform distribution logic
# Gender: 70% Female, 30% Male
# Age: Skewed to 25-40
members = []
cities = ['Taipei'] * 50 + ['New Taipei'] * 30 + ['Taichung'] * 10 + ['Kaohsiung'] * 10
districts = ['East', 'West', 'North', 'South']

for i in range(NUM_MEMBERS):
    mid = f'M{i+1:08d}'
    gender = 'F' if random.random() < 0.7 else 'M'
    
    # Age skew
    age_seed = random.gammavariate(7.5, 1.0) # shape, scale -> peak around 7.5
    # Mapping roughly to 18-60 range
    age = 18 + int(age_seed * 4) 
    if age > 80: age = 80
    
    birth_year = today.year - age
    birthday = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    
    reg_date = random_date(datetime.datetime(2021,1,1), today).strftime('%Y-%m-%d')
    city = random.choice(cities)
    
    members.append({
        'id': mid,
        'gender': gender,
        'birthday': birthday,
        'city': city,
        'reg': reg_date,
        'level': 'VIP' if random.random() < 0.1 else 'Standard'
    })

    cursor.execute("INSERT INTO members (member_id, name, gender, birthday, city, register_date, membership_level, opt_in_edm, opt_in_sms) VALUES (?,?,?,?,?,?,?,?,?)",
                   (mid, f'Member_{i}', gender, birthday, city, reg_date, 
                    'VIP' if random.random() < 0.1 else 'Standard',
                    1 if random.random() < 0.6 else 0,
                    1 if random.random() < 0.4 else 0
                   ))

conn.commit()
print("Members generated.")

# ---------------------------------------------------------
# 6. Generate Transactions
# ---------------------------------------------------------
# Gamma distribution for # of orders per member
# Valid range 1-12
tx_list = []

# Pre-fetch product prices for lookup
prod_lookup = {p['id']: p['price'] for p in products}
prod_keys = list(prod_lookup.keys())

# Weight products for non-uniform sales
# 20% of products get 80% of weight
prod_weights = [10] * (len(prod_keys)//5) + [1] * (len(prod_keys) - len(prod_keys)//5)
random.shuffle(prod_weights) # Shuffle so it's not just the first ones

# Channel weights (EC is high volume)
# CH_WEB index 0
chan_ids = [c['id'] for c in channels]
chan_weights = [50] + [5] * (len(chan_ids)-1) # Web is 10x more likely than single store

tx_id_counter = 1

for m in members:
    # Gamma for order count: shape=2, scale=2 => mean=4
    # We want 1-12
    val = random.gammavariate(2.0, 2.0)
    num_orders = int(val)
    if num_orders < 1: num_orders = 1
    if num_orders > 12: num_orders = 12
    
    # For each order
    for _ in range(num_orders):
        tid = f'TX{tx_id_counter:09d}'
        tx_id_counter += 1
        
        # Date logic: more recent is more likely? Or seasonality?
        # Let's do simple seasonality (more in Winter)
        tx_dt = random_date(datetime.datetime(2023,1,1), datetime.datetime(2023,12,31))
        # Simple skew: if month is 11 or 12, keep, else 50% chance to re-roll to 11/12
        if tx_dt.month not in [11, 12] and random.random() < 0.3:
             tx_dt = random_date(datetime.datetime(2023,11,1), datetime.datetime(2023,12,31))
        
        tx_date_str = tx_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Select Channel
        # Weighted selection
        chid = random.choices(chan_ids, weights=chan_weights, k=1)[0]
        
        # Line Items (1-5 items per order)
        num_items = random.randint(1, 5)
        
        # Select products
        chosen_prods = random.choices(prod_keys, weights=prod_weights, k=num_items)
        
        for idx, pid in enumerate(chosen_prods):
            orig_price = prod_lookup[pid]
            qty = 1 # mostly 1
            if random.random() < 0.1: qty = 2
            
            sales_amt = orig_price * qty
            # Random discount
            disc = 0
            if random.random() < 0.2:
                disc = sales_amt * 0.1 # 10% off
            
            net = sales_amt - disc
            
            cursor.execute("""
                INSERT INTO transaction_details 
                (transaction_id, line_item_id, transaction_date, member_id, product_id, channel_id, quantity, unit_price, sales_amount, discount_amount, net_amount, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tid, idx+1, tx_date_str, m['id'], pid, chid, qty, orig_price, sales_amt, disc, net, 'CreditCard'))
            
    if tx_id_counter % 1000 == 0:
        conn.commit()
        print(f"Generated transactions for member count: {m['id']}...")

conn.commit()
print("Transactions generated.")

# ---------------------------------------------------------
# 7. Campaign Logs (Granular)
# ---------------------------------------------------------
# 10 Campaigns
# Create Campaigns
camp_names = ['New Year Sale', 'Spring Collection', 'Member Day', 'Black Friday', 'Cyber Monday', 
              'Summer Cool', 'Winter Warm', 'Valentine', 'Mother Day', '11.11']
campaigns = []
for i, cn in enumerate(camp_names):
    cid = f'CMP{i+1:03d}'
    channel = random.choice(['EDM', 'SMS', 'LINE'])
    cost_per = 0.5 if channel == 'EDM' else 1.5
    start_d = random_date(datetime.datetime(2023,1,1), datetime.datetime(2023,12,1)).strftime('%Y-%m-%d')
    
    cursor.execute("INSERT INTO campaigns VALUES (?,?,?,?,?,?)", 
                   (cid, cn, channel, start_d, None, cost_per))
    
    campaigns.append({'id': cid, 'chan': channel, 'date': start_d})

conn.commit()
print("Campaign master generated.")

# Generate Logs
# For each campaign, select random subset of members (target audience)
# e.g. 20% - 50% of members
log_counter = 1
for cmp in campaigns:
    # Target audience size
    target_size = int(NUM_MEMBERS * random.uniform(0.2, 0.5))
    target_members = random.sample(members, target_size)
    
    # Typical rates
    open_rate = 0.3 if cmp['chan'] == 'EDM' else 0.8 # SMS/LINE high open
    click_rate = 0.1 if cmp['chan'] == 'EDM' else 0.15
    conv_rate = 0.05
    
    batch_data = []
    
    for tm in target_members:
        is_opened = 1 if random.random() < open_rate else 0
        is_clicked = 0
        is_converted = 0
        
        if is_opened:
            is_clicked = 1 if random.random() < click_rate else 0
        if is_clicked:
            is_converted = 1 if random.random() < conv_rate else 0
            
        # Send time = campaign date + random minutes
        # We need to parse date string back to object or just append time
        # string concat is easier
        send_time = f"{cmp['date']} {random.randint(9,20):02d}:{random.randint(0,59):02d}:00"
        
        # log_id = uuid? or int? Let's use int-str
        lid = f"LOG{log_counter:09d}"
        log_counter += 1
        
        batch_data.append((lid, cmp['id'], tm['id'], send_time, is_opened, is_clicked, is_converted))
        
        if len(batch_data) >= 5000:
            cursor.executemany("INSERT INTO campaign_logs VALUES (?,?,?,?,?,?,?)", batch_data)
            batch_data = []
            
    if batch_data:
        cursor.executemany("INSERT INTO campaign_logs VALUES (?,?,?,?,?,?,?)", batch_data)
        
    print(f"Generated logs for campaign {cmp['id']}: {target_size} sends.")

conn.commit()
conn.close()
print(f"Database generated at: {DB_PATH}")

