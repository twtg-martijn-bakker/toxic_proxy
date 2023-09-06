from typing import Tuple
import socket
import toxic_proxy.sideeffects as sideeffects
import asyncio

chunk_size = 2048

side_effects = {
    "latency": sideeffects.lattency,
    "timeout": sideeffects.timeout,
    "bandwidth_rate_kb": sideeffects.bandwidth_rate_kb,
}

async def toxic_proxy(destination: Tuple(str, int),
                      port: int,
                      latency: int = None,
                      timeout: int = None,
                      bandwidth_rate_kb: int = None,
                      slow_close = None):

    opts = dict(
        latency=latency,
        timeout=timeout,
        bandwidth_rate_kb=bandwidth_rate_kb,
        slow_close=slow_close)

    async def handle_client(local_reader, local_writer):
        try:
            remote_reader, remote_writer = await asyncio.open_connection(
                *destination)
            upstream = _pipe(local_reader, remote_writer, **opts)
            downstream = _pipe(remote_reader, local_writer, **opts)
            await asyncio.gather(upstream, downstream)
        finally:
            local_writer.close()

    return await asyncio.start_server(handle_client, '0.0.0.0', port)


async def _pipe(reader, writer, **opts):
    try:
        while not reader.at_eof():
            for name, val in opts.items():
                sd = side_effects.get(name)
                if not sd or val is None:
                    continue
                print('Launching', name, val)
                await sd(**opts)
            writer.write(await reader.read(chunk_size))
    finally:
        writer.close()
