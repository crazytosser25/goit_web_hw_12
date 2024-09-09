# goit_web_hw_12
Homework 12 FastAPI + Authorization

  1.  Дані доступу до БД, а також зовнішні хост і порт застосунку, algorythm & secret key
      повинні бути прописані у файлі .env згідно зразку.

  2.  Залежності можна встановити з файлу requirenments.txt

  3.  БД запускається командою:
      ```
      docker compose up
      ```

  4.  Міграції БД можна виконати командою:
      ```
      alembic upgrade head
      ```

  5.  Запуск застосунку із папки goit_web_hw_11 командою:
      ```
      python start.py
      ```

Коллекція запитів для перевірки створення юзера і оновлення токена
у файлі:   HW12.postman_collection.json
