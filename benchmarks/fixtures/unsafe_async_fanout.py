import asyncio


async def fetch_all(urls, fetch):
    return await asyncio.gather(*(fetch(url) for url in urls))
