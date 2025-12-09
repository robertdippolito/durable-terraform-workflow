import asyncio
import logging

from temporalio.client import Client, WorkflowFailureError

from workflows.parent_workflow import ParentWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("terraform-workflow")

    client = await Client.connect("localhost:7233", namespace="default")

    infra_config = {
            "vpc": {"vpc_cidr": "10.0.0.0/16"},
            "compute": {"tags": {"Name": "dev-instance"}},
        }

    try:
        result = await client.execute_workflow(
            ParentWorkflow.run,
            infra_config,
            id="terraform-parent-workflow",
            task_queue="MY_TASK_QUEUE",
        )
        logger.info("Workflow completed successfully: %s", result)
    except WorkflowFailureError:
        logger.exception("Workflow execution failed")
        raise


if __name__ == "__main__":
    asyncio.run(main())
