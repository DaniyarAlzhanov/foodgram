# Проект «Foodgram»

## Содержание
- [Описание](#описание)
- [Технологии](#технологии)
- [Запуск проекта с помощью Docker](#запуск проекта с помощью Docker)
- [Документация](#документация находится по роуту: /api/docs/)
- [Примеры запросов к API](#примеры запросов к API)
- [Автор](#автор)

## Описание
Cайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии
* Python 3.9.10
* Django 4.2.11
* DRF 3.15.1
* Nginx
* Gunicorn
* Docker
* Djoser
* PostgreSQL (pycopg2 2.9.9)

В проекте реализованы следующие возможности:
* Регистрация и получение токена новыми пользователями;
* Аутентификация и авторизация пользователей;
* Создание, удаление и редактирование рецептов;
* Просмотр списка рецептов (на главной странице, в профиле пользователя и в списке покупок);
* Добавление и удаление рецептов в список покупок;
* Добавление в избранное рецептов;
* Подписка на авторов.

# Запуск проекта с помощью Docker
* Создайте рабочую директорию проекта и перейдите в неё:
  ```
  mkdir foodgram/
  cd foodgram
  ```
* Создайте директорию docs и скопируйте в неё файлы redoc.html, openapi-schema.yml из текущего репозитория
* Скопируйте файл docker-compose.production.yml из текущего репозитория в корневую папку проекта foodgram/
* В корневой папке проекта foodgram/ создайте файл .env и заполните его согласно примеру .env.example:
  ```
  POSTGRES_DB=name_of_db
  POSTGRES_USER=name_of_user
  POSTGRES_PASSWORD=db_password
  DB_NAME=name_of_db
  DB_HOST=host_name_of_db
  DB_PORT=port_of_db
  SECRET_KEY=django_key
  ALLOWED_HOSTS=yourdomainname.org
  DEBUG=TRUE
  CSRF_TRUSTED_ORIGINS=https://yourdomainname.org http://yourdomainname.org
  ```
* Установите на сервере Docker и Docker Compose нижеуказанными коммандами:
  ```
  sudo apt update
  sudo apt install curl
  curl -fSL https://get.docker.com -o get-docker.sh
  sudo sh ./get-docker.sh
  sudo apt-get install docker-compose-plugin
  ```
* Запустите систему контейнеров в режиме "демона" нижеуказанной коммандой:
  ```
  sudo docker compose -f docker-compose.production.yml up -d
  ```
* Создайте и выполните миграции:
  ```
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py nakemigrations
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
  ```
* Импортируйте данные ингредиентов:
  ```
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_csv
  ```
* Создайте администратора:
  ```
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
  ```
* Соберите и скопируййте статику:
  ```
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
  sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/static/. /staticfiles/
  ```
## Документация находится по роуту: /api/docs/

## Примеры запросов к API

* Список пользователей:
  GET
  ```
  /api/users/
  ```
* Регистрация пользователя:
  POST
  ```
  /api/users/
  ```
* Профиль пользователя:
  GET
  ```
  /api/users/{id}/
  ```
* Текущий пользователь:
  GET
  ```
  /api/users/me/
  ```
* Добавление аватара:
  PATCH
  ```
  /api/users/me/avatar/
  ```
* Удаление аватара:
  DELETE
  ```
  /api/users/me/avatar/
  ```
* Изменение пароля:
  POST
  ```
  /api/users/set_password/
  ```
* Получить токен авторизации:
  POST
  ```
  /api/auth/token/login/
  ```  
* Удаление токена:
  POST
  ```
  /api/auth/token/logout/
  ```  
* Список тегов:
  GET
  ```
  /api/tags/
  ```    
* Получение тега:
  GET
  ```
  /api/tags/{id}/
  ```
* Список тегов:
  GET
  ```
  /api/tags/
  ```  
* Список рецептов:
  GET
  ```
  /api/recipes/
  ```  
* Создание рецепта:
  POST
  ```
  /api/recipes/
  ```  
* Получение рецепта:
  GET
  ```
  /api/recipes/{id}/
  ```  
* Обновление рецепта:
  PATCH
  ```
  /api/recipes/{id}/
  ```  
* Удаление рецепта:
  DELETE
  ```
  /api/recipes/{id}/
  ```  
* Получить короткую ссылку на рецепт:
  GET
  ```
  /api/recipes/{id}/get-link/
  ```  
* Скачать список покупок:
  GET
  ```
  /api/recipes/download_shopping_cart/
  ```  
* Добавить рецепт в список покупок:
  POST
  ```
  /api/recipes/{id}/shopping_cart/
  ```  
* Удалить рецепт из списка покупок:
  DELETE
  ```
  /api/recipes/{id}/shopping_cart/
  ```  
* Добавить рецепт в избранное:
  POST
  ```
  /api/recipes/{id}/favorite/
  ```  
* Удалить рецепт из избранного:
  DELETE
  ```
  /api/recipes/{id}/favorite/
  ```  
* Мои подписки:
  GET
  ```
  /api/users/subscriptions/
  ```  
* Подписаться на пользователя:
  POST
  ```
  /api/users/{id}/subscribe/
  ```
* Отписаться от пользователя:
  DELETE
  ```
  /api/users/{id}/subscribe/
  ```  
* Список ингредиентов:
  GET
  ```
  /api/ingredients/
  ```  
* Получение ингредиента:
  GET
  ```
  /api/ingredients/{id}/
  ``` 


## Автор

- [Данияр Альжанов](https://github.com/DaniyarAlzhanov)
