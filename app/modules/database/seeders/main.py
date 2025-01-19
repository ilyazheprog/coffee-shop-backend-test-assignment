import asyncio

from ..connect import async_session
from .all_seeds import all_seeds
from .helpers import fill_seed


async def main():
    for model, field, data in all_seeds:
        async with async_session() as session:
            await fill_seed(session, model, field, data)


if __name__ == "__main__":
    asyncio.run(main())
