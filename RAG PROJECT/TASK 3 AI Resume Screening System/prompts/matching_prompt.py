from langchain_core.prompts import PromptTemplate

matching_prompt = PromptTemplate(
    input_variables=["extracted_profile", "job_description"],
    template="""
You are a technical recruiter. Compare the candidate's extracted profile with the job description below.

Candidate Profile:
{extracted_profile}

Job Description:
{job_description}

Perform a detailed match analysis:
1. Matched Skills       → Skills present in both profile and job description
2. Missing Skills       → Skills required by job but NOT found in profile
3. Bonus Skills         → Skills in profile but not required (extra value)
4. Experience Match     → Does experience meet the job requirement? (Yes/No + reason)
5. Education Match      → Does education meet the job requirement? (Yes/No + reason)

STRICT RULES:
- Only mark a skill as matched if it is explicitly in the candidate profile.
- Do NOT assume or guess.

Output Format (JSON):
{{
  "matched_skills": [...],
  "missing_skills": [...],
  "bonus_skills": [...],
  "experience_match": "...",
  "education_match": "..."
}}
"""
)
