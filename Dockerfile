FROM kernsuite/base:5
RUN docker-apt-install python3 virtualenv npm make rabbitmq-server libgconf-2-4 python3-dev git python3-pip docker.io python3-numpy
RUN pip3 install --upgrade pip
ADD requirements.txt /
RUN pip3 install -r /requirements.txt
ADD . /code
WORKDIR /code
