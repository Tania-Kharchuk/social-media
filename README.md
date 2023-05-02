# Social media API

The RESTful API for a social media platform. The API allow users to create profiles, follow other users, create and retrieve posts, manage likes and comments, and perform basic social media actions.

## Installing using GitHub


```shell
git clone https://github.com/Tania-Kharchuk/social-media
cd library-service
- Create venv:
python -m venv venv
- Activate venv:
source venv/bin/activate
- Install requirements:
pip install -r requirements.txt
- Create new Postgres DB and user
- Copy .env.sample and populate with all required data
python manage.py migrate
python manage.py runserver
```

## Run with Docker

```shell
- Copy .env.sample and populate with all required data
docker-compose build
docker-compose up
```

## Getting access

* create user via api/user/register
* get access token via api/user/login
