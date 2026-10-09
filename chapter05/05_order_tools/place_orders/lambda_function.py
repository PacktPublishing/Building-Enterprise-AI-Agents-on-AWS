import os
import boto3
from botocore.exceptions import ClientError

client = boto3.client("dynamodb")
ORDERS_TABLE = os.environ.get("ORDERS_TABLE", "orders")
VALID_PRODUCT_IDS = {
    value.strip()
    for value in os.environ.get("VALID_PRODUCT_IDS", "").split(",")
    if value.strip()
}


def error(code, message):
    return {"ok": False, "error": code, "message": message}


def lambda_handler(event, context):
    product_id = str(event.get("product_id", "")).strip()
    idempotency_key = str(event.get("idempotency_key", "")).strip()
    confirmed = event.get("confirmed") is True

    try:
        quantity = int(event.get("quantity", 1))
    except (TypeError, ValueError):
        return error("invalid_quantity", "quantity must be an integer")

    if not confirmed:
        return error("confirmation_required", "Explicit confirmation is required before order creation")
    if not product_id:
        return error("missing_product_id", "product_id is required")
    if VALID_PRODUCT_IDS and product_id not in VALID_PRODUCT_IDS:
        return error("invalid_product_id", "The requested product_id is not in the approved catalog")
    if not 1 <= quantity <= 10:
        return error("invalid_quantity", "quantity must be between 1 and 10")
    if not idempotency_key:
        return error("missing_idempotency_key", "idempotency_key is required for a confirmed order")

    # Use the request identifier as the stable order ID for this teaching example.
    order_id = idempotency_key
    item = {
        "order_id": {"S": order_id},
        "product_id": {"S": product_id},
        "quantity": {"N": str(quantity)},
        "status": {"S": "Pending"},
        "idempotency_key": {"S": idempotency_key},
    }

    try:
        client.put_item(
            TableName=ORDERS_TABLE,
            Item=item,
            ConditionExpression="attribute_not_exists(order_id)",
        )
        return {
            "ok": True,
            "duplicate": False,
            "order_id": order_id,
            "status": "Pending",
        }
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
            raise

    existing = client.get_item(
        TableName=ORDERS_TABLE,
        Key={"order_id": {"S": order_id}},
        ConsistentRead=True,
    ).get("Item")
    if not existing:
        return error("retry_lookup_failed", "The duplicate request could not be resolved safely")

    return {
        "ok": True,
        "duplicate": True,
        "order_id": existing["order_id"]["S"],
        "status": existing["status"]["S"],
    }
