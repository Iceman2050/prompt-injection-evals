"""HTTP adapter: POSTs the attack to a real target endpoint.

Protocol:
  - single-turn case:  POST {"prompt": <text>, "case_id": <id>}
  - multi-turn case:   POST {"messages": [{"role": "user", "content": ...}, ...],
                             "case_id": <id>}
  - expects response: {"response": <model text>}  (also accepts {"text": ...})

AUTHORIZATION: only test agents you own or have explicit written permission to
test. The runner prints a notice and requires --target; never point this at a
third-party service without authorization.
"""
import json
import urllib.request

from . import BaseAdapter


class HttpAdapter(BaseAdapter):
    name = "http"

    def __init__(self, target, timeout=60):
        if not target or not target.startswith(("http://", "https://")):
            raise ValueError("--target must be an http(s) URL")
        self.target = target
        self.timeout = timeout

    def respond(self, prompt, case):
        case = case or {}
        if case.get("turns"):
            payload = {
                "case_id": case.get("id"),
                "messages": [{"role": "user", "content": t} for t in case["turns"]],
            }
        else:
            payload = {"case_id": case.get("id"), "prompt": prompt}
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.target, data=body, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace"))
        except Exception as exc:  # transport failure -> explicit error, not a score
            raise RuntimeError("HTTP adapter request failed: %s" % exc)
        if isinstance(data, dict):
            for key in ("response", "text", "output", "reply"):
                if isinstance(data.get(key), str):
                    return data[key]
        raise RuntimeError("HTTP adapter: target returned no usable 'response' field")
