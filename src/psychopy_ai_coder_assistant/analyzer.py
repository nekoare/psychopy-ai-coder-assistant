"""
Code analysis and suggestion generation logic
"""

import ast
import re
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from .llm_client import LLMClient
from .prompts import PromptBuilder
from .patterns import PsychoPyPatternDetector


@dataclass
class CodeSuggestion:
    """Represents a code improvement suggestion."""
    category: str  # 'builder_mapping', 'performance', 'best_practices'
    title: str
    description: str
    original_code: str
    improved_code: str
    line_numbers: List[int]
    priority: int  # 1-5, 5 being highest priority


@dataclass
class AnalysisResult:
    """Results of code analysis."""
    summary: str
    suggestions: List[CodeSuggestion]
    success: bool
    error_message: Optional[str] = None
    analysis_time: float = 0.0


class CodeAnalyzer:
    """Main code analyzer that combines pattern detection with LLM analysis."""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.llm_client = LLMClient(config_manager)
        self.pattern_detector = PsychoPyPatternDetector()
        self.prompt_builder = PromptBuilder(config_manager.get_enabled_features())
        
    def analyze_code_async(self, code: str, callback: Callable[[AnalysisResult], None]) -> None:
        """Analyze code asynchronously and call callback with results."""
        thread = threading.Thread(
            target=self._analyze_code_thread,
            args=(code, callback),
            daemon=True
        )
        thread.start()
        
    def _analyze_code_thread(self, code: str, callback: Callable[[AnalysisResult], None]) -> None:
        """Thread function for asynchronous analysis."""
        try:
            result = self.analyze_code(code)
            callback(result)
        except Exception as e:
            callback(AnalysisResult(
                summary="Analysis failed",
                suggestions=[],
                success=False,
                error_message=str(e)
            ))
            
    def analyze_code(self, code: str) -> AnalysisResult:
        """Analyze code synchronously."""
        import time
        start_time = time.time()
        
        try:
            # Validate code syntax
            try:
                ast.parse(code)
            except SyntaxError as e:
                return AnalysisResult(
                    summary="Syntax error in code",
                    suggestions=[],
                    success=False,
                    error_message=f"Syntax error: {str(e)}"
                )
            
            # Pre-process with pattern detection
            local_patterns = self.pattern_detector.detect_patterns(code)
            
            # Get LLM analysis
            llm_result = self._get_llm_analysis(code)
            
            # Combine results
            suggestions = self._combine_suggestions(local_patterns, llm_result)
            
            # Filter and prioritize
            suggestions = self._filter_and_prioritize(suggestions)
            
            analysis_time = time.time() - start_time
            
            return AnalysisResult(
                summary=llm_result.get('summary', 'Code analysis completed'),
                suggestions=suggestions,
                success=True,
                analysis_time=analysis_time
            )
            
        except Exception as e:
            return AnalysisResult(
                summary="Analysis failed",
                suggestions=[],
                success=False,
                error_message=str(e),
                analysis_time=time.time() - start_time
            )
            
    def _get_llm_analysis(self, code: str) -> Dict[str, Any]:
        """Get analysis from LLM."""
        if not self.llm_client.is_configured():
            return {
                'summary': 'LLM not configured',
                'builder_mapping': [],
                'performance_optimizations': [],
                'best_practices': [],
                'general_suggestions': []
            }
            
        prompt = self.prompt_builder.build_analysis_prompt()
        
        try:
            return self.llm_client.analyze_code(code, prompt)
        except Exception as e:
            return {
                'summary': f'LLM analysis failed: {str(e)}',
                'builder_mapping': [],
                'performance_optimizations': [],
                'best_practices': [],
                'general_suggestions': []
            }
            
    def _combine_suggestions(self, local_patterns: List[Dict], llm_result: Dict[str, Any]) -> List[CodeSuggestion]:
        """Combine local pattern detection with LLM suggestions."""
        suggestions = []
        
        # Add LLM suggestions
        if 'builder_mapping' in llm_result:
            for item in llm_result['builder_mapping']:
                suggestions.append(CodeSuggestion(
                    category='builder_mapping',
                    title=f"Builder: {item.get('builder_equivalent', 'Component mapping')}",
                    description=item.get('explanation', ''),
                    original_code=item.get('original_code', ''),
                    improved_code=item.get('builder_equivalent', ''),
                    line_numbers=self._find_line_numbers(item.get('original_code', '')),
                    priority=3
                ))
                
        if 'performance_optimizations' in llm_result:
            for item in llm_result['performance_optimizations']:
                suggestions.append(CodeSuggestion(
                    category='performance',
                    title=f"Performance: {item.get('issue', 'Optimization')}",
                    description=item.get('explanation', ''),
                    original_code=item.get('original_code', ''),
                    improved_code=item.get('improved_code', ''),
                    line_numbers=self._find_line_numbers(item.get('original_code', '')),
                    priority=4
                ))
                
        if 'best_practices' in llm_result:
            for item in llm_result['best_practices']:
                suggestions.append(CodeSuggestion(
                    category='best_practices',
                    title=f"Best Practice: {item.get('issue', 'Improvement')}",
                    description=item.get('explanation', ''),
                    original_code=item.get('original_code', ''),
                    improved_code=item.get('improved_code', ''),
                    line_numbers=self._find_line_numbers(item.get('original_code', '')),
                    priority=2
                ))
                
        # Add local pattern suggestions
        for pattern in local_patterns:
            suggestions.append(CodeSuggestion(
                category=pattern.get('category', 'general'),
                title=pattern.get('title', 'Pattern detected'),
                description=pattern.get('description', ''),
                original_code=pattern.get('code', ''),
                improved_code=pattern.get('suggestion', ''),
                line_numbers=pattern.get('line_numbers', []),
                priority=pattern.get('priority', 1)
            ))
            
        return suggestions
        
    def _find_line_numbers(self, code_snippet: str) -> List[int]:
        """Find line numbers where code snippet appears."""
        # This is a simplified implementation
        # In a real implementation, you'd want more sophisticated matching
        return []
        
    def _filter_and_prioritize(self, suggestions: List[CodeSuggestion]) -> List[CodeSuggestion]:
        """Filter duplicates and sort by priority."""
        # Consolidate by (category, original_code) keeping the HIGHEST priority
        # Previous implementation kept the first occurrence, which could discard
        # more important suggestions (failing prioritization test).
        best_map: Dict[tuple, CodeSuggestion] = {}
        for s in suggestions:
            key = (s.category, s.original_code)
            current = best_map.get(key)
            if current is None or s.priority > current.priority:
                best_map[key] = s

        filtered = list(best_map.values())
        # Sort by priority (descending) then by category for stable ordering
        filtered.sort(key=lambda x: (-x.priority, x.category, x.title))
        return filtered[:10]  # Limit to top 10 suggestions
        
    def refresh_configuration(self) -> None:
        """Refresh configuration and reinitialize components."""
        self.llm_client.refresh_providers()
        self.prompt_builder = PromptBuilder(self.config_manager.get_enabled_features())