from .server import mcp, _alan_adi_ctx, _yetki_kodu_ctx
import os


def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "http":
        import uvicorn
        from starlette.middleware import Middleware
        from starlette.middleware.base import BaseHTTPMiddleware
        from starlette.responses import JSONResponse

        class KimlikMiddleware(BaseHTTPMiddleware):
            """Her istekten alan adı ve yetki kodunu okur, context'e yazar."""
            async def dispatch(self, request, call_next):
                alan = request.query_params.get("alan", "")
                yetki = request.query_params.get("yetki", "")

                if not alan or not yetki:
                    return JSONResponse(
                        {
                            "hata": "alan ve yetki parametreleri gerekli.",
                            "ornek": "/mcp?alan=magazan.com&yetki=TICIMAX_YETKI_KODUN"
                        },
                        status_code=400
                    )

                t1 = _alan_adi_ctx.set(alan)
                t2 = _yetki_kodu_ctx.set(yetki)
                try:
                    response = await call_next(request)
                finally:
                    _alan_adi_ctx.reset(t1)
                    _yetki_kodu_ctx.reset(t2)
                return response

        port = int(os.getenv("PORT", 8000))
        app = mcp.http_app(middleware=[Middleware(KimlikMiddleware)])
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        mcp.run()
