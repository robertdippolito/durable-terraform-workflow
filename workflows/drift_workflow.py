from datetime import timedelta

from temporalio import workflow


@workflow.defn
class DriftWorkflow:
    @workflow.run
    async def run(self, vpc_cidr: str, interval_minutes: int = 1) -> None:
        while True:
            plan_result = await workflow.execute_activity(
                "terraform_plan_vpc_activity",
                vpc_cidr,
                start_to_close_timeout=timedelta(minutes=5),
            )
            summary = plan_result.get("summary")
            drift_detected = summary and any(
                summary.get(key, 0) > 0 for key in ("add", "change", "destroy")
            )

            if drift_detected:
                workflow.logger.warning("Drift detected: %s", summary)
            else:
                workflow.logger.info("No drift detected: %s", summary)

            await workflow.sleep(interval_minutes * 60)
