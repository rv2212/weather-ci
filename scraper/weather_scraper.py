from bs4 import BeautifulSoup
import requests
import json


class Scraper:

    def __init__(self):
        pass

    @staticmethod
    def getContentFromPage(url):
        result = {}
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')

        result['Temperature'] = soup.find('span', attrs={"class": "wr-value--temperature--c"}).text

        # Wind speed
        result['Wind_speed'] = soup.find('span', attrs={'class': "wr-value--windspeed wr-value--windspeed--mph"}).text

        # time slot
        result['time'] = soup.find('span', attrs={'class': 'wr-time-slot-primary__time'}).text

        # Precipitation
        result['Precipitation'] = soup.find('span', attrs={'class': "wr-u-font-weight-500"}).text

        return result


def lambda_handler(event, context):
    data = Scraper()
    print(data.getContentFromPage("https://www.bbc.co.uk/weather/2644605"))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
