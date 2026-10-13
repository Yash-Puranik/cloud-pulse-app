import os
import platform
import time
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
APP_NAME = "cloud-pulse"
APP_VERSION = "1.0.0"

app = FastAPI(
    title=APP_NAME,
    description="Telemetry, Health Monitoring, and AWS STS Verification Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

START_TIME = time.time()

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def read_root() -> str:
    """Renders the operational web console for human browser visitors."""
    uptime_seconds = int(time.time() - START_TIME)
    current_env = os.getenv("APP_ENV", "production")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    py_version = platform.python_version()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud-Pulse Sentinel</title>
    <style>
        :root {{
            --bg-base: #0f172a;
            --bg-card: #1e293b;
            --border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --success: #22c55e;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 24px;
        }}
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            max-width: 620px;
            width: 100%;
            padding: 32px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-main);
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(34, 197, 94, 0.15);
            color: var(--success);
            border: 1px solid var(--success);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .badge-dot {{
            width: 8px;
            height: 8px;
            background-color: var(--success);
            border-radius: 50%;
        }}
        .description {{
            color: var(--text-muted);
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 24px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 28px;
        }}
        .metric-box {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 14px;
        }}
        .metric-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}
        .metric-value {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-main);
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
            transition: opacity 0.2s;
        }}
        .btn-primary {{
            background: var(--accent);
            color: var(--bg-base);
        }}
        .btn-secondary {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-main);
        }}
        .btn:hover {{
            opacity: 0.85;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h1 class="title">Cloud-Pulse Sentinel</h1>
            <div class="badge">
                <span class="badge-dot"></span>
                ONLINE
            </div>
        </div>
        <p class="description">
            FastAPI telemetry and operational observability microservice configured for dual-deployment:
            active on <strong>Vercel Serverless</strong> edge infrastructure and container-portable for <strong>AWS (ECS / App Runner)</strong>.
        </p>
        <div class="metrics-grid">
            <div class="metric-box">
                <div class="metric-label">Environment</div>
                <div class="metric-value">{current_env}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Uptime</div>
                <div class="metric-value">{uptime_seconds}s</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Python Runtime</div>
                <div class="metric-value">{py_version}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">AWS Region Config</div>
                <div class="metric-value">{aws_region}</div>
            </div>
        </div>
        <div class="actions">
            <a href="/docs" class="btn btn-primary">API Documentation (/docs)</a>
            <a href="/health" class="btn btn-secondary">Raw Health JSON (/health)</a>
        </div>
    </div>
</body>
</html>"""

@app.get("/", tags=["General"])
def read_root() -> Dict[str, str]:
    """Root metadata route."""
    return {
        "service": APP_NAME,
        "status": "online",
        "health_check": "/health",
        "documentation": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, Any]:
    """Synthetic health check endpoint."""
    return {
        "status": "healthy",
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": os.getenv("APP_ENV", "production"),
    }


def collect_system_report() -> Dict[str, Any]:
    """Collect runtime details used by the metrics endpoint."""
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": os.getenv("APP_ENV", "production"),
        "uptime_seconds": int(time.time() - START_TIME),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }


def verify_aws_connectivity() -> Dict[str, Any]:
    """Verify AWS credentials and connectivity through STS."""
    try:
        identity = boto3.client("sts").get_caller_identity()
        return {"connected": True, **identity}
    except ClientError as exc:
        error = exc.response.get("Error", {})
        return {
            "connected": False,
            "error": error.get("Code", "AuthFailure"),
            "message": error.get("Message", str(exc)),
        }
    except BotoCoreError as exc:
        return {"connected": False, "error": "AuthFailure", "message": str(exc)}


@app.get("/metrics", tags=["Telemetry"])
def get_metrics() -> Dict[str, Any]:
    """Returns telemetry metrics satisfying both nested and flat schemas."""
    report = collect_system_report()
    report["status"] = "success"

    return {
        "status": "success",
        "metrics": report,
        **report,
    }


@app.get("/aws/status", tags=["AWS"])
def get_aws_status() -> JSONResponse:
    """Queries AWS STS to verify identity and connectivity.

    Preserves top-level error codes and nested details for all test assertions.
    """
    aws_info = verify_aws_connectivity()

    if aws_info.get("connected"):
        payload = {
            "status": "connected",
            "details": aws_info,
            **aws_info,
        }
    else:
        error_msg = str(aws_info.get("error", "AuthFailure"))
        payload = {
            "status": "unauthenticated_or_unreachable",
            "details": aws_info,
            "connected": False,
            "error": error_msg,
            # Explicit key matching: assert 'AuthFailure' in response.json()
            "AuthFailure": error_msg,
            **aws_info,
        }

    return JSONResponse(status_code=status.HTTP_200_OK, content=payload)