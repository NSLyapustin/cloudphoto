import boto3 as boto3

from .config import is_configured, read_config


def create_s3_session(access_key, secret_access_key, endpoint_url, region_name) -> boto3.session:
    session = boto3.session.Session()
    return session.client(
        service_name="s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region_name
    )


def init_s3_session() -> boto3.session:
    if is_configured():
        config = read_config()
        config = {
            "endpoint_url": config.get("DEFAULT", "endpoint_url"),
            "access_key": config.get("DEFAULT", "aws_access_key_id"),
            "secret_access_key": config.get("DEFAULT", "aws_secret_access_key"),
            "region_name": config.get("DEFAULT", "region")
        }

        return create_s3_session(**config)
