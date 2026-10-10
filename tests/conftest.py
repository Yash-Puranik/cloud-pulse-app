import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Set dummy environment variables BEFORE importing application code
# This ensures that any module-level settings read safe test defaults
os.environ["APP_ENV"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing-mock-key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing-mock-secret"
os.environ["AWS_SECURITY_TOKEN"] = "testing-mock-token"
os.environ["AWS_SESSION_TOKEN"] = "testing-mock-session"

from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configures the asynchronous event loop backend for pytest."""
    return "asyncio"


@pytest.fixture
def mock_aws_cloudwatch() -> Generator[MagicMock, None, None]:
    """
    Mocks the boto3 CloudWatch client so tests do not make real AWS network calls.
    Yields the mock object for test-specific assertions.
    """
    with patch("boto3.client") as mock_boto_client:
        mock_cw = MagicMock()
        # Default mock response for put_metric_data
        mock_cw.put_metric_data.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }
        mock_boto_client.return_value = mock_cw
        yield mock_cw


@pytest.fixture
def mock_system_metrics() -> Generator[dict, None, None]:
    """
    Provides standardized mock system metrics (CPU, Memory, Disk)
    to verify predictable responses in API endpoints.
    """
    mock_data = {
        "cpu_usage_percent": 12.5,
        "memory_usage_percent": 45.2,
        "disk_usage_percent": 30.1,
        "status": "healthy",
    }
    with patch("app.services.system_metrics.collect_metrics", return_value=mock_data):
        yield mock_data


@pytest.fixture
def client(mock_aws_cloudwatch, mock_system_metrics) -> Generator[TestClient, None, None]:
    """
    FastAPI TestClient fixture. Automatically injects mock AWS and metrics
    services into the application lifespan.
    """
    with TestClient(app) as test_client:
        yield test_client
