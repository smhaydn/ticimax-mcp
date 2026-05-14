from .server import mcp, _alan_adi_ctx, _yetki_kodu_ctx
import os
import json


class KimlikASGIMiddleware:
    """Her istekten alan adı ve yetki kodunu okur, context'e yazar."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            from urllib.parse import parse_qs

            path = scope.get("path", "")

            # /health isteği — credentials gerekmez
            if path == "/health":
                await self._saglik_cevabi(send)
                return

            query_string = scope.get("query_string", b"").decode()
            params = parse_qs(query_string)
            alan = params.get("alan", [""])[0]
            yetki = params.get("yetki", [""])[0]

            # Credentials yoksa hata döndür
            if not alan or not yetki:
                await self._hata_cevabi(send)
                return

            t1 = _alan_adi_ctx.set(alan)
            t2 = _yetki_kodu_ctx.set(yetki)
            try:
                await self.app(scope, receive, send)
            finally:
                _alan_adi_ctx.reset(t1)
                _yetki_kodu_ctx.reset(t2)
        else:
            await self.app(scope, receive, send)

    async def _saglik_cevabi(self, send):
        body = json.dumps({"durum": "çalışıyor"}).encode()
        await send({"type": "http.response.start", "status": 200, "headers": [[b"content-type", b"application/json"]]})
        await send({"type": "http.response.body", "body": body})

    async def _hata_cevabi(self, send):
        body = json.dumps({
            "hata": "alan ve yetki parametreleri gerekli.",
            "ornek": "/mcp?alan=magazan.com&yetki=TICIMAX_YETKI_KODUN"
        }).encode()
        await send({"type": "http.response.start", "status": 400, "headers": [[b"content-type", b"application/json"]]})
        await send({"type": "http.response.body", "body": body})


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
