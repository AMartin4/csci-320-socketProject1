import socket
import os
import hashlib  # needed to verify file hash


IP = '127.0.0.1'  # change to the IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size


def get_file_info(data: bytes) -> (str, int):
    return data[8:].decode(), int.from_bytes(data[:8],byteorder='big')


def upload_file(server_socket: socket, file_name: str, file_size: int):
    # create a SHA256 object to verify file hash
    file_verify = hashlib.sha256()

    # create a new file to store the received data
    with open(file_name+'.temp', 'wb') as file:
        byte_size = 0
        while True:
            chunk, client_address = server_socket.recvfrom(BUFFER_SIZE)
            byte_size += len(chunk)
            file.write(chunk)
            file_verify.update(chunk)
            server_socket.sendto(b'received', client_address)
            if byte_size == file_size:
                break

    # get hash from client to verify
    hash_calculated = (file_verify.digest())

    response_3, server_address = server_socket.recvfrom(BUFFER_SIZE)

    if response_3 == hash_calculated:
        server_socket.sendto(b'success', client_address)
    else:
        server_socket.sendto(b'failed', client_address)


def start_server():
    # create a UDP socket and bind it to the specified IP and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f'Server ready and listening on {IP}:{PORT}')

    try:
        while True:
            message, client_address = server_socket.recvfrom(BUFFER_SIZE)
            # expecting an 8-byte byte string for file size followed by file name
            file_name, file_size = get_file_info(message)
            server_socket.sendto(b'go ahead', client_address)
            upload_file(server_socket, file_name, file_size)
    except KeyboardInterrupt as ki:
        pass
    except Exception as e:
        print(f'An error occurred while receiving the file:str {e}')
    finally:
        server_socket.close()


if __name__ == '__main__':
    start_server()

