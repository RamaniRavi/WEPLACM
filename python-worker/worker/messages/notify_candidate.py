import asyncio
import grpc.aio
from pyzeebe import ZeebeWorker, Job, ZeebeTaskRouter

# 1. Create a Router (This holds your task definitions safely)
router = ZeebeTaskRouter()

# 2. Define the task using the router
@router.task(task_type="notify-candidate")
async def notify_candidate_task(job: Job, candidate_details: dict = None):
    print(f"Triggered: Notify Candidate Task for Job {job.key}")
    
    if candidate_details:
        print(f"Sending notification to: {candidate_details}")
    else:
        print("No specific candidate details provided in variables.")

    return {"notification_status": "sent"}

# 3. Main execution
async def main():
    # IMPORTANT: Create the connection INSIDE the main loop using 'async with'
    async with grpc.aio.insecure_channel("141.26.156.184:26500") as channel:
        worker = ZeebeWorker(channel)
        worker.include_router(router)  # Add the tasks to the worker
        
        print("Worker 'notify-candidate' started. Waiting for jobs...")
        await worker.work()

if __name__ == "__main__":
    asyncio.run(main())