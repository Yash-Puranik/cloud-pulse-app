import logging
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


class AWSClientManager:
    """Manages AWS credentials, connection verification, and metric publishing."""

    def __init__(self, region_name: Optional[str] = None):
        """
        Initializes the AWS Client Manager.
        Relies on the standard Boto3 credential lookup chain.
        """
        self.region_name = region_name
        self._session: Optional[boto3.Session] = None
        self._cw_client = None
        self._sts_client = None

    @property
    def session(self) -> boto3.Session:
        """Lazily initializes and caches the Boto3 session."""
        if self._session is None:
            self._session = boto3.Session(region_name=self.region_name)
        return self._session

    @property
    def cloudwatch(self):
        """Lazily initializes the CloudWatch low-level client."""
        if self._cw_client is None:
            self._cw_client = self.session.client("cloudwatch")
        return self._cw_client

    @property
    def sts(self):
        """Lazily initializes the STS (Security Token Service) client."""
        if self._sts_client is None:
            self._sts_client = self.session.client("sts")
        return self._sts_client

    def verify_connection(self) -> Dict[str, Any]:
        """
        Verifies AWS connectivity by inspecting active credentials using STS.
        Returns connection status, account ID, and active identity ARN.
        """
        try:
            caller_identity = self.sts.get_caller_identity()
            return {
                "connected": True,
                "account_id": caller_identity.get("Account"),
                "arn": caller_identity.get("Arn"),
                "user_id": caller_identity.get("UserId"),
            }
        except (ClientError, BotoCoreError) as err:
            logger.warning("AWS connectivity verification failed: %s", str(err))
            return {
                "connected": False,
                "error": str(err),
            }

    def publish_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "Percent",
        namespace: str = "CloudPulse/Sentinel",
        dimensions: Optional[list] = None,
    ) -> bool:
        """
        Publishes a single custom metric datum to AWS CloudWatch.
        """
        if dimensions is None:
            dimensions = [{"Name": "Environment", "Value": "Production"}]

        metric_data = [
            {
                "MetricName": metric_name,
                "Value": float(value),
                "Unit": unit,
                "Dimensions": dimensions,
            }
        ]

        try:
            response = self.cloudwatch.put_metric_data(
                Namespace=namespace,
                MetricData=metric_data,
            )
            status_code = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            return status_code == 200
        except (ClientError, BotoCoreError) as err:
            logger.error("Failed to publish metric %s to CloudWatch: %s", metric_name, str(err))
            return False


# Singleton instance for application-wide reuse
aws_manager = AWSClientManager()
