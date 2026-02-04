import asyncio
import grpc.aio
from pyzeebe import ZeebeWorker, Job, ZeebeTaskRouter

# 1. Create a Router
router = ZeebeTaskRouter()

# 2. Define the worker for 'Publish job posting online'
# IMPORTANT: The task_type must match exactly what is in your BPMN (including spaces)
@router.task(task_type="Publish job posting online")
async def publish_job_task(job: Job, job_title: str = "Unknown Role", job_id: str = "Unknown ID"):
    print(f"========================================")
    print(f"STARTING TASK: Publish Job Posting")
    print(f"Job Key: {job.key}")
    print(f"Publishing Position: {job_title} (ID: {job_id})")
    print(f"Posting to: LinkedIn and StepStone...")
    print(f"========================================")

    # 3. Return variables to the process (e.g., the URL of the new post)
    return {
        "job_posting_status": "PUBLISHED",
        "posting_url": "https://linkedin.com/jobs/view/123456",
        "platform_used": "LinkedIn"
    }

# 4. Main execution loop
async def main():
    print("Worker 'Publish job posting online' starting...")
    
    # Connect to Camunda 8
    async with grpc.aio.insecure_channel("141.26.156.184:26500") as channel:
        worker = ZeebeWorker(channel)
        worker.include_router(router)
        await worker.work()

if __name__ == "__main__":
    asyncio.run(main())