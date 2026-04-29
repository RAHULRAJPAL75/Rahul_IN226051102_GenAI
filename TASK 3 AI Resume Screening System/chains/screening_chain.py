
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from prompts import (
    extraction_prompt,
    matching_prompt,
    scoring_prompt,
    explanation_prompt,
)


def build_llm(api_key: str, provider: str = "gemini", model: str = None, temperature: float = 0.0):
    """
    Initialize LLM via LangChain.
    
    Providers:
    - gemini: Google Gemini (FREE) - RECOMMENDED
    - openai: OpenAI GPT (PAID)
    """
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model or "gemini-pro",
            temperature=temperature,
            google_api_key=api_key
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or "gpt-3.5-turbo",
            temperature=temperature,
            openai_api_key=api_key
        )
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'gemini' or 'openai'")


def build_screening_pipeline(llm):
    """
    Build the full 4-step LCEL screening pipeline.
    Each step feeds its output into the next step.
    """

    parser = StrOutputParser()

    extraction_chain = extraction_prompt | llm | parser

    matching_chain = matching_prompt | llm | parser

    scoring_chain = scoring_prompt | llm | parser

    explanation_chain = explanation_prompt | llm | parser

    def run_full_pipeline(inputs: dict) -> dict:
        """
        Runs all 4 pipeline steps sequentially.
        inputs must contain: resume, job_description, candidate_name
        """
        resume          = inputs["resume"]
        job_description = inputs["job_description"]
        candidate_name  = inputs["candidate_name"]

        extracted_profile = extraction_chain.invoke({"resume": resume})

        match_analysis = matching_chain.invoke({
            "extracted_profile": extracted_profile,
            "job_description": job_description
        })
        
        score_result = scoring_chain.invoke({
            "match_analysis": match_analysis,
            "job_description": job_description
        })

        explanation = explanation_chain.invoke({
            "candidate_name": candidate_name,
            "score_result": score_result,
            "match_analysis": match_analysis,
            "job_description": job_description
        })

        return {
            "candidate_name"   : candidate_name,
            "extracted_profile": extracted_profile,
            "match_analysis"   : match_analysis,
            "score_result"     : score_result,
            "explanation"      : explanation
        }

    return RunnableLambda(run_full_pipeline)
