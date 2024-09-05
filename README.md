# web-scraper


### Установка с помощью Docker

1. **Установите Docker:**

   ```sh
   bash <(curl -sSL https://get.docker.com)
   ```

2. **Склонируйте репозиторий проекта:**

   ```sh
   git clone https://github.com/AlexanderErofeev/web-scraper.git
   cd web-scraper
   ```

3. **Скопируйте .env.example в .env, и измените при необходимости:**

   ```sh
   cp .env.example .env
   nano .env
   ```

4. **Запустите сервис:**

   ```sh
   docker compose up -d
   ```
   
5. **Соберите данные с сайта:**

   ```sh
   docker exec web-scraper-api python app/scraper.py https://anextour.ru/ 5 10
   ```
   

### Cпецификация API

| Метод | Путь       | Действие   |
|:-----:|------------|------------|
| `GET` | `"/docs"`  | Swagger UI |
| `GET` | `"/redoc"` | ReDoc      |

   