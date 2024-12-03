import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision, BucketsApi
from influxdb_client.client.write_api import WriteOptions
import time
import os

# Scrape the Filo Mortgage website to get the percentage
def getPercentage():
    url = "https://www.filomortgage.com/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        pattern = re.compile(r'fixed rate loan today is as low as.*?(\d+(\.\d+)?)%')
        result = soup.find(text=pattern)

        if result:
            match = pattern.search(result)
            if match:
                return float(match.group(1))  # Get the number part and convert to float
    return None

# Retrieve the rate from the Zillow API
def getZillowRate(zillowPID):
    url = "https://mortgageapi.zillow.com/getRates"
    params = {
        'partnerId': zillowPID,
        'durationDays': 1
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['rates']['default']['samples'][0]['apr']  # First APR value
    return None

# Check if the bucket exists, create it if it doesn't
def ensureBucketExists(client, bucketName, org):
    bucketsApi = client.buckets_api()

    # Check if the bucket exists
    buckets = bucketsApi.find_buckets().buckets
    for bucket in buckets:
        if bucket.name == bucketName:
            print(f"Bucket '{bucketName}' already exists.")
            return

    # Create the bucket if it doesn't exist
    retentionRules = None  # Set custom retention rules if needed
    bucketsApi.create_bucket(bucket_name=bucketName, org=org, retention_rules=retentionRules)
    print(f"Bucket '{bucketName}' created.")

# Save the rate to InfluxDB
def saveToInfluxDB(rate, client, bucket, org, source):
    # Initialize the write API with WriteOptions
    writeApi = client.write_api(write_options=WriteOptions(batch_size=1))

    # Prepare data point to write
    point = (
        Point("mortgage_rate")
        .tag("source", source)  # Tag with the source of the rate
        .field("rate", rate)
        .time(datetime.utcnow(), WritePrecision.NS)  # Add the timestamp
    )

    # Write the data point to the specified bucket
    writeApi.write(bucket=bucket, org=org, record=point)
    print(f"Rate {rate} from {source} written to InfluxDB.")

# Main function
def main():
    # InfluxDB configuration (replace with your InfluxDB details)
    token = os.getenv('INFLUXDB_TOKEN')
    org = os.getenv('INFLUXDB_ORG')
    url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
    bucket = os.getenv('INFLUXDB_BUCKET', 'mortgage_rates')
    scrapeTime = int(os.getenv('SCRAPE_TIME', 24))
    zillowPID = os.getenv('ZILLOW_PID')

    # Initialize the InfluxDB client
    client = InfluxDBClient(url=url, token=token, org=org)

    # Ensure the bucket exists, or create it
    ensureBucketExists(client, bucket, org)

    # Infinite loop to check the rates
    try:
        while True:
            # Get rates from both sources
            filoRate = getPercentage()
            zillowRate = getZillowRate(zillowPID)

            # Write each rate to InfluxDB if available
            if filoRate:
                print(f"Extracted Filo Mortgage rate: {filoRate}")
                saveToInfluxDB(filoRate, client, bucket, org, "Filo Mortgage")
            else:
                print("Failed to extract the Filo Mortgage rate.")

            if zillowRate:
                print(f"Extracted Zillow rate: {zillowRate}")
                saveToInfluxDB(zillowRate, client, bucket, org, "Zillow")
            else:
                print("Failed to extract the Zillow rate.")

            # Sleep for the specified interval before the next check
            print("Waiting for the next check...")
            time.sleep(scrapeTime * 60 * 60)

    except KeyboardInterrupt:
        print("Stopping the loop...")
        client.close()

if __name__ == "__main__":
    main()
