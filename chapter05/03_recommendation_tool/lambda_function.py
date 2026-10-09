import os
import boto3

client = boto3.client("bedrock-agent-runtime")
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]
GENERATION_MODEL_ARN = os.environ["GENERATION_MODEL_ARN"]


def lambda_handler(event, context):
    prompt = str(event.get("prompt", "")).strip()
    if not prompt:
        return {
            "ok": False,
            "error": "missing_prompt",
            "message": "Provide a product question.",
        }

    response = client.retrieve_and_generate(
        input={"text": prompt},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": GENERATION_MODEL_ARN,
            },
        },
    )

    return {
        "ok": True,
        "answer": response["output"]["text"],
    }
