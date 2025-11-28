from __future__ import annotations

from datetime import timedelta

from temporalio import workflow


@workflow.defn
class VPCWorkflow:
    @workflow.run
    async def run(self, vpc_cidr: str) -> dict:
        workflow.logger.info("Starting Terraform init for VPC CIDR %s", vpc_cidr)
        init_output = await workflow.execute_activity(
            "terraform_init_vpc_activity",
            start_to_close_timeout=timedelta(minutes=1),
        )
        workflow.logger.info("Init completed")

        plan_output = await workflow.execute_activity(
            "terraform_plan_vpc_activity",
            vpc_cidr,
            start_to_close_timeout=timedelta(minutes=5),
        )
        workflow.logger.info("Plan completed with summary: %s", plan_output.get("summary"))

        outputs = await workflow.execute_activity(
            "terraform_output_vpc_activity",
            start_to_close_timeout=timedelta(minutes=1),
        )
        return {
            "init": init_output,
            "plan": plan_output,
            "outputs": outputs,
        }
