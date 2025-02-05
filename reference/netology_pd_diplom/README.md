# Пример API-сервиса для магазина

[Документация по запросам в PostMan](https://documenter.getpostman.com/view/5037826/SVfJUrSc) 




## **Получить исходный код**

    git config --global user.name "YOUR_USERNAME"
    
    git config --global user.email "your_email_address@example.com"
    
    mkdir ~/my_diplom
    
    cd my_diplom
    
    git clone git@github.com:A-Iskakov/netology_pd_diplom.git
    
    cd netology_pd_diplom
    
    sudo pip3 install  --upgrade pip
    
    sudo pip3 install -r requirements.txt
    
    python3 manage.py makemigrations
     
    python3 manage.py migrate
    
    python3 manage.py createsuperuser    
    
 
## **Проверить работу модулей**
    
    
    python3 manage.py runserver 0.0.0.0:8000


## **Установить СУБД (опционально)**

    sudo nano  /etc/apt/sources.list.d/pgdg.list
    
    ----->
    deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main
    <<----
    
    
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    
    sudo apt-get update
    
    sudo apt-get install postgresql-11 postgresql-server-dev-11
    
    sudo -u postgres psql postgres
    
    create user diplom_user with password 'password';
    
    alter role diplom_user set client_encoding to 'utf8';
    
    alter role diplom_user set default_transaction_isolation to 'read committed';
    
    alter role diplom_user set timezone to 'Europe/Moscow';
    
    create database diplom_db owner mploy;
    alter user mploy createdb;

## **Для тестирования меденных методов нужно**

Установка Docker-контейнера с Redis (когда не в Docker-образе):

    docker pull redis:latest

    docker run -d --name redis-server -p 6379:6379 redis:latest

Запуск worker в терминале для записи логов в файл

    celery -A netology_pd_diplom worker -l info -P solo -f celery.log

Тестирование медленных функций из другого терминала

    python manage.py shell
    from backend.tasks import do_import, send_email
    result_email = send_email.delay("netology.diplom@mail.ru", "Тестовое письмо", "Это тестовое сообщение.")
    result_import = do_import.delay()
    print("Email result:", result_email.get(timeout=10))
    print("Import result:", result_import.get(timeout=10)) 

Тестовые данные для импорта лежат в файле importfile.json

Установка всего проекта из Docker-образа

    docker-compose up --build -d
