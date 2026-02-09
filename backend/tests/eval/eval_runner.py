"""
Eval Runner - Nightly regression framework for quality evaluation.
Runs canonical test cases and reports quality scores.
"""
import asyncio
import json
import structlog
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

logger = structlog.get_logger()


@dataclass
class EvalCase:
    """A single evaluation test case."""
    id: str
    name: str
    input_video: str
    expected_duration_range: tuple[float, float]  # min, max seconds
    expected_min_cuts: int = 1
    expected_max_cuts: int = 50
    max_render_time: int = 300  # seconds
    
    # Quality thresholds
    min_qc_score: int = 6
    max_loudness_variance: float = 3.0  # LUFS
    subtitle_required: bool = False


@dataclass
class EvalResult:
    """Result of a single eval case."""
    case_id: str
    passed: bool
    scores: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0


@dataclass
class EvalReport:
    """Complete evaluation report."""
    timestamp: str
    total_cases: int
    passed: int
    failed: int
    pass_rate: float
    results: List[EvalResult] = field(default_factory=list)
    avg_scores: Dict[str, float] = field(default_factory=dict)


class EvalRunner:
    """
    Runs evaluation test cases and generates reports.
    """
    
    def __init__(self, cases_dir: str = "tests/eval/cases"):
        self.cases_dir = Path(cases_dir)
        self.results_dir = Path("tests/eval/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def load_cases(self) -> List[EvalCase]:
        """Load eval cases from JSON files."""
        cases = []
        
        cases_file = self.cases_dir / "cases.json"
        if cases_file.exists():
            with open(cases_file) as f:
                data = json.load(f)
                for item in data.get("cases", []):
                    cases.append(EvalCase(
                        id=item["id"],
                        name=item["name"],
                        input_video=item["input_video"],
                        expected_duration_range=tuple(item.get("duration_range", [10, 300])),
                        expected_min_cuts=item.get("min_cuts", 1),
                        expected_max_cuts=item.get("max_cuts", 50),
                        max_render_time=item.get("max_render_time", 300),
                        min_qc_score=item.get("min_qc_score", 6),
                    ))
        
        return cases
    
    async def run_case(self, case: EvalCase) -> EvalResult:
        """Run a single eval case."""
        import time
        
        start_time = time.time()
        result = EvalResult(case_id=case.id, passed=True)
        
        try:
            # Import here to avoid circular imports
            from app.graph.workflow import app as langgraph_app
            from app.services.metrics_collector import metrics_collector
            
            # Create test state
            state = {
                "job_id": hash(case.id) % 100000,
                "source_path": case.input_video,
                "user_request": {"mood": "energetic", "pacing": "fast"},
                "tier": "standard",
                "errors": [],
            }
            
            # Run workflow
            final_state = langgraph_app.invoke(state)
            
            # Check QC score
            qc_result = final_state.get("qc_result", {})
            qc_score = qc_result.get("score", 0)
            result.scores["qc"] = qc_score
            
            if qc_score < case.min_qc_score:
                result.passed = False
                result.errors.append(f"QC score {qc_score} < {case.min_qc_score}")
            
            # Check cut count
            cuts = final_state.get("cuts", [])
            result.metrics["cut_count"] = len(cuts)
            
            if len(cuts) < case.expected_min_cuts:
                result.passed = False
                result.errors.append(f"Too few cuts: {len(cuts)}")
            
            if len(cuts) > case.expected_max_cuts:
                result.passed = False
                result.errors.append(f"Too many cuts: {len(cuts)}")
            
            # Check validation
            validation = final_state.get("validation_result", {})
            if not validation.get("passed", True):
                result.passed = False
                result.errors.extend(validation.get("errors", []))
            
            result.scores["validation"] = 10 if validation.get("passed", True) else 0
            
        except Exception as e:
            result.passed = False
            result.errors.append(f"Exception: {str(e)}")
            logger.error("eval_case_failed", case_id=case.id, error=str(e))
        
        result.duration_seconds = time.time() - start_time
        result.metrics["duration_seconds"] = result.duration_seconds
        
        return result
    
    async def run_all(self) -> EvalReport:
        """Run all eval cases and generate report."""
        cases = self.load_cases()
        results = []
        
        logger.info("eval_run_start", case_count=len(cases))
        
        for case in cases:
            logger.info("eval_case_start", case_id=case.id, name=case.name)
            result = await self.run_case(case)
            results.append(result)
            logger.info(
                "eval_case_complete",
                case_id=case.id,
                passed=result.passed,
                duration=result.duration_seconds
            )
        
        # Calculate statistics
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        
        # Average scores
        avg_scores = {}
        all_score_keys = set()
        for r in results:
            all_score_keys.update(r.scores.keys())
        
        for key in all_score_keys:
            scores = [r.scores.get(key, 0) for r in results if key in r.scores]
            if scores:
                avg_scores[key] = sum(scores) / len(scores)
        
        report = EvalReport(
            timestamp=datetime.utcnow().isoformat(),
            total_cases=len(cases),
            passed=passed,
            failed=failed,
            pass_rate=passed / len(cases) if cases else 0,
            results=results,
            avg_scores=avg_scores
        )
        
        # Save report
        self.save_report(report)
        
        logger.info(
            "eval_run_complete",
            passed=passed,
            failed=failed,
            pass_rate=report.pass_rate
        )
        
        return report
    
    def save_report(self, report: EvalReport):
        """Save eval report to JSON."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = self.results_dir / f"eval_{timestamp}.json"
        
        with open(report_path, "w") as f:
            json.dump(asdict(report), f, indent=2)
        
        # Also save as latest
        latest_path = self.results_dir / "latest.json"
        with open(latest_path, "w") as f:
            json.dump(asdict(report), f, indent=2)
        
        logger.info("eval_report_saved", path=str(report_path))


# Sample cases configuration
SAMPLE_CASES = {
    "cases": [
        {
            "id": "talking_head_short",
            "name": "Short Talking Head Video",
            "input_video": "tests/eval/fixtures/talking_head_60s.mp4",
            "duration_range": [15, 45],
            "min_cuts": 3,
            "max_cuts": 15,
            "min_qc_score": 7
        },
        {
            "id": "gameplay_long",
            "name": "Long Gameplay Video",
            "input_video": "tests/eval/fixtures/gameplay_300s.mp4",
            "duration_range": [30, 120],
            "min_cuts": 10,
            "max_cuts": 50,
            "min_qc_score": 6
        },
        {
            "id": "tutorial_medium",
            "name": "Medium Tutorial Video",
            "input_video": "tests/eval/fixtures/tutorial_180s.mp4",
            "duration_range": [60, 120],
            "min_cuts": 5,
            "max_cuts": 25,
            "min_qc_score": 7
        }
    ]
}


if __name__ == "__main__":
    # CLI entry point
    runner = EvalRunner()
    report = asyncio.run(runner.run_all())
    
    print(f"\n{'='*50}")
    print(f"Eval Report: {report.timestamp}")
    print(f"{'='*50}")
    print(f"Total Cases: {report.total_cases}")
    print(f"Passed: {report.passed}")
    print(f"Failed: {report.failed}")
    print(f"Pass Rate: {report.pass_rate:.1%}")
    print(f"\nAverage Scores:")
    for key, value in report.avg_scores.items():
        print(f"  {key}: {value:.2f}")
