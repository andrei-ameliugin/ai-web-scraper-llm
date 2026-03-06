import httpx
from fastapi import HTTPException

from config import settings


async def fetch_page(url: str) -> str:
    """Download page HTML from the given URL.

    Raises:
        HTTPException 502: if the target site is unreachable or times out.
    """
    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=502,
            detail=f"Request to {url} timed out after {settings.request_timeout}s",
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Target returned HTTP {exc.response.status_code}",
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to reach {url}: {exc}",
        )
