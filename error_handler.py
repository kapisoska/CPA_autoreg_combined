from sms_api import get_germany, get_phone_code, cancel_number
import time
from random import uniform
import playwright
import playwright.sync_api
import requests
from colorama import init, Fore
from playwright.sync_api import sync_playwright


def human_type_2(page, selector, text, start_delay=0, dct_delays=None, delay_range=(0.2, 0.45)):
    if dct_delays is None:
        dct_delays = {('a', 'color'): 0.15}
    last_char = ' '

    time.sleep(start_delay)
    for char in text:
        delay = dct_delays.get((last_char, char), uniform(delay_range[0], delay_range[1]))
        time.sleep(delay)
        page.locator(selector).type(char)
        last_char = char


def phone_error_handler(page):
    phone_input = page.wait_for_selector('#phoneNumberId')
    next_but = page.locator(
        '#view_container > div > div > div.pwWryf.bxPAYd > div > div.zQJV3 > div > div.qhFLie > div > div > '
        'button > span')
    time.sleep(uniform(1.9, 4.1))
    num_id, phone_number = get_germany()

    # *paste phone number
    phone_input.hover()
    time.sleep(uniform(0.4, 0.8))
    phone_input.click()
    phone_input.fill("")

    time.sleep(uniform(0.8, 1.4))
    human_type_2(page, '#phoneNumberId', '+{}'.format(phone_number))
    time.sleep(uniform(1.2, 2.3))

    # *click next but
    next_but.hover()
    time.sleep(uniform(0.4, 0.8))
    next_but.click()

    # !phone number error handler
    try:
        page.wait_for_selector(
            "#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc > div > form > span > section > "
            "div > div > div.bAnubd.OcVpRe.Jj6Lae > div.VsO7Kb > div.gFxJE > div.jPtpFe > div > span",
            timeout=20000)
    except playwright.sync_api.TimeoutError:
        print("Good number, next step")
        return num_id, phone_number
    else:
        print("Bad number, try to get new number")
        cancel_number(num_id)
        print("current activation is canceled")
        phone_error_handler(page)
