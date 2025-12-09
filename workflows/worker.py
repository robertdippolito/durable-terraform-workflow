import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from workflows.parent_workflow import ParentWorkflow
from workflows.drift_workflow import DriftWorkflow
from workflows.resources.vpc_terraform_workflow import VPCWorkflow
from workflows.resources.compute_terraform_workflow import ComputeWorkflow

from activities.terraform_activities import (
    terraform_init_activity,
    terraform_plan_activity,
    terraform_apply_activity,
)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("terraform-worker")

    client = await Client.connect("localhost:7233", namespace="default")

    worker = Worker(
        client,
        task_queue="MY_TASK_QUEUE",
        workflows=[ParentWorkflow, VPCWorkflow, DriftWorkflow, ComputeWorkflow],
        activities=[
            terraform_init_activity,
            terraform_plan_activity,
            terraform_apply_activity,
        ],
    )

    logger.info("Worker listening on task queue MY_TASK_QUEUE")
    try:
        await worker.run()
    except Exception:
        logger.exception("Worker crashed")
        raise


if __name__ == "__main__":
    asyncio.run(main())
