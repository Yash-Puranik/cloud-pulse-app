# Cloud-Pulse Sentinel (`cloud-pulse`)

[![Deploy to Vercel](https://github.com/Yash-Puranik/cloud-pulse-app/actions/workflows/deploy.yml/badge.svg)](https://github.com/Yash-Puranik/cloud-pulse-app/actions/workflows/deploy.yml)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Cloud-Pulse** is a lightweight, cloud-native operational telemetry microservice and live dashboard built with **FastAPI** and **Boto3**.

The architecture implements a **dual-target deployment strategy**: it runs serverlessly on **Vercel Edge/Serverless Functions** while remaining container-portable for **AWS ECS Fargate, AWS App Runner, and standard Docker runtimes**.

---

## 🌟 Key Features

* **Dual-Mode Response Gateway**:
  * **Human Dashboard (`/`)**: Embedded, dark-themed HTML/CSS status page with real-time uptime counters, platform specifications, and active AWS region reporting.
  * **Deterministic Machine Telemetry (`/health`, `/system`)**: Low-latency JSON payloads designed for load balancer health probes, container orchestrator liveness checks, and synthetic uptime monitors.
* **AWS Identity & STS Integration (`/aws/identity`)**:
  * Integrates with AWS Security Token Service via `boto3` to audit calling IAM roles and Account IDs.
  * Implements deterministic offline mock fallbacks when `AWS_ACCESS_KEY_ID=mock_key`, allowing offline unit testing and isolated CI execution without live cloud credentials.
* **Hardened CI/CD Quality Gates**:
  * Automated testing pipeline via GitHub Actions using `pytest` and `httpx`.
  * Automated dependency resolution via Astral's `uv` engine for reproducible builds.
  * Headless zero-downtime production deployments to Vercel via the Vercel CLI.
* **Production-Grade Container Architecture**:
  * Multi-stage OCI-compliant `Dockerfile` using `python:3.11-slim`.
  * Runs as an unprivileged non-root user (`appuser`).
  * Built-in container-level `HEALTHCHECK` probe and unbuffered stdout/stderr logging.

---

## 🏗️ Architecture Overview

```text
                           [ Client / Operator ]
                                     |
                                     v
                       +---------------------------+
                       |   Traffic Ingress Router  |
                       +---------------------------+
                                     |
                 +-------------------+-------------------+
                 |                                       |
                 v                                       v
    [ Vercel Edge Serverless ]               [ AWS Portable Container ]
     - @vercel/python runtime                 - AWS ECS Fargate / App Runner
     - vercel.json rewrite rules              - Non-root user: appuser
     - Ephemeral execution                    - Port 8080 (Uvicorn ASGI)
                 |                                       |
                 +-------------------+-------------------+
                                     |
                                     v
                           [ FastAPI Core Engine ]
                 +-------------------+-------------------+
                 |                                       |
                 v                                       v
         [ / (HTML Dashboard) ]              [ /health, /system, /aws/* ]
         Visual Telemetry Web UI             Structured JSON API Contracts
