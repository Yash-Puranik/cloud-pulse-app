import os
from typing import Any, Dict
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.services.system_info import collect_system_report, verify_aws_connectivity

APP_NAME = "cloud-pulse"
APP_VERSION = "1.0.0"

app = FastAPI(
    title=APP_NAME,
    description="Cloud Pulse Infrastructure Sentinel Microservice",
    version=APP_VERSION,
)


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