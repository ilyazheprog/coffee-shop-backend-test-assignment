from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def fill_seed(session: AsyncSession, table, fields, values, replacible=True):
    # Преобразуем значения в список словарей
    data = [{col: row[i] for i, col in enumerate(fields)} for row in values]
    ids_in_data = [row["id"] for row in data]  # Собираем id из новых данных

    # Получаем все существующие записи в таблице
    result = await session.execute(select(table))
    existing_records = result.scalars().all()
    existing_ids = [
        record.id for record in existing_records
    ]  # Собираем все существующие id

    # Удаляем записи, которые есть в таблице, но отсутствуют в новых данных
    # ids_to_delete = set(existing_ids) - set(ids_in_data)
    # if ids_to_delete:
    #     await session.execute(delete(table).where(table.id.in_(ids_to_delete)))

    # Обрабатываем обновление или вставку новых данных
    for row_data in data:
        result = await session.execute(select(table).where(table.id == row_data["id"]))
        existing_record = result.scalars().first()

        if existing_record and replacible:
            # Если запись существует, обновляем её
            await session.execute(
                update(table).where(table.id == row_data["id"]).values(row_data)
            )
        elif not existing_record:
            # Если записи нет, вставляем новую
            await session.execute(insert(table).values(row_data))

    # Фиксируем изменения
    await session.commit()
