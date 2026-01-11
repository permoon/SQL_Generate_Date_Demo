import markdown
import os

# Configuration
INPUT_FILE = 'c:/My_Repo/SQL_TEST/AI_CRM_Collaboration_Guide.md'
OUTPUT_FILE = 'c:/My_Repo/SQL_TEST/AI_CRM_Collaboration_Guide_Compiled.html'

# CSS Style (Bootstrap + Custom)
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI CRM Collaboration Guide</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; color: #333; padding: 20px; }
        .container { max-width: 900px; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
        h1, h2, h3 { color: #2c3e50; margin-top: 1.5em; }
        h1 { border-bottom: 3px solid #3498db; padding-bottom: 15px; margin-top: 0; }
        h2 { border-left: 5px solid #3498db; padding-left: 15px; background: #f1f8fe; padding-top: 10px; padding-bottom: 10px; border-radius: 0 5px 5px 0; }
        code { background-color: #f1f2f6; padding: 2px 5px; border-radius: 3px; color: #e74c3c; font-family: 'Consolas', monospace; }
        pre { background-color: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 5px; position: relative; }
        blockquote { border-left: 4px solid #f1c40f; background: #fffcf0; padding: 15px; margin: 20px 0; border-radius: 3px; }
        table { width: 100%; margin-bottom: 1rem; color: #212529; border-collapse: collapse; }
        th, td { padding: 0.75rem; vertical-align: top; border-top: 1px solid #dee2e6; }
        th { background-color: #2c3e50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        {{CONTENT}}
    </div>
</body>
</html>
"""

def compile_markdown():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file not found: {INPUT_FILE}")
        return

    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert to HTML
    # extensions=['extra'] enables tables, fenced code blocks, etc.
    html_body = markdown.markdown(text, extensions=['extra', 'toc', 'tables', 'fenced_code'])

    # Inject into template
    final_html = HTML_TEMPLATE.replace('{{CONTENT}}', html_body)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"Successfully compiled to: {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        compile_markdown()
    except ImportError:
        print("Error: The 'markdown' library is not installed.")
        print("Please run: pip install markdown")
    except Exception as e:
        print(f"An error occurred: {e}")
