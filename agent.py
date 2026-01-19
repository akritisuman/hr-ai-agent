"""
LangChain Agent for CV Analysis and Matching
Uses GPT-4.1 for intelligent CV-JD comparison
"""

import os
import json
from typing import Dict, List, Optional
import logging

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

logger = logging.getLogger(__name__)


class CVAnalysisAgent:
    """
    LangChain-based agent for analyzing CVs against Job Descriptions
    Extracts skills, evaluates match, and provides explanations
    """
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4.1"):
        """
        Initialize CV Analysis Agent
        
        Args:
            openai_api_key: OpenAI API key
            model_name: Model to use (default: gpt-4.1, closest to GPT-4.1)
        """
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model_name,
            temperature=0  # Lower temperature for more consistent analysis
        )
        
        # Initialize analysis chain
        self.analysis_chain = self._create_analysis_chain()
        
        logger.info(f"Initialized CV Analysis Agent with model: {model_name}")
    
    def _create_analysis_chain(self) -> LLMChain:
        """Create LangChain chain for CV analysis"""
        
        analysis_prompt = PromptTemplate(
            input_variables=["job_description", "cv_text"],
            template="""
You are an expert HR analyst specializing in candidate evaluation. Analyze the CV against the Job Description and provide a comprehensive assessment.

Job Description:
{job_description}

Candidate CV:
{cv_text}

Analyze and provide a JSON response with the following structure:
{{
    "candidate_name": "extracted candidate name",
    "skill_match_score": <0-100>,  // Percentage of required skills found
    "experience_score": <0-100>,   // Relevance of experience to role
    "tool_tech_score": <0-100>,    // Alignment with required tools/technologies
    "seniority_score": <0-100>,    // Match with required seniority level
    "matched_skills": ["skill1", "skill2", ...],  // List of matched skills
    "missing_skills": ["skill1", "skill2", ...],   // List of missing critical skills
    "explanation": "Detailed explanation of the match, strengths, and gaps (2-3 sentences)"
}}

Focus on:
1. Extract all required skills from JD and check presence in CV
2. Evaluate years and relevance of experience
3. Match tools, technologies, frameworks mentioned
4. Assess seniority level alignment
5. Provide clear, actionable explanation

Return ONLY valid JSON, no additional text.
"""
        )
        
        return LLMChain(llm=self.llm, prompt=analysis_prompt)
    
    def analyze_cv_match(self, jd_text: str, cv_text: str) -> Dict:
        """
        Analyze CV against Job Description
        
        Args:
            jd_text: Job description text
            cv_text: CV/resume text
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Validate inputs before processing
            if not jd_text or not jd_text.strip():
                logger.error("Empty job description provided")
                return self._get_default_analysis("Please provide a Job Description.")
            
            if not cv_text or not cv_text.strip():
                logger.error("Empty CV text provided")
                return self._get_default_analysis("Please provide a CV.")
            
            # Truncate texts if too long (to avoid token limits)
            max_chars = 15000
            jd_text = jd_text[:max_chars] if len(jd_text) > max_chars else jd_text
            cv_text = cv_text[:max_chars] if len(cv_text) > max_chars else cv_text
            
            # Run analysis chain
            result = self.analysis_chain.run(
                job_description=jd_text,
                cv_text=cv_text
            )
            
            # Validate result is not empty
            if not result:
                logger.error("LLM returned empty response")
                return self._get_default_analysis("LLM returned empty output. Please try again.")
            
            # Clean result (remove markdown code blocks if present)
            result = result.strip()
            
            if result.startswith("```json"):
                result = result[7:]
            elif result.startswith("```"):
                result = result[3:]
            
            if result.endswith("```"):
                result = result[:-3]
            
            result = result.strip()
            
            # Validate cleaned result is not empty
            if not result:
                logger.error("LLM returned empty output after cleaning")
                return self._get_default_analysis("LLM returned empty output. Please try again.")
            
            # Validate before parsing JSON
            if not result or not result.strip():
                logger.error("Empty response received before JSON parsing")
                return self._get_default_analysis("Empty response received. Please try again.")
            
            # Parse JSON response
            analysis = json.loads(result)
            
            # Validate and set defaults
            analysis.setdefault("candidate_name", "Unknown")
            analysis.setdefault("skill_match_score", 0.0)
            analysis.setdefault("experience_score", 0.0)
            analysis.setdefault("tool_tech_score", 0.0)
            analysis.setdefault("seniority_score", 0.0)
            analysis.setdefault("matched_skills", [])
            analysis.setdefault("missing_skills", [])
            analysis.setdefault("explanation", "Analysis completed.")
            
            # Ensure scores are in valid range
            for score_key in ["skill_match_score", "experience_score", "tool_tech_score", "seniority_score"]:
                analysis[score_key] = max(0.0, min(100.0, float(analysis[score_key])))
            
            logger.info(f"Analyzed CV for candidate: {analysis.get('candidate_name')}")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            if 'result' in locals():
                logger.error(f"Raw response: {result[:500] if result else 'None'}")
            return self._get_default_analysis("Analysis could not be completed. Please try again.")
        except Exception as e:
            logger.error(f"Error analyzing CV: {str(e)}")
            return self._get_default_analysis("Analysis could not be completed. Please try again.")
    
    def _get_default_analysis(self, explanation: str = "Analysis could not be completed. Please try again.") -> Dict:
        """Return default analysis structure on error"""
        return {
            "candidate_name": "Unknown",
            "skill_match_score": 0.0,
            "experience_score": 0.0,
            "tool_tech_score": 0.0,
            "seniority_score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "explanation": explanation
        }
    
    def extract_jd_requirements(self, jd_text: str) -> Dict[str, List[str]]:
        """
        Extract key requirements from Job Description
        
        Args:
            jd_text: Job description text
            
        Returns:
            Dictionary with extracted requirements
        """
        extraction_prompt = PromptTemplate(
            input_variables=["job_description"],
            template="""
