"""
Local pattern detection for PsychoPy code analysis
"""

import ast
import re
from typing import List, Dict, Any


class PsychoPyPatternDetector:
    """Detects common PsychoPy patterns and anti-patterns in code."""
    
    def __init__(self):
        self.patterns = [
            self._detect_stimulus_in_loop,
            self._detect_trial_loops,
            self._detect_magic_numbers,
            self._detect_inefficient_timing,
            self._detect_missing_cleanup,
            self._detect_resource_loading_in_loop,
        ]
        
    def detect_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Detect all patterns in the given code."""
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            detected = []
            
            for pattern_func in self.patterns:
                try:
                    pattern_results = pattern_func(tree, lines)
                    detected.extend(pattern_results)
                except Exception:
                    # Skip problematic patterns
                    continue
                    
            return detected
            
        except SyntaxError:
            return []
            
    def _detect_stimulus_in_loop(self, tree: ast.AST, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect stimulus creation inside loops."""
        results = []
        
        class LoopVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Look for stimulus creation in for loops
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                        if (hasattr(child.func.value, 'id') and 
                            child.func.value.id == 'visual' and
                            child.func.attr in ['TextStim', 'ImageStim', 'CircleStim', 'RectStim']):
                            
                            results.append({
                                'category': 'performance',
                                'title': f'Stimulus creation in loop ({child.func.attr})',
                                'description': f'Creating {child.func.attr} inside loop is inefficient. Create outside loop and update properties inside.',
                                'code': ast.unparse(child) if hasattr(ast, 'unparse') else str(child.lineno),
                                'suggestion': f'# Create outside loop\nstim = visual.{child.func.attr}(...)\n# Update inside loop\nstim.setText(...) or stim.setPos(...)',
                                'line_numbers': [child.lineno] if hasattr(child, 'lineno') else [],
                                'priority': 4
                            })
                            
                self.generic_visit(node)
                
        visitor = LoopVisitor()
        visitor.visit(tree)
        return results
        
    def _detect_trial_loops(self, tree: ast.AST, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect trial loops that could be TrialHandler."""
        results = []
        
        class TrialLoopVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Look for range() calls that could be trials
                if (isinstance(node.iter, ast.Call) and
                    isinstance(node.iter.func, ast.Name) and
                    node.iter.func.id == 'range' and
                    len(node.iter.args) >= 1):
                    
                    # Check if loop contains stimulus presentation or key collection
                    has_stim = False
                    has_keys = False
                    
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if (isinstance(child.func, ast.Attribute) and
                                hasattr(child.func, 'attr')):
                                if child.func.attr in ['draw', 'present', 'flip']:
                                    has_stim = True
                                elif 'key' in child.func.attr.lower():
                                    has_keys = True
                                    
                    if has_stim or has_keys:
                        results.append({
                            'category': 'builder_mapping',
                            'title': 'Trial loop detected',
                            'description': 'This loop pattern could be implemented using a TrialHandler component in Builder.',
                            'code': f'for {node.target.id} in range({ast.unparse(node.iter.args[0]) if hasattr(ast, "unparse") else "N"}):',
                            'suggestion': 'TrialHandler component with nReps parameter',
                            'line_numbers': [node.lineno] if hasattr(node, 'lineno') else [],
                            'priority': 3
                        })
                        
                self.generic_visit(node)
                
        visitor = TrialLoopVisitor()
        visitor.visit(tree)
        return results
        
    def _detect_magic_numbers(self, tree: ast.AST, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect magic numbers that should be constants."""
        results = []
        magic_contexts = [
            ('key', r'["\']space["\']|["\']return["\']|["\']escape["\']'),
            ('color', r'["\']red["\']|["\']blue["\']|["\']green["\']'),
            ('position', r'\b\d+\.\d+\b|\b\d+\b')
        ]
        
        for i, line in enumerate(lines):
            for context, pattern in magic_contexts:
                matches = re.finditer(pattern, line)
                for match in matches:
                    if context == 'key' and ('key' in line.lower() or 'response' in line.lower()):
                        results.append({
                            'category': 'best_practices',
                            'title': 'Magic key string',
                            'description': 'Define key constants for better maintainability.',
                            'code': match.group(),
                            'suggestion': f'{context.upper()}_RESPONSE = {match.group()}\n# Then use: {context.upper()}_RESPONSE',
                            'line_numbers': [i + 1],
                            'priority': 2
                        })
                        
        return results
        
    def _detect_inefficient_timing(self, tree: ast.AST, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect inefficient timing methods."""
        results = []
        
        class TimingVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if (isinstance(node.func, ast.Attribute) and
                    hasattr(node.func.value, 'id') and
                    node.func.value.id == 'time' and
                    node.func.attr == 'sleep'):
                    
                    results.append({
                        'category': 'performance',
                        'title': 'Inefficient timing with time.sleep()',
                        'description': 'time.sleep() is not precise for stimulus presentation. Use frame-based timing or core.wait().',
                        'code': 'time.sleep(...)',
                        'suggestion': 'core.wait(...) or frame-based timing with win.flip()',
                        'line_numbers': [node.lineno] if hasattr(node, 'lineno') else [],
                        'priority': 3
                    })
                    
                self.generic_visit(node)
                
        visitor = TimingVisitor()
        visitor.visit(tree)
        return results
        
    def _detect_missing_cleanup(self, tree: ast.AST, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect missing cleanup calls."""
        results = []
        
        has_window = any('Window(' in line for line in lines)
        has_close = any('win.close()' in line or '.close()' in line for line in lines)
        has_quit = any('core.quit()' in line for line in lines)
        
        if has_window and not has_close:
            results.append({
                'category': 'best_practices',
                'title': 'Missing window cleanup',
                'description': 'Always close the window with win.close() when done.',
                'code': 'win = visual.Window(...)',
                'suggestion': 'win.close()  # Add at end of experiment',
                'line_numbers': [],
                'priority': 2
            })
            
        if has_window and not has_quit:
            results.append({
                'category': 'best_practices',
                'title': 'Missing core.quit()',
                'description': 'Call core.quit() to ensure proper cleanup.',
                'code': 'End of experiment',
                'suggestion': 'core.quit()  # Add at end of experiment',
                'line_numbers': [],
                'priority': 1
            })
            
        return results
        
    def _detect_resource_loading_in_loop(self, tree: ast.AST, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect resource loading inside loops."""
        results = []
        
        class ResourceLoopVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                        if (hasattr(child.func.value, 'id') and 
                            child.func.value.id == 'sound' and
                            child.func.attr == 'Sound'):
                            
                            results.append({
                                'category': 'performance',
                                'title': 'Sound loading in loop',
                                'description': 'Loading sounds inside loops causes delays. Pre-load before trials.',
                                'code': 'sound.Sound(...) in loop',
                                'suggestion': '# Pre-load sounds\nsounds = [sound.Sound(file) for file in sound_files]\n# Use in loop: sounds[index].play()',
                                'line_numbers': [child.lineno] if hasattr(child, 'lineno') else [],
                                'priority': 4
                            })
                            
                self.generic_visit(node)
                
        visitor = ResourceLoopVisitor()
        visitor.visit(tree)
        return results