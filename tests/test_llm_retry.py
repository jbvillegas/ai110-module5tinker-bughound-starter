from bughound_agent import BugHoundAgent

class DeterministicRetryClient:
    """
    First call returns empty string, second returns valid JSON.
    """
    def __init__(self):
        self.calls = 0
    def complete(self, system_prompt, user_prompt):
        self.calls += 1
        if self.calls == 1:
            return "   "  # Simulate empty output
        return '[{"type": "Code Quality", "severity": "Low", "msg": "Test issue"}]'

def test_llm_analyze_retries_once_and_succeeds():
    client = DeterministicRetryClient()
    agent = BugHoundAgent(client=client)
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)
    # Should succeed on retry, not fallback to heuristics
    assert any(issue.get("type") == "Code Quality" for issue in result["issues"])
    # Should log the retry
    retry_msgs = [entry["message"] for entry in result["logs"] if "Retrying" in entry["message"]]
    assert retry_msgs, "Retry log missing"
    # Should not log fallback to heuristics
    assert not any("Falling back to heuristics" in entry["message"] for entry in result["logs"]), "Should not fallback if retry succeeds"

def test_llm_analyze_retries_and_falls_back():
    class AlwaysEmptyClient:
        def __init__(self):
            self.calls = 0
        def complete(self, system_prompt, user_prompt):
            self.calls += 1
            return "   "
    client = AlwaysEmptyClient()
    agent = BugHoundAgent(client=client)
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)
    # Should fallback to heuristics after two empty outputs
    assert any("Falling back to heuristics" in entry["message"] for entry in result["logs"]), "Should log fallback after retry"
    # Should log the retry
    retry_msgs = [entry["message"] for entry in result["logs"] if "Retrying" in entry["message"]]
    assert retry_msgs, "Retry log missing"
