# Durable Terraform Workflow
Temporal-powered workflows that run Terraform (init/plan/apply) for a simple VPC module and a compute module, plus a recurring drift detector.

## Table of Contents
- [What This Is](#what-this-is)
- [Repo Structure](#repo-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running the Worker](#running-the-worker)
- [Triggering Workflows](#triggering-workflows)
- [Configuration & Inputs](#configuration--inputs)
- [Terraform Notes](#terraform-notes)
- [Troubleshooting](#troubleshooting)

## What This Is
- A Temporal worker (`workflows/worker.py`) that exposes workflows to run Terraform against two modules:
  - `terraform/vpc`: creates a VPC, public subnets, internet gateway, and route table.
  - `terraform/compute`: creates an example S3 bucket (placeholder for compute resources).
- Activities in `activities/terraform_activities.py` shell out to `terraform init/plan/apply`, parse summaries, and return structured results.
- A drift detection workflow polls `terraform plan` on a schedule and logs if changes are detected.

## Repo Structure
- `workflows/` – Temporal workflow definitions:
  - `parent_workflow.py`: orchestrates VPC then compute child workflows.
  - `resources/vpc_terraform_workflow.py`, `resources/compute_terraform_workflow.py`: child workflows for each module.
  - `drift_workflow.py`: recurring plan checks for drift on the VPC module.
  - `start_workflow.py`, `start_drift_workflow.py`: convenience launchers for local runs.
  - `worker.py`: starts a Temporal worker that registers workflows and activities.
- `activities/terraform_activities.py` – Activities that run Terraform CLI commands and parse outputs.
- `utils/cmds.py` – Helpers to run terraform with optional overrides/tfvars.
- `terraform/` – Module directories (`vpc/`, `compute/`) and lockfiles/state used for demos.
- `requirements.txt` – Python dependencies (Temporal SDK).

## Prerequisites
- Python 3.9+ and `pip`.
- Terraform CLI installed and on `PATH`.
- Temporal server reachable at `localhost:7233` (e.g., run `temporal server start-dev` or use Temporal Cloud and update the address/namespace).
- AWS credentials available in your environment for Terraform to create resources.

## Setup
```bash
cd durable-terraform-workflow
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Worker
Start the Temporal worker so it can execute workflows and activities:
```bash
python workflows/worker.py
```
It connects to `localhost:7233`, registers workflows/activities, and listens on task queue `MY_TASK_QUEUE`.

## Triggering Workflows
- **Full VPC + Compute apply** (executes parent workflow):
  ```bash
  python workflows/start_workflow.py
  ```
  The payload is defined in that script (`infra_config`).

- **Drift detection loop** (repeated plans on the VPC module):
  ```bash
  python workflows/start_drift_workflow.py
  ```
  Default interval is 1 minute; logs when plan shows add/change/destroy.

If you launch manually via the Temporal SDK/CLI, call `ParentWorkflow.run` or `DriftWorkflow.run` on task queue `MY_TASK_QUEUE` and supply the desired spec dictionaries.

## Configuration & Inputs
- Workflow inputs are simple Python dicts:
  - VPC example: `{"vpc_cidr": "10.0.0.0/16"}` (uses defaults for env and AZs if not overridden).
  - Compute example: `{"tags": {"Name": "dev-instance"}}` (used in the S3 bucket tags).
- `infra.auto.tfvars` files:
  - `terraform/compute/infra.auto.tfvars` exists (tags example).
  - `terraform/vpc/infra.auto.tfvars` is referenced but not committed; create one if you want to supply defaults instead of passing overrides.
- Update task queue, Temporal target, or inputs in `start_workflow.py` / `start_drift_workflow.py` as needed.

## Terraform Notes
- Modules are minimal for demo purposes:
  - VPC module creates a VPC with public subnets and internet gateway.
  - Compute module currently provisions an S3 bucket named `my-tf-temporal-test-bucket`.
- State files in `terraform/**/terraform.tfstate` are checked in for illustration; consider removing them and using remote state for real use.
- Activities parse `terraform` stdout for summaries; if Terraform output format changes, adjust the regex patterns in `activities/terraform_activities.py`.

## Troubleshooting
- **Terraform not found**: ensure `terraform` is on PATH in the environment where the worker runs.
- **Temporal connection errors**: verify the server address/namespace in `start_*` scripts and `worker.py`.
- **AWS auth errors**: export credentials (env vars, profile) before running workflows.
- **Plan/apply parsing issues**: check worker logs; update regex in `terraform_activities.py` if needed.
