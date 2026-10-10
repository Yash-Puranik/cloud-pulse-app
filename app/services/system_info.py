import psutil

try:
    import boto3  # type: ignore[import-not-found]
    from botocore.exceptions import ClientError, NoCredentialsError  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency handling
    boto3 = None
    ClientError = NoCredentialsError = Exception

from app.config import settings


def get_system_metrics() -> dict:
    """Collects real-time host CPU, memory, and process information."""
    return {
        "cpu_usage_percent": psutil.cpu_percent(interval=None),
        "memory_usage_percent": psutil.virtual_memory().percent,
        "active_pids": len(psutil.pids()),
    }


def verify_aws_connectivity() -> dict:
    """
    Executes a read-only STS GetCallerIdentity call to verify
    IAM credentials and AWS connectivity without altering infrastructure.
    """
    if boto3 is None:
        return {
            "status": "unavailable",
            "details": "boto3 is not installed",
            "region": settings.AWS_REGION,
        }

    try:
        sts_client = boto3.client("sts", region_name=settings.AWS_REGION)
        caller_identity = sts_client.get_caller_identity()
        return {
            "status": "connected",
            "account_id": caller_identity.get("Account"),
            "arn": caller_identity.get("Arn"),
            "region": settings.AWS_REGION,
        }
    except (NoCredentialsError, ClientError) as error:
        return {
            "status": "unauthenticated_or_unreachable",
            "details": str(error),
            "region": settings.AWS_REGION,
        }

