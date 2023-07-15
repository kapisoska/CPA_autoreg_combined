import requests
import time


def check_proxy(proxy_port: int):
    proxies = {
        "http": "127.0.0.1:{}".format(str(proxy_port)),
        "https": "127.0.0.1:{}".format(str(proxy_port)),
    }
    try:
        time_start = time.time()
        response = requests.get("http://jsonip.com", proxies=proxies)
        time_end = time.time()
        print("request time: ", time_end - time_start)
        if time_end - time_start > 2.5:
            print("proxy so slow, try get new")
            return False
        print(response)
        # print(response.json())
        ip = response.json()["ip"]

        print("Your public IP is:", ip.split(",")[0])
    except requests.exceptions.ProxyError:
        print("BAD PROXY proxy")
        return False
    except Exception as ex:
        # print(ex)
        print("BAD PROXY json")
        return False

    r = requests.get("http://ip-api.com/json/{}".format(ip.split(",")[0]))

    print(r.json())
    return r.json()["countryCode"], r.json()["country"], r.json()["city"]


# print(check_proxy(40003))


def get_proxy(port, country):
    r = requests.get(
        "http://127.0.0.1:10101/api/get_ip_list?num=1&country={}&state=all&city=all&zip=all&isp=all&t=1&port={}"
        "&ip_time=1".format(country, port))

    proxy_info = check_proxy(port)
    while proxy_info is None:
        proxy_info = check_proxy(port)

    print(proxy_info)
    if proxy_info:
        if country != proxy_info[0]:
            print("Bad proxy, get new")
            get_proxy(port, country)
        return proxy_info
    else:
        get_proxy(port, country)


# print(get_proxy(40000, "AU"))


def check_proxy_v2(proxy_port):
    proxies = {
        "http": "127.0.0.1:{}".format(str(proxy_port)),
        "https": "127.0.0.1:{}".format(str(proxy_port)),
    }
    geo_time = 0.0
    g_time = 0.0
    for i in range(6):
        time_start = time.time()
        try:
            response = requests.get("http://ip-api.com/json/", proxies=proxies)
        except requests.exceptions.ProxyError:
            print("BAD PROXY")
            return False
        time_end = time.time()
        geo_time += time_end - time_start

    for i in range(6):
        time_start = time.time()
        res = requests.get("http://google.com", proxies=proxies)
        print(res)
        time_end = time.time()
        g_time += time_end - time_start



    print("ip/geo time: ", geo_time/6)
    print("goggle time: ", g_time / 6)


        # print(response.json())

    # print("request time: ", time_end - time_start)



check_proxy_v2(40003)
