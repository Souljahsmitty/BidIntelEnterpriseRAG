from __future__ import annotations

import json
import os


class LocalBedrockSimulation:
    model_id = "local-simulation:claude-sonnet-bedrock"

    def invoke(self, prompt: str) -> dict:
        return {
            "model": self.model_id,
            "answer": "[SIMULATED BEDROCK RESPONSE] " + prompt[:240],
            "simulation_boundary": "Set USE_BEDROCK=true with AWS credentials to call Amazon Bedrock.",
        }


def call_bedrock(prompt: str) -> dict:
    region = os.getenv("AWS_REGION", "us-east-1")
    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
    if os.getenv("USE_BEDROCK", "false").lower() not in {"1", "true", "yes"}:
        return LocalBedrockSimulation().invoke(prompt)
    try:
        import boto3
    except ImportError as exc:
        return {
            "model": model_id,
            "error": "boto3_not_installed",
            "fix": "Install boto3 in production runtime: python -m pip install boto3",
            "exception": str(exc),
        }
    client = boto3.client("bedrock-runtime", region_name=region)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": prompt}],
    }
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return {"model": model_id, "answer": result["content"][0]["text"], "region": region}


def bedrock_config_status() -> dict:
    return {
        "USE_BEDROCK": os.getenv("USE_BEDROCK", "false"),
        "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
        "BEDROCK_MODEL_ID": os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        "mode": "real_bedrock" if os.getenv("USE_BEDROCK", "false").lower() in {"1", "true", "yes"} else "local_simulation",
    }
