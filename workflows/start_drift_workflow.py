import asyncio
import logging

from temporalio.client import Client, WorkflowFailureError

from workflows.drift_workflow import DriftWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("drifet-detection-workflow")

    infra_config = {
        "vpc": {"vpc_cidr": "10.0.0.0/16"},
        "compute": {"tags": {"Name": "dev-instance"}},
    }

    client = await Client.connect("localhost:7233", namespace="default")

    try:
        result = await client.execute_workflow(
            DriftWorkflow.run,
            infra_config["vpc"],
            id="drift-detection-workflow",
            task_queue="MY_TASK_QUEUE",
        )
        logger.info("Workflow completed successfully: %s", result)
    except WorkflowFailureError:
        logger.exception("Workflow execution failed")
        raise


if __name__ == "__main__":
    asyncio.run(main())
