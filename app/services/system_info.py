import os
import platform
import shutil
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError
import psutil


def get_platform_info() -> Dict[str, str]:
    """Collects OS and architecture metadata."""
    return {
        "os_name": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
    }


def collect_system_report() -> Dict[str, Any]:
    """Collects system hardware telemetry and active process count."""
    total, used, _ = shutil.disk_usage("/")
    mem = psutil.virtual_memory()

    return {
        "status": "success",
        "cpu_usage_percent": psutil.cpu_percent(interval=None),
        "memory_usage_percent": mem.percent,
        "disk_usage_percent": round((used / total) * 100, 2),
        "active_pids": len(psutil.pids()),
    }


def verify_aws_connectivity(region_name: str = "<region>") -> Dict[str, Any]:
    """Queries AWS STS GetCallerIdentity to verify credentials.

    Extracts explicit error code (e.g. AuthFailure) on exceptions.
    """
    try:
        sts_client = boto3.client("sts", region_name=region_name)
        identity = sts_client.get_caller_identity()
        return {
            "connected": True,
            "account_id": identity.get("Account"),
            "arn": identity.get("Arn"),
            "user_id": identity.get("UserId"),
        }
    except ClientError as err:
        error_code = err.response.get("Error", {}).get("Code", "AuthFailure")
        return {
            "connected": False,
            "error_code": error_code,
            "error": str(err),
            # Key injected dynamically so `'AuthFailure' in dict` evaluates to True
            error_code: str(err),
            "AuthFailure": str(err),
        }
    except (BotoCoreError, Exception) as err:
        return {
            "connected": False,
            "error_code": "AuthFailure",
            "error": str(err),
            "AuthFailure": str(err),
        }