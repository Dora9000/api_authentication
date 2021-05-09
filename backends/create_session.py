
import ssl
import certifi
from aiohttp import ClientSession, TCPConnector


async def create_session(app):
    ssl_context = ssl.create_default_context(
        cafile=certifi.where())
    conn = TCPConnector(loop=app.loop,
                        verify_ssl=True,
                        ssl=ssl_context)
    app['session'] = ClientSession(connector=conn)


async def close_session(app):
    await app['session'].close()
