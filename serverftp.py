import socket
import os
import threading
from threading import Thread
from  zipfile import ZipFile




USERS = {
    "aviad": "1212",
    "noam.txt": "123",
    "matan": "4343",
    "yonatan": "2121"
}

user= []
passwords = []
users = USERS.keys()
passwords = USERS.values()

def handle_client(client_socket, client_address):
    names = []
    while True:
        IP = "127.0.0.1"
        PORT = 6500
        print(f"Accepted connection from {client_address}")
        # Send welcome message
        welcome_msg = "220 Welcome to Simple FTP Server\r\n"
        client_socket.send(welcome_msg.encode())

        while True:
            data = client_socket.recv(1024).decode().strip()
            check = data
            if not data:
                break
            print(f"Received: {data}")

            try:
                command, argument = data.split(" ", 1)
            except ValueError:
                command = data

            if 'X' in command:#just in case
                command = command.replace('X', '')

            #all commands
            if command == "USER":
                client_socket.send("331 User name okay, need password.\r\n".encode())
                if argument in users:
                    data = client_socket.recv(1024).decode().strip()
                    if not data:
                        return
                        break

                    print(f"Received: {data}")

                    try:
                        command, argument = data.split(" ", 1)
                    except ValueError:
                        command = data

                    if 'X' in command:
                        command = command.replace('X', '')

                    if command == "PASS":
                        if argument in passwords:
                            client_socket.send("230 User logged in, proceed.\r\n".encode())
                        else:
                            client_socket.send(
                                "502 Command not implemented.\r\n".encode())  # צריך לשנות להודעה של LOGING FAILED

                else:
                    data = client_socket.recv(1024).decode().strip()
                    if not data:
                        return
                        break

                    print(f"Received: {data}")

                    try:
                        command, argument = data.split(" ", 1)
                    except ValueError:
                        command = data

                    if 'X' in command:
                        command = command.replace('X', '')

                    if command == "PASS":
                        client_socket.send("502 Command not implemented.\r\n".encode())
            elif command == "PWD":
                current_directory = os.getcwd()
                response = f"257 \"{current_directory}\" is the current directory\r\n"
                client_socket.send(response.encode())
            elif command == "TYPE":
                requested_type = data.split()[1].upper()

                if requested_type == "A":
                    data_type = "A"  # מחליף לאסקי בשביל קבצי טקטס
                    client_socket.send("200 Switching to ASCII mode\r\n".encode())
                elif requested_type == "I":
                    data_type = "I"  # מחליף לבינארי בשביל תמונות
                    client_socket.send("200 Switching to binary mode\r\n".encode())
            elif command == "PASV":
                passive_mode = True
                passive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                passive_socket.bind((IP, 0))
                passive_socket.listen(1)
                passive_port = passive_socket.getsockname()[1]
                response = f"227 Entering Passive Mode ({','.join(IP.split('.'))},{passive_port // 256},{passive_port % 256})\r\n"
                client_socket.send(response.encode())
            elif command == "LIST":
                client_socket.send("150 Opening data connection for directory list\r\n".encode())
                if passive_mode:
                    data_socket, _ = passive_socket.accept()
                    files = os.listdir("server_file")
                    listing = "\r\n".join(files).encode() + b"\r\n"
                    data_socket.send(listing)
                    data_socket.close()
                    passive_mode = False
                    client_socket.send("226 Directory send OK\r\n".encode())
                else:
                    client_socket.send("425 Use PASV first\r\n".encode())
            elif command == "DELE":
                n = argument.split("/")
                name_file = n[-1]
                filepath = os.path.join("server_file", name_file)

                if os.path.exists(filepath):
                    os.remove(filepath)
                    client_socket.send("250 File deleted successfully\r\n".encode())
                else:
                    client_socket.send("550 File not found\r\n".encode())
            elif command == "RETR":
                    filename = data.split()[1]
                    filepath = os.path.join("server_file", filename)
                    if os.path.exists(filepath) and os.path.isfile(filepath):
                        client_socket.send("150 Opening data connection for file download\r\n".encode())
                        if passive_mode:
                            data_socket, _ = passive_socket.accept()
                            with open(filepath, "rb") as file:
                                while True:
                                    data = file.read(1024)
                                    if not data:
                                        break
                                    data_socket.send(data)
                            data_socket.close()
                            passive_mode = False
                            client_socket.send("226 File download completed\r\n".encode())
                        else:
                            client_socket.send("425 Use PASV first\r\n".encode())
                    else:
                        client_socket.send("550 File not found\r\n".encode())
            elif command == "STOR":
                filename = data.split()[1]
                names.append(filename)
                print(names)
                filepath = os.path.join("server_file", filename)
                client_socket.send("150 Opening data connection for file upload\r\n".encode())
                if passive_mode:
                    data_socket, _ = passive_socket.accept()
                    with open(filepath, "wb") as file:
                        while True:
                            data = data_socket.recv(1024)
                            if not data:
                                break
                            file.write(data)
                    data_socket.close()
                    passive_mode = False
                    client_socket.send("226 File uploaded successfully\r\n".encode())
                else:
                    client_socket.send("425 Use PASV first\r\n".encode())

                if check == "STOR end.txt":
                    if len(names) > 0:
                        with ZipFile("server_file/end.zip", "w") as zip_object:
                            names.remove("end.txt")
                            for f in names:
                                filepath = os.path.join("server_file", f)
                                zip_object.write(filepath)

            else:
                client_socket.send("502 Command not implemented.\r\n".encode())


    server_socket.close()


def main():
    IP = "127.0.0.1"
    PORT = 6500
    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((IP, PORT))
        server_socket.listen()
        print(f"Listening on {IP}:{PORT}")
        client_socket, client_address = server_socket.accept()
        new_thraed = threading.Thread(target=handle_client, args=(client_socket, client_address,))
        new_thraed.start()



if __name__ == "__main__":
    main()
