#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
FROM debian:jessie

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key 3FF5FFCAD71472C4

RUN echo "deb     http://qgis.org/debian-ltr jessie main" >> /etc/apt/sources.list
RUN echo "deb-src http://qgis.org/debian-ltr jessie main" >> /etc/apt/sources.list

RUN apt-get -y update; apt-get -y --force-yes install qgis python-qgis
RUN apt-get -y update; apt-get -y --force-yes install build-essential autoconf libtool pkg-config

RUN export DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND noninteractive
RUN dpkg-divert --local --rename --add /sbin/initctl

RUN apt-get -y update; apt-get -y --force-yes install pwgen git inotify-tools

#-------------Application Specific Stuff ----------------------------------------------------
# Install git, xvfb
RUN apt-get -y update; apt-get -y --force-yes install git xvfb python-setuptools python-dev libssl-dev libffi-dev
RUN easy_install pip==7.1.2

# Copy ubuntu fonts
RUN apt-get -y install wget unzip
RUN wget -c http://font.ubuntu.com/download/ubuntu-font-family-0.83.zip
RUN unzip ubuntu-font-family-0.83.zip
RUN mv ubuntu-font-family-0.83 /usr/share/fonts/truetype/ubuntu-font-family
RUN fc-cache -f -v

ADD . /home/src/inasafe
WORKDIR /home/src/inasafe
RUN pip install -r REQUIREMENTS.txt
RUN pip install -r src/headless/REQUIREMENTS.txt
RUN pip install -r src/realtime/REQUIREMENTS.txt

RUN chmod +x docker-entrypoint.sh

# Environment variable
ENV C_FORCE_ROOT="True" \
	PYTHONPATH="/home/src/inasafe/src" \
	DISPLAY=":99" \
	INASAFE_HEADLESS_BROKER_HOST="amqp://guest:guest@rabbitmq:5672/" \
	INASAFE_HEADLESS_DEPLOY_OUTPUT_DIR="/home/output/" \
	INASAFE_HEADLESS_DEPLOY_OUTPUT_URL="http://inasafe-output/output/" \
	QGIS_LOG_FILE="/tmp/inasafe/realtime/logs/qgis.log" \
	QGIS_DEBUG_FILE="/tmp/inasafe/realtime/logs/qgis-debug.log" \
	QGIS_DEBUG="0" \
	INASAFE_WORK_DIR="/tmp/inasafe"

CMD ["./docker-entrypoint.sh", "prod", "inasafe-headless"]
