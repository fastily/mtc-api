"""mtc-api entry point"""

import logging

from flask import Flask, redirect, request
from rich.logging import RichHandler

from .core import generate_text_multi


app = Flask(__name__)


@app.route('/generate', methods=["POST"])
def generate():
    return generate_text_multi(titles) if (titles := request.json.get("titles")) else ({"error": "empty or malformed request"}, 400)


@app.route('/')
def index():
    return redirect("https://github.com/fastily/mtc-api")


if __name__ == "__main__":
    handler = RichHandler(rich_tracebacks=True)
    for s in ("pwiki", "fastilybot", "mtc_api"):
        lg = logging.getLogger(s)
        lg.addHandler(handler)
        lg.setLevel("DEBUG")

    app.run(port=8000, debug=True)
