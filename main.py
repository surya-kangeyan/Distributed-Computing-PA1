import socket
import os
import argparse

import mimetypes
from threading import Thread, Lock
from datetime import datetime

# Global count of active connections and lock for thread-safe operations
active_connections = 0
lock = Lock()
# BASE_PATH = "/Users/suryakangeyan/Projects/DC/PA1/www.sjsu.edu"


mime_types = {
    '.html': 'text/html',
    '.htm': 'text/html',
    '.shtml': 'text/html',
    '.css': 'text/css',
    '.xml': 'text/xml',
    '.gif': 'image/gif',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.js': 'application/javascript',
    '.txt': 'text/plain',
    '.png': 'image/png',
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.ico': 'image/x-icon',
    '.svg': 'image/svg+xml',
    '.svgz': 'image/svg+xml',
    '.webp': 'image/webp',
    '.woff': 'font/woff',
    '.jar': 'application/java-archive',
    '.json': 'application/json',
    '.doc': 'application/msword',
    '.pdf': 'application/pdf',
    '.xhtml': 'application/xhtml+xml',
    '.zip': 'application/zip',
    '.bin': 'application/octet-stream',
    '.exe': 'application/octet-stream',
    '.dll': 'application/octet-stream',
    '.deb': 'application/octet-stream',
    '.dmg': 'application/octet-stream',
    '.iso': 'application/octet-stream',
    '.img': 'application/octet-stream',
    '.msi': 'application/octet-stream',
    '.msp': 'application/octet-stream',
    '.msm': 'application/octet-stream',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.mid': 'audio/midi',
    '.midi': 'audio/midi',
    '.kar': 'audio/midi',
    '.mp3': 'audio/mpeg',
    '.ogg': 'audio/ogg',
    '.m4a': 'audio/x-m4a',
    '.ra': 'audio/x-realaudio',
    '.3gpp': 'video/3gpp',
    '.3gp': 'video/3gpp',
    '.mp4': 'video/mp4',
    '.mpeg': 'video/mpeg',
    '.mpg': 'video/mpeg',
    '.mov': 'video/quicktime',
    '.webm': 'video/webm',
    '.flv': 'video/x-flv',
    '.m4v': 'video/x-m4v',
    '.mng': 'video/x-mng',
    '.asx': 'video/x-ms-asf',
    '.asf': 'video/x-ms-asf',
    '.wmv': 'video/x-ms-wmv',
    '.avi': 'video/x-msvideo',
}

def get_mime_type(file_path, is_error=False):
    if is_error:
        return "text/html"
    _, ext = os.path.splitext(file_path)
    return mime_types.get(ext, "application/octet-stream")


def read_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def calculate_timeout():
    # Simple heuristic: base timeout value minus a factor of the active connections
    base_timeout = 10  # Base timeout in seconds (adjust based on needs)
    reduction_factor = 0.5  # Reduction per active connection
    with lock:
        timeout = max(1, base_timeout - (reduction_factor * active_connections))
    return timeout

def generate_response_header(http_version,status_code, content_type, content_length,keep_alive):
    response_lines = [
        f"{http_version} {status_code}",
        f"Content-Type: {content_type}",
        f"Content-Length: {content_length}",
        f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        "Connection: keep-alive" if keep_alive else "Connection: close",
    ]
    return "\r\n".join(response_lines)

def process_request(client_connection, method, path, http_version, keep_alive):
    if method != "GET":
        file_content =  b"<h1>405 Method Not Allowed</h1>"
        response = f"{http_version} 405 Method Not Allowed \r\nAllow: GET\r\n\r\n"
        client_connection.sendall(response.encode('utf-8')+file_content)
        return
    if path == "/":
        path = "/index.html"
    file_path = os.path.join(BASE_PATH, path.lstrip("/"))

    if os.path.exists(file_path) and not os.path.isdir(file_path):
        if os.access(file_path, os.R_OK):
            file_content = read_file(file_path)
            if file_content is None:  # Handling potential 500 Internal Server Error
                file_content = b"<h1>500 Internal Server Error</h1>"
                resp = generate_response_header(http_version, "500 Internal Server Error",
                                                get_mime_type(file_path, True), len(file_content), keep_alive)
            else:
                mime_type = get_mime_type(file_path)
                resp = generate_response_header(http_version, "200 OK", mime_type, len(file_content), keep_alive)

            # print("Secondary headers")
            # print(resp)
            # response = f"{http_version} 200 OK\r\nContent-Type: {mime_type}\r\n"
        else:
            file_content = b"<h1>403 Permission denied</h1>"
            resp = generate_response_header(http_version, "403 Forbidden", get_mime_type(file_path, True), len(file_content),
                                            keep_alive)

    else:
        file_content = b"<h1>404 Not Found</h1>"
        resp = generate_response_header(http_version, "404 Not Found", get_mime_type(file_path,True), len(file_content), keep_alive)
        # response = f"{http_version} 404 Not Found\r\nContent-Type: text/html\r\n"
    resp += "\r\n\r\n"
    # response += "Connection: keep-alive\r\n" if keep_alive else "Connection: close\r\n"
    #
    # response += f"Content-Length: {len(file_content)}\r\n\r\n"
    #
    # print("main3.py printing the response headers")
    # print(response)
    client_connection.sendall(resp.encode('utf-8') + file_content)

def handle_client_connection(client_connection, client_address):
    global active_connections
    with lock:
        active_connections += 1

    keep_alive = True
    while keep_alive:
        try:
            client_connection.settimeout(calculate_timeout())
            request_data = client_connection.recv(1024).decode('utf-8')
            if not request_data:
                break

            request_lines = request_data.split('\n')
            request_line = request_lines[0].strip()
            print(f"Received request: {request_line}")

            try:
                method, path, http_version = request_line.split(" ", 2)
            except ValueError:
                print(f"Ignoring malformed request: {request_line}")
                continue

            if "HTTP/1.1" in http_version:
                process_request(client_connection, method, path, http_version, keep_alive=True)
            elif "HTTP/1.0" in http_version:
                process_request(client_connection, method, path, http_version, keep_alive=False)
                break
            else:
                print("Unsupported HTTP version.")
                # break

        except socket.timeout:
            print("No further requests received. Closing the connection due to inactivity.")
            break

    with lock:
        active_connections -= 1
    client_connection.close()
    print(f"Connection with {client_address} has been closed.")

def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server listening on {host}:{port}...")
        while True:
            client_connection, client_address = server_socket.accept()
            print(f"Connection from {client_address} | Active connections: {active_connections}")
            Thread(target=handle_client_connection, args=(client_connection, client_address)).start()

def get_command_line_arguments():
    parser = argparse.ArgumentParser(description='Programming Assignment 1 Server')
    parser.add_argument('-document_root', type=str, required=True, help='The directory from which to serve files')
    parser.add_argument('-port', type=int, required=True, help='The port on which the server listens', choices=range(8000, 9999))
    args = parser.parse_args()
    return args.document_root, args.port

if __name__ == "__main__":
    document_root, port = get_command_line_arguments()
    BASE_PATH = document_root
    start_server('127.0.0.1', port)
