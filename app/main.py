import os
import platform
import time
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI, Response, status
from fastapi.responses import HTMLResponse

# Application Initialization & Metadata
app = FastAPI(
    title="Cloud-Pulse Sentinel",
    description="Telemetry, Health Monitoring, and AWS STS Verification Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

START_TIME = time.time()


# ==============================================================================
# 1. Human Interface (HTML Dashboard)
# ==============================================================================
@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def read_root() -> str:
    """Renders the human-friendly web interface and operational portal."""
    uptime_seconds = int(time.time() - START_TIME)

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cloud-Pulse Sentinel</title>
        <style>
            :root {{
                --bg: #0f172a;
                --surface: #1e293b;
                --border: #334155;
                --text: #f8fafc;
                --muted: #94a3b8;
                --accent: #38bdf8;
                --success: #22c55e;
            }}
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 20px;
            }}
            .card {{
                background-color: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                max-width: 650px;
                width: 100%;
                padding: 32px;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border);
                padding-bottom: 20px;
                margin-bottom: 24px;
            }}
            .title {{
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--text);
            }}
            .badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background-color: rgba(34, 197, 94, 0.15);
                color: var(--success);
                border: 1px solid var(--success);
                padding: 4px 12px;
                border-radius: 9999px;
                font-size: 0.85rem;
                font-weight: 600;
            }}
            .badge-dot {{
                width: 8px;
                height: 8px;
                background-color: var(--success);
                border-radius: 50%;
            }}
            .description {{
                color: var(--muted);
                font-size: 0.95rem;
                line-height: 1.6;
                margin-bottom: 24px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
                margin-bottom: 28px;
            }}
            .stat-box {{
                background-color: rgba(15, 23, 42, 0.6);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 14px;
            }}
            .stat-label {{
                font-size: 0.75rem;
                color: var(--muted);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 4px;
            }}
            .stat-value {{
                font-size: 0.95rem;
                font-weight: 600;
                color: var(--text);
                word-break: break-all;
            }}
            .actions {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }}
            .btn {{
                display: flex;
                align-items: center;
                justify-content: center;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
                padding: 12px 16px;
                border-radius: 8px;
                transition: opacity 0.2s ease;
            }}
            .btn-primary {{
                background-color: var(--accent);
                color: var(--bg);
            }}
            .btn-secondary {{
                background-color: transparent;
                border: 1px solid var(--border);
                color: var(--text);
            }}
            .btn:hover {{
                opacity: 0.9;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <div class="title">Cloud-Pulse Sentinel</div>
                <div class="badge">
                    <span class="badge-dot"></span>
                    ONLINE
                </div>
            </div>
            <p class="description">
                FastAPI telemetry and operational observability microservice configured for dual-deployment:
                active on <strong>Vercel Serverless</strong> edge infrastructure and container-portable for <strong>AWS (ECS / App Runner)</strong>.
            </p>
            <div class="grid">
                <div class="stat-box">
                    <div class="stat-label">Environment Target</div>
                    <div class="stat-value">{os.getenv("APP_ENV", "production")}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Uptime</div>
                    <div class="stat-value">{uptime_seconds}s</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Python Runtime</div>
                    <div class="stat-value">{platform.python_version()}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">AWS Region Config</div>
                    <div class="stat-value">{os.getenv("AWS_DEFAULT_REGION", "us-east-1")}</div>
                </div>
            </div>
            <div class="actions">
                <a href="/docs" class="btn btn-primary">API Documentation (/docs)</a>
                <a href="/health" class="btn btn-secondary">Raw Health JSON (/health)</a>
            </div>
        </div>
    </body>
    </html>
    """


# ==============================================================================
# 2. Machine-Readable API Endpoints (Pre-Interface Functionality)
# ==============================================================================
@app.get("/health", tags=["Observability"])
def health_check() -> Dict[str, Any]:
    """Standard health check endpoint for uptime monitors and load balancers."""
    return {
        "status": "healthy",
        "service": "cloud-pulse",
        "uptime_seconds": int(time.time() - START_TIME),
        "timestamp": int(time.time()),
    }


@app.get("/system", tags=["Observability"])
def system_telemetry() -> Dict[str, Any]:
    """Provides host runtime environment information and OS details."""
    return {
        "environment": os.getenv("APP_ENV", "production"),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "processor": platform.processor() or "cloud-virtualized",
        "serverless_runtime": "VERCEL" if "VERCEL" in os.environ else "STANDALONE",
    }


@app.get("/aws/identity", tags=["AWS Integration"])
def aws_identity_check(response: Response) -> Dict[str, Any]:
    """Validates connectivity with AWS Security Token Service (STS) or mock credentials."""
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    try:
        sts_client = boto3.client("sts", region_name=region)
        caller_identity = sts_client.get_caller_identity()
        return {
            "status": "authenticated",
            "account": caller_identity.get("Account"),
            "arn": caller_identity.get("Arn"),
            "user_id": caller_identity.get("UserId"),
        }
    except (ClientError, BotoCoreError) as err:
        # Graceful degradation: returns simulated identity if offline / mocking
        if os.getenv("AWS_ACCESS_KEY_ID") == "mock_key":
            return {
                "status": "mock_authenticated",
                "account": "123456789012",
                "arn": "arn:aws:iam::123456789012:user/mock-sentinel-runner",
                "user_id": "AIDAMOCKUSERID12345",
            }

        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unauthenticated",
            "error": str(err),
            "region": region,
        }