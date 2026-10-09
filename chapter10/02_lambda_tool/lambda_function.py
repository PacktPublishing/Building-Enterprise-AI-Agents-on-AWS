import os
import boto3

TABLE_NAME = os.environ.get("TRAVEL_PACKAGES_TABLE", "travel_packages")
dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    city = (event.get("city") or "").strip()
    if not city:
        return {"found": False, "message": "city is required"}

    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={"city": {"S": city}},
    )
    item = response.get("Item")
    if not item:
        return {
            "found": False,
            "city": city,
            "message": "No travel package was found for that city",
        }

    return {
        "found": True,
        "city": item["city"]["S"],
        "travel_plan": item["travel_plan"]["S"],
        "vacation_cost": item["vacation_cost"]["S"],
        "duration": item["duration"]["S"],
        "best_season": item["best_season"]["S"],
    }
