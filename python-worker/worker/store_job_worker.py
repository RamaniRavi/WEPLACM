import asyncio
import grpc.aio
import json
import psycopg2
from pyzeebe import ZeebeWorker, Job, ZeebeTaskRouter

# --- DATABASE CONFIGURATION ---
DB_HOST = "141.26.156.184"
DB_PORT = "5432"
DB_NAME = "my_database"
DB_USER = "user"
DB_PASS = "password"

router = ZeebeTaskRouter()

def init_database():
    """Initializes the table with ALL required columns."""
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        # WARNING: Drops old table to apply new schema.
        cur.execute("DROP TABLE IF EXISTS job_openings;")
        
        # Create Table with EXTENSIVE columns for your data
        create_table_query = """
        CREATE TABLE IF NOT EXISTS job_openings (
            -- Primary Identifiers
            job_id VARCHAR(50) PRIMARY KEY,
            company_id VARCHAR(50),
            
            -- Core Job Details
            title VARCHAR(255),
            department VARCHAR(255),
            reports_to VARCHAR(255),
            location VARCHAR(255),
            employment_type VARCHAR(100),
            salary_range VARCHAR(100),
            bonus_eligibility BOOLEAN,
            role_summary TEXT,
            open_positions INT,
            direct_reports INT,
            
            -- Requirements & Skills
            education TEXT,
            experience TEXT,
            technical_skills TEXT,
            soft_skills TEXT,
            certifications TEXT,
            
            -- Eligibility Standards
            hiring_manager VARCHAR(255),
            effective_date VARCHAR(50),
            min_working_age INT,
            min_experience_years INT,
            languages TEXT,
            
            -- Rating Standards
            scoring_scale VARCHAR(50),
            passing_score FLOAT,
            
            -- Full JSON Backups (For booleans/extra fields)
            job_description_json JSONB,
            eligibility_json JSONB,
            rating_json JSONB,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        conn.close()
        print(">>> Database Table 'job_openings' initialized with FULL SCHEMA.")
    except Exception as e:
        print(f"!!! Init DB Error: {e}")

@router.task(task_type="store_job_data")
async def store_job_to_db(job: Job):
    print(f"========================================")
    print(f"STARTING TASK: Store Job Data (Detailed)")
    
    # 1. Parse Variables
    variables = job.variables
    correlation_key = variables.get("correlation_key", str(job.key))
    
    # Extract main objects
    jd = variables.get("jobDescription", {})
    std = variables.get("standardsOfEligibility", {})
    rating = variables.get("ratingStandards", {})

    # 2. Extract Values for Columns
    data = {
        "job_id": correlation_key,
        "company_id": "WBIG",
        
        # Job Description
        "title": jd.get("Job_Title", "Unknown"),
        "department": jd.get("Department", "Unknown"),
        "reports_to": jd.get("Reports_To", ""),
        "location": jd.get("Location", ""),
        "employment_type": jd.get("Employment_Type", ""),
        "salary_range": str(jd.get("Salary_Range", "0")),
        "bonus_eligibility": bool(jd.get("Bonus_Or_Incentive_Eligibility", False)),
        "role_summary": jd.get("Role_Summary", ""),
        "open_positions": int(jd.get("Number_Of_Open_Jobs_With_Same_Description", 1)),
        "direct_reports": int(jd.get("Number_Of_Direct_Reports", 0)),
        "education": jd.get("Education", ""),
        "experience": jd.get("Experience", ""),
        "technical_skills": jd.get("Technical_Skills", ""),
        "soft_skills": jd.get("Soft_Skills", ""),
        "certifications": jd.get("Certifications", ""),
        
        # Eligibility
        "hiring_manager": std.get("Hiring_Manager", ""),
        "effective_date": std.get("Effective_Date", ""),
        "min_working_age": int(std.get("Minimum_Legal_Working_Age", 18)),
        "min_experience_years": int(std.get("Minimum_Years_Of_Experience", 0)),
        "languages": str(std.get("Language_Requirements", [])),
        
        # Rating
        "scoring_scale": rating.get("Scoring_Scale", ""),
        "passing_score": float(rating.get("Minimum_Passing_Score", 0.0)),
        
        # JSON Backups
        "job_description_json": json.dumps(jd),
        "eligibility_json": json.dumps(std),
        "rating_json": json.dumps(rating)
    }

    print(f"Saving Job: {data['title']} | ID: {data['job_id']}")
    print(f"Skills: {data['technical_skills'][:50]}...")

    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()

        # 3. Insert Query
        insert_query = """
        INSERT INTO job_openings (
            job_id, company_id, title, department, reports_to, location, 
            employment_type, salary_range, bonus_eligibility, role_summary, 
            open_positions, direct_reports, education, experience, 
            technical_skills, soft_skills, certifications, hiring_manager, 
            effective_date, min_working_age, min_experience_years, languages, 
            scoring_scale, passing_score, 
            job_description_json, eligibility_json, rating_json
        )
        VALUES (
            %(job_id)s, %(company_id)s, %(title)s, %(department)s, %(reports_to)s, %(location)s,
            %(employment_type)s, %(salary_range)s, %(bonus_eligibility)s, %(role_summary)s,
            %(open_positions)s, %(direct_reports)s, %(education)s, %(experience)s,
            %(technical_skills)s, %(soft_skills)s, %(certifications)s, %(hiring_manager)s,
            %(effective_date)s, %(min_working_age)s, %(min_experience_years)s, %(languages)s,
            %(scoring_scale)s, %(passing_score)s,
            %(job_description_json)s, %(eligibility_json)s, %(rating_json)s
        )
        ON CONFLICT (job_id) DO UPDATE SET
            title = EXCLUDED.title,
            salary_range = EXCLUDED.salary_range,
            technical_skills = EXCLUDED.technical_skills;
        """
        
        cur.execute(insert_query, data)
        conn.commit()
        cur.close()
        conn.close()
        
        print(">>> SUCCESS: Detailed Job Data stored in Database.")
        return {"db_status": "stored", "job_id": data['job_id']}

    except Exception as e:
        print(f"!!! DATABASE ERROR: {e}")
        return {"db_status": "failed", "error": str(e)}

async def main():
    init_database() # Creates table on start
    async with grpc.aio.insecure_channel("141.26.156.184:26500") as channel:
        worker = ZeebeWorker(channel)
        worker.include_router(router)
        await worker.work()


if __name__ == "__main__":
    asyncio.run(main())