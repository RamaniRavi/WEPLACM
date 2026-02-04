import logging
import asyncio
from pyzeebe import ZeebeWorker, ZeebeClient, Job, create_insecure_channel


def register(worker: ZeebeWorker, client: ZeebeClient):
    @worker.task(task_type="receiveHiringRequest")
    async def sendJobInformation(job: Job):
        """Send information for new job opening to WEPLACEM"""
        logging.info("Message 'sendJobInformation' triggered")

        messageVariables = {
            "correlation_key": "key",
            "ratingStandards": job.variables.get("ratingStandards"),
            "standardsOfEligibility": job.variables.get("standardsOfEligibility"),
            "jobDescription": job.variables.get("jobDescription")
        }

        await client.publish_message(
            name="StartMessage_testProcess",
            correlation_key=str(job.process_instance_key),
            variables=messageVariables
        )
        logging.info("Message published successfully")
        return {"process_instance_key": str(job.process_instance_key)}
    

async def main():
    # create connection
    channel_WPLACM = create_insecure_channel(grpc_address="141.26.156.184:26500")

    worker = ZeebeWorker(channel_WPLACM)

    logging.info("Infrastructure initialized. Registering tasks...")

    register(worker, worker)

    await worker.work()


if __name__ == '__main__':
    asyncio.run(main())