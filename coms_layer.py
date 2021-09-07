import socket
import time


def Coms(file_input, args):

    if args.send is True:
        if args.destination:
            ip = socket.gethostbyname(args.destination)
            if ip:
                send(file_input, args)
                print(ip)

    elif args.receive is True:
        receive(file_input, args)
        # receve a messege

    else:
        if args.receive is None:
            print(f"not a valid argument {args.receive}")
        elif args.send is None:
            print(f"not a valid argument {args.send }")


def send(file_input, args):

    print("file input", file_input)

    with open(file_input, "rb") as file_bytes:
        test_bytes = file_bytes.read()

    print("type: ", type(test_bytes),"\nmessege: ",test_bytes)


    HOST = args.destination  # The server's hostname or IP address
    PORT = args.port  # The port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(test_bytes)
        data = s.recv(1024)

    print('Sent', repr(data))


def receive(file_input, args):
    HOST = args.destination  # Standard loopback interface address (localhost)
    PORT = args.port  # Port to listen on (non-privileged ports are > 1023)

    print("file input", file_input)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"received message: {data}")
                conn.sendall(data)
