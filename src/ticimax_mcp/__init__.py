from .server import mcp, _alan_adi_ctx, _yetki_kodu_ctx
import os


class KimlikASGIMiddleware:
    """Her istekten alan adı ve yetki kodunu okur, context'e yazar."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            from urllib.parse import parse_qs
            query_string = scope.get("query_string", b"").decode()
            params = parse_qs(query_string)
            alan = params.get("alan", [""])[0]
            yetki = params.get("yetki", [""])[0]

            t1 = _alan_adi_ctx.set(alan)
            t2 = _yetki_kodu_ctx.set(yetki)
            try:
                await self.app(scope, receive, send)
            finally:
                _alan_adi_ctx.reset(t1)
                _yetki_kodu_ctx.reset(t2)
        else:
            await self.app(scope, receive, send)


def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "http":
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        base_app = mcp.http_app()
        app = KimlikASGIMiddleware(base_app)
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        mcp.run()