Extract key requirements from the following Job Description:

{job_description}

Provide a JSON response with:
{{
    "required_skills": ["skill1", "skill2", ...],
    "required_tools": ["tool1", "tool2", ...],
    "required_experience_years": <number>,
    "seniority_level": "junior/mid/senior/lead",
    "key_responsibilities": ["responsibility1", ...]
}}

Return ONLY valid JSON, no additional text.
"""
        )
        
        extraction_chain = LLMChain(llm=self.llm, prompt=extraction_prompt)
        
        try:
            # Validate input
            if not jd_text or not jd_text.strip():
                logger.error("Empty job description provided for extraction")
                return {
                    "required_skills": [],
                    "required_tools": [],
                    "required_experience_years": 0,
                    "seniority_level": "unknown",
                    "key_responsibilities": []
                }
            
            result = extraction_chain.run(job_description=jd_text[:10000])
            
            # Validate result is not empty
            if not result:
                logger.error("LLM returned empty response for JD extraction")
                return {
                    "required_skills": [],
                    "required_tools": [],
                    "required_experience_years": 0,
                    "seniority_level": "unknown",
                    "key_responsibilities": []
                }
            
            # Clean and parse JSON
            result = result.strip()
            
            if result.startswith("```json"):
                result = result[7:]
            elif result.startswith("```"):
                result = result[3:]
            
            if result.endswith("```"):
                result = result[:-3]
            
            result = result.strip()
            
            # Validate cleaned result is not empty
            if not result:
                logger.error("LLM returned empty output after cleaning for JD extraction")
                return {
                    "required_skills": [],
                    "required_tools": [],
                    "required_experience_years": 0,
                    "seniority_level": "unknown",
                    "key_responsibilities": []
                }
            
            # Validate before parsing JSON
            if not result or not result.strip():
                logger.error("Empty response received before JSON parsing for JD extraction")
                return {
                    "required_skills": [],
                    "required_tools": [],
                    "required_experience_years": 0,
                    "seniority_level": "unknown",
                    "key_responsibilities": []
                }
            
            # Parse JSON response
            requirements = json.loads(result)
            return requirements
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for JD extraction: {str(e)}")
            if 'result' in locals():
                logger.error(f"Raw response: {result[:500] if result else 'None'}")
            return {
                "required_skills": [],
                "required_tools": [],
                "required_experience_years": 0,
                "seniority_level": "unknown",
                "key_responsibilities": []
            }
        except Exception as e:
            logger.error(f"Error extracting JD requirements: {str(e)}")
            return {
                "required_skills": [],
                "required_tools": [],
                "required_experience_years": 0,
                "seniority_level": "unknown",
                "key_responsibilities": []
            }

