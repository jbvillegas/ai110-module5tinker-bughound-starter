from bughound_agent import BugHoundAgent
import pytest

class RateLimitClient:
    def complete(self, system_prompt, user_prompt):
        raise Exception("Rate limit exceeded: too many requests")

class NetworkErrorClient:
    def complete(self, system_prompt, user_prompt):
        raise Exception("Network connection lost")

class TimeoutErrorClient:
    def complete(self, system_prompt, user_prompt):
        raise Exception("Timeout while waiting for response")

class UnknownErrorClient:
    def complete(self, system_prompt, user_prompt):
        raise Exception("Something unexpected happened")

def test_rate_limit_error_logged():
    agent = BugHoundAgent(client=RateLimitClient())
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)
    assert any("Rate Limit Error" in entry["message"] for entry in result["logs"])

def test_network_error_logged():
    agent = BugHoundAgent(client=NetworkErrorClient())
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)
    assert any("Network/Timeout Error" in entry["message"] for entry in result["logs"])

def test_timeout_error_logged():
    agent = BugHoundAgent(client=TimeoutErrorClient())
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)
    assert any("Network/Timeout Error" in entry["message"] for entry in result["logs"])

def test_unknown_error_logged():
    agent = BugHoundAgent(client=UnknownErrorClient())
    code = "def f():\n    print('hi')\n    return True\n"
    result = agent.run(code)
    assert any("Unknown API Error" in entry["message"] for entry in result["logs"])
