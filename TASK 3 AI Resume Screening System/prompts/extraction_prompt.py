
from langchain_core.prompts import PromptTemplate

extraction_prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
You are an expert HR analyst. Carefully read the resume below and extract ONLY the information that is explicitly mentioned.

Resume:
{resume}

Extract the following:
1. Technical Skills (programming languages, frameworks, libraries)
2. Tools & Technologies (software, platforms, cloud services)
3. Years of Experience (total professional experience)
4. Education (degree, field, institution)
5. Domain Knowledge (e.g., Machine Learning, Data Analysis, NLP)

STRICT RULES:
- Do NOT assume or infer skills not explicitly written in the resume.
- If a field is not mentioned, write "Not mentioned".
- Be concise and factual.

Output Format (JSON):
{{
  "technical_skills": [...],
  "tools": [...],
  "experience_years": "...",
  "education": "...",
  "domain_knowledge": [...]
}}
"""
)
