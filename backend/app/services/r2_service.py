import os
import uuid
import json

import boto3
from botocore.exceptions import ClientError


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

def put_json_object(
    object_key: str,
    data: dict,
):
    client = get_r2_client()
    bucket_name = get_r2_bucket_name()

    body = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")

    client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=body,
        ContentType="application/json",
    )

    return object_key


def get_json_object(
    object_key: str,
):
    client = get_r2_client()
    bucket_name = get_r2_bucket_name()

    try:
        response = client.get_object(
            Bucket=bucket_name,
            Key=object_key,
        )

    except ClientError as error:
        code = str(
            error.response.get(
                "Error",
                {},
            ).get(
                "Code",
                "",
            )
        )

        if code in (
            "NoSuchKey",
            "404",
            "NotFound",
        ):
            return None

        raise

    body = response["Body"].read()

    return json.loads(
        body.decode("utf-8")
    )


def delete_r2_object(
    object_key: str,
):
    client = get_r2_client()
    bucket_name = get_r2_bucket_name()

    client.delete_object(
        Bucket=bucket_name,
        Key=object_key,
    )

    return True


def list_r2_keys(
    prefix: str,
):
    client = get_r2_client()
    bucket_name = get_r2_bucket_name()

    keys = []
    continuation_token = None

    while True:
        params = {
            "Bucket": bucket_name,
            "Prefix": prefix,
        }

        if continuation_token:
            params["ContinuationToken"] = (
                continuation_token
            )

        response = client.list_objects_v2(
            **params
        )

        for item in response.get(
            "Contents",
            [],
        ):
            key = item.get("Key")

            if key:
                keys.append(key)

        if not response.get(
            "IsTruncated"
        ):
            break

        continuation_token = (
            response.get(
                "NextContinuationToken"
            )
        )

        if not continuation_token:
            break

    return keys
    def put_bytes_object(
    object_key: str,
    data: bytes,
    content_type: str = "application/octet-stream",
    ):
     client = get_r2_client()
     bucket_name = get_r2_bucket_name()

     client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=data,
        ContentType=content_type,
    )

    return object_key


def get_bytes_object(
    object_key: str,
):
    client = get_r2_client()
    bucket_name = get_r2_bucket_name()

    try:
        response = client.get_object(
            Bucket=bucket_name,
            Key=object_key,
        )

    except ClientError as error:
        code = str(
            error.response.get(
                "Error",
                {},
            ).get(
                "Code",
                "",
            )
        )

        if code in (
            "NoSuchKey",
            "404",
            "NotFound",
        ):
            return None

        raise

    return response["Body"].read()
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