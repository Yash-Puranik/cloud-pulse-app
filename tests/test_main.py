from unittest.mock import patch
from fastapi.testclient import TestClient
from botocore.exceptions import ClientError
from app.main import app

# Initialize test client using the FastAPI application instance
client = TestClient(app)


def test_health_check_endpoint():
    """
    Verifies that /health returns HTTP 200 and the expected JSON contract.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "environment" in data


def test_metrics_endpoint():
    """
    Verifies that /metrics returns HTTP 200 with valid CPU, RAM, and PID data.
    """
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "metrics" in data
    metrics = data["metrics"]
    assert "cpu_usage_percent" in metrics
    assert "memory_usage_percent" in metrics
    assert "active_pids" in metrics
    assert isinstance(metrics["active_pids"], int)


@patch("app.services.system_info.boto3.client")
def test_aws_status_connected(mock_boto_client):
    """
    Tests /aws/status when valid AWS STS credentials exist (simulated via mock).
    """
    mock_sts = mock_boto_client.return_value
    mock_sts.get_caller_identity.return_value = {
        "Account": "123456789012",
        "Arn": "arn:aws:iam::123456789012:role/cloud-pulse-role",
    }

    response = client.get("/aws/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert data["account_id"] == "123456789012"
    assert "cloud-pulse-role" in data["arn"]


@patch("app.services.system_info.boto3.client")
def test_aws_status_unauthenticated(mock_boto_client):
    """
    Tests /aws/status handles AWS API errors gracefully without crashing the server.
    """
    mock_sts = mock_boto_client.return_value
    mock_sts.get_caller_identity.side_effect = ClientError(
        error_response={"Error": {"Code": "AuthFailure", "Message": "Invalid credentials"}},
        operation_name="GetCallerIdentity",
    )

    response = client.get("/aws/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unauthenticated_or_unreachable"
    assert "AuthFailure" in data["details"]
