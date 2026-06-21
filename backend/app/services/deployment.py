from __future__ import annotations


def deployment_checklist() -> dict:
    return {
        "definition": "Deployment means packaging the backend as a container, running tests in CI/CD, pushing the image to a registry, and starting the service in a cloud runtime.",
        "acronyms": {
            "CI/CD": "Continuous Integration / Continuous Delivery",
            "ECR": "Elastic Container Registry",
            "ECS": "Elastic Container Service",
            "RDS": "Relational Database Service",
            "VPC": "Virtual Private Cloud",
        },
        "local_proof": [
            "docker compose up -d postgres",
            "curl localhost:18129/health",
            "python demos/run_ch29_real_pgvector_pipeline.py",
            "docker exec bidintel_ch29_real_pgvector psql -U bidintel -d bidintel -c 'SELECT COUNT(*) FROM chunks;'",
        ],
        "docker_build_proof": [
            "docker build -t bidintel-api:enterprise-hardening .",
            "docker run --rm -p 8000:8000 --env USE_BEDROCK=false bidintel-api:enterprise-hardening",
            "curl http://localhost:8000/health",
        ],
        "ci_cd": [
            "GitHub Actions runs unit/security tests on pull request.",
            "python -m pytest tests/test_enterprise_hardening.py -v",
            "Build backend container image.",
            "Push image to Amazon ECR.",
            "Deploy ECS service with task role and Secrets Manager references.",
            "Run smoke test against /health, /api/vector-db, /api/security/tests.",
        ],
        "github_actions_file": ".github/workflows/ci.yml",
        "rollback": [
            "Keep the last known-good container image tag.",
            "If smoke tests fail, redeploy the prior ECS task definition revision.",
            "Confirm /health, /api/security/tests, and /api/vector-db return good output.",
        ],
        "runtime": {
            "compute": "Amazon ECS Fargate",
            "database": "Amazon RDS PostgreSQL with pgvector extension",
            "secrets": "AWS Secrets Manager",
            "llm": "Claude Sonnet through Amazon Bedrock",
            "logs": "CloudWatch Logs",
            "metrics": "CloudWatch Alarms",
        },
        "simulation_boundary": "REAL LOCAL proof runs Docker plus PostgreSQL/pgvector. SIMULATED CLOUD proof explains ECR/ECS/RDS/CloudWatch click paths until a live AWS account is connected.",
    }
