# Chapter 5 - AnyCart back-end tools

This chapter prepares the AnyCart data and tool boundaries before LangGraph orchestration is added in Chapter 6.

- `02_product_catalog/product_catalog.pdf`: catalog used by the Bedrock Knowledge Base
- `03_recommendation_tool/lambda_function.py`: catalog-grounded recommendation Lambda
- `04_order_backend/README.md`: DynamoDB `orders` table contract
- `05_order_tools/place_orders/lambda_function.py`: validated, idempotent order placement
- `05_order_tools/order_status/lambda_function.py`: safe order lookup

Environment-specific IDs are supplied through Lambda environment variables rather than hardcoded in source.
