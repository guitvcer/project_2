# project_2

## Описание
project_2 - это веб-сайт с новостями. Разрабатывалась в целях обучения.

___

## Запуск на локальном сервере
    git clone https://github.com/guitvcer/project_2.git
    cd project_2
    pip install -r requirements.txt
    python manage.py makemigrations news
    python manage.py migrate
    python manage.py runserver