Buis
====

A webfrontend for toil.

demo: https://demo.pythonic.nl/


Quick setup
===========

There are multiple ways to deploy this project, but the easiest is to use Docker and Docker compose.

* install Docker and Python 3
* Git checkout this repository
* Inside the repository type: `make docker-compose-up`. This will set up all the containers and start them.
* The first time you start the project you need to run `make docker-compose-migrate` to populate the database and also
  `make docker-compose-createsuperuser` to create a user for logging in on the website.
* Now go to http://localhost:8000 and boom, go! 


[![Build Status](https://travis-ci.org/gijzelaerr/buis.svg?branch=master)](https://travis-ci.org/gijzelaerr/buis)


Development
===========

for a normal deployment:

 * python3.6+
 * virtualenv
 * rabbitmq
 
on OSX with homebrew:
```
$ brew install python3 rabbitmq pyenv-virtualenv npm
$ brew services start rabbitmq
```

on debian/ubuntu:
```
$ sudo apt-get install rabbitmq-server python3 virtualenv npm  python3-dev
```

Explore the various make targets in the `Makefile` to figure out how to start the various services. To access the
webinterface you only need to start the Django server, but to schedule tasks you need to start a celery worker. By
default the celery worker is configured to connect to the rabbit MQ message broker.