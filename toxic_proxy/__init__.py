import logging
from .app import toxic_proxy, asyncio

def run():
    logging.basicConfig(level=logging.INFO)
    p = toxic_proxy(
        destination=('localhost', 1884),
        port=1883
    )

    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(p)
    logging.info('Listening on %s:%u', *server.sockets[0].getsockname())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
