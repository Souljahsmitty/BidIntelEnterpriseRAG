from __future__ import annotations


def bedrock_iam_secrets_click_path() -> dict:
    return {
        "label": "REAL AWS CONSOLE PATH - shown as a click-by-click runbook; local course uses simulation unless a live AWS account is connected",
        "region_setup": [
            "AWS Console -> top-right region -> choose us-east-1 or us-west-2.",
            "Search Amazon Bedrock -> open Bedrock -> Model access.",
            "Click Modify model access -> select Anthropic Claude Sonnet and Amazon Titan Embeddings.",
            "Click Submit -> wait for Available or Authorized.",
            "Terminal proof: aws --version",
            "Terminal proof: aws sts get-caller-identity",
            "Terminal proof: aws bedrock list-foundation-models --region us-east-1",
        ],
        "iam_clicks": [
            "AWS Console -> IAM -> Policies -> Create policy.",
            "Choose JSON -> paste BidIntelRuntimePolicy JSON.",
            "Name: BidIntelRuntimePolicy -> Create policy.",
            "IAM -> Users or Roles -> attach BidIntelRuntimePolicy.",
            "Terminal proof: aws iam get-policy --policy-arn arn:aws:iam::ACCOUNT_ID:policy/BidIntelRuntimePolicy",
        ],
        "secrets_manager_clicks": [
            "AWS Console -> Secrets Manager -> Store a new secret.",
            "Secret type: Other type of secret.",
            "Add BEDROCK_MODEL_ID, AWS_REGION, DATABASE_URL, USE_BEDROCK.",
            "Secret name: bidintel/prod/app.",
            "Terminal proof: aws secretsmanager get-secret-value --secret-id bidintel/prod/app --region us-east-1",
        ],
        "bedrock_fastapi_wiring": [
            "Create backend/app/services/bedrock_runtime.py.",
            "Read AWS_REGION, BEDROCK_MODEL_ID, and USE_BEDROCK from environment or Secrets Manager.",
            "If USE_BEDROCK=true, call boto3 bedrock-runtime invoke_model.",
            "If USE_BEDROCK=false, use LocalBedrockSimulation so the course runs without AWS cost.",
            "Test: curl -X POST http://localhost:8000/api/ask with a contract-risk question.",
        ],
        "cloudwatch_clicks": [
            "AWS Console -> CloudWatch -> Log groups -> Create log group /bidintel/prod/api.",
            "Create metric filter for ERROR.",
            "Create alarm: error count > 5 for 5 minutes.",
            "Show alarm state and acknowledgement path.",
            "Terminal proof: aws logs create-log-group --log-group-name /bidintel/prod/api --region us-east-1",
        ],
        "least_privilege_policy_example": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "BedrockInvokeOnly",
                    "Effect": "Allow",
                    "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                    "Resource": "*",
                },
                {
                    "Sid": "ReadBidIntelSecrets",
                    "Effect": "Allow",
                    "Action": ["secretsmanager:GetSecretValue"],
                    "Resource": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:bidintel/*",
                },
                {
                    "Sid": "WriteBidIntelLogs",
                    "Effect": "Allow",
                    "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                    "Resource": "*",
                },
            ],
        },
        "env_example": {
            "AWS_REGION": "us-east-1",
            "BEDROCK_MODEL_ID": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "USE_BEDROCK": "false",
            "BIDINTEL_SECRET_ID": "bidintel/prod/app",
        },
        "simulation_boundary": "REAL AWS path is click-by-click above. LOCAL MOCK path uses USE_BEDROCK=false and LocalBedrockSimulation so learners can finish without AWS charges.",
    }
