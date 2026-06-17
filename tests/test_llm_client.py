import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from llm_client import LLMClient, get_client

def test_default_backend_is_claude():
    os.environ.pop("PPT_LLM_BACKEND", None)
    client = get_client()
    assert client.backend == "claude"

def test_glm_backend_requires_key():
    os.environ["PPT_LLM_BACKEND"] = "glm"
    os.environ.pop("GLM_API_KEY", None)
    try:
        client = get_client()
        client.validate_config()
        assert False, "should raise"
    except SystemExit as e:
        assert "GLM_API_KEY" in str(e)

def test_claude_complete_returns_string():
    client = LLMClient("claude")
    result = client.complete("Say hi", temperature=0)
    assert isinstance(result, str)
    assert len(result) > 0
