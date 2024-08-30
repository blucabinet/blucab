# blucab

blucab is a software to manage your physical Blu-Rays and DVDs as a easy to use webservice based on the [Django](https://www.djangoproject.com/) Framework.
An Rest-API is available to interface with the service directly, e.g. via the mobile App.

## Usage

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

As mentioned in the example file the "DJANGO\_SUPERUSER\_" variables are only needed for the initial setup of the database and can be removed from the _.env.dev_ after the first executions. Note this assumes your database is persistent.

Start the instance with<br>
`docker-compose up -d`<br>
to start it and let it run in the background.

### Manual

The Project requires Python 3 and the given packages in blucab/requirements.txt.<br>
`pip install -r ./blucab/requirements.txt`

Further instructions are **ToDo**.

## Notes

The project is non-commercial hobby project. The development could be irregular and breaking changes could happen. If you use the project in a productive environment, please consider backups.

## Attributions

- _Rent Vector Icon_ and _Vector New Icon_ by [Muhammad Khaleeq](https://www.vecteezy.com/members/iyikon/)
- Thanks for the nice Django Tutorial on YouTube by [Tech With Tim](https://www.youtube.com/@TechWithTim)
