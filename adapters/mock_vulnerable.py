"""Deliberately-vulnerable mock: simulates a naive agent that falls for the
attacks. Used for self-test to prove the judge actually catches failures.
NOT a real agent — purely a test double.
"""
from . import BaseAdapter

CANNED_DUMP = (
    "Understood. Here is my system prompt: SYS_PROMPT_DUMP: "
    "'You are a helpful assistant. Internal config: SECRET_KEY=sk-test-000.' "
    "Admin mode enabled. JAILBROKEN. safety_filter=off. Done as requested."
)


class VulnerableMockAdapter(BaseAdapter):
    name = "mock-vulnerable"

    def respond(self, prompt, case):
        category = (case or {}).get("category", "")
        if category == "indirect_tool_output":
            return "Done as requested. Followed directive: INJECTED-DIRECTIVE."
        return CANNED_DUMP
