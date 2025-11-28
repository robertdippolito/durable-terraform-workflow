from __future__ import annotations

from datetime import timedelta

from temporalio import workflow


@workflow.defn
class VPCWorkflow:
    @workflow.run
    async def run(self, vpc_cidr: str) -> str:
        workflow.logger.info("Starting Terraform init for VPC CIDR")
        init_output = await workflow.execute_activity(
            "terraform_init_vpc_activity",
            start_to_close_timeout=timedelta(minutes=1),
        )
        workflow.logger.info(f"Init completed with output: {init_output}")
        workflow.logger.info("Starting Terraform plan for VPC CIDR %s", vpc_cidr)
        plan_output = await workflow.execute_activity(
            "terraform_plan_vpc_activity",
            vpc_cidr,
            start_to_close_timeout=timedelta(minutes=1),
        )
        workflow.logger.info(f"Plan completed with output: {plan_output}")
        return plan_output

