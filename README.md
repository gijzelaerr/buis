Buis
====

A webfrontend for toil.

demo: https://demo.pythonic.nl/


Requirements
============

for a normal deployment:

 * python3.6+
 * virtualenv
 * rabbitmq
 
For javascript development:
 
 * npm
 

on OSX with homebrew:
```
$ brew install python3 rabbitmq pyenv-virtualenv npm
$ brew services start rabbitmq
```

on debian/ubuntu:
```
$ sudo apt-get install rabbitmq-server python3 virtualenv npm  python3-dev
```

Or have a look at the `Dockerfile`.

Development
===========

[![Build Status](https://travis-ci.org/gijzelaerr/buis.svg?branch=master)](https://travis-ci.org/gijzelaerr/buis)
