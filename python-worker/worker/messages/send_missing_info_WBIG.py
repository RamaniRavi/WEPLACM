import asyncio
import logging
from pyzeebe import ZeebeWorker, ZeebeClient, Job, create_insecure_channel


def register(worker: ZeebeWorker, client: ZeebeClient):
    @worker.task(task_type="sendJobMissingInformation")
    async def sendJobMissingInformation(job: Job):
        """Send information for new job opening to WBIG"""
        logging.info("Message 'sendJobMissingInformation' triggered")

        validation = job.variables.get("validation")

        messageVariables = {
            "jobInfoChangeRequestText": validation.get("missingInfo")
        }

        await client.publish_message(
            name="testJobInformationChangeRequest",#receiveJobInformationChangeRequest
            correlation_key=str(job.process_instance_key),
            variables=messageVariables
        )
        logging.info("Message published successfully")
        return {"process_instance_key": str(job.process_instance_key)}

async def main():
    channel_WPLACM = create_insecure_channel(grpc_address="141.26.156.184:26500")
    channel_WBIG = create_insecure_channel(grpc_address="141.26.156.185:26500")    

    worker = ZeebeWorker(channel_WPLACM)
    client_WBIG = ZeebeClient(channel_WBIG)

    register(worker, client_WBIG)

    await worker.work()

if __name__ == "__main__":
    asyncio.run(main())