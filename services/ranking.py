"""
Ranking Logic for CV Matching
Multi-factor scoring system for candidate evaluation
"""

from typing import List, Dict, Optional
from pathlib import Path
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CandidateScore:
    """Structured candidate scoring result"""
    candidate_name: str
    file_path: str
    match_score: float  # 0-100
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: str
    skill_match_score: float
    experience_score: float
    tool_tech_score: float
    seniority_score: float
    semantic_score: float


class RankingEngine:
    """
    Ranking engine that scores candidates based on multiple factors
    Uses AI agent analysis combined with semantic similarity
    """
    
    # Weight configuration for different scoring factors
    WEIGHTS = {
        "skill_match": 0.40,      # Highest weight - skills are critical
        "experience": 0.25,        # Relevant experience matters
        "tool_tech": 0.20,        # Tools and technologies alignment
        "seniority": 0.10,        # Role seniority match
        "semantic": 0.05          # Overall semantic similarity
    }
    
    def __init__(self, agent_analyzer):
        """
        Initialize ranking engine
        
        Args:
            agent_analyzer: LangChain agent for CV analysis
        """
        self.agent_analyzer = agent_analyzer
        logger.info("Initialized ranking engine")
    
    def rank_candidates(
        self,
        jd_text: str,
        cv_data: Dict[str, str],
        semantic_scores: Dict[str, float],
        session_id: str
    ) -> List[CandidateScore]:
        """
        Rank candidates based on multiple factors
        
        Args:
            jd_text: Job description text
            cv_data: Dict mapping file_path -> CV text
            semantic_scores: Dict mapping file_path -> semantic similarity score
            session_id: Session identifier
            
        Returns:
            List of CandidateScore objects, sorted by match_score (descending)
        """
        candidate_scores = []
        
        for file_path, cv_text in cv_data.items():
            if cv_text is None:
                continue
            
            logger.info(f"Ranking candidate: {file_path}")
            
            # Get AI agent analysis
            analysis = self.agent_analyzer.analyze_cv_match(jd_text, cv_text)
            
            # Extract scores from analysis
            skill_match_score = analysis.get("skill_match_score", 0.0)
            experience_score = analysis.get("experience_score", 0.0)
            tool_tech_score = analysis.get("tool_tech_score", 0.0)
            seniority_score = analysis.get("seniority_score", 0.0)
            
            # Get semantic score (normalize to 0-100)
            semantic_score = semantic_scores.get(file_path, 0.0) * 100
            
            # Calculate weighted final score
            final_score = (
                skill_match_score * self.WEIGHTS["skill_match"] +
                experience_score * self.WEIGHTS["experience"] +
                tool_tech_score * self.WEIGHTS["tool_tech"] +
                seniority_score * self.WEIGHTS["seniority"] +
                semantic_score * self.WEIGHTS["semantic"]
            )
            
            # Ensure score is in 0-100 range
            final_score = max(0.0, min(100.0, final_score))
            
            candidate_score = CandidateScore(
                candidate_name=analysis.get("candidate_name", Path(file_path).stem),
                file_path=file_path,
                match_score=round(final_score, 2),
                matched_skills=analysis.get("matched_skills", []),
                missing_skills=analysis.get("missing_skills", []),
                explanation=analysis.get("explanation", ""),
                skill_match_score=round(skill_match_score, 2),
                experience_score=round(experience_score, 2),
                tool_tech_score=round(tool_tech_score, 2),
                seniority_score=round(seniority_score, 2),
                semantic_score=round(semantic_score, 2)
            )
            
            candidate_scores.append(candidate_score)
        
        # Sort by match score (descending)
        candidate_scores.sort(key=lambda x: x.match_score, reverse=True)
        
        logger.info(f"Ranked {len(candidate_scores)} candidates")
        return candidate_scores
    
    def get_top_candidates(
        self,
        ranked_candidates: List[CandidateScore],
        top_n: int = 3
    ) -> List[CandidateScore]:
        """
        Get top N candidates from ranked list
        
        Args:
            ranked_candidates: List of ranked CandidateScore objects
            top_n: Number of top candidates to return
            
        Returns:
            Top N candidates
        """
        return ranked_candidates[:top_n]

