# Cloud-Pulse Sentinel

[![Deploy to Vercel](https://github.com/<your-username>/cloud-pulse/actions/workflows/deploy.yml/badge.svg)](https://github.com/<your-username>/cloud-pulse/actions/workflows/deploy.yml)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Runtime Target](https://img.shields.io/badge/deployment-Vercel%20%7C%20AWS%20Ready-black.svg)](https://vercel.com/)

Cloud-Pulse Sentinel is a lightweight, cloud-native operational telemetry microservice engineered with **FastAPI**. It features dual-target deployment readiness: it runs serverlessly on **Vercel's Edge Network** while maintaining container compatibility for container orchestration platforms such as **AWS ECS**, **AWS App Runner**, or standalone Docker environments.

---

## 🌟 Key Architectural Features

- **Dual-Audience Routing:**
  - **Human Web Console (`/`):** A zero-dependency dark-mode HTML/CSS status dashboard reporting live process uptime and runtime environments.
  - **Machine REST Endpoints (`/health`, `/system`):** Predictable JSON contracts for external pingers, load balancers, and Kubernetes/ECS health checks.
  - **Interactive Documentation (`/docs`, `/redoc`):** Built-in OpenAPI Swagger interface for instant API experimentation.
- **AWS STS Integration & Mock Fallback (`/aws/identity`):** Interrogates AWS Security Token Service via `boto3` to retrieve the active IAM caller identity. Includes an offline mock fallback layer to ensure CI/CD test suites run without external network dependencies.
- **Automated GitHub Actions CI/CD:** A hardened pipeline that runs unit tests with `pytest`, provisions the Astral `uv` package manager, and uses the Vercel CLI to compile and release production artifacts.
- **Container Hardening:** Includes explicit `.dockerignore` and `.gitignore` masks to prevent credential leakage and accelerate Docker build layer caching.

---

## 🏗️ System Architecture

```text
                       [ Developer ]
                             │
                       (git push main)
                             │
                             ▼
                ┌─────────────────────────┐
                │  GitHub Actions Runner   │
                │  - Checkout Code        │
                │  - Setup Python 3.11    │
                │  - Run pytest Suite     │
                │  - Setup Astral 'uv'    │
                │  - Vercel Build & Deploy│
                └────────────┬────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
   ┌──────────────────────┐      ┌──────────────────────┐
   │   Vercel Serverless  │      │ AWS Portable Docker  │
   │  Edge Python Runtime │      │ (ECS / App Runner)   │
   └──────────────────────┘      └──────────────────────┘
