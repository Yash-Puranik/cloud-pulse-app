from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from app.config import settings
from app.services.system_info import get_system_metrics, verify_aws_connectivity

app = FastAPI(
    title=settings.APP_NAME,
    description="DevOps Microservice for CI/CD Pipeline Training",
    version="1.0.0",
)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Liveness & readiness probe for Load Balancers and Orchestrators."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@app.get("/metrics", status_code=status.HTTP_200_OK)
def read_metrics():
    """Exposes host hardware metrics collected via psutil."""
    return {
        "metrics": get_system_metrics(),
        "status": "success",
    }


@app.get("/aws/status")
def read_aws_status():
    """Validates AWS authentication and returns the active IAM identity."""
    result = verify_aws_connectivity()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result,
    )
