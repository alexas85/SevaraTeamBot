from database import set_instruction_content

# Данные для админов
ADMIN_DATA = [
    {
        "role": "admin",
        "key": "opening_closing",
        "text": "🔑 Открытие и закрытие салона\n\n1. Проверка сигнализации.\n2. Включение света и оборудования.\n3. Проверка чистоты зон ресепшн."
    },
    {
        "role": "admin",
        "key": "yclients_fitmost",
        "text": "📊 Работа в Yclients и Fitmost\n\nИнструкции по переносу записей и работе с клиентами."
    },
    {
        "role": "admin",
        "key": "cash_reports",
        "text": "💵 Кассовая дисциплина\n\nПравила закрытия смены и формирования отчета."
    },
    {
        "role": "admin",
        "key": "scripts_sales",
        "text": "📣 Скрипты общения\n\nСтандартные фразы для продаж доп. услуг."
    }
]

# Данные для мастеров (дополнительно, если нужно)
MASTER_DATA = [
    {
        "role": "master",
        "key": "cleanliness",
        "text": "💨 Чистота и оборудование\n\n1. Протирание поверхностей после каждого клиента.\n2. Проверка наличия расходников."
    }
]

if __name__ == "__main__":
    print("💾 Наполнение базы инструкций...")

    for item in ADMIN_DATA:
        set_instruction_content(
            role=item["role"],
            key=item["key"],
            text_content=item["text"]
        )
        print(f"✅ Добавлено: {item['key']} (Admin)")

    for item in MASTER_DATA:
        set_instruction_content(
            role=item["role"],
            key=item["key"],
            text_content=item["text"]
        )
        print(f"✅ Добавлено: {item['key']} (Master)")

    print("🎉 Готово! Можно запускать бота.")
