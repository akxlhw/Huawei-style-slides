"""Abstract LLM client: Claude Code default, GLM optional."""

import os
import json
from typing import Optional


class LLMClient:
    def __init__(self, backend: Optional[str] = None):
        self.backend = (backend or os.getenv("PPT_LLM_BACKEND", "claude")).lower()

    def validate_config(self) -> None:
        if self.backend == "glm":
            key = os.getenv("GLM_API_KEY")
            if not key:
                raise SystemExit(
                    "ERROR: GLM_API_KEY is not set.\n"
                    "  export GLM_API_KEY='your-key'"
                )

    def complete(self, prompt: str, temperature: float = 0.7, json_mode: bool = False) -> str:
        """Return raw text completion.

        When running inside Claude Code, 'claude' backend is a pass-through:
        the caller (orchestrator) should pass the prompt to Claude Code via
        normal chat and feed the result back in. This method is a shim so the
        rest of the codebase stays backend-agnostic.
        """
        if self.backend == "claude":
            # In Claude Code context the orchestrator calls this and then
            # asks Claude Code with the prompt. We return a placeholder that
            # tests can patch.
            return self._claude_placeholder(prompt, json_mode)

        if self.backend == "glm":
            self.validate_config()
            return self._call_glm(prompt, temperature, json_mode)

        raise ValueError(f"Unknown backend: {self.backend}")

    def _claude_placeholder(self, prompt: str, json_mode: bool) -> str:
        # Placeholder for unit tests; real usage passes prompt to Claude Code.
        if json_mode:
            return json.dumps({"placeholder": True, "prompt": prompt})
        return f"PLACEHOLDER: {prompt[:80]}"

    def _call_glm(self, prompt: str, temperature: float, json_mode: bool) -> str:
        # Stub: replace with actual GLM SDK call in production.
        import urllib.request
        key = os.getenv("GLM_API_KEY")
        payload = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        req = urllib.request.Request(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]


def get_client() -> LLMClient:
    return LLMClient()
