import socket
import os
import argparse

import mimetypes
from threading import Thread, Lock
from datetime import datetime

activeConnections = 0
lock = Lock()

# functions to be created
# handle request
# parse request
# handle error
# handle filetypes
# http1.1 handler
# http1.0 handler
#
# server start
# time heuristic - > need to research
# response json generator sender

mimeTypes = {
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

def getMimeTypeForFile(filePath, is_error=False):
    if is_error:
        return "text/html"
    print("getMimeTypeForFile checking the file path  ---->")
    print(filePath)
    dummyVal, ext = os.path.splitext(filePath)
    return mimeTypes.get(ext, "application/octet-stream")



def timeoutHeuristic():
    baseTimeout = 10
    redFac = 0.5
    with lock:
        timeout = max(1, baseTimeout - (redFac * activeConnections))
        #basically reducing half seconfd for each connection
    print(f"heuristic to get a sample timeout value ----> {timeout} ")
    return timeout

def headerTemplateGenerator(httpVer, statusCode, contentType, contenLength, keepAlive):
    #changing connection header depending on the http version
    headerString = [
        f"{httpVer} {statusCode}",
        f"Content-Type: {contentType}",
        f"Content-Length: {contenLength}",
        f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        "Connection: keep-alive" if keepAlive else "Connection: close",
    ]
    print(f"headerTemplateGenerator checking the sample template header ----> {headerString}")

    return "\r\n".join(headerString)

def requestHandler(clientConnection, method, path, httpVer, keepAlive):
    # only handle GET reqs, ignore all other reqs
    if method != "GET":
        fileContent =  b"<h1>405 Method Not Allowed</h1>"
        # response = " 405 Method Not Allowed \r\n"
        response = f"{httpVer} 405 Method Not Allowed \r\nAllow: GET\r\n\r\n"
        clientConnection.sendall(response.encode('utf-8') + fileContent)
        return
    if path == "/":
        path = "/index.html"
    filePath = os.path.join(BASE_PATH, path.lstrip("/"))

    if os.path.exists(filePath) and not os.path.isdir(filePath):
        if os.access(filePath, os.R_OK):
            fileContent = fileReaderFromPath(filePath)
            if fileContent is None:  # Handling potential 500 Internal Server Error
                fileContent = b"<h1>500 Internal Server Error</h1>"
                resp = headerTemplateGenerator(httpVer, "500 Internal Server Error",
                                               getMimeTypeForFile(filePath, True), len(fileContent), keepAlive)
            else:
                mime_type = getMimeTypeForFile(filePath)
                resp = headerTemplateGenerator(httpVer, "200 OK", mime_type, len(fileContent), keepAlive)

            # print("Secondary headers")
            # print(resp)
            # response = f"{http_version} 200 OK\r\nContent-Type: {mime_type}\r\n"
        else:
            fileContent = b"<h1>403 Permission denied</h1>"
            resp = headerTemplateGenerator(httpVer, "403 Forbidden", getMimeTypeForFile(filePath, True), len(fileContent),
                                           keepAlive)

    else:
        fileContent = b"<h1>404 Not Found</h1>"
        resp = headerTemplateGenerator(httpVer, "404 Not Found", getMimeTypeForFile(filePath, True), len(fileContent), keepAlive)
        # response = f"{http_version} 404 Not Found\r\nContent-Type: text/html\r\n"
    resp += "\r\n\r\n"
    # response += "Connection: keep-alive\r\n" if keep_alive else "Connection: close\r\n"
    #
    # response += f"Content-Length: {len(file_content)}\r\n\r\n"
    #
    # print("main.py printing the response headers")
    # print(response)
    clientConnection.sendall(resp.encode('utf-8') + fileContent)

def clientConnectionHandler(clientConnection, client_address):
    global activeConnections
    with lock:
        activeConnections += 1

    keepAlive = True
    while keepAlive:
        try:
            clientConnection.settimeout(timeoutHeuristic())
            requestData = clientConnection.recv(1024).decode('utf-8')
            if not requestData:
                break

            splitRequestData = requestData.split('\n')
            firstReqData = splitRequestData[0].strip()
            print(f"Received req from the client ----> {firstReqData}")
            try:
                method, path, httpVer = firstReqData.split(" ", 2)
            except ValueError:
                print(f"Ignoring malformed request and continuing with further reqs ----> {firstReqData}")
                continue
            if "HTTP/1.1" in httpVer:
                requestHandler(clientConnection, method, path, httpVer, keepAlive=True)
            elif "HTTP/1.0" in httpVer:
                requestHandler(clientConnection, method, path, httpVer, keepAlive=False)
                break #this break is what forces the thread to break (results in opening a new thread for further connections)
            else:
                print(f"Unsupported HTTP version boi  ----> {httpVer}")
                # break

        except socket.timeout:
            print("Timeout exception received received. Closing connection ")
            break

    with lock:
        activeConnections -= 1
    clientConnection.close()
    print(f"Connection with ----> {client_address} has been closed.")

def bootServer(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((host, port))
        serverSocket.listen(5)
        print(f"Programming Assignment 1 Server listening on {host} ---> {port}...")
        while True:
            clientConnection, clientAddress = serverSocket.accept()
            print(f"Connection from {clientAddress}")
            Thread(target=clientConnectionHandler, args=(clientConnection, clientAddress)).start()

def parseCommandLineArguments():
    argumentPArser = argparse.ArgumentParser(description='Programming Assignment 1 Server')
    argumentPArser.add_argument('-document_root', type=str, required=True, help='Location of Index.html')
    argumentPArser.add_argument('-port', type=int, required=True, help='Port to diaplay the website', choices=range(8000, 9999))
    args = argumentPArser.parse_args()
    return args.document_root, args.port

def fileReaderFromPath(filePath):
    try:
        with open(filePath, 'rb') as file:
            return file.read()
    except Exception as e:
        print(f"error while reading the file ----> {filePath}: {e}")
        return None



if __name__ == "__main__":
    documentRoot, port = parseCommandLineArguments()
    BASE_PATH = documentRoot
    bootServer('127.0.0.1', port)
