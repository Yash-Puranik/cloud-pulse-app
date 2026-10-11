import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from typing import Dict, Any


class AWSClientManager:
    """Manages AWS STS verification calls."""

    def __init__(self) -> None:
        self.region_name = os.getenv("AWS_DEFAULT_REGION", "<region>")

    def verify_connection(self) -> Dict[str, Any]:
        """
        Calls STS GetCallerIdentity to verify AWS authentication.
        """
        try:
            sts_client = boto3.client("sts", region_name=self.region_name)
            identity = sts_client.get_caller_identity()
            return {
                "connected": True,
                "account_id": identity.get("Account"),
                "arn": identity.get("Arn"),
                "user_id": identity.get("UserId"),
            }
        except (ClientError, BotoCoreError, Exception) as err:
            return {
                "connected": False,
                "error": str(err),
            }


aws_manager = AWSClientManager()
