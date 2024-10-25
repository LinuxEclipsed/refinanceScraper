FROM python:3.9-alpine

LABEL maintainer="LinuxEclipsed"

WORKDIR /opt

RUN pip install requests \
    beautifulsoup4 \
    influxdb-client \
    lxml

COPY src/scrapeWebpage.py /opt
RUN chmod 755 /opt/scrapeWebpage.py

CMD ["python3", "/opt/scrapeWebpage.py"]