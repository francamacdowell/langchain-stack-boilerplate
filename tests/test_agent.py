import urllib.error
import urllib.request
from unittest.mock import MagicMock

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langgraph.checkpoint.memory import InMemorySaver

import agent


class FakeToolModel(FakeListChatModel):
    """FakeListChatModel that satisfies bind_tools calls from deepagents."""

    def bind_tools(self, tools, **kwargs):
        return self


def _mock_urlopen(content: bytes, monkeypatch):
    mock_resp = MagicMock()
    mock_resp.read.return_value = content
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr(urllib.request, "urlopen", MagicMock(return_value=mock_resp))


def test_fetch_text_from_url_happy(monkeypatch):
    _mock_urlopen(b"hello world", monkeypatch)
    result = agent.fetch_text_from_url.invoke({"url": "https://example.com"})
    assert result == "hello world"


def test_fetch_text_from_url_url_error(monkeypatch):
    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        MagicMock(side_effect=urllib.error.URLError("connection refused")),
    )
    result = agent.fetch_text_from_url.invoke({"url": "https://example.com"})
    assert result.startswith("Fetch failed:")
    # The tool must not raise — error surfaces as a string.


def test_fetch_text_from_url_decodes_with_replacement(monkeypatch):
    _mock_urlopen(b"\xff\xfe", monkeypatch)
    result = agent.fetch_text_from_url.invoke({"url": "https://example.com"})
    assert "�" in result


def test_build_graph_returns_invokable():
    graph = agent.build_graph()
    assert hasattr(graph, "invoke")
    assert hasattr(graph, "ainvoke")


def test_build_graph_end_to_end_with_fake_model(monkeypatch):
    monkeypatch.setattr(agent, "_model", FakeToolModel(responses=["Final answer."]))
    graph = agent.build_graph(checkpointer=InMemorySaver())
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "hi"}]},
        config={"configurable": {"thread_id": "t1"}},
    )
    last = result["messages"][-1]
    assert "Final answer." in last.content
