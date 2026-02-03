import asyncio
import grpc.aio
import random
from pyzeebe import ZeebeWorker, Job, ZeebeTaskRouter

router = ZeebeTaskRouter()

# IMPORTANT: Task type matches the BPMN definition
@router.task(task_type="ats-score")
async def ats_score_task(job: Job):
    print(f"========================================")
    print(f"STARTING TASK: Check ATS Score")
    
    # 1. Generate a random score
    # We force a score between 75 and 99 to ensure we pass the next gateway
    # (The BPMN requires ats_score >= 75 to proceed to the 'Happy Path')
    score = random.randint(75, 99) 
    
    print(f"Analyzing Candidate Data...")
    print(f"ATS Score Generated: {score}/100")
    print(f"Result: PASSED (>= 75)")
    print(f"========================================")

    # 2. Return the 'ats_score' variable required by the next Gateway
    return {"ats_score": score}

async def main():
    print("Worker 'ats-score' starting...")
    # Standard AsyncIO connection
    async with grpc.aio.insecure_channel("141.26.156.184:26500") as channel:
        worker = ZeebeWorker(channel)
        worker.include_router(router)
        await worker.work()

if __name__ == "__main__":
    asyncio.run(main())