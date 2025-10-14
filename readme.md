# blucab

blucab is a software to manage your physical Blu-Rays and DVDs as a easy to use webservice based on the [Django](https://www.djangoproject.com/) Framework.
An -still in development- Rest-API is available to interface with the service directly, e.g. via the planned mobile App.

## Disclaimer

This project is a full open-source, non-commercial hobby project and developed in my spare time after work.
The development could be irregular and breaking changes could happen without further notice.
If you use the project in a productive environment, please consider backups.
I will create releases if I consider the project as ready to use.
Please use it as it is and check the license agreement.

Some planned features are hidden within the GitHub Issue-Tracker.

General plan of this project:

- Create a solution to manage your DVD and Blu-Ray library (Vinyls as well in the future? 🤔)
- Be a replacement for the sunset flickrack.com (Do a .json export as long as you can! 😉)
  - A importer for the flickrack .json is working fine already
- Be stable and self-hostable at some point (there are unresolved issues)
  - Get releases build automatically and pushed to Docker-Hub or similar
  - Host a webpage for everyone? (Funding?, Legal aspects due to user-data?)
- Be usable without an mobile App first
- Integrate django based tests

## Usage (Not updated for a long time!)

This service is meant to be be self-hosted. To run it a docker-based and a manual way are available.

### Docker

The provided files in this project assume, that [docker](https://www.docker.com/) and [docker-compose](https://github.com/docker/compose) are installed on your system. The setup is different between Windows and Linux systems.
Please look for tutorials externally.<br><br>

The _docker-compose.yml_ file includes examples for persistent volume-folders to hold files for this project.
We recommend to add at least the database (if the default sqlite is used) and the downloaded covers.<br><br>

A environment-file _.env.dev_ can be derived from the _.env.dev.example_ and includes basic settings for the instance. Just copy it and rename it. The file is overwritten by the _docker-compose.yml_ file.

For a productive instance make sure:

- DEBUG is set to False
- SECRET_KEY is a long random unique string

As mentioned in the example file the "DJANGO_SUPERUSER\_" variables are only needed for the initial setup of the database and can be removed from the _.env.dev_ after the first executions. Note this assumes your database is persistent.

Start the instance with<br>
`docker-compose up -d`<br>
to start it and let it run in the background.

### Manual

The Project requires Python 3 and the given packages in blucab/requirements.txt.<br>

```
cd blucab
pip install -r ./requirements.txt
```

Afterward a one-time migration and setup of the superuser needs to be done.
The first migration commands need execution after each update of this project.

```
python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable

python manage.py createsuperuser
```

After installation you can run the service with your desired port.

```
python manage.py runserver 0.0.0.0:8000
```

## API (Not updated for a long time!)

The API is based on django-rest-framework and the knox token authentication.

### Http-header

All requests need the http-header:

```
Content-Type: application/json; charset=UTF-8
```

### Authentication

#### Login

The token can be derived via _/api/login/_ with the given Content-Type and the following body.
Multiple tokens can be tied to a user (e.g. here admin) via this POST-request.

```
{
    "username": "admin",
    "password": "PASSWORD"
}
```

A response might be:

```
{
    "user": {
        "id": 1,
        "username": "admin"
    },
    "token": "TOKEN_STRING"
}
```

#### Logout

Either one token can be logged out or all tokens of the user.
_/api/auth/logout/_ does the logout for one token, given by the following header next to the Content-Type as GET-request:

```
Authorization: Token TOKEN_STRING
```

To logout from all tokens, use _/api/auth/logoutall/_

### Movie

There are multiple endpoints to GET information about movies.
Based on the same database either all movies _/api/movie/_ or selective movies can be received.

#### Selective movies

A selective request can be either the EAN _/api/movie/EAN_ of the movie or the internal ID _/api/movie/ID_.

A response might be like:

```
[
    {
        "ean": "4010884245141",
        "asin": "B007IZ41EQ",
        "title": "Transformers 3 [Blu-ray]",
        "title_clean": "Transformers 3",
        "format": "Blu-Ray",
        "release_year": 2012,
        "runtime": 154,
        "fsk": "Freigegeben ab 12 Jahren",
        "content": "Product Description:Transformers 3 Kurzbeschreibung:Ein [...]",
        "actor": "Shia LaBeouf, Josh Duhamel, Rosie Huntington-Whiteley, Patrick Dempsey, Frances McDormand",
        "regisseur": "Michael Bay",
        "studio": "Paramount Home Entertainment",
        "genre": "",
        "language": "",
        "disc_count": 1,
        "movie_count": 1,
        "season_count": 0,
        "episode_count": 0,
        "is_series": false,
        "picture_available": false,
        "picture_url": "/static/main/dummy.jpg"
    }
]
```

#### Movies of user

To get all movies a user owns, use _/api/movie/user/_.
A movie is references by its internal ID.

A response might be like:

```
[
    {
        "user_name": "admin",
        "movie": 661,
        "movie_title_clean": "Transformers 3",
        "movie_format": "Blu-Ray",
        "activated": true,
        "rating": 0,
        "viewed": false,
        "rented": false,
        "rented_to": "",
        "date_added": "2024-05-21",
        "price": "0.00"
    }
]
```

### User specific

User settings are available through _/api/user/settings/_ as GET-request.

A response might be like:

```
[
    {
        "user_name": "admin",
        "price_unit": "€",
        "days_for_new": 21,
        "view_is_public": true,
        "show_view_title": true,
        "show_view_details": true,
        "show_view_icon_new": true,
        "show_view_icon_rented": true,
        "show_view_count_disc": true,
        "show_view_count_movie": true,
        "show_view_button_details": true
    }
]
```

## Attributions

- _Rent Vector Icon_ and _Vector New Icon_ by [Muhammad Khaleeq](https://www.vecteezy.com/members/iyikon/)
- Thanks for the nice Django Tutorial on YouTube by [Tech With Tim](https://www.youtube.com/@TechWithTim)
- Thanks to bhuma08 for the good overview about [Authentication using knox](https://dev.to/bhuma08/django-user-authentication-using-knox-5f17)
- Thanks to fraxel and Victor for the [picture trimming code](https://stackoverflow.com/a/10616717)
