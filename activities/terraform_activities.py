from temporalio import activity

import json
import re
from pathlib import Path
from typing import Union


from utils.cmds import (
    run_tf_init_command,
    run_tf_plan_command_v2
)

TERRAFORM_EC2_DIR = Path(__file__).parent.parent / "terraform" / "compute"
INIT_SUCCESS_TOKEN = "Terraform has been successfully initialized"
PLAN_SUMMARY_PATTERN = re.compile(
    r"Plan:\s+(\d+)\s+to add,\s+(\d+)\s+to change,\s+(\d+)\s+to destroy",
    re.IGNORECASE,
)

ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

def _strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_PATTERN.sub("", text)

@activity.defn(name="terraform_init_activity")
async def terraform_init_activity(directory: Union[str, Path] = TERRAFORM_EC2_DIR) -> dict:
    activity.logger.info("Initializing the Terraform init activity")
    raw_output = await run_tf_init_command(directory)
    cleaned = _strip_ansi(raw_output)
    success = INIT_SUCCESS_TOKEN in cleaned 
    return {
        "stage": "init",
        "success": success,
        "summary":(
            "Terraform initialization completed successfully"
            if success
            else "Terraform initialization did not complete successfully"
        )
    }

@activity.defn(name="terraform_plan_activity")
async def terraform_plan_activity(inputs: dict, directory: Union[str, Path] = TERRAFORM_EC2_DIR) -> dict:
    activity.logger.info("Running a terraform plan to initialize terraform resources")
    raw_output = await run_tf_plan_command_v2(inputs, directory)
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
    }