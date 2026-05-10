import re
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

import api
from api import _extract_text, _thread, app
from tests.conftest import collect_sse


@pytest.fixture(autouse=True)
def _mock_api_tracing(monkeypatch):
    """Prevent the FastAPI lifespan and request path from calling real external services."""
    monkeypatch.setattr("api.get_handler", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr("api.shutdown", MagicMock())
    monkeypatch.setattr("api.AsyncPostgresSaver", MagicMock())
    # build_config (in api.py request handlers) calls tracing.get_handler internally —
    # mock that binding too so the Langfuse reachability probe never runs.
    monkeypatch.setattr("tracing.get_handler", MagicMock(return_value=MagicMock()))


@pytest.fixture
def mock_agent(monkeypatch):
    """Agent that returns 'pong' on both invoke and stream."""
    mock = MagicMock()
    mock.ainvoke = AsyncMock(return_value={"messages": [type("Msg", (), {"content": "pong"})()]})

    async def _stream(*args, **kwargs):
        chunk = type("Chunk", (), {"content": "pong"})()
        yield {"event": "on_chat_model_stream", "data": {"chunk": chunk}}

    mock.astream_events = _stream
    monkeypatch.setattr(api, "_agent", mock)
    return mock


@pytest.fixture
def error_agent(monkeypatch):
    """Agent that raises on every call."""
    mock = MagicMock()
    mock.ainvoke = AsyncMock(side_effect=RuntimeError("boom"))

    async def _error_stream(*args, **kwargs):
        raise RuntimeError("stream broken")
        yield  # marks this as an async generator

    mock.astream_events = _error_stream
    monkeypatch.setattr(api, "_agent", mock)
    return mock


@pytest.fixture
async def client(_mock_api_tracing):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ── /health ───────────────────────────────────────────────────────────────────


async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ── _extract_text ─────────────────────────────────────────────────────────────


def test_extract_text_str():
    assert _extract_text("hi") == "hi"


def test_extract_text_list_of_dict_blocks():
    assert _extract_text([{"text": "a"}, {"text": "b"}]) == "ab"


def test_extract_text_list_dict_missing_text_key():
    assert _extract_text([{"foo": "bar"}]) == ""


def test_extract_text_list_of_non_dicts():
    assert _extract_text(["a", 1]) == "a1"


def test_extract_text_non_iterable_fallback():
    class Obj:
        def __str__(self):
            return "obj"

    assert _extract_text(Obj()) == "obj"


# ── _thread ───────────────────────────────────────────────────────────────────


def test_thread_default_generates_uuid():
    tid = _thread("")
    assert re.fullmatch(r"[0-9a-f]{32}", tid)


def test_thread_passthrough():
    assert _thread("abc") == "abc"


# ── POST /chat ────────────────────────────────────────────────────────────────


async def test_chat_empty_thread_id_generates_uuid(client, mock_agent):
    r = await client.post("/chat", json={"message": "hi", "thread_id": ""})
    assert r.status_code == 200
    data = r.json()
    assert re.fullmatch(r"[0-9a-f]{32}", data["thread_id"])
    assert data["response"] == "pong"


async def test_chat_passes_through_thread_id(client, mock_agent):
    r = await client.post("/chat", json={"message": "hi", "thread_id": "custom"})
    assert r.status_code == 200
    assert r.json()["thread_id"] == "custom"


async def test_chat_500_on_agent_error(client, error_agent):
    r = await client.post("/chat", json={"message": "hi"})
    assert r.status_code == 500
    assert "boom" in r.json()["detail"]


# ── POST /chat/stream ─────────────────────────────────────────────────────────


async def test_chat_stream_ends_with_done(client, mock_agent):
    async with client.stream("POST", "/chat/stream", json={"message": "hi"}) as resp:
        content = await resp.aread()
    frames = collect_sse(content)
    assert frames[-1] == "[DONE]"


async def test_chat_stream_chunk_shape(client, mock_agent):
    async with client.stream(
        "POST", "/chat/stream", json={"message": "hi", "thread_id": "t1"}
    ) as resp:
        content = await resp.aread()
    frames = collect_sse(content)
    data_frames = [f for f in frames if f != "[DONE]"]
    assert len(data_frames) >= 1
    assert data_frames[0]["content"] == "pong"
    assert data_frames[0]["thread_id"] == "t1"


async def test_chat_stream_error_path(client, error_agent):
    async with client.stream("POST", "/chat/stream", json={"message": "hi"}) as resp:
        content = await resp.aread()
    frames = collect_sse(content)
    error_frames = [f for f in frames if isinstance(f, dict) and "error" in f]
    assert error_frames, "expected at least one error frame"
    assert frames[-1] == "[DONE]"
