import logging
import asyncio
from datetime import datetime, date
from pyzeebe import ZeebeWorker, Job, create_insecure_channel


def register(worker: ZeebeWorker):
    @worker.task(task_type="check_date_difference_10days")
    async def check_date_difference_10days(job: Job):
        logging.info("ServiceTask check_date_difference_10days triggered")

        # Get jobDescription safely
        job_description = job.variables.get("jobDescription", {})

        # Get starting date (expected format: YYYY-MM-DD)
        starting_date_str = job_description.get("Starting_Date")

        difference_in_date = 0
        if not starting_date_str:
            logging.error("Starting_Date not found in jobDescription")
        else:
            starting_date = datetime.strptime(starting_date_str, "%Y-%m-%d").date()
            today = date.today()
            difference_in_date = (starting_date - today).days

        logging.info(f"Difference in date: {difference_in_date} days")

        return {
            "difference_in_date": difference_in_date
        }

async def main():
    channel_WPLACM = create_insecure_channel(grpc_address="141.26.156.184:26500")
    worker = ZeebeWorker(channel_WPLACM)
    register(worker)

    await worker.work()

if __name__ == "__main__":
    asyncio.run(main())