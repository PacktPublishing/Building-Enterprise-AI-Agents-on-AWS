# Local setup

From `chapter06/01_local_deployment/order_management`:

```text
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Set these environment variables before running `graph.py`:

```text
AWS_REGION=us-east-1
MODEL_ID=amazon.nova-pro-v1:0
RECOMMEND_FUNCTION=recommend_product
PLACE_ORDER_FUNCTION=place_orders
ORDER_STATUS_FUNCTION=order_status
```
