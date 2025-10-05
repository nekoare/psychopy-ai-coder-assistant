from psychopy_ai_coder_assistant.analyzer import CodeSuggestion, CodeAnalyzer
from psychopy_ai_coder_assistant.config import ConfigManager


class _DummyConfig(ConfigManager):
    def __init__(self):
        pass
    def get_enabled_features(self):
        return {"builder_mapping": True, "performance_optimization": True, "best_practices": True}


def test_highest_priority_kept_for_duplicates():
    analyzer = CodeAnalyzer(_DummyConfig())
    suggestions = [
        CodeSuggestion('performance', 'Low', 'd', 'same-code', '', [], 1),
        CodeSuggestion('performance', 'High', 'd', 'same-code', '', [], 5),
        CodeSuggestion('performance', 'Mid', 'd', 'same-code', '', [], 3),
    ]
    result = analyzer._filter_and_prioritize(suggestions)
    # 重複は 1 件に統合され最高 priority=5 が保持される
    assert len([s for s in result if s.original_code == 'same-code']) == 1
    assert result[0].priority == 5