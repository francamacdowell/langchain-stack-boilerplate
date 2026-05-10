from unittest.mock import MagicMock

import pytest

import tracing


@pytest.mark.parametrize("var", ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"])
def test_require_env_raises_for_each_missing_var(monkeypatch, var):
    monkeypatch.delenv(var)
    with pytest.raises(RuntimeError, match=var):
        tracing._require_env()


def test_require_env_passes_when_all_set():
    tracing._require_env()  # env vars set by conftest; must not raise


def test_get_handler_is_cached(monkeypatch):
    mock_handler = MagicMock()
    mock_class = MagicMock(return_value=mock_handler)
    monkeypatch.setattr(tracing, "CallbackHandler", mock_class)
    tracing.get_handler.cache_clear()
    try:
        h1 = tracing.get_handler()
        h2 = tracing.get_handler()
        assert h1 is h2
        assert mock_class.call_count == 1
    finally:
        tracing.get_handler.cache_clear()


def test_build_config_shape(monkeypatch):
    mock_handler = MagicMock()
    monkeypatch.setattr(tracing, "CallbackHandler", MagicMock(return_value=mock_handler))
    tracing.get_handler.cache_clear()
    try:
        cfg = tracing.build_config("thread-x")
    finally:
        tracing.get_handler.cache_clear()

    assert cfg["configurable"]["thread_id"] == "thread-x"
    assert cfg["metadata"]["langfuse_session_id"] == "thread-x"
    assert cfg["callbacks"] == [mock_handler]


def test_shutdown_calls_client_shutdown(monkeypatch):
    mock_client = MagicMock()
    monkeypatch.setattr(tracing, "get_client", MagicMock(return_value=mock_client))
    tracing.shutdown()
    mock_client.shutdown.assert_called_once()
