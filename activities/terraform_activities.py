from temporalio import activity

import json
import re
from pathlib import Path

from utils.cmds import (
    run_tf_init_command
)

TERRAFORM_EC2_DIR = Path(__file__).parent.parent / "terraform" / "compute"
INIT_SUCCESS_TOKEN = "Terraform has been successfully initialized"

ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

def _strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_PATTERN.sub("", text)

@activity.defn(name="terraform_init_activity")
async def terraform_init_activity() -> dict:
    activity.logger.info("Initializing the Terraform init activity")
    raw_output = await run_tf_init_command(TERRAFORM_EC2_DIR)
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