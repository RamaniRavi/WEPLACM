import asyncio
import grpc.aio
from pyzeebe import ZeebeWorker, Job, ZeebeTaskRouter

router = ZeebeTaskRouter()

# IMPORTANT: Task type from BPMN Source 46
@router.task(task_type="collect_and_store_cv")
async def collect_cv_task(job: Job):
    print(f"========================================")
    print(f"STARTING TASK: Collect and Store CVs")
    
    # Simulate finding candidates
    # We return 5 candidates so the next gateway says "Yes, candidates found"
    applicants_count = 5 
    
    print(f"Collecting applications from database...")
    print(f"Found {applicants_count} new applicants.")
    print(f"========================================")

    # Return the variable 'applicants_found' which is used in the next Gateway [cite: 8]
    return {
        "applicants_found": applicants_count,
        "applicant_list": ["Candidate A", "Candidate B", "Candidate C"]
    }

async def main():
    print("Worker 'collect_and_store_cv' starting...")
    async with grpc.aio.insecure_channel("141.26.156.184:26500") as channel:
        worker = ZeebeWorker(channel)
        worker.include_router(router)
        await worker.work()

if __name__ == "__main__":
    asyncio.run(main())