import os
import uuid

import boto3


def get_r2_client():
    endpoint_url = os.getenv("R2_ENDPOINT_URL")
    access_key_id = os.getenv("R2_ACCESS_KEY_ID")
    secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
    region = os.getenv("R2_REGION", "auto")

    if not endpoint_url:
        raise RuntimeError(
            "R2_ENDPOINT_URL is not configured."
        )

    if not access_key_id:
        raise RuntimeError(
            "R2_ACCESS_KEY_ID is not configured."
        )

    if not secret_access_key:
        raise RuntimeError(
            "R2_SECRET_ACCESS_KEY is not configured."
        )

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region,
    )


def get_r2_bucket_name():
    bucket_name = os.getenv(
        "R2_BUCKET_NAME"
    )

    if not bucket_name:
        raise RuntimeError(
            "R2_BUCKET_NAME is not configured."
        )

    return bucket_name


def test_r2_round_trip():
    client = get_r2_client()
    bucket_name = get_r2_bucket_name()

    object_key = (
        "system-tests/"
        f"r2-test-{uuid.uuid4().hex}.txt"
    )

    expected_content = (
        b"AI Content OS R2 connection test"
    )

    try:
        client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=expected_content,
            ContentType="text/plain",
        )

        response = client.get_object(
            Bucket=bucket_name,
            Key=object_key,
        )

        returned_content = (
            response["Body"].read()
        )

        if returned_content != expected_content:
            raise RuntimeError(
                "R2 read-back verification failed."
            )

        return {
            "status": "success",
            "write": True,
            "read": True,
            "delete": True,
            "bucket": bucket_name,
        }

    finally:
        try:
            client.delete_object(
                Bucket=bucket_name,
                Key=object_key,
            )
        except Exception:
            pass