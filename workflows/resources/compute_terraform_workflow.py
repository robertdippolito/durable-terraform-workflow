from datetime import timedelta
from temporalio import workflow


@workflow.defn
class ComputeWorkflow:
    @workflow.run
    async def run(self, spec: dict) -> dict:
        workflow.logger.info("Starting Terraform init for EC2 config %s", spec)
        init_output = await workflow.execute_activity(
            "terraform_init_activity",
            start_to_close_timeout=timedelta(minutes=1)
        )
        workflow.logger.info("Initialization completed")

        plan_output = await workflow.execute_activity(
            "terraform_plan_activity",
            spec,
            start_to_close_timeout=timedelta(minutes=5),
        )
        workflow.logger.info("Plan completed with summary: %s", plan_output.get("summary"))

        # apply_output = await workflow.execute_activity(
        #     "terraform_apply_activity",
        #     spec,
        #     start_to_close_timeout=timedelta(minutes=5),
        # )
        # workflow.logger.info("Apply completed with summary: %s", apply_output.get("summary"))

        return {
            "init": init_output,
            "plan": plan_output,
            "apply": "Not completed yet.."
        }
