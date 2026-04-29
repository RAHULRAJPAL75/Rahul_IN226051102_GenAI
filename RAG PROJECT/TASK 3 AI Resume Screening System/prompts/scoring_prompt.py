from langchain_core.prompts import PromptTemplate

scoring_prompt = PromptTemplate(
    input_variables=["match_analysis", "job_description"],
    template="""
You are an AI hiring assistant. Based on the match analysis below, assign a fit score from 0 to 100.

Match Analysis:
{match_analysis}

Job Description:
{job_description}

Scoring Criteria:
- Technical Skills Match  → 40 points max
- Tools & Technologies    → 20 points max
- Experience Match        → 25 points max
- Education Match         → 15 points max

STRICT RULES:
- Score must be between 0 and 100.
- Base score ONLY on the match analysis provided.
- Do NOT inflate scores. Be honest and accurate.

Output Format (JSON):
{{
  "skills_score": <0-40>,
  "tools_score": <0-20>,
  "experience_score": <0-25>,
  "education_score": <0-15>,
  "total_score": <0-100>,
  "grade": "<Excellent / Good / Average / Weak>"
}}
"""
)
