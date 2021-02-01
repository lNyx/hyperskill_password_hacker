import json
import socket
from time import sleep

HOST = "127.0.0.1"  # Standard loop-back interface (localhost)
PORT = 9090  # Port to listen on. All non-privileged ports > 1023


def serialize_response(response):
    return json.dumps({"result": response}).encode()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("Connected by:", addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                data = json.loads(data.decode())
                user_login = data["login"]
                user_pass = data["password"]
            except:
                conn.sendall(serialize_response('Bad request!'))
                continue

            if user_login == "root":
                if user_pass == "qwertY":
                    conn.sendall(serialize_response('Connection success!'))
                    exit()
                elif user_pass != "" and "qwertY".startswith(user_pass):
                    sleep(0.1)
                    conn.sendall(serialize_response('Wrong password!'))
                    # conn.sendall(serialize_response('Exception happened during login'))
                else:
                    conn.sendall(serialize_response('Wrong password!'))
            else:
                conn.sendall(serialize_response('Wrong login!'))
