"""Run: .venv/bin/python -m pytest tests -q

A local mock server stands in for the gateway. It records each request.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from dify_plugin.entities.model.message import UserPromptMessage

from models.llm import llm as llm_module
from models.llm.llm import TokenifyLargeLanguageModel

REQUESTS = []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        REQUESTS.append({"path": self.path, "auth": self.headers["Authorization"], "body": body})
        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for part in ["Hel", "lo"]:
                chunk = {"id": "1", "object": "chat.completion.chunk", "model": body["model"],
                         "choices": [{"index": 0, "delta": {"content": part}, "finish_reason": None}]}
                self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            end = {"id": "1", "object": "chat.completion.chunk", "model": body["model"],
                   "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                   "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5}}
            self.wfile.write(f"data: {json.dumps(end)}\n\ndata: [DONE]\n\n".encode())
            return
        resp = {"id": "1", "object": "chat.completion", "model": body["model"],
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hello"},
                             "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4}}
        data = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


@pytest.fixture(autouse=True)
def server(monkeypatch):
    srv = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setattr(llm_module, "ENDPOINT_URL", f"http://127.0.0.1:{srv.server_port}/v1")
    REQUESTS.clear()
    yield
    srv.shutdown()


def make_model():
    return TokenifyLargeLanguageModel(model_schemas=[])


def test_validate_credentials_sends_chat_request():
    make_model().validate_credentials("deepseek/deepseek-v4-pro", {"api_key": "test-key"})
    assert REQUESTS[0]["path"] == "/v1/chat/completions"
    assert REQUESTS[0]["auth"] == "Bearer test-key"
    assert REQUESTS[0]["body"]["model"] == "deepseek/deepseek-v4-pro"


def test_user_cannot_change_endpoint():
    creds = {"api_key": "test-key", "endpoint_url": "https://example.com/v1"}
    make_model().validate_credentials("deepseek/deepseek-v4-pro", creds)
    assert creds["endpoint_url"] == llm_module.ENDPOINT_URL
    assert len(REQUESTS) == 1


def test_invoke_blocking_and_stream():
    model = make_model()
    result = model._invoke("deepseek/deepseek-v4-pro", {"api_key": "k"}, [UserPromptMessage(content="Hi")], {}, stream=False)
    assert result.message.content == "Hello"
    chunks = list(model._invoke("deepseek/deepseek-v4-pro", {"api_key": "k"}, [UserPromptMessage(content="Hi")], {}, stream=True))
    assert "".join(c.delta.message.content for c in chunks) == "Hello"
    assert REQUESTS[1]["body"]["stream"] is True
