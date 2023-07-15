import random
import time
from random import uniform
from datetime import datetime
import datetime as dt
from concurrent.futures import ThreadPoolExecutor
import json

import playwright.sync_api
import requests
from colorama import init, Fore
from playwright.sync_api import sync_playwright
import logging

from proxy_utils import get_proxy
from sms_api import get_germany, get_phone_code, cancel_number, get_second_code
from utils import get_pass, get_full_name, extract_codes
from google_sheets import reports_to_db

# logger = logging.getLogger(__name__)

init(autoreset=True)
LOCAL_API = "http://localhost:61135/api/profiles"


def get_debug_port(profile_id):
    data = requests.post(
        f'{LOCAL_API}/start', json={'uuid': profile_id, 'headless': False, 'debug_port': True}
    ).json()
    print(data['ws_endpoint'])
    return data


def human_type_2(page, selector, text, start_delay=0, dct_delays=None, delay_range=(0.2, 0.45)):
    if dct_delays is None:
        dct_delays = {('a', 'color'): 0.15}
    last_char = ' '

    time.sleep(start_delay)
    for char in text:
        delay = dct_delays.get((last_char, char), uniform(delay_range[0], delay_range[1]))
        time.sleep(delay)
        page.locator(selector).type(char, timeout=4000)
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
            timeout=10000)
    except playwright.sync_api.TimeoutError:
        print("Good number, next step")
        return num_id, phone_number
    else:
        print("Bad number, try to get new number")
        cancel_number(num_id)
        print("current activation is canceled")
        phone_error_handler(page)


