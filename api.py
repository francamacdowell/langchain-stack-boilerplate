import json
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel

from agent import build_graph

app = FastAPI(title="LangChain Agent API")

# Permissive CORS for local dev — tighten allow_origins for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_agent = build_graph(checkpointer=InMemorySaver())


class ChatRequest(BaseModel):
    message: str
    thread_id: str = ""


def _thread(req_thread_id: str) -> str:
    return req_thread_id or uuid4().hex


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: ChatRequest):
    thread_id = _thread(req.thread_id)
    try:
        result = await _agent.ainvoke(
            {"messages": [{"role": "user", "content": req.message}]},
            config=_config(thread_id),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "response": _extract_text(result["messages"][-1].content),
        "thread_id": thread_id,
    }


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    thread_id = _thread(req.thread_id)

    async def event_stream():
        try:
            async for event in _agent.astream_events(
                {"messages": [{"role": "user", "content": req.message}]},
                config=_config(thread_id),
                version="v2",
            ):
                if event["event"] == "on_chat_model_stream":
                    text = _extract_text(event["data"]["chunk"].content)
                    if text:
                        yield f"data: {json.dumps({'content': text, 'thread_id': thread_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
