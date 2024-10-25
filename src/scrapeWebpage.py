import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision, BucketsApi
from influxdb_client.client.write_api import WriteOptions
import time
import os

# Scrape the website to get the percentage
def get_percentage():
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

# Check if the bucket exists, create it if it doesn't
def ensure_bucket_exists(client, bucket_name, org):
    buckets_api = client.buckets_api()

    # Check if the bucket exists
    buckets = buckets_api.find_buckets().buckets
    for bucket in buckets:
        if bucket.name == bucket_name:
            print(f"Bucket '{bucket_name}' already exists.")
            return

    # Create the bucket if it doesn't exist
    retention_rules = None  # Set custom retention rules if needed
    buckets_api.create_bucket(bucket_name=bucket_name, org=org, retention_rules=retention_rules)
    print(f"Bucket '{bucket_name}' created.")

# Save the rate to InfluxDB
def save_to_influxdb(rate, client, bucket, org):
    # Initialize the write API with WriteOptions
    write_api = client.write_api(write_options=WriteOptions(batch_size=1))

    # Prepare data point to write
    point = (
        Point("mortgage_rate")
        .field("rate", rate)
        .time(datetime.utcnow(), WritePrecision.NS)  # Add the timestamp
    )

    # Write the data point to the specified bucket
    write_api.write(bucket=bucket, org=org, record=point)
    print(f"Rate {rate} written to InfluxDB.")

# Main function
def main():
    # InfluxDB configuration (replace with your InfluxDB details)
    token = os.getenv('INFLUXDB_TOKEN')
    org = os.getenv('INFLUXDB_ORG')
    url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
    bucket = os.getenv('INFLUXDB_BUCKET', 'mortgage_rates')
    scrapeTime = os.getenv('SCRAPE_TIME', 24)

    # Initialize the InfluxDB client
    client = InfluxDBClient(url=url, token=token, org=org)

    # Ensure the bucket exists, or create it
    ensure_bucket_exists(client, bucket, org)

    # Infinite loop to check the rate
    try:
        while True:
            rate = get_percentage()
            if rate:
                print(f"Extracted rate: {rate}")
                save_to_influxdb(rate, client, bucket, org)
            else:
                print("Failed to extract the rate.")

            # Sleep for 12 hours (43200 seconds) before the next check
            print("Waiting for the next check...")
            time.sleep(scrapTime * 60 * 60)

    except KeyboardInterrupt:
        print("Stopping the loop...")
        client.close()

if __name__ == "__main__":
    main()
