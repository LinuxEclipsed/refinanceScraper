# Refinance Website Scraper

## Introduction

As I am on the quest to automate actions I do often. I found I was checking the interest rates often in hopes of refinancing my loan at a lower rate. This container is used to scrape the filo mortgage website for the current interest rate they are offering. This then gets saved to an influxdb bucket. From there I can import the data to grafana. I can now chart the are and make alerts on drops. This is more of project for run rather than something very useful.

## Configuration

**Environment Variables**

- INFLUXDB_TOKEN = API token from Ifluxdb. This needs access to the buket
- INFLUXDB_ORG = Orginization set in Influxdb
- INFLUXDB_URL (Default)(http://localhost:8086)
- INFLUXDB_BUCKET (Default)(mortgage_rates)
- SCRAPE_TIME (Default)(24) = Time in hours before the next website scrape

### Quick start

**Build container**

Optional build the container locally or it can be pulled using the podman command.

```
podman build --tag refinancescraper .
```

**Podman/Docker**

```
podman container create \
--name refinancescraper \
-e INFLUXDB_TOKEN="<Influfdb Token>" \
-e INFLUXDB_ORG="<Orginization Name>" \
-e INFLUXDB_URL="http://<IP Address>:8086" \
-e SCRAPE_TIME="24" \
058264541271.dkr.ecr.us-west-1.amazonaws.com/linuxeclipsed/refinancescraper:latest
```
