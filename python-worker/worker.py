import asyncio
from pyzeebe import ZeebeWorker, create_insecure_channel, Job, JobController

def register_prepare_missing_requirements(worker: ZeebeWorker) -> None:
    @worker.task(task_type="prepare-missing-requirements")
    async def prepare_missing_requirements(job: Job):
        print("Worker: prepare-missing-requirements")
        variables = job.variables

        hiring_request = variables.get("hiringRequest", {})
        job_opening = hiring_request.get("job_opening", {})
        requirements = job_opening.get("requirements", {})
        employment = job_opening.get("employment_details", {})

        missing = []

        if not job_opening.get("job_title"):
            missing.append("Job title")

        if not job_opening.get("job_description"):
            missing.append("Job description")

        if not requirements.get("education"):
            missing.append("Education")

        if not requirements.get("technical_skills"):
            missing.append("Technical skills")

        if not employment.get("salary_range", {}).get("min"):
            missing.append("Minimum salary")

        if not employment.get("salary_range", {}).get("max"):
            missing.append("Maximum salary")

        email_body = (
            "Hello WBIG Team,\n\n"
            "The following required information is missing in your hiring request:\n\n"
            + "\n".join(f"- {field}" for field in missing) +
            "\n\nPlease update and resubmit the request.\n\n"
            "Best regards,\nRecruitment Team"
        )

        return {
            "missingRequirements": {"count": len(missing), "fields": missing},
            "notification": {"subject": "Missing information in hiring request", "body": email_body},
        }
    
def register_capture_joining_date(worker: ZeebeWorker) -> None:
    @worker.task(task_type="requested_joining_date")
    async def capture_joining_date(job: Job):
        variables = job.variables
        hiring_request = variables.get("hiringRequest", {})
        job_opening = hiring_request.get("job_opening", {})

        # adjust the key to match your real request structure
        joining_date = job_opening.get("starting_date") or hiring_request.get("requested_joining_date")

        return {
            "requestedJoiningDate": joining_date
        }

# def register_create_job_posting_template(worker: ZeebeWorker) -> None:
#     @worker.task(task_type="create-job-posting-template")
#     async def create_job_posting_template(job: Job):
#         # TODO: implement
#         return {"templateCreated": True}


# def register_send_missing_requirements(worker: ZeebeWorker) -> None:
#     @worker.task(task_type="send-missing-requirements-email")
#     async def send_missing_requirements_email(job: Job):
#         # TODO: implement email sending
#         return {"emailSent": True}


async def main():
    channel = create_insecure_channel(grpc_address="141.26.156.184:26500")
    print("Channel created")
    worker = ZeebeWorker(channel)
    print("Worker created")
    
    # Register all task handlers
    register_prepare_missing_requirements(worker)
    register_capture_joining_date(worker)
    # register_create_job_posting_template(worker)
    # register_send_missing_requirements(worker)

    await worker.work()

if __name__ == "__main__":
    asyncio.run(main())
