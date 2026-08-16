import asyncio

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings


async def main() -> None:
    settings = get_settings()

    engine = create_async_engine(settings.database_url)

    async with engine.connect() as connection:
        tables = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_table_names()
        )

        print("SQLAlchemy sees tables:")
        for table in tables:
            print(f"  - {table}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
