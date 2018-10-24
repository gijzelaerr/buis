FROM kernsuite/base:dev
RUN docker-apt-install python3 virtualenv npm make rabbitmq-server libgconf-2-4 python3-dev
ADD . /code
WORKDIR /code
RUN make django-test
RUN make django-migrate
