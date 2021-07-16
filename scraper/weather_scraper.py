import logging
from bs4 import BeautifulSoup
from datetime import datetime, timezone, date
from botocore.exceptions import ClientError
import requests
import boto3
import json


class Scraper:

    def __init__(self):
        self.url = "https://www.bbc.co.uk/weather/2644605"

    def getContentFromPage(self):
        """
        Get the weather data from the page
        :param url: weather url
        :return: File to s3 bucket
        """
        try:

            result = {}
            soup = BeautifulSoup(requests.get(self.url).content, 'html.parser')

            # Date
            today = date.today()
            d1 = today.strftime("%d/%m/%Y")
            result['Date'] = d1

            # time slot
            result['Time'] = soup.find('span', attrs={'class': 'wr-time-slot-primary__time'}).text

            result['Temperature'] = soup.find('span', attrs={"class": "wr-value--temperature--c"}).text
            # Wind speed
            result['Wind_speed'] = soup.find('span',
                                             attrs={'class': "wr-value--windspeed wr-value--windspeed--mph"}).text

            # Precipitation
            result['Precipitation'] = soup.find('span', attrs={'class': "wr-u-font-weight-500"}).text

            return write_to_s3("ec2-s3-weather-v7s30dq4fxw", result)

        except AttributeError as e:
            logging.error(f"Attribute not found {e}")


def write_to_s3(bucket_name, object_body):
    """
        Write a file to S3 bucket
        :param bucket_name: Bucket to write
        :param object_body: data to write
        :return: True if file was uploaded else False
        """
    PREFIX = "weather-data" + "/" + "temp_" + datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p") + ".json"
    try:
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Body=bytes(json.dumps(object_body).encode("UTF-8")), Key=PREFIX,
                      ACL='public-read',
                      ContentType='application/json')
        print("S3 file put done")
    except ClientError as e:
        logging.error('Error occurred :' + str(e))
        return False
    return True


def lambda_handler(event, context):
    weather_data = Scraper()
    weather_data.getContentFromPage()
    bucketName = "hourly-weather"
    today = datetime.now(timezone.utc)

    fileName = "temp" + str(today) + ".json"

    s3 = boto3.client("s3")
    uploadByteStream = bytes(json.dumps(weather_data).encode('UTF-8'))
    s3.put_object(bucketName, fileName, uploadByteStream)

    print('Put Complete')

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


data = Scraper()
data.getContentFromPage()
