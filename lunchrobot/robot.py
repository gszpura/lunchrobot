import re
import requests
import time
import logging
from logging.handlers import SysLogHandler
from bs4 import BeautifulSoup
from datetime import datetime
from lunchrobot.config import RULES
from lunchrobot.config import ORDER_ZUPA
from lunchrobot.config import USERNAME, PASSWD
from lunchrobot.config import CHECK_EVERY
from lunchrobot.config import STARTING_TIME


DISH_SPLIT = re.compile(r"[:\.] ")


def logging_setup():
    my_logger = logging.getLogger(__name__)
    my_logger.setLevel(logging.DEBUG)
    handler = SysLogHandler(address='/dev/log')
    my_logger.addHandler(handler)
    return my_logger


LOG = logging_setup()



class LuncherSite(object):

    GOOGLE_LOGIN_URL = "https://accounts.google.com/ServiceLogin"
    LUNCHER_LOGIN_URL = "http://luncher.codilime.com/authenticate/google"
    LUNCHER_MENU_URL = "http://luncher.codilime.com/lunch/menu.html"
    LUNCHER_SELECT_URL = "http://luncher.codilime.com/lunch/select.html"

    def __init__(self, username, passwd):
        self._username = username
        self._passwd = passwd
        self._session = requests.Session()

        site = self._session.post(
            self.GOOGLE_LOGIN_URL + "#identifier",
            data={'Email': self._username}
        )
        inputs = BeautifulSoup(
            site.content, "html.parser"
        ).find('form').find_all('input')

        session_dict = {}
        for inp in inputs:
            if inp.has_attr('value'):
                session_dict[inp['name']] = inp['value']
        session_dict['Passwd'] = self._passwd

        site = self._session.post(
            self.GOOGLE_LOGIN_URL + "#password",
            data=session_dict
        )

        site = self._session.get(self.LUNCHER_LOGIN_URL)
        self._dishes_per_rest = self._get_dishes_per_rest(site.content)

    def _get_dishes_per_rest(self, content):
        """
        For future use: exclusion of a restaurant from search.
        """
        sections = BeautifulSoup(
            content, "html.parser"
        ).find_all('section')

        dishes_per_rest = {}
        for section in sections:
            restaurant = section.find('h2').text
            meals = []
            dishes = section.find('table').find('tbody').find_all('tr')
            for dish in dishes:
                dish_str = dish.find_all('td')[1].text
                meals.append(DISH_SPLIT.split(dish_str)[1])
            dishes_per_rest[restaurant] = set(meals)
        return dishes_per_rest

    def _parse_dishes(self, content):
        controls = BeautifulSoup(
            content, "html.parser"
        ).find_all('div', {'class': 'controls'})
        dishes = {}
        for control in controls:
            inps = control.find_all('input')
            if inps:
                no, name_of_dish = DISH_SPLIT.split(inps[0]['value'])
                checkbox_name = inps[0]['name']
                dishes[name_of_dish] = checkbox_name
        self.dishes = dishes

    def _match(self, rule):
        for lunch in self.dishes:
            if rule.match(lunch):
                return [lunch, self.dishes[lunch]]

    def order(self, rules):
        content = self._session.get(self.LUNCHER_MENU_URL).content
        self._parse_dishes(content)

        payload = {}
        for rule in rules:
            match = self._match(rule)
            if match:
                payload[match[1]] = "on"
                break
        self._session.post(self.LUNCHER_SELECT_URL, data=payload)


def time_to_order(ordered_already):
    if not ordered_already:
        now = datetime.now()
        LOG.info("LUNCH_ROBOT: Checking at: {0}:{1}".format(now.hour, now.minute))
        starting_h, starting_m = STARTING_TIME
        if now.hour >= starting_h and now.minute >= starting_m:
            return True
    return False


def main():
    """
    Simple loop
    TODO: make service for ubuntu
    TODO: add ORDER_ZUPA flag
    TODO: make a git package + gitignore
    """
    ordered = False
    while True:
        if time_to_order(ordered):
            LOG.info("LUNCH_ROBOT: Going to order.")
            ordered = True
            luncher = LuncherSite(USERNAME, PASSWD)
            luncher.order(RULES)
        now = datetime.now()
        if now.hour >= 13:
            ordered = False
            LOG.info("LUNCH_ROBOT: Unsetting order flag.")
        time.sleep(CHECK_EVERY*60)

if __name__ == "__main__":
    main()