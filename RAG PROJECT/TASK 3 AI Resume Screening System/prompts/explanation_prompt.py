from langchain_core.prompts import PromptTemplate

explanation_prompt = PromptTemplate(
    input_variables=["candidate_name", "score_result", "match_analysis", "job_description"],
    template="""
You are an AI recruiter writing a professional evaluation report.

Candidate: {candidate_name}
Score Result: {score_result}
Match Analysis: {match_analysis}
Job Description: {job_description}

Write a clear, professional explanation covering:
1. Overall Assessment   → Summary of the candidate's fit
2. Strengths            → What makes this candidate suitable
3. Weaknesses/Gaps      → What is missing or insufficient
4. Hiring Recommendation → Should the recruiter proceed? (Strongly Recommend / Consider / Not Recommended)

STRICT RULES:
- Base explanation ONLY on the data provided above.
- Do NOT fabricate or assume any skills or experience.
- Keep it professional, concise, and factual (max 200 words).

Output Format (JSON):
{{
  "overall_assessment": "...",
  "strengths": "...",
  "weaknesses": "...",
  "recommendation": "..."
}}
"""
)
