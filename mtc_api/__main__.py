"""mtc-api entry point"""

from contextlib import suppress
from typing import Any

import uvicorn

from fastapi import FastAPI, HTTPException, Request

from .core import generate_text_multi


app = FastAPI(title="mtc-api", docs_url=None, redoc_url=None)


@app.get("/")
async def show_index() -> dict[str, str]:
    """Shows the web UI"""
    return {"docs": "https://github.com/fastily/mtc-api"}


@app.post('/generate')
async def generate(request: Request) -> dict[str, list[Any]]:
    """Endpoint which generates commons descriptions for the given titles

    Args:
        request (Request): The FastAPI request

    Returns:
        dict[str, Any]: json where each key is the original name of the file and the value contains a dict with the new title and new description.
    """
    with suppress(Exception):
        if (titles := (body := await request.json()).get("titles")) and len(titles) <= 25:
            return generate_text_multi(titles, body.get("force", False))

    raise HTTPException(400, "empty, malformed, or overly large request (max is 25 titles)")


if __name__ == '__main__':
    uvicorn.run("mtc_api.__main__:app", reload=True)
