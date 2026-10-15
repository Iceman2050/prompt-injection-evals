"""Adapter interface: every adapter implements ``respond(prompt, case) -> str``.

``prompt`` is the text sent to the target (the attack). ``case`` is the full
case dict (id, category, ...), which adapters may use to tailor behaviour.
The http adapter ignores ``case`` and just sends the prompt.
"""


class BaseAdapter:
    name = "base"

    def respond(self, prompt, case):  # pragma: no cover - interface only
        raise NotImplementedError
