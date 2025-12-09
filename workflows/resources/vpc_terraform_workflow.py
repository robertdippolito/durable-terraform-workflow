from __future__ import annotations
from pathlib import Path

from datetime import timedelta

from temporalio import workflow

VPC_MODULE_DIR = str(Path("terraform") / "vpc")
VPC_TFVARS_PATH = str(Path("terraform") / "vpc" / "infra.auto.tfvars")

@workflow.defn
class VPCWorkflow:
    @workflow.run
    async def run(self, spec: str) -> dict:
        workflow.logger.info("Starting Terraform init for VPC CIDR %s", spec)
        init_output = await workflow.execute_activity(
            "terraform_init_activity",
            VPC_MODULE_DIR,
            start_to_close_timeout=timedelta(minutes=1),
        )
        workflow.logger.info("Init completed")

        plan_output = await workflow.execute_activity(
            "terraform_plan_activity",
            args=[VPC_MODULE_DIR, VPC_TFVARS_PATH, {"vpc_cidr": spec}],
            start_to_close_timeout=timedelta(minutes=5),
        )
        workflow.logger.info("Plan completed with summary: %s", plan_output.get("summary"))

        apply_output = await workflow.execute_activity(
            "terraform_apply_activity",
            args=[{"vpc_cidr": spec}, VPC_MODULE_DIR, VPC_TFVARS_PATH],
            start_to_close_timeout=timedelta(minutes=5),
        )
        workflow.logger.info("Apply completed with summary: %s", apply_output.get("summary"))

        outputs = await workflow.execute_activity(
            "terraform_output_vpc_activity",
            start_to_close_timeout=timedelta(minutes=1),
        )
        return {
            "init": init_output,
            "plan": plan_output,
            "apply": apply_output,
            "outputs": outputs,
        }
