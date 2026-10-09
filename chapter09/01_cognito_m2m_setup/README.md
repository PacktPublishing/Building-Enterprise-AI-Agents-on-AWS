# Cognito machine-to-machine setup

The manuscript uses these logical values:

```text
User pool: vacation-planner-identity-lab
App client: vacation-planner-m2m
Resource server identifier: vacation-planner-gateway
Scope name: invoke
Resulting scope: vacation-planner-gateway/invoke
```

Configure a user-pool domain so the client can request tokens from `/oauth2/token`. Store the client secret outside source control.
