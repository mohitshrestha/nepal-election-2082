# fetch.py

import httpx

URL = "https://result.election.gov.np/JSONFiles/ElectionResultCentral2082.txt"


async def fetch_raw_text() -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(URL)
        r.raise_for_status()
        return r.text
