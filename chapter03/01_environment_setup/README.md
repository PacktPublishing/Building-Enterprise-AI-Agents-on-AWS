# Environment readiness checks

Run these checks before continuing to the CrewAI project:

```text
python --version
uv --version
crewai --version
aws --version
aws sts get-caller-identity --profile agent-builder
aws configure get region --profile agent-builder
```

The manuscript uses Python 3.11 and AWS CLI v2. Confirm that the selected Bedrock model is available in your account and Region before invoking it.
