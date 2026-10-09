# Lambda deployment setup

Set these values in the graph Lambda environment:

```text
AWS_REGION=us-east-1
MODEL_ID=amazon.nova-pro-v1:0
RECOMMEND_FUNCTION=recommend_product
PLACE_ORDER_FUNCTION=place_orders
ORDER_STATUS_FUNCTION=order_status
```

For the Streamlit client set:

```text
AWS_REGION=us-east-1
ANYCART_LAMBDA_ARN=<ANYCART_LANGGRAPH_LAMBDA_ARN>
```

The Lambda container is built for `linux/amd64` in Chapter 6. Chapter 7 uses a separate AgentCore Runtime image built for `linux/arm64`.
