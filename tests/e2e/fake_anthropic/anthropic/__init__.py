"""A stand-in `anthropic` package for the Starter e2e test (DIVASTRO-155).

tests/e2e/test_starter_email.py puts this directory first on the test server's
PYTHONPATH, so `import anthropic` inside app/llm.py gets this module and no request
leaves the machine. It answers the two calls the emailed-answer worker makes:

* client.beta.messages.stream(...)   a short fixed reading (the Claude narration path)
* client.messages.create(...)        a "translation": a fixed Hindi reading when the
                                     system prompt asks for Hindi, else the text unchanged
"""

from __future__ import annotations

import types

HINDI = (
    "**आपके करियर का प्रश्न।** कुंडली मेहनत से धीरे-धीरे आगे बढ़ने का संकेत देती है, भाग्य से "
    "अचानक नहीं। दशम भाव पर शनि का प्रभाव धैर्य माँगता है, और चल रही दशा ज़िम्मेदारी और "
    "धीरे-धीरे मिलने वाली पहचान का साथ देती है।\n\n"
    "आने वाला समय बदलाव से पहले अपनी स्थिति मज़बूत करने के लिए अच्छा है। अपने काम का हिसाब "
    "रखें, वरिष्ठों से साफ़ बात करें और सहकर्मियों से विवाद से बचें।\n\n"
    "उपाय के रूप में शनिवार सादगी से बिताएँ और हाथ से काम करने वालों की सहायता करें।"
)
READING = ("**A short reading.** The tenth house and its lord show a slow and steady rise; the "
           "running period rewards patience and careful work over sudden moves.")


class _Stream:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    @property
    def text_stream(self):
        yield READING

    def get_final_message(self):
        return types.SimpleNamespace(stop_reason="end_turn")


class _Messages:
    def stream(self, **kw):
        return _Stream()

    def create(self, **kw):
        text = kw["messages"][0]["content"]
        out = HINDI if "Hindi" in kw.get("system", "") else text
        return types.SimpleNamespace(stop_reason="end_turn",
                                     content=[types.SimpleNamespace(text=out)])


class Anthropic:
    def __init__(self, **kw):
        self.messages = _Messages()
        self.beta = types.SimpleNamespace(messages=_Messages())