def create_account(data_list):
    profile_name = data_list[0]
    uuid = data_list[1]
    proxy_country_code = data_list[2]
    proxy_city = data_list[3]
    proxy_port = [4]
    time_start = time.time()
    DEBUG_CODE = 0  # ?debug status code
    try:
        with sync_playwright() as p:
            ws_endpoint = get_debug_port(uuid)['ws_endpoint']
            # ws_endpoint = 'ws://127.0.0.1:53916/devtools/browser/7609aacf-a913-4ea3-b146-41cd89ddea19'
            browser = p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0]
            page = context.pages[0]

            # two_fa_but = page.get_by_text("2-Step Verification is off") print(two_fa_but) try: two_fa_but.hover(
            # timeout=1500) except playwright.sync_api.TimeoutError: print("timeout error") # two_fa_but =
            # page.get_by_text("2-Step Verification is off").click() get_started_but = page.get_by_text("Get
            # started").hover() next_but = page.locator("#yDmH0d > c-wiz > div > div:nth-child(2) > div:nth-child(2)
            # > c-wiz > div > div > " "div.hyMrOd > div.qNeFe.RH9rqf > div > div.A9wyqf > div:nth-child(1) > span >
            # span") next_but.click()

            # print("succes")
            # # #
            # return False
            # ?------------------- get google page
            page.goto('https://google.com')
            print("wait loading search page")
            page.wait_for_selector('#L2AGLb > div')
            print("search page loaded")

            # # ?------------------- click accept all but
            time.sleep(uniform(0.5, 1.5))
            page.hover('#L2AGLb > div')
            time.sleep(uniform(0.4, 0.8))
            page.click('#L2AGLb > div')
            time.sleep(uniform(1.5, 3.0))

            # # ?------------------- search 'google account'
            flag = False
            try:
                human_type_2(page,
                             'body > div.L3eUgb > div.o3j99.ikrT4e.om7nvf > form > '
                             'div:nth-child(1) > div.A8SBwf > div.RNNXgb '
                             '> div > div.a4bIc > input',
                             'google account')
            except playwright.sync_api.TimeoutError:
                flag = True
            if flag:
                human_type_2(page, '#APjFqb', 'google account')

            time.sleep(uniform(0.4, 0.8))

            if not flag:
                page.locator(
                    'body > div.L3eUgb > div.o3j99.ikrT4e.om7nvf > form > div:nth-child(1) > div.A8SBwf > div.RNNXgb > '
                    'div > '
                    'div.a4bIc > input').press('Enter', timeout=10000)
            else:
                page.locator(
                    '#APjFqb').press('Enter', timeout=10000)

            # # ?------------------- click create account
            DEBUG_CODE = 1  # ?debug status code
            try:
                but = page.wait_for_selector(
                    '#xaiYPc > div > div:nth-child(3) > div > ga-signed-out-buttons > div > ga-text-button > a > div',
                    timeout=11000)
            except playwright.sync_api.TimeoutError:
                print("Bad proxy, try gen new")
                proxy_country_code, _, proxy_city = get_proxy(proxy_port, "GB")
                page.reload()
                time.sleep(2)
                try:
                    but = page.wait_for_selector(
                        '#xaiYPc > div > div:nth-child(3) > div > ga-signed-out-buttons > div > ga-text-button > a > '
                        'div',
                        timeout=11000)
                except playwright.sync_api.TimeoutError:
                    print("Прокси санина ебаная")

            time.sleep(uniform(3.0, 6.0))
            but.hover()
            time.sleep(uniform(0.4, 0.8))
            but.click()

            # # ?------------------- paste login info
            try:
                page.wait_for_selector("#initialView > div.xkfVF > div.NlMX9c > div > figure > img", timeout=11000)
            except playwright.sync_api.TimeoutError:
                print("Bad proxy, try gen new")
                proxy_country_code, _, proxy_city = get_proxy(proxy_port, "GB")
                page.reload()
                time.sleep(2)
                try:
                    page.wait_for_selector("#initialView > div.xkfVF > div.NlMX9c > div > figure > img", timeout=11000)
                except playwright.sync_api.TimeoutError:
                    print("Прокси санина ебаная")

            email_input = page.wait_for_selector('#username')
            name_input = page.locator('//*[@id="firstName"]')
            surname_input = page.locator('#lastName')
            password_input = page.locator('#passwd > div.aCsJod.oJeWuf > div > div.Xb9hP > input')
            confirm_pass = page.locator('#confirm-passwd > div.aCsJod.oJeWuf > div > div.Xb9hP > input')
            next_but = page.locator('#accountDetailsNext > div > button > span')

            # *get user info
            name, surname = get_full_name()
            email = name + str(random.randint(0, 100)) + surname + str(random.randint(0, 100))
            password = get_pass()
            print(Fore.GREEN + name + ' ' + surname)
            print(Fore.GREEN + email)
            print(Fore.GREEN + password)
            time.sleep(uniform(3.0, 6.0))

            # *email
            email_input.hover()
            time.sleep(uniform(0.4, 0.8))
            email_input.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '#username', email)
            time.sleep(uniform(1.2, 2.3))

            # *name
            name_input.hover()
            time.sleep(uniform(0.4, 0.8))
            name_input.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '//*[@id="firstName"]', name)
            time.sleep(uniform(1.2, 2.3))

            # *surname
            surname_input.hover()
            time.sleep(uniform(0.4, 0.8))
            surname_input.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '#lastName', surname)
            time.sleep(uniform(1.2, 2.3))

            # *password
            password_input.hover()
            time.sleep(uniform(0.4, 0.8))
            password_input.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '#passwd > div.aCsJod.oJeWuf > div > div.Xb9hP > input', password)
            time.sleep(uniform(1.2, 2.3))

            # *confirm_pass
            confirm_pass.hover()
            time.sleep(uniform(0.4, 0.8))
            confirm_pass.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '#confirm-passwd > div.aCsJod.oJeWuf > div > div.Xb9hP > input', password)
            time.sleep(uniform(1.2, 2.3))

            # *click next but
            next_but.hover()
            time.sleep(uniform(0.4, 0.8))
            next_but.click()

            # # ?------------------- paste phone number and verif them
            DEBUG_CODE = 2  # ?debug status code
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
                    "#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc > div > form > span > section "
                    "> "
                    "div > div > div.bAnubd.OcVpRe.Jj6Lae > div.VsO7Kb > div.gFxJE > div.jPtpFe > div > span",
                    timeout=10000)
            except playwright.sync_api.TimeoutError:
                print("Good number, next step")
            else:
                print("Bad number, try to get new number")
                cancel_number(num_id)
                print("current activation is canceled")
                num_id, phone_number = phone_error_handler(page)

            # *wait page with verif input and paste verif code
            code_input = page.wait_for_selector('#code')
            verif_but = page.locator(
                '#view_container > div > div > div.pwWryf.bxPAYd > div > div.zQJV3 > div > div.qhFLie > div > div > '
                'button > span')
            time.sleep(uniform(3.0, 6.0))

            code_input.hover()
            time.sleep(uniform(0.4, 0.8))
            code_input.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '#code', str(get_phone_code(num_id)))
            time.sleep(uniform(1.2, 2.3))

            verif_but.hover()
            time.sleep(uniform(0.4, 0.8))
            verif_but.click()
            time.sleep(uniform(1.2, 2.3))

            # # ?------------------- paste user info
            day_input = page.wait_for_selector('#day')
            moth_select = page.locator('#month')
            year_input = page.locator('#year')
            gender_select = page.locator('#gender')
            next_but = page.locator(
                '#view_container > div > div > div.pwWryf.bxPAYd > div > div.zQJV3 > div > div.qhFLie > div > div > '
                'button > span')
            time.sleep(uniform(3.0, 6.0))

            # *day paste
            day_input.hover()
            time.sleep(uniform(0.4, 0.8))
            day_input.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '#day', str(random.randint(1, 27)))
            time.sleep(uniform(1.2, 2.3))

            # *month paste
            month_list = ['jan', 'feb', 'mar', 'april', 'may', 'june', 'july', 'aug', 'sep', 'oct', 'nov', 'dec']
            moth_select.hover()
            time.sleep(uniform(0.4, 0.8))
            moth_select.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '#month', random.choice(month_list))
            moth_select.press("Enter")
            time.sleep(uniform(1.2, 2.3))

            # *year paste
            year_input.hover()
            time.sleep(uniform(0.4, 0.8))
            year_input.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '#year', str(random.randint(1987, 1992)))
            time.sleep(uniform(1.2, 2.3))

            # *gender paste
            gender_select.hover()
            time.sleep(uniform(0.4, 0.8))
            gender_select.click()
            time.sleep(uniform(0.8, 1.4))
            human_type_2(page, '#gender', 'male')
            gender_select.press("Enter")
            time.sleep(uniform(1.2, 2.3))

            # *click next but
            next_but.hover()
            time.sleep(uniform(0.4, 0.8))
            next_but.click()
            time.sleep(uniform(1.9, 4.1))

            # ?Get more from your phone number PAGE
            yes_im_in_but = page.wait_for_selector(
                "#view_container > div > div > div.pwWryf.bxPAYd > div > div.zQJV3 > div.dG5hZc > div.qhFLie > div > "
                "div "
                "> button > span")
            time.sleep(uniform(1.9, 4.1))
            yes_im_in_but.hover()
            time.sleep(uniform(0.4, 0.8))
            yes_im_in_but.click()
            time.sleep(uniform(1.2, 2.3))

            # ?Choose personalisation settings PAGE
            variant = random.choice([True, False])
            if variant:
                first_point = page.wait_for_selector(
                    "#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc "
                    "> div > form > span > section > div > div > div > div > div.ci67pc "
                    "> div > span > div:nth-child(1) > div > div.DVnhEd")
            else:
                first_point = page.wait_for_selector(
                    "#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc "
                    "> div > form > span > section > div > div > div > div > div.ci67pc "
                    "> div > span > div:nth-child(1) > div > div.enBDyd > div > "
                    "div.SCWude > div")

            next_but = page.wait_for_selector(
                "#view_container > div > div > div.pwWryf.bxPAYd > div > div.zQJV3 > div > "
                "div > div > div > button > span")
            first_point.hover()
            time.sleep(uniform(0.4, 0.8))
            first_point.click()
            time.sleep(uniform(0.8, 1.7))

            # *click next but
            next_but.hover()
            time.sleep(uniform(0.4, 0.8))
            next_but.click()
            time.sleep(uniform(1.9, 4.1))

            # ?Confirm personalisation settings and cookies PAGE
            page.wait_for_selector("#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc > div > form > "
                                   "span > div.pQ0lne > ul > li:nth-child(1) > div > div.vxx8jf > div.R1xbyb > div")
            page.mouse.wheel(0, 1000)
            time.sleep(uniform(0.8, 1.7))
            confirm_but = page.wait_for_selector("#view_container > div > div > div.pwWryf.bxPAYd > div > "
                                                 "div.zQJV3.F8PBrb > div > div > div:nth-child(2) > div > div > "
                                                 "button > "
                                                 "span")
            confirm_but.hover()
            time.sleep(uniform(0.4, 0.8))
            confirm_but.click()
            time.sleep(uniform(0.8, 1.7))

            # ?Privacy and Terms PAGE
            page.wait_for_selector("#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc > div > form > "
                                   "span > section > div > div > div.pQ0lne > ul > li:nth-child(1) > div")
            page.mouse.wheel(0, 3000)
            time.sleep(uniform(0.4, 0.8))
            i_agree_but = page.wait_for_selector(
                "#view_container > div > div > div.pwWryf.bxPAYd > div > div.zQJV3 > div "
                "> div.qhFLie > div > div > button > span")
            i_agree_but.hover()
            time.sleep(uniform(0.4, 0.8))
            i_agree_but.click()
            time.sleep(uniform(0.8, 1.7))
            DEBUG_CODE = 3  # ?debug status code
            # ?Account home PAGE

            print("Account successfully created, getting 2FA")
            page.wait_for_selector(
                "#gb > div.gb_Td.gb_ae.gb_0d > div.gb_Sd.gb_3d.gb_Te.gb_Je.gb_Qe > div.gb_Le > form > div > div > div "
                "> "
                "div > div > div.d1dlne > input.Ax4B8.ZAGvjd")
            print("home page loaded")
            DEBUG_CODE = 4  # ?debug status code

            try:
                secure_but = page.wait_for_selector(
                    "#yDmH0d > c-wiz > div > div:nth-child(2) > div > c-wiz > c-wiz > div "
                    "> div.wrDwse > div.tC9kZd > c-wiz > nav > ul > li:nth-child(4) > a >"
                    " div.iKN8Oe > figure > img", timeout=15000)
            except playwright.sync_api.TimeoutError:
                print("secure but type 1 not found")
                # try:
                #     secure_but = page.locator(
                #         'xpath=//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/c-wiz/c-wiz/div/div[1]/div[3]/c-wiz/nav/ul/li[4]/a/div['
                #         '1]/figure/img')
                # except playwright.sync_api.TimeoutError:
                #     print("unable to find secure button")
                #     return False
            time.sleep(uniform(1.2, 3.0))
            secure_but.hover()
            time.sleep(uniform(0.4, 0.8))
            secure_but.click()

            # ?Secure PAGE
            # *locate and click 2fa but
            try:
                two_fa_but = page.get_by_text("2-Step Verification is off")
                two_fa_but.hover(timeout=1500)
            except playwright.sync_api.TimeoutError:
                print("cant find by text 2, try another method")
                try:
                    two_fa_but = page.get_by_text("2-Step Verification")
                    two_fa_but.hover(timeout=1500)
                except playwright.sync_api.TimeoutError:
                    print("cant find by text 2, try another method")
                    try:
                        two_fa_but = page.wait_for_selector(
                            "#yDmH0d > c-wiz:nth-child(18) > div > div:nth-child(2) > div > c-wiz > c-wiz > div > "
                            "div.s7iwrf.gMPiLc.Kdcijb > div > div > c-wiz > section > div:nth-child(4) > div > div > "
                            "div:nth-child(2) > div > a > div > div.X9g6he > figure > img",
                            timeout=17000)
                    except playwright.sync_api.TimeoutError:
                        print("not found first type 2Fa, try another")
                        try:
                            two_fa_but = page.wait_for_selector(
                                "#c19 > div > div.msXOjf > div > h3",
                                timeout=10000)
                        except playwright.sync_api.TimeoutError:
                            print("non detected second type, try another")
                            try:
                                two_fa_but = page.wait_for_selector(
                                    "#i24 > div > div.iintNd > div > div.YaVKnd > figure > img",
                                    timeout=10000)
                            except playwright.sync_api.TimeoutError:
                                print("non detected type 3")

            two_fa_but.hover()
            time.sleep(uniform(0.4, 0.8))
            two_fa_but.click()
            time.sleep(uniform(1.2, 3.3))

            # ?wait main 2fa page and click "get started" but
            get_started_but = page.get_by_text("Get started")
            time.sleep(uniform(0.9, 1.6))
            get_started_but.hover()
            time.sleep(uniform(0.4, 0.8))
            get_started_but.click()
            time.sleep(uniform(1.2, 3.3))

            # ?2FA phone number page
            next_but = page.wait_for_selector(
                "#yDmH0d > c-wiz > div > div:nth-child(2) > div:nth-child(2) > c-wiz > div > div > "
                "div.hyMrOd > div.qNeFe.RH9rqf > div > div.A9wyqf > div:nth-child(1) > span > span", timeout=70000)
            next_but.hover()
            time.sleep(uniform(0.4, 0.8))
            next_but.click()
            time.sleep(uniform(1.2, 3.3))

            # ?2FA code input page
            DEBUG_CODE = 5  # ?debug status code
            code_input = page.locator(
                "#yDmH0d > c-wiz > div > div:nth-child(2) > div:nth-child(2) > c-wiz > div > div > "
                "div.hyMrOd > div.fuXTM > div > div:nth-child(1) > div > div.I4mZgb > "
                "div.qDDjIb.fKMMOd > div.OLq3Sc > div > div.aCsJod.oJeWuf > div > div.Xb9hP > input")
            code_input.hover()
            time.sleep(uniform(0.4, 0.8))
            code_input.click()
            time.sleep(uniform(0.4, 0.8))
            human_type_2(page, "#yDmH0d > c-wiz > div > div:nth-child(2) > div:nth-child(2) > c-wiz > div > div > "
                               "div.hyMrOd > div.fuXTM > div > div:nth-child(1) > div > div.I4mZgb > "
                               "div.qDDjIb.fKMMOd > "
                               "div.OLq3Sc > div > div.aCsJod.oJeWuf > div > div.Xb9hP > input",
                         "{}".format(get_second_code(num_id)))
            time.sleep(uniform(0.7, 1.4))

            # *search and click next but
            next_but = page.locator("#yDmH0d > c-wiz > div > div:nth-child(2) > div:nth-child(2) > c-wiz > div > div > "
                                    "div.hyMrOd > div.qNeFe.RH9rqf > div > div.A9wyqf > div:nth-child(1) > span > span")
            next_but.hover()
            time.sleep(uniform(0.4, 0.8))
            next_but.click()
            time.sleep(uniform(1.2, 3.3))

            try:
                fa_alt = page.wait_for_selector("#c16 > div > div.msXOjf > div > h3", timeout=7000)
                fa_alt.hover()
                time.sleep(uniform(0.4, 0.8))
                fa_alt.click()
                time.sleep(uniform(1.2, 3.3))
            except Exception as e:
                print(e, "non located alternative button")
            # ? It worked! turn on PAGE
            # * Find and click "TURN ON" button
            turn_on_but = page.locator(
                "#yDmH0d > c-wiz > div > div:nth-child(2) > div:nth-child(2) > c-wiz > div > div > "
                "div.hyMrOd > div.qNeFe.RH9rqf > div > div.A9wyqf > div:nth-child(2) > span > span")
            time.sleep(uniform(1.2, 3.3))
            turn_on_but.hover()
            time.sleep(uniform(0.4, 0.8))
            turn_on_but.click()
            time.sleep(uniform(1.2, 3.3))

            # ? 2FA add second steps to login PAGE
            DEBUG_CODE = 6  # ?debug status code
            # * Try find and click "backup codes" arrow
            codes_arrow = page.locator("#yDmH0d > c-wiz > div > div:nth-child(2) > div:nth-child(2) > c-wiz > "
                                       "div:nth-child(1) > div > div.YwhQ0 > div:nth-child(12) > div:nth-child(1) > "
                                       "div > "
                                       "div > div > div.GzPZ0c > div > a > span > span > span")

            codes_arrow.hover()
            time.sleep(uniform(0.4, 0.8))
            codes_arrow.click()
            time.sleep(uniform(1.2, 3.3))

            # ? Backup codes PAGE
            # * Find and click "Get backup codes" button
            get_codes_but = page.locator(
                "#yDmH0d > c-wiz > div > div:nth-child(2) > div:nth-child(2) > c-wiz > div > div "
                "> div.ciRgbc.Ru61We > div.Mwd2Jc > div > div > div > button > "
                "span.VfPpkd-vQzf8d")
            get_codes_but.hover()
            time.sleep(uniform(0.4, 0.8))
            get_codes_but.click()
            time.sleep(uniform(3, 6.3))

            # * Locate and extract codes
            codes_box = page.locator(
                "#yDmH0d > c-wiz > div > div:nth-child(2) > div:nth-child(2) > c-wiz > div > div > "
                "div:nth-child(4) > "
                "div.VfPpkd-WsjYwc.VfPpkd-WsjYwc-OWXEXe-INsAgc.KC1dQ.Usd1Ac.AaN0Dd.F2KCCe.HYI7Re"
                ".yOXhRb.E2bpG.injfOc > div > div:nth-child(2) > ul")
            backup_codes = extract_codes(codes_box.text_content().replace(" ", ""))
            print(backup_codes)

            DEBUG_CODE = 7  # ?debug status code
            # ?return registration report

            time_end = time.time()
            work_time = str(dt.timedelta(seconds=(time_end - time_start)))[3:7]
            finish_date = datetime.now().strftime("%d.%m")
            finish_time = str(datetime.now().time())[:5]
            proxy_geo = "{} // {}".format(proxy_country_code, proxy_city)
            return [[profile_name, uuid, finish_date, finish_time, proxy_geo, "GR", "None", "Test", "Test", email,
                     password, "None", work_time, DEBUG_CODE], backup_codes]
    except Exception as e:
        print(e)
        time_end = time.time()
        work_time = str(dt.timedelta(seconds=(time_end - time_start)))[3:7]
        finish_date = datetime.now().strftime("%d.%m")
        finish_time = str(datetime.now().time())[:5]
        proxy_geo = "{} // {}".format(proxy_country_code, proxy_city)
        return [[profile_name, uuid, finish_date, finish_time, proxy_geo, "GR", "ERROR", "ERROR", "ERROR", "ERROR",
                 "ERROR", "ERROR", work_time, DEBUG_CODE], "NONE"]


