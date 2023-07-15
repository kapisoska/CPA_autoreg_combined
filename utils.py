import random
import names


def get_full_name():
    """
    0 element - Name
    1 element - Surname
    :return: list
    """
    fullname = names.get_full_name(gender='male').split()
    return fullname


def get_pass(length=11):
    """

    :param length: password length (Default: 11 symbols)
    :return: string
    """
    pas = ''
    for x in range(length):  # Количество символов (Default = 11)
        pas = pas + random.choice(list(
            '1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))  # Символы, из которых будет составлен пароль
    return pas


def grouper(iterable, n):
    args = [iter(iterable)] * n
    return zip(*args)


def extract_codes(codes_str):
    l = [''.join(i) for i in grouper(codes_str, 8)]
    codes = ""
    for code in l:
        codes = codes + code + "\n"
    return codes
