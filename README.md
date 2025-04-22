# Refinance Website Scraper

## Introduction

As I am on the quest to automate actions I do often. I found I was checking the interest rates often in hopes of refinancing my loan at a lower rate. This container is used to scrape the filo mortgage website and the Zillow API for the current interest rate they are offering. This then gets saved to an InfluxDB bucket. From there, I can import the data to Grafana. I can now chart the area and make alerts on drops. This is more of a project for fun rather than something very useful.

## Configuration

**Environment Variables**

- INFLUXDB_TOKEN = API token from Ifluxdb. This needs access to the bucket
- INFLUXDB_ORG = Organization set in Influxdb
- INFLUXDB_URL (Default)(http://localhost:8086)
- INFLUXDB_BUCKET (Default)(mortgage_rates)
- ZILLOW_PID (Optional) = [Zillow Partner ID](https://www.zillow.com/mortgage/api/#/). 

### Quick start

**Build container**

Optionally, build the container locally, or it can be pulled using the podman command.

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
-e ZILLOW_PID="<Zillow Partner ID>
public.ecr.aws/b7c8g1g5/linuxeclipsed/refinancescraper:latest
```

### Kubernetes

The latest update to the source favors running this as a cronjob

``` yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mortgage-rate-scraper
spec:
  schedule: "0 */24 * * *"  # Runs every 24 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scraper
            image: your-registry/your-image:tag
            env:
            - name: INFLUXDB_TOKEN
              valueFrom:
                secretKeyRef:
                  name: influxdb-secret
                  key: token
            - name: INFLUXDB_ORG
              valueFrom:
                secretKeyRef:
                  name: influxdb-secret
                  key: org
            - name: INFLUXDB_URL
              value: "http://influxdb:8086"
            - name: INFLUXDB_BUCKET
              value: "mortgage_rates"
            - name: ZILLOW_PID
              valueFrom:
                secretKeyRef:
                  name: zillow-secret
                  key: pid
          restartPolicy: OnFailure
```
