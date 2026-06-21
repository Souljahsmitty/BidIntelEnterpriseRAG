from __future__ import annotations

class MockClaudeSonnetBedrock:
    model_id = "local-mock:claude-sonnet-bedrock"

    def invoke(self, prompt: str) -> dict:
        return {
            "model": self.model_id,
            "answer": (
                "The opportunity is a strong bid if the team can cover the transition timeline. "
                "The strongest evidence is the SOC monitoring requirement and prior SOC past performance. "
                "Use the cited chunks for the technical approach and keep compliance risks visible."
            ),
            "production_equivalent": "boto3 bedrock-runtime invoke_model with Claude Sonnet on Amazon Bedrock",
        }
