# Building Enterprise AI Agents on AWS

Source files for the Packt book **Building Enterprise AI Agents on AWS**.

Canonical repository: https://github.com/PacktPublishing/Building-Enterprise-AI-Agents-on-AWS

## Source-code coverage

Chapters 1 and 2 are conceptual/design chapters and do not require downloadable source files. The repository therefore begins with Chapter 3.

| Folder | Coverage |
| --- | --- |
| `chapter03` | CrewAI environment and scaffold |
| `chapter04` | CrewAI vacation planner: CLI and Streamlit |
| `chapter05` | AnyCart product catalog and Lambda back-end tools |
| `chapter06` | LangGraph orchestration, Lambda container, and Streamlit client |
| `chapter07` | Amazon Bedrock AgentCore Runtime deployment |
| `chapter08` | AgentCore observability and OpenTelemetry instrumentation |
| `chapter09` | Cognito machine-to-machine identity and token testing |
| `chapter10` | AgentCore Gateway travel-package tool and end-to-end integration |

## Before you run a chapter

- The book examples use the AWS Region `us-east-1` unless a chapter explicitly says otherwise.
- Use temporary AWS credentials or IAM Identity Center rather than long-lived access keys.
- Copy `.env.example` values into your local environment where a chapter requires them. Never commit real secrets.
- Replace placeholders such as `<ACCOUNT_ID>` and `<..._ARN>` only in your local environment or deployment commands.
- Follow each chapter's README and the matching manuscript instructions for resource creation and cleanup.

## Pre-publication version note

This repository snapshot is aligned to the manuscript currently under review. Dependency pins and lock files will be revalidated during the post-review technical pass before publication. Do not treat package versions as a recommendation to upgrade independently of the tested chapter baseline.
