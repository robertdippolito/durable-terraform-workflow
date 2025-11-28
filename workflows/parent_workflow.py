from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.workflow import ParentClosePolicy

from .resources.vpc_terraform_workflow import VPCWorkflow


@workflow.defn
class ParentWorkflow:
    @workflow.run
    async def run(self, vpc_cidr: str) -> dict:
        retry_policy = RetryPolicy(
            maximum_attempts=5,
            maximum_interval=timedelta(seconds=10),
        )
        result = await workflow.execute_child_workflow(
            VPCWorkflow.run,
            vpc_cidr,
            retry_policy=retry_policy,
            execution_timeout=timedelta(hours=1),
            run_timeout=timedelta(minutes=30),
            parent_close_policy=ParentClosePolicy.ABANDON,
        )
        workflow.logger.info("VPC child workflow completed: %s", result)
        return result
