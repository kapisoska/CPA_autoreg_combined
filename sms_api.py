import time
from smsactivate.api import SMSActivateAPI

import config

APIKEY1 = config.APIKEY1  # 1st
APIKEY2 = config.APIKEY2  # 2nd
APIKEY3 = config.APIKEY3  # 3rd
APIKEY4 = config.APIKEY4  # 4th
APIKEY5 = config.APIKEY5  # 5th

sa1 = SMSActivateAPI(APIKEY1)
sa2 = SMSActivateAPI(APIKEY2)
sa3 = SMSActivateAPI(APIKEY3)
sa4 = SMSActivateAPI(APIKEY4)
sa5 = SMSActivateAPI(APIKEY5)

activators = [sa1, sa2, sa3, sa4, sa5]
sa1.debug_mode = True
sa2.debug_mode = True
sa3.debug_mode = True
sa4.debug_mode = True
sa5.debug_mode = True

# config selected activator
main_sa = sa1


# sa2.getActiveActivations()

# print(sa1.getBalance()["balance"])
# print(sa2.getBalance()["balance"])
# print(sa3.getBalance()["balance"])
# print(sa4.getBalance()["balance"])
# print(sa5.getBalance()["balance"])

def get_active_mun_count():
    count_active_numbers = []
    for sa in activators:
        activ_numbers = sa.getActiveActivations()
        if activ_numbers["status"] == "success":
            count_active_numbers.append(str(len(sa.getActiveActivations()["activeActivations"])))
        else:
            count_active_numbers.append("0")
    return count_active_numbers


# print(get_active_mun_count())


# activations = sa.getActiveActivations()
# try:
#     print(activations['activeActivations'])
# except:
#     print(activations['error'])  # Статус ошибки


# status = sa.getNumbersStatus(country=23)
# print(status["go_0"])

# activations = sa1.getActiveActivations()
# print(activations["activeActivations"])
# number = sa.getNumber(service='go', country=43, verification="false")

# status = sa3.getStatus(id=1243779371)
# status = status.split(":")
# print(status[1])

# status = sa.setStatus(id=1234373406, status=8)
# 78 - FR // 43 - GR
def get_germany():
    number = main_sa.getNumber(service='go', country=43, verification="false")
    num_id = number["activation_id"]
    phone_num = number["phone"]
    return num_id, phone_num


# get_germany()


def get_phone_code(id):
    wait_time = 0
    status = main_sa.getStatus(id)  # STATUS_WAIT_CODE
    while main_sa.activationStatus(status)["status"] == "STATUS_WAIT_CODE" and wait_time < 120:
        status = main_sa.getStatus(id)
        print("already wait code, wait time is: {} s".format(wait_time))
        time.sleep(3)
        wait_time += 3
    if wait_time < 120:
        status = status.split(":")
        # print(status[1])
        return status[1]
    else:
        print("phone number is not valid")
        main_sa.setStatus(id, 8)
        return False


def get_second_code(id):
    wait_time = 0
    main_sa.setStatus(id=id, status=3)
    time.sleep(0.5)
    status = main_sa.getStatus(id)  # STATUS_WAIT_RETRY
    time.sleep(0.5)
    print("st: ", main_sa.activationStatus(status))
    time.sleep(1.5)
    while wait_time < 45 and main_sa.activationStatus(status)["status"].split(":")[0] != "STATUS_OK":
        print("st: ", main_sa.activationStatus(status)["status"])
        status = main_sa.getStatus(id)
        print("already wait second code, wait time is: {} s".format(wait_time))
        time.sleep(3)
        wait_time += 3
    if wait_time < 45:
        status = status.split(":")
        # print(status[1])
        return status[1]
    else:
        status = status.split(":")
        # print(status[1])
        return status[1]


def cancel_number(activation_id, status_to_set=8):
    main_sa.setStatus(id=activation_id, status=status_to_set)

# ids, ph = get_germany()
# print(ph)

# print( get_phone_code(ids))

# activ1 = sa1.getActiveActivations()["activeActivations"][0]
# print(type(activ1))
