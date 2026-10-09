import os
import boto3

client = boto3.client("dynamodb")
ORDERS_TABLE = os.environ.get("ORDERS_TABLE", "orders")


def lambda_handler(event, context):
    order_id = str(event.get("order_id", "")).strip()
    if not order_id:
        return {
            "found": False,
            "message": "order_id is required",
        }

    item = client.get_item(
        TableName=ORDERS_TABLE,
        Key={"order_id": {"S": order_id}},
        ConsistentRead=True,
    ).get("Item")

    if not item:
        return {
            "found": False,
            "order_id": order_id,
            "message": "Order not found",
        }

    return {
        "found": True,
        "order_id": item["order_id"]["S"],
        "product_id": item["product_id"]["S"],
        "quantity": int(item["quantity"]["N"]),
        "status": item["status"]["S"],
    }
