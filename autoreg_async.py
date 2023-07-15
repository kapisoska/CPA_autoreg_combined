import time
import asyncio
import requests
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from random import uniform
import random
from utils import get_pass, get_full_name
from colorama import init, Fore, Back, Style
from sms_api import get_germany, get_phone_code, get_second_code

init(autoreset=True)
LOCAL_API = "http://localhost:61135/api/profiles"


def get_debug_port(profile_id):
    data = requests.post(
        f'{LOCAL_API}/start', json={'uuid': profile_id, 'headless': False, 'debug_port': True}
    ).json()
    print(data['ws_endpoint'])
    return data


async def human_type(page, selector, text):
    for symbol in text:
        await page.locator(selector).type(symbol)
        delay = uniform(0.05, 0.1)
        print(delay)
        await asyncio.sleep(delay)


async def human_type_2(page, selector, text, strt_delay=0, dct_delays={('a', 'color'): 0.15}, delayrange=(0.2, 0.45)):
    last_char = ' '

    time.sleep(strt_delay)
    for char in text:
        delay = dct_delays.get((last_char, char), uniform(delayrange[0], delayrange[1]))
        await asyncio.sleep(delay)
        await page.locator(selector).type(char)
        last_char = char


async def main(uuid):
    async with async_playwright() as p:
        ws_endpoint = get_debug_port(uuid)['ws_endpoint']
        # ws_endpoint = 'ws://127.0.0.1:54300/devtools/browser/31e5947d-0ace-49ae-b122-a315be4b3126'
        browser = await p.chromium.connect_over_cdp(ws_endpoint)
        context = browser.contexts[0]
        page = context.pages[0]

        # page2 = context.pages[1]
        # print(page.url)
        # print(await page2.title())

        # await page.mouse.wheel(delta_x=0, delta_y=500)

        # print("done")
        # input()

        # # ------------------- get google page
        await page.goto('https://google.com')
        print("wait loading search page")
        await page.wait_for_selector('#L2AGLb > div')
        print("search page loaded")

        # # ------------------- click accept all but
        await asyncio.sleep(uniform(0.5, 1.5))
        await page.hover('#L2AGLb > div')
        await asyncio.sleep(uniform(0.4, 0.8))
        await page.click('#L2AGLb > div')
        await asyncio.sleep(uniform(1.0, 2.0))

        # # ------------------- search 'google account'
        await human_type_2(page,
                           'body > div.L3eUgb > div.o3j99.ikrT4e.om7nvf > form > div:nth-child(1) > div.A8SBwf > div.RNNXgb > div > div.a4bIc > input',
                           'google account')
        await asyncio.sleep(uniform(0.4, 0.8))
        await page.locator(
            'body > div.L3eUgb > div.o3j99.ikrT4e.om7nvf > form > div:nth-child(1) > div.A8SBwf > div.RNNXgb > div > div.a4bIc > input').press(
            'Enter')

        # # ------------------- click create account
        but = await page.wait_for_selector(
            '#xaiYPc > div > div:nth-child(3) > div > ga-signed-out-buttons > div > ga-text-button > a > div')
        await asyncio.sleep(uniform(3.0, 6.0))
        await but.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await but.click()

        # # ------------------- paste login info
        email_input = await page.wait_for_selector('#username')
        name_input = page.locator('//*[@id="firstName"]')
        surname_input = page.locator('#lastName')
        password_input = page.locator('#passwd > div.aCsJod.oJeWuf > div > div.Xb9hP > input')
        confirm_pass = page.locator('#confirm-passwd > div.aCsJod.oJeWuf > div > div.Xb9hP > input')
        next_but = page.locator('#accountDetailsNext > div > button > span')

        # get user info
        name, surname = get_full_name()
        email = name + str(random.randint(0, 100)) + surname + str(random.randint(0, 100))
        password = get_pass()
        print(Fore.GREEN + name + ' ' + surname)
        print(Fore.GREEN + email)
        print(Fore.GREEN + password)
        await asyncio.sleep(uniform(3.0, 6.0))

        # email
        await email_input.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await email_input.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#username', email)
        await asyncio.sleep(uniform(1.2, 2.3))
        # name
        await name_input.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await name_input.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '//*[@id="firstName"]', name)
        await asyncio.sleep(uniform(1.2, 2.3))
        # surname
        await surname_input.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await surname_input.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#lastName', surname)
        await asyncio.sleep(uniform(1.2, 2.3))

        # password
        await password_input.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await password_input.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#passwd > div.aCsJod.oJeWuf > div > div.Xb9hP > input', password)
        await asyncio.sleep(uniform(1.2, 2.3))

        # confirm_pass
        await confirm_pass.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await confirm_pass.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#confirm-passwd > div.aCsJod.oJeWuf > div > div.Xb9hP > input', password)
        await asyncio.sleep(uniform(1.2, 2.3))

        # click next but
        await next_but.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await next_but.click()

        # # ------------------- paste phone number and verif them
        phone_input = await page.wait_for_selector('#phoneNumberId')
        next_but = page.locator(
            '#view_container > div > div > div.pwWryf.bxPAYd > div > div.zQJV3 > div > div.qhFLie > div > div > button > span')
        await asyncio.sleep(uniform(1.9, 4.1))
        num_id, phone_number = get_germany()

        # paste phone number
        await phone_input.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await phone_input.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#phoneNumberId', '+{}'.format(phone_number))
        await asyncio.sleep(uniform(1.2, 2.3))

        # click next but
        await next_but.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await next_but.click()

        # wait page with verif input and paste verif code
        code_input = await page.wait_for_selector('#code')
        verif_but = page.locator(
            '#view_container > div > div > div.pwWryf.bxPAYd > div > div.zQJV3 > div > div.qhFLie > div > div > button > span')
        await asyncio.sleep(uniform(3.0, 6.0))

        await code_input.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await code_input.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#code', str(get_phone_code(num_id)))
        await asyncio.sleep(uniform(1.2, 2.3))

        await verif_but.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await verif_but.click()
        await asyncio.sleep(uniform(1.2, 2.3))
        # # ------------------- paste user info

        day_input = await page.wait_for_selector('#day')
        moth_select = page.locator('#month')
        year_input = page.locator('#year')
        gender_select = page.locator('#gender')
        next_but = page.locator(
            '#view_container > div > div > div.pwWryf.bxPAYd > div > div.zQJV3 > div > div.qhFLie > div > div > button > span')
        await asyncio.sleep(uniform(3.0, 6.0))

        # day paste
        await day_input.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await day_input.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#day', str(random.randint(1, 27)))
        await asyncio.sleep(uniform(1.2, 2.3))

        # month paste
        month_list = ['janu', 'feb', 'mar', 'april', 'may', 'june', 'july', 'aug', 'sep', 'oct', 'nov', 'dec']
        await moth_select.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await moth_select.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#month', random.choice(month_list))
        await moth_select.press("Enter")
        await asyncio.sleep(uniform(1.2, 2.3))

        # year paste
        await year_input.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await year_input.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#year', str(random.randint(1987, 1993)))
        await asyncio.sleep(uniform(1.2, 2.3))

        # gender paste
        await gender_select.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await gender_select.click()
        await asyncio.sleep(uniform(0.8, 1.4))
        await human_type_2(page, '#gender', 'male')
        await gender_select.press("Enter")
        await asyncio.sleep(uniform(1.2, 2.3))

        # click next but
        await next_but.hover()
        await asyncio.sleep(uniform(0.4, 0.8))
        await next_but.click()


from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor()


def run(uuid):
    asyncio.run(main(uuid))

AR_12 = '526ee5ecb5574822b468dd5768dc7ffd'
AR_11 = '8a230d9c764c45cfb8aa013c26ecbb2b'
pool.submit(run(AR_11))
pool.submit(run(AR_12))
print("started 2 profiles")

