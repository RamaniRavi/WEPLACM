import asyncio
import grpc.aio
from pyzeebe import ZeebeWorker, Job, ZeebeTaskRouter
from datetime import datetime

router = ZeebeTaskRouter()

# IMPORTANT: The task_type must match the BPMN exactly, including the typo 'calulate'
@router.task(task_type="calulate_time")
async def calculate_time_task(job: Job):
    print(f"========================================")
    print(f"STARTING TASK: Calculate Time (Typo: 'calulate_time')")
    
    # 1. Get the starting date from variables
    # Based on your Yaak screenshot, it is nested inside hiringRequest -> job_opening
    variables = job.variables
    try:
        start_date_str = variables.get("hiringRequest", {}).get("job_opening", {}).get("starting_date")
        
        if start_date_str:
            # Parse the date (assuming format YYYY-MM-DD from your screenshot)
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            current_date = datetime.now()
            
            # Calculate difference
            delta = start_date - current_date
            days_diff = delta.days
            print(f"Start Date: {start_date_str}")
            print(f"Calculated Difference: {days_diff} days")
        else:
            # Fallback if variable is missing (for testing)
            print("WARNING: 'starting_date' not found. Using default testing value.")
            days_diff = 45 # Sets it to the '30-60 days' path
            
    except Exception as e:
        print(f"Error parsing date: {e}")
        days_diff = 45 # Fallback to ensure process continues

    print(f"========================================")

    # 2. Return the variable required by the next Gateway
    return {"joining_date_difference": days_diff}

async def main():
    print("Worker 'calculate_time' starting...")
    async with grpc.aio.insecure_channel("141.26.156.184:26500") as channel:
        worker = ZeebeWorker(channel)
        worker.include_router(router)
        await worker.work()

if __name__ == "__main__":
    asyncio.run(main())