from datetime import timedelta
from pathlib import Path

from temporalio import workflow

VPC_MODULE_DIR = str(Path("terraform") / "vpc")
VPC_TFVARS_PATH = str(Path("terraform") / "vpc" / "infra.auto.tfvars")


@workflow.defn
class DriftWorkflow:
    @workflow.run
    async def run(self, spec: dict, interval_minutes: int = 1) -> None:
        while True:
            plan_result = await workflow.execute_activity(
                "terraform_plan_activity",
                args=[VPC_MODULE_DIR, VPC_TFVARS_PATH, spec],
                start_to_close_timeout=timedelta(minutes=5),
            )
            summary = plan_result.get("summary")
            drift_detected = summary and any(
                summary.get(key, 0) > 0 for key in ("add", "change", "destroy")
            )

            if drift_detected:
                workflow.logger.warning("Drift detected!")
            else:
                workflow.logger.info("No drift detected")

            await workflow.sleep(interval_minutes * 60)
