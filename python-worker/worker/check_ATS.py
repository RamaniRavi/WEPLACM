import logging
import asyncio
import random
from pyzeebe import ZeebeWorker, Job, create_insecure_channel


def register(worker: ZeebeWorker):
    @worker.task(task_type="check_ATS_Score")
    async def check_ATS_Score(job: Job):
        print("ServiceTask check_ATS_Score triggered")

        job_description = job.variables.get("jobDescription", {}) or {}

        ats_score = random.randint(75, 99)

        print(f"ATS Score calculated: {ats_score}")

        return {
            "ats_score": ats_score
        }


async def main():
    channel_WPLACM = create_insecure_channel(grpc_address="141.26.156.184:26500")
    worker = ZeebeWorker(channel_WPLACM)
    register(worker)
    await worker.work()


if __name__ == "__main__":
    asyncio.run(main())
