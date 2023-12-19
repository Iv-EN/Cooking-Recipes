# FoodGram

## https://mybestfoodgram.ddns.net
- IP 84.201.161.161
Проект развёрнут по адресу https://mybestfoodgram.ddns.net.
Вход в админку по адресу:
  ```
  https://mybestfoodgram.ddns.net/admin/
  ```
  - E-mail: admin@admin.ru
  - Password: admin

## Описание
Здесь вы можете публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.
Для работы проекта выполнено:
- настроено взаимодействие Python-приложения с внешними API-сервисами;
- создан собственный API-сервис на базе проекта Django;
- подключено SPA к бэкенду на Django через API;
- созданы образы и запущены контейнеры Docker;
- созданы, развёрнуты и запущены на сервере мультиконтейнерные приложения;
- закреплены на практике основы DevOps, включая CI&CD.

**Инструменты и стек:** #python #JSON #YAML #Django #React #Telegram #API #Docker #Nginx #PostgreSQL #Gunicorn #JWT #Postman #Djoser #PyJWT #Pillow

## Запуск приложения в контейнере локально:
1. Загрузите проект
    ```bash
    git clone git@github.com:Iv-EN/foodgram-project-react.git
    ```
2. В папкe backend создайте файл `.env` со следующими переменными:
   ```
   SECRET_KEY=... # секретный ключ django-проекта
   DEBUG=False # в режиме отладки рекомендуется указать True
   ALLOWED_HOSTS=... # IP/домен хоста, БД (указывается через запятую без пробелов)
   POSTGRES_USER=... # имя пользователя БД
   POSTGRES_PASSWORD=... # пароль от БД
   POSTGRES_DB=... #django
   DB_HOST=db
   DB_PORT=5432
   ```
3. Перейдите в папку /infra/ 
4. Соберите и запустите контейнеры:
   ```bash
   sudo docker compose up -d
   ```
5. Создайте супер пользователя:
   ```bash
   docker compose exec foodgram_backend python manage.py createsuperuser
   ```


## Об авторе
Python-разработчик
>[Евгений Иванов](https://github.com/Iv-EN).
