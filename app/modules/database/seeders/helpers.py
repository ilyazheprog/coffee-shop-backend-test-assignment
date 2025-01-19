from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def fill_seed(session: AsyncSession, table, fields, values):
    # Преобразуем значения в список словарей
    data = [{col: row[i] for i, col in enumerate(fields)} for row in values]

    for row_data in data:
        result = await session.execute(select(table).where(table.id == row_data["id"]))
        existing_record = result.scalars().first()

        if not existing_record:
            # Если записи нет, вставляем новую
            await session.execute(insert(table).values(row_data))

    # Фиксируем изменения
    await session.commit()
