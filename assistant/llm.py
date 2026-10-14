"""All AI calls go through here.

Backends (config.yaml -> llm.backend):
- claude-code    (default) runs the `claude` CLI headless. It uses whatever Claude Code is
                 signed in with on this Mac, or AgentRouter when AGENTROUTER_API_KEY is set
                 in .env (the gateway is applied to this subprocess only).
- anthropic-api  calls the Anthropic SDK directly; needs ANTHROPIC_API_KEY.
"""
import json
import os
import shutil
import subprocess
import tempfile

from pydantic import BaseModel, ValidationError

from .config import CFG, env

AGENTROUTER_URL = "https://agentrouter.org/"


class LLMError(RuntimeError):
    pass


def _settings() -> dict:
    return CFG.get("llm", {})


def _model() -> str:
    s = _settings()
    if env("AGENTROUTER_API_KEY"):
        return s.get("agentrouter_model") or s.get("model", "")
    return s.get("model", "")


def structured[T: BaseModel](system: str, prompt: str, schema: type[T], effort: str) -> T:
    """One model call that returns a validated instance of `schema`."""
    backend = _settings().get("backend", "claude-code")
    if backend == "anthropic-api":
        return _anthropic_api(system, prompt, schema, effort)
    return _claude_code(system, prompt, schema, effort)


def _claude_code[T: BaseModel](system: str, prompt: str, schema: type[T], effort: str) -> T:
    exe = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    if not os.path.exists(exe):
        raise LLMError("Claude Code CLI not found. Install it, or set llm.backend: anthropic-api in config.yaml.")

    child_env = os.environ.copy()
    if env("AGENTROUTER_API_KEY"):
        child_env.update({
            "ANTHROPIC_BASE_URL": env("AGENTROUTER_BASE_URL", AGENTROUTER_URL),
            "ANTHROPIC_AUTH_TOKEN": env("AGENTROUTER_API_KEY"),
            "ANTHROPIC_API_KEY": env("AGENTROUTER_API_KEY"),
        })

    cmd = [
        exe, "-p",
        "--output-format", "json",
        "--json-schema", json.dumps(schema.model_json_schema()),
        "--system-prompt", system,
        "--tools", "",               # pure text-in / JSON-out: no file, shell or web access
        "--strict-mcp-config",
        "--no-session-persistence",
        "--effort", effort,
    ]
    if _model():
        cmd += ["--model", _model()]

    # Run outside the project so no CLAUDE.md or project settings leak into the prompt.
    with tempfile.TemporaryDirectory() as cwd:
        try:
            proc = subprocess.run(
                cmd, input=prompt, capture_output=True, text=True, env=child_env, cwd=cwd,
                timeout=int(_settings().get("timeout_seconds", 600)),
            )
        except subprocess.TimeoutExpired:
            raise LLMError("The model took too long to answer — try again.")

    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        detail = (proc.stderr or proc.stdout).strip()[-800:]
        raise LLMError(f"Claude Code failed (exit {proc.returncode}): {detail or 'no output'}")
    if out.get("is_error") or out.get("subtype") != "success":
        detail = out.get("result") or out.get("api_error_status") or out.get("subtype")
        if env("AGENTROUTER_API_KEY"):
            detail = f"{detail} (via AgentRouter — check the key, credit balance and llm.agentrouter_model)"
        raise LLMError(f"Model call failed: {detail}")

    data = out.get("structured_output")
    if data is None:
        try:
            data = json.loads(out.get("result", ""))
        except json.JSONDecodeError:
            raise LLMError("The model did not return structured output — try again.")
    try:
        return schema.model_validate(data)
    except ValidationError as e:
        raise LLMError(f"The model's answer didn't match the expected format: {e}")


def _anthropic_api[T: BaseModel](system: str, prompt: str, schema: type[T], effort: str) -> T:
    import anthropic

    if not env("ANTHROPIC_API_KEY"):
        raise LLMError("ANTHROPIC_API_KEY is not set in .env (needed for llm.backend: anthropic-api).")
    client = anthropic.Anthropic()
    try:
        resp = client.beta.messages.parse(
            model=_model() or "claude-opus-5-5",
            max_tokens=16000,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
            output_format=schema,
            output_config={"effort": effort},
            # If a safety classifier declines, the API retries on a suitable fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError:
        raise LLMError("Claude rejected the API key — check ANTHROPIC_API_KEY in .env.")
    except anthropic.RateLimitError:
        raise LLMError("Claude rate limit hit — try again in a minute.")
    except anthropic.BadRequestError as e:
        raise LLMError(f"Claude request was rejected: {e.message}")
    except anthropic.APIStatusError as e:
        raise LLMError(f"Claude API error {e.status_code}: {e.message}")
    except anthropic.APIConnectionError:
        raise LLMError("Could not reach the Claude API — check your internet connection.")

    if resp.stop_reason == "refusal":
        raise LLMError("Claude declined this request.")
    if resp.stop_reason == "max_tokens" or resp.parsed_output is None:
        raise LLMError("Claude's answer was cut off or unparseable — try again.")
    return resp.parsed_output
