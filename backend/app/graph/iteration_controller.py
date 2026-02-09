"""
Iteration Controller - Manages Planner-Critic-Executor iteration loop.
Implements max iterations and confidence thresholds for quality control.
"""
import structlog
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = structlog.get_logger()


@dataclass
class IterationConfig:
    """Configuration for iteration control."""
    max_iterations: int = 3
    min_confidence: float = 0.7
    improvement_threshold: float = 0.1  # Minimum score improvement to continue
    timeout_seconds: int = 300


@dataclass
class IterationState:
    """State tracking for iteration loop."""
    iteration: int = 0
    previous_score: float = 0.0
    current_score: float = 0.0
    converged: bool = False
    reason: str = ""


class IterationController:
    """
    Controls the Planner-Critic-Executor iteration loop.
    
    Flow:
    1. Planner (Director) creates initial plan
    2. Critic (QC Gate) evaluates plan quality
    3. If score < threshold, feedback is sent to Planner for revision
    4. Loop continues until:
       - Score meets threshold
       - Max iterations reached
       - No improvement between iterations
    """
    
    def __init__(self, config: Optional[IterationConfig] = None):
        self.config = config or IterationConfig()
        self.state = IterationState()
    
    def should_iterate(self, qc_score: float, qc_feedback: Dict[str, Any]) -> bool:
        """
        Determine if another iteration is needed.
        
        Returns True if:
        - Score is below threshold AND
        - Max iterations not reached AND
        - Score is improving
        """
        self.state.iteration += 1
        self.state.previous_score = self.state.current_score
        self.state.current_score = qc_score
        
        normalized_score = qc_score / 10.0  # Assuming 0-10 scale
        
        # Check if we've met the quality threshold
        if normalized_score >= self.config.min_confidence:
            self.state.converged = True
            self.state.reason = f"Quality threshold met: {normalized_score:.2f} >= {self.config.min_confidence}"
            logger.info(
                "iteration_converged",
                iteration=self.state.iteration,
                score=qc_score,
                reason=self.state.reason
            )
            return False
        
        # Check max iterations
        if self.state.iteration >= self.config.max_iterations:
            self.state.converged = False
            self.state.reason = f"Max iterations reached: {self.state.iteration}"
            logger.warning(
                "iteration_max_reached",
                iteration=self.state.iteration,
                score=qc_score
            )
            return False
        
        # Check if score is improving
        if self.state.iteration > 1:
            improvement = self.state.current_score - self.state.previous_score
            if improvement < self.config.improvement_threshold:
                self.state.converged = False
                self.state.reason = f"No improvement: {improvement:.2f} < {self.config.improvement_threshold}"
                logger.warning(
                    "iteration_no_improvement",
                    iteration=self.state.iteration,
                    improvement=improvement
                )
                return False
        
        logger.info(
            "iteration_continue",
            iteration=self.state.iteration,
            score=qc_score,
            target=self.config.min_confidence * 10
        )
        return True
    
    def get_revision_prompt(self, qc_feedback: Dict[str, Any]) -> str:
        """
        Generate a revision prompt for the Planner based on Critic feedback.
        """
        issues = qc_feedback.get("issues", [])
        suggestions = qc_feedback.get("suggestions", [])
        score = qc_feedback.get("score", 0)
        verdict = qc_feedback.get("verdict", "")
        
        prompt_parts = [
            f"## Revision Required (Iteration {self.state.iteration}/{self.config.max_iterations})",
            f"Current quality score: {score}/10",
            f"Verdict: {verdict}",
            "",
            "### Issues to Address:",
        ]
        
        for i, issue in enumerate(issues, 1):
            prompt_parts.append(f"{i}. {issue}")
        
        if suggestions:
            prompt_parts.append("")
            prompt_parts.append("### Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                prompt_parts.append(f"{i}. {suggestion}")
        
        prompt_parts.extend([
            "",
            "Please revise the edit plan to address these issues while maintaining the original creative intent.",
            f"Target score: {self.config.min_confidence * 10}/10 or higher."
        ])
        
        return "\n".join(prompt_parts)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get iteration summary for logging/reporting."""
        return {
            "total_iterations": self.state.iteration,
            "final_score": self.state.current_score,
            "converged": self.state.converged,
            "reason": self.state.reason,
            "max_iterations": self.config.max_iterations,
            "min_confidence": self.config.min_confidence,
        }
    
    def reset(self):
        """Reset state for a new job."""
        self.state = IterationState()


def create_iteration_node(config: Optional[IterationConfig] = None):
    """
    Create a LangGraph node that manages iteration.
    """
    from ..state import GraphState
    
    controller = IterationController(config)
    
    def iteration_node(state: GraphState) -> GraphState:
        """Node that decides whether to iterate or proceed."""
        qc_result = state.get("qc_result", {})
        qc_score = qc_result.get("score", 0)
        
        # Track retry count
        retry_count = state.get("retry_count", 0)
        
        if controller.should_iterate(qc_score, qc_result):
            # Need another iteration
            revision_prompt = controller.get_revision_prompt(qc_result)
            
            return {
                **state,
                "retry_count": retry_count + 1,
                "revision_prompt": revision_prompt,
                "iteration_summary": controller.get_summary(),
                "should_revise": True,
            }
        else:
            # Done iterating
            return {
                **state,
                "iteration_summary": controller.get_summary(),
                "should_revise": False,
            }
    
    return iteration_node


def should_revise(state: Dict[str, Any]) -> str:
    """Conditional edge function for iteration loop."""
    if state.get("should_revise", False):
        return "revise"
    return "proceed"
