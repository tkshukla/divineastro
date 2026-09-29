"""Anthropic-fails -> local-model-fallback regression test (DIVASTRO-96).

Pure unit test with a fake Anthropic client and a fake Ollama HTTP endpoint —
no real network, no real API key needed, deterministic. Exercises the exact
branch in app.llm.stream_polish() that falls back to a local Ollama model
when Anthropic fails before any text reached the visitor, and confirms it
does NOT fall back once partial text has already streamed out (that case
must raise as before, so the caller's existing plain-text fallback in
polish() takes over instead of silently switching voice mid-answer).

    C:\\Astro\\.venv\\Scripts\\python.exe -m tests.test_llm_ollama_fallback
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import llm  # noqa: E402

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


ANALYSIS = {"answer": "engine's own plain wording", "verdict": "Mixed", "evidence": []}


def _fake_anthropic_module(fail: bool, fail_after_text: str = ""):
    """A stand-in for the `anthropic` module, shaped just enough for the
    `client.beta.messages.stream(...)` context-manager path stream_polish uses."""

    class FakeStream:
        def __init__(self):
            self._emitted = False

        def __enter__(self):
            if fail and not fail_after_text:
                raise RuntimeError("simulated: insufficient_quota")
            return self

        def __exit__(self, *a):
            return False

        @property
        def text_stream(self):
            if fail_after_text:
                yield fail_after_text
                raise RuntimeError("simulated: connection dropped mid-stream")
            yield "polished anthropic answer."

        def get_final_message(self):
            return types.SimpleNamespace(stop_reason="end_turn")

    class FakeMessages:
        def stream(self, **kwargs):
            return FakeStream()

    class FakeBeta:
        messages = FakeMessages()

    class FakeClient:
        beta = FakeBeta()

    mod = types.SimpleNamespace(Anthropic=lambda: FakeClient())
    return mod


def _fake_ollama_chat(model_used: list, reply: str = "local model's Hindi-or-English answer."):
    """Patches urllib so _ollama_models() and the /api/chat call both work
    without touching the network."""

    def fake_urlopen(request, timeout=None):
        url = request.full_url if hasattr(request, "full_url") else request
        if "/api/tags" in url:
            body = json.dumps({"models": [{"name": "qwen2.5:3b"}, {"name": "qwen2.5:7b"}]}).encode()
        elif "/api/chat" in url:
            payload = json.loads(request.data)
            model_used.append(payload["model"])
            lines = [
                json.dumps({"message": {"content": reply}, "done": False}).encode(),
                json.dumps({"done": True, "done_reason": "stop"}).encode(),
            ]
            body = b"\n".join(lines)
        else:
            raise AssertionError(f"unexpected URL in test: {url}")

        class Resp:
            def __enter__(self_): return self_
            def __exit__(self_, *a): return False
            def __iter__(self_): return iter(body.splitlines(keepends=True))
            def read(self_): return body
        return Resp()

    return fake_urlopen


def main() -> int:
    print("Anthropic -> local model fallback")

    # 1. Anthropic fails immediately (the billing-exhausted case this exists
    #    for) -> falls back to Ollama and the visitor gets a real answer.
    model_used: list[str] = []
    with mock.patch.dict(sys.modules, {"anthropic": _fake_anthropic_module(fail=True)}), \
         mock.patch("app.llm._ollama_models", return_value=["qwen2.5:3b", "qwen2.5:7b"]), \
         mock.patch("app.llm.OLLAMA_MODEL", "qwen2.5:7b"), \
         mock.patch("urllib.request.urlopen", side_effect=_fake_ollama_chat(model_used)):
        meta: dict = {}
        text = "".join(llm.stream_polish(ANALYSIS, "en", "anthropic", "Will I get promoted?",
                                          history=[], meta=meta))
    check("a real answer comes back (not empty, not the raw engine text)",
          bool(text.strip()) and text != ANALYSIS["answer"], repr(text))
    check("it used the configured OLLAMA_MODEL", model_used == ["qwen2.5:7b"], str(model_used))
    check("meta records that Anthropic failed", "anthropic_failed" in meta, str(meta))
    check("meta records which provider actually answered",
          meta.get("fallback_provider") == "ollama:qwen2.5:7b", str(meta))

    # 2. Anthropic fails immediately AND Ollama is not configured/reachable at
    #    all -> must still raise (so polish()'s existing plain-engine-text
    #    fallback takes over), never a silent empty answer.
    with mock.patch.dict(sys.modules, {"anthropic": _fake_anthropic_module(fail=True)}), \
         mock.patch("app.llm._ollama_models", return_value=[]):
        raised = False
        try:
            "".join(llm.stream_polish(ANALYSIS, "en", "anthropic", "Will I get promoted?", history=[]))
        except RuntimeError:
            raised = True
    check("with no local model available, the original failure still propagates", raised)

    # 3. Anthropic fails AFTER some text already streamed to the visitor -> no
    #    fallback restart (that would read as the answer switching voice
    #    mid-sentence); the original error must still propagate.
    model_used2: list[str] = []
    with mock.patch.dict(sys.modules, {"anthropic": _fake_anthropic_module(fail=True, fail_after_text="Your chart shows")}), \
         mock.patch("app.llm._ollama_models", return_value=["qwen2.5:7b"]), \
         mock.patch("urllib.request.urlopen", side_effect=_fake_ollama_chat(model_used2)):
        raised = False
        try:
            "".join(llm.stream_polish(ANALYSIS, "en", "anthropic", "Will I get promoted?", history=[]))
        except RuntimeError as exc:
            raised = "mid-stream" in str(exc)
    check("a mid-stream failure (partial text already sent) does NOT fall back", raised)
    check("...and never calls the local model in that case", model_used2 == [], str(model_used2))

    # 4. Anthropic succeeds cleanly -> Ollama is never touched at all.
    model_used3: list[str] = []
    ollama_called = []
    with mock.patch.dict(sys.modules, {"anthropic": _fake_anthropic_module(fail=False)}), \
         mock.patch("app.llm._ollama_models", side_effect=lambda: ollama_called.append(1) or []):
        text = "".join(llm.stream_polish(ANALYSIS, "en", "anthropic", "Will I get promoted?", history=[]))
    check("Anthropic succeeding never even checks for a local fallback",
          ollama_called == [], f"{len(ollama_called)} checks")
    check("the real Anthropic text is returned unchanged",
          text == "polished anthropic answer.", repr(text))

    # 5. An explicit ollama:<model> choice is untouched by any of this - a
    #    visitor who deliberately picked local-only must never silently be
    #    routed anywhere else.
    model_used4: list[str] = []
    with mock.patch("urllib.request.urlopen", side_effect=_fake_ollama_chat(model_used4)):
        text = "".join(llm.stream_polish(ANALYSIS, "en", "ollama:qwen2.5:3b", "Will I get promoted?", history=[]))
    check("an explicit ollama: provider choice runs that model directly, no Anthropic call involved",
          model_used4 == ["qwen2.5:3b"], str(model_used4))

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} FAILURES")
        for f in failures:
            print("  -", f)
        return 1
    print("ollama fallback: all green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
