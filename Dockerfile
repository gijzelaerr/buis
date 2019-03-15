FROM kernsuite/base:dev
RUN docker-apt-install python3 virtualenv npm make rabbitmq-server libgconf-2-4 python3-dev git python3-pip
ADD requirements.txt /
RUN pip3 install -r /requirements.txt
ADD . /code
WORKDIR /code
#RUN make django-test
#RUN make django-migrate
