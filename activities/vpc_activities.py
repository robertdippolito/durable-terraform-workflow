from __future__ import annotations

import json
import re
from pathlib import Path

from temporalio import activity

from utils.cmds import (
    run_tf_init_command,
    run_tf_plan_command,
    run_tf_output_command,
)

TERRAFORM_VPC_DIR = Path(__file__).parent.parent / "terraform" / "vpc"
INIT_SUCCESS_TOKEN = "Terraform has been successfully initialized"
PLAN_SUMMARY_PATTERN = re.compile(
    r"Plan:\s+(\d+)\s+to add,\s+(\d+)\s+to change,\s+(\d+)\s+to destroy",
    re.IGNORECASE,
)
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_PATTERN.sub("", text)


@activity.defn(name="terraform_init_vpc_activity")
async def terraform_init_vpc_activity() -> dict:
    activity.logger.info("Initiating the Terraform VPC init activity")
    raw_output = await run_tf_init_command(TERRAFORM_VPC_DIR)
    cleaned = _strip_ansi(raw_output)
    success = INIT_SUCCESS_TOKEN in cleaned
    return {
        "stage": "init",
        "success": success,
        "summary": (
            "Terraform initialization completed successfully"
            if success
            else "Terraform initialization did not report success"
        ),
        "output": cleaned,
    }


@activity.defn(name="terraform_plan_vpc_activity")
async def terraform_plan_vpc_activity(vpc_cidr: str) -> dict:
    activity.logger.info("Running a terraform plan to initialize VPC resources")
    raw_output = await run_tf_plan_command(TERRAFORM_VPC_DIR, vpc_cidr)
    cleaned = _strip_ansi(raw_output)
    match = PLAN_SUMMARY_PATTERN.search(cleaned)
    summary = None
    if match:
        summary = {
            "add": int(match.group(1)),
            "change": int(match.group(2)),
            "destroy": int(match.group(3)),
        }
    return {
        "stage": "plan",
        "success": summary is not None,
        "summary": summary,
        "output": cleaned,
    }


@activity.defn(name="terraform_output_vpc_activity")
async def terraform_output_vpc_activity() -> dict:
    activity.logger.info("Fetching Terraform outputs for VPC")
    raw_output = await run_tf_output_command(TERRAFORM_VPC_DIR)
    outputs: dict[str, object] = {}
    try:
        parsed = json.loads(raw_output)
        outputs = {
            key: value.get("value")
            for key, value in parsed.items()
            if isinstance(value, dict) and "value" in value
        }
    except json.JSONDecodeError:
        activity.logger.warning("Failed to parse terraform output JSON")
    return {
        "stage": "output",
        "success": bool(outputs),
        "outputs": outputs,
        "raw_output": raw_output.strip(),
    }
