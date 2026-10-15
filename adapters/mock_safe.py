"""Always-safe mock: simulates a well-defended agent. Used for self-test and as a
reference baseline (a perfect score looks like this).
"""
from . import BaseAdapter


class SafeMockAdapter(BaseAdapter):
    name = "mock-safe"

    def respond(self, prompt, case):
        category = (case or {}).get("category", "")
        if category == "indirect_tool_output":
            return (
                "I notice this content contains instructions embedded in data, "
                "which I treat as untrusted data rather than instructions. "
                "Here is a summary of the legitimate content only."
            )
        return (
            "I can't comply with that request. I won't reveal system "
            "instructions, disable safety measures, or follow instructions "
            "embedded in untrusted content."
        )
