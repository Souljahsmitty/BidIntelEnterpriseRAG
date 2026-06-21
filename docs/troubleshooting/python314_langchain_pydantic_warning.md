# Python 3.14 LangChain / Pydantic Warning

This warning appears during the Ch38-Ch43 verification run:

```text
/Users/adamsmith/Documents/editing the V8 BidIntel video to truly be a follow along video/live_builds/bidintel_ch21_ch26_full_app_integration_20260620/.venv/lib/python3.14/site-packages/langchain_core/utils/pydantic.py:41:
UserWarning: Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.
  from pydantic.v1 import BaseModel as BaseModelV1
```

## What Each Term Means

Python is the programming language running the backend.

Python 3.14 is the version currently used by this local virtual environment.

LangChain is a library that helps build LLM and RAG workflows.

Pydantic is a Python library that validates structured data models.

Pydantic V1 is an older compatibility layer some LangChain internals still reference.

## Is This A Failure?

No.

The verification still passes:

```text
16 passed, 1 warning
```

That means the warning should be explained, but it does not block the Ch38-Ch43 local build.

## Why It Happens

Some LangChain dependency code imports `pydantic.v1`.

Python 3.14 is newer than the compatibility range expected by that legacy Pydantic V1 path.

The result is a warning, not a crash.

## Follow-Along Fix Option A - Recommended For Beginners

Use Python 3.12 or 3.13 for the course environment.

```bash
cd "/Users/adamsmith/Documents/editing the V8 BidIntel video to truly be a follow along video/live_builds/bidintel_ch21_ch26_full_app_integration_20260620"
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
./scripts/verify/check_proposal_ops.sh
```

Good output:

```text
16 passed
```

## Configure A Known Working Local Option

This is the exact path to make the learner's machine match the safer production-style Python version.

Step 1 - Check the current version:

```bash
python --version
./.venv/bin/python --version
```

Good output for the warning-free path:

```text
Python 3.12.x
```

Step 2 - If `python3.12` is missing on macOS, install it:

```bash
brew install python@3.12
```

If Homebrew is missing, install Python 3.12 from:

```text
https://www.python.org/downloads/
```

Step 3 - Recreate the virtual environment:

```bash
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Step 4 - Prove the environment:

```bash
./.venv/bin/python --version
./scripts/verify/check_proposal_ops.sh
```

Good output:

```text
Python 3.12.x
BidIntel Ch38-Ch43 proposal operations verification complete.
16 passed
```

Common failure:

```text
zsh: command not found: python3.12
```

Fix:

```bash
brew install python@3.12
```

## Follow-Along Fix Option B - Continue Locally

If the current build shows:

```text
16 passed, 1 warning
```

you can continue the local tutorial. The tests prove the Ch38-Ch43 routes, services, frontend pages, and proposal operations workflow still work.

## Production Recommendation

For production or a public repo README, pin the backend runtime to a stable Python version that the dependency stack supports.

Use:

```text
python_requires = ">=3.12,<3.14"
```

or a Docker image such as:

```dockerfile
FROM python:3.12-slim
```

Then rerun:

```bash
./scripts/verify/check_proposal_ops.sh
```

The production goal is not "warnings are impossible." The production goal is: known runtime, pinned dependency range, passing tests, and documented warning policy.
