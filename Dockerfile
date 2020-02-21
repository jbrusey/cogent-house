# ------------------------------------------------------------
# Dockerfile for jenkins test
#
# ------------------------------------------------------------
FROM ubuntu:14.04
RUN gpg --keyserver keyserver.ubuntu.com --recv-keys A9B913B9
RUN gpg -a --export A9B913B9 | sudo apt-key add -

RUN apt-get update -q 
RUN apt-get install wget -qy
RUN wget -O - http://tinyprod.net/repos/debian/tinyprod.key | apt-key add - 
# add tinyprod to apt sources

RUN echo "deb http://tinyprod.net/repos/debian wheezy main" > /etc/apt/sources.list.d/tinyprod.list
RUN echo "deb http://tinyprod.net/repos/debian msp430-46 main" >> /etc/apt/sources.list.d/tinyprod.list
RUN apt-get install software-properties-common -qy
RUN add-apt-repository ppa:deadsnakes/ppa

# update apt database
RUN apt-get update -q

# upgrade all packages before we start

RUN apt-get upgrade -qy 

# Install tos essentials

RUN apt-get install autoconf automake gawk build-essential libtool \
    python3.6 \
    git \
    python-dev openjdk-6-jdk graphviz ntp -qy 

# install tinyos (wheezy)

RUN apt-get install nesc tinyos-tools msp430-46 avr-tinyos -qy 

# remove anything unnecessary

RUN apt-get autoremove -qy

# Get the code from the TinyOS release repository:

RUN cd /opt && wget -q http://github.com/tinyos/tinyos-release/archive/tinyos-2_1_2.tar.gz 
RUN cd /opt && tar xf tinyos-2_1_2.tar.gz
RUN cd /opt && rm tinyos-2_1_2.tar.gz

# python
COPY requirements.txt requirements.txt
RUN apt-get install python3-pip -qy
RUN pip install -r requirements.txt

ENV TOSROOT "/opt/tinyos-release-tinyos-2_1_2"
ENV TOSDIR "$TOSROOT/tos"
ENV CLASSPATH $TOSROOT/support/sdk/java/tinyos.jar
ENV PYTHONPATH $TOSROOT/support/sdk/python
ENV MAKERULES $TOSROOT/support/make/Makerules

# # Extend path for java
# type java >/dev/null 2>/dev/null || PATH=`/usr/local/bin/locate-jre --java`:$PATH
# type javac >/dev/null 2>/dev/null || PATH=`/usr/local/bin/locate-jre --javac`:$PATH
# echo $PATH | grep -q /usr/local/bin ||  PATH=/usr/local/bin:$PATH

WORKDIR /data
