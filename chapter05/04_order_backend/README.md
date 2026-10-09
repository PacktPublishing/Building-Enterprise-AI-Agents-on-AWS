# Orders table

Create a DynamoDB table named `orders` with `order_id` as the string partition key.

The placement function stores `product_id`, `quantity`, `status`, and `idempotency_key`. In the teaching implementation, the idempotency key is used as the stable order identifier so a safe retry can return the existing order instead of creating a duplicate.
