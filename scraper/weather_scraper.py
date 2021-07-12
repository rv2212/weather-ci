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
        Get the wether data from the page
        :param url: weather url
        :return: weather data dictionary
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

        except AttributeError as e:
            print(f"Attribute not found {e}")

        else:
            with open("data.json", "w") as fp:
                json.dump(result, fp)

            return write_to_s3("ec2-s3-weather-v7s30dq4fxw", fp)


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


def write_to_s3(file_name, bucket_name):
    s3 = boto3.client("s3")
    PREFIX = 'weather-data/'
    try:
        res = s3.put_object(Body=file_name, bucket_name=bucket_name, key=PREFIX + '_DATA').put(Body=file_name)
    except ClientError as e:
        logging.error(e)
    else:
        return res


data = Scraper()
print(data.getContentFromPage())
