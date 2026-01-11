import sqlite3
import json
import os
from collections import Counter

# Configuration
DB_PATH = 'c:/My_Repo/SQL_TEST/crm_data.db'
REPORT_PATH = 'c:/My_Repo/SQL_TEST/crm_eda_report.html'

def get_table_data(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    col_names = [c[1] for c in columns_info]
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    return col_names, rows

def analyze_data(col_names, rows):
    stats = {}
    distributions = {}
    
    # Transpose rows to columns for analysis
    cols_data = list(zip(*rows)) if rows else []
    
    for i, col_name in enumerate(col_names):
        if not cols_data:
            stats[col_name] = {"count": 0}
            continue
            
        data = cols_data[i]
        clean_data = [x for x in data if x is not None]
        
        # Basic Stats
        col_stats = {
            "count": len(data),
            "missing": len(data) - len(clean_data),
            "unique": len(set(clean_data))
        }
        
        # Type inference (simple)
        is_numeric = all(isinstance(x, (int, float)) for x in clean_data[:100]) if clean_data else False
        
        if is_numeric and clean_data:
            col_stats['min'] = min(clean_data)
            col_stats['max'] = max(clean_data)
            col_stats['avg'] = sum(clean_data) / len(clean_data)
            
            # Histogram-ish data for chart
            # Simple binning
            min_val = min(clean_data)
            max_val = max(clean_data)
            range_val = max_val - min_val
            if range_val == 0:
                distributions[col_name] = {str(min_val): len(clean_data)}
            else:
                bins = 10
                step = range_val / bins
                hist = [0] * bins
                labels = []
                for b in range(bins):
                    low = min_val + b * step
                    high = low + step
                    labels.append(f"{low:.1f}-{high:.1f}")
                
                for val in clean_data:
                    idx = int((val - min_val) / step)
                    if idx >= bins: idx = bins - 1
                    hist[idx] += 1
                
                distributions[col_name] = dict(zip(labels, hist))
                
        else:
            # Categorical - Top 10
            counts = Counter(clean_data)
            top_10 = dict(counts.most_common(10))
            distributions[col_name] = top_10
            
        stats[col_name] = col_stats
        
    return stats, distributions

def generate_html(tables_analysis):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CRM Data EDA Report</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { padding: 20px; font-family: sans-serif; background-color: #f8f9fa; }
            .card { margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .chart-container { position: relative; height: 300px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center mb-5">CRM Database Exploratory Data Analysis</h1>
    """
    
    chart_scripts = []
    chart_id = 0
    
    for table_name, (stats, dists, sample_cols, sample_rows) in tables_analysis.items():
        html += f"""
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h2 class="h4 mb-0">{table_name}</h2>
            </div>
            <div class="card-body">
                <h5 class="card-title">Sample Data</h5>
                <div class="table-responsive mb-4">
                    <table class="table table-sm table-bordered">
                        <thead><tr>{''.join(f'<th>{c}</th>' for c in sample_cols)}</tr></thead>
                        <tbody>
                            {''.join('<tr>' + ''.join(f'<td>{str(x)[:50]}</td>' for x in row) + '</tr>' for row in sample_rows)}
                        </tbody>
                    </table>
                </div>
                
                <h5 class="card-title">Field Statistics</h5>
                <div class="table-responsive mb-4">
                    <table class="table table-striped table-sm">
                        <thead><tr><th>Field</th><th>Count</th><th>Missing</th><th>Unique</th><th>Min</th><th>Max</th><th>Avg</th></tr></thead>
                        <tbody>
        """
        
        for col, s in stats.items():
            html += f"""
            <tr>
                <td>{col}</td>
                <td>{s['count']}</td>
                <td>{s['missing']}</td>
                <td>{s['unique']}</td>
                <td>{s.get('min', '-')}</td>
                <td>{s.get('max', '-')}</td>
                <td>{f"{s.get('avg', 0):.2f}" if 'avg' in s else '-'}</td>
            </tr>
            """
            
        html += """
                        </tbody>
                    </table>
                </div>
                
                <h5 class="card-title">Distributions (Top Fields)</h5>
                <div class="row">
        """
        
        for col, data in dists.items():
            # Skip if unique count is too high (like IDs) unless it's numeric binning
            if stats[col]['unique'] > 50 and 'min' not in stats[col]:
                 continue
                 
            c_id = f"chart_{chart_id}"
            chart_id += 1
            
            html += f"""
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h6>{col}</h6>
                        <div class="chart-container">
                            <canvas id="{c_id}"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            """
            
            labels = list(data.keys())
            values = list(data.values())
            chart_type = 'bar'
            
            chart_scripts.append(f"""
            new Chart(document.getElementById('{c_id}'), {{
                type: '{chart_type}',
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: [{{
                        label: 'Count',
                        data: {json.dumps(values)},
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ y: {{ beginAtZero: true }} }}
                }}
            }});
            """)
            
        html += "</div></div></div>"
        
    html += f"""
        </div>
        <script>
            {''.join(chart_scripts)}
        </script>
    </body>
    </html>
    """
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Report generated at {REPORT_PATH}")

# Main execution
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = ['members', 'products', 'channels', 'campaigns', 'campaign_logs', 'transaction_details']
analysis_results = {}

for t in tables:
    print(f"Processing {t}...")
    cols, rows = get_table_data(cursor, t)
    stats, dists = analyze_data(cols, rows)
    sample_rows = rows[:5]
    analysis_results[t] = (stats, dists, cols, sample_rows)

generate_html(analysis_results)
conn.close()