def find_profile():
    with open("profiles.json", 'r') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
    profiles = file_data["profiles"]

    for profile in profiles:
        if not profiles[profile]["used"]:
            print("find not used profile: ", profile)
            file_data["profiles"][profile]["used"] = True
            with open("profiles.json", 'w') as file:
                json.dump(file_data, file)
            return profile, file_data["profiles"][profile]


def main():
    time_start = time.time()
    profile_name, profile_data = find_profile()
    proxy_port = profile_data["port"]
    profile_uuid = profile_data["UUID"]
    country_code, _, city = get_proxy(proxy_port, "GB")
    report = create_account([profile_name, profile_uuid, country_code, city, proxy_port])
    print(report)
    reports_to_db([report])
    time_end = time.time()
    print("time: ", time_end - time_start)


def main_multi_thread():
    time_start = time.time()
    start_data = []
    for i in range(5):
        profile_name, profile_data = find_profile()
        proxy_port = profile_data["port"]
        profile_uuid = profile_data["UUID"]
        country_code, _, city = get_proxy(proxy_port, "GB")
        start_data.append([profile_name, profile_uuid, country_code, city, proxy_port])
    print(start_data)
    task1 = pool.submit(create_account, start_data[0])
    time.sleep(11)
    task2 = pool.submit(create_account, start_data[1])
    time.sleep(11)
    task3 = pool.submit(create_account, start_data[2])
    time.sleep(11)
    task4 = pool.submit(create_account, start_data[3])
    time.sleep(11)
    task5 = pool.submit(create_account, start_data[4])
    time.sleep(11)

    rep1 = task1.result()
    rep2 = task2.result()
    rep3 = task3.result()
    rep4 = task4.result()
    rep5 = task5.result()

    # report = create_account(profile_name, profile_uuid, country_code, city, proxy_port)
    # print(report)
    reports_to_db([rep1, rep2, rep3, rep4, rep5])
    time_end = time.time()
    print("time: ", time_end - time_start)


pool = ThreadPoolExecutor()
main_multi_thread()

# main()
# create_account("123", 2, 3, 4, 40003)
# get_debug_port("140d2b6b74b74d86b351b344fda1892d")


