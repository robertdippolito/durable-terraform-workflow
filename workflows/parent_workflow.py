from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.workflow import ParentClosePolicy

from .resources.vpc_terraform_workflow import VPCWorkflow
from .resources.compute_terraform_workflow import ComputeWorkflow


@workflow.defn
class ParentWorkflow:
    @workflow.run
    async def run(self, payload: dict) -> dict:
        retry_policy = RetryPolicy(
            maximum_attempts=5,
            maximum_interval=timedelta(seconds=10),
        )
        vpc_result = await workflow.execute_child_workflow(
            VPCWorkflow.run,
            payload["vpc"]["cidr"],
            retry_policy=retry_policy,
            execution_timeout=timedelta(hours=1),
            run_timeout=timedelta(minutes=30),
            parent_close_policy=ParentClosePolicy.ABANDON,
        )
        compute_result = await workflow.execute_child_workflow(
            ComputeWorkflow.run,
            payload["compute"]["tags"],
            execution_timeout=timedelta(hours=1),
            run_timeout=timedelta(minutes=30),
            parent_close_policy=ParentClosePolicy.ABANDON,
        )

        workflow.logger.info("VPC child workflow completed: %s", vpc_result)
        workflow.logger.info("EC2 child workflow completed: %s", compute_result)

        return {
            "vpc": vpc_result,
            "compute": compute_result,
        }
    