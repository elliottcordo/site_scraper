"""
simple scraper for finding a 3060 graphics card
"""
import sys
import logging
from time import sleep
from random import randrange
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import boto3
import yaml
import pprint

YAML_FILE = sys.argv[1]
print(YAML_FILE)

# load configuration
with open(YAML_FILE) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# setup
logging.basicConfig(format='%(asctime)s %(message)s')
LOG = logging.getLogger('scraper')
LOG.setLevel(logging.DEBUG)

client = boto3.client('sns')
DRIVER_PATH = '/Users/elliott/projects/site_scraper/chromedriver'


# assign constants
NE_URL = config.get('URL')
NE_STRING = config.get('STRING')
NE_TGT_CNT = config.get('TGT_CNT')
NE_NAME = config.get('NAME')
print(NE_URL)
print(NE_STRING)
print(NE_TGT_CNT)

# other settings
MAX_ERROR = 5
PHONE_NUMBERS = ['+16465842049', '+12016001703'] # '+19086039726']


class DriverWrapper:
    """
    do this to combat issue with headless initialization time
    """
    def __init__(self):
        """

        """
        # web driver setup
        options = Options()
        # options.add_argument("--window-size=20,20")
        options.add_argument("--disable-gpu")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument('--no-proxy-server')
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    def get_source(self, url):
        """

        :param url:
        :return:
        """
        self.driver.get(url=url)
        return self.driver.page_source


def send_txt(msg):
    """

    :param msg:
    :return:
    """
    for phone in PHONE_NUMBERS:
        client.publish(
            PhoneNumber=phone,
            Message=msg)
    sleep(15)


def monitor_sites():
    """
    iterate sites and scrape!
    :return:
    """
    error_count = 0
    driver_wrap = DriverWrapper()


    while True:
        LOG.info('--Starting Iteration -->')
        try:
            # ===============================================
            # process ne - requests, so fast
            # this check is different as we are waiting for add-to-cart to appear
            # ===============================================
            ne_txt = driver_wrap.get_source(NE_URL)
            cnt = ne_txt.count(NE_STRING)
            LOG.info(f'THE {NE_NAME} COUNT IS: {cnt}')
            if cnt != NE_TGT_CNT:
                LOG.info(f'BUY BUY BUY {NE_NAME}!!! {NE_URL}')
                send_txt(f'BUY! {NE_URL}')
                sleep(900)
            sleep(randrange(0, 10))
        except Exception as err:
            LOG.warning(str(err))
            error_count += 1
        if error_count >= MAX_ERROR:
            LOG.error('too many errors')
            send_txt('scraper failed, goodbye cruel world')
            sys.exit()
        sleep(randrange(0, 360))


if __name__ == "__main__":
    monitor_sites()
