from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="Cloud-Pulse Sentinel",
    description="Telemetry, Health, and AWS STS Verification Service",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cloud-Pulse Sentinel</title>
        <style>
            :root {
                --bg: #0f172a;
                --card-bg: #1e293b;
                --text: #f8fafc;
                --muted: #94a3b8;
                --primary: #38bdf8;
                --success: #22c55e;
                --border: #334155;
            }
            body {
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
            }
            .container {
                width: 90%;
                max-width: 600px;
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 32px;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            }
            .header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-bottom: 1px solid var(--border);
                padding-bottom: 16px;
                margin-bottom: 24px;
            }
            .badge {
                background: rgba(34, 197, 94, 0.15);
                color: var(--success);
                border: 1px solid var(--success);
                padding: 4px 12px;
                border-radius: 9999px;
                font-size: 0.85rem;
                font-weight: 600;
            }
            .links {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin-top: 24px;
            }
            .btn {
                display: block;
                text-align: center;
                text-decoration: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: 500;
                transition: background 0.2s;
            }
            .btn-primary {
                background: var(--primary);
                color: var(--bg);
            }
            .btn-secondary {
                background: transparent;
                border: 1px solid var(--border);
                color: var(--text);
            }
            .btn:hover { opacity: 0.9; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Cloud-Pulse Sentinel</h2>
                <span class="badge">Online</span>
            </div>
            <p style="color: var(--muted); line-height: 1.5;">
                FastAPI telemetry and AWS compatibility monitoring service active on Vercel Serverless Edge runtime.
            </p>
            <div class="links">
                <a href="/docs" class="btn btn-primary">Interactive Docs (/docs)</a>
                <a href="/health" class="btn btn-secondary">Health Check (/health)</a>
            </div>
        </div>
    </body>
    </html>
    """