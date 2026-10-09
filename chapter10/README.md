# Chapter 10 - AgentCore Gateway

The chapter adds one read-only enterprise tool to the vacation-planner path.

- `01_travel_package_data/dynamodb_travel_data.json`
- `02_lambda_tool/lambda_function.py`
- `03_gateway_schema/travel_package_tool.json`
- `04_gateway_test/gateway_test.py`
- `05_end_to_end_app/crew.py`
- `05_end_to_end_app/config/agents.yaml`
- `05_end_to_end_app/config/tasks.yaml`

The Gateway reuses the Chapter 9 Cognito authorizer. Keep the full discovered tool name in `TRAVEL_TOOL_NAME` rather than hardcoding a target-name prefix in application source.
