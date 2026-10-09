import json
import os
import uuid
import boto3

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AGENT_RUNTIME_ARN = os.environ["AGENT_RUNTIME_ARN"]
AGENT_RUNTIME_QUALIFIER = os.getenv("AGENT_RUNTIME_QUALIFIER", "DEFAULT")
client = boto3.client("bedrock-agentcore", region_name=AWS_REGION)


def lambda_handler(event, context):
    prompt = str(event.get("prompt") or event.get("topic") or "").strip()
    if not prompt:
        return {"statusCode": 400, "body": json.dumps({"error": "prompt is required"})}

    session_id = str(event.get("session_id") or uuid.uuid4())
    if len(session_id) < 33:
        session_id = f"{session_id}-{uuid.uuid4()}"

    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_RUNTIME_ARN,
        qualifier=AGENT_RUNTIME_QUALIFIER,
        runtimeSessionId=session_id,
        payload=json.dumps({"topic": prompt}).encode("utf-8"),
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["response"].read())
    return {
        "statusCode": 200,
        "body": json.dumps(result),
    }
