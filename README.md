# Distributed-Computing-PA1

README
======

##### Name: Suryakangeyan kandasamy gowdaman  

##### Assignment: Programming Assignment 1   

##### Course : Distributed computing  

Description:
------------
This server is a lightweight, multi-threaded HTTP server that can handle several client connections while serving static material from a defined document root directory. It only allows GET requests and adjusts its behavior dynamically using simple heuristics like adaptive timeout based on server load or recent response times to ensure optimal resource efficiency and responsiveness. When the server receives a request, it parses it, decides the necessary action depending on the HTTP method, retrieves the requested file from the local filesystem if it is available, and creates an HTTP response with the relevant MIME type. It supports common HTTP status codes such as 200 OK for successful requests and 404 Not Found, 403 Forbidden, 405 Method Not Allowed, and 500 Internal Server problem for various problem scenarios.

List Of Submitted Files:
------------
1. Main.py
2. README.md
3. PDF (containing all the necessary screenshots and method explanations.)

Instructions for Running the Server:
------------------------------------
1. Ensure Python 3 is installed on your system. This server was developed and tested with Python 3.8

2. Open a terminal or command prompt.

3. Navigate to the directory containing the server.py file.

4. Run the server using the following command, replacing [document_root] with the path to your document root directory and [port] with the desired port number:

    python server.py -document_root "[document_root]" -port [port]

   Example:
   
    python server.py -document_root "/path/to/web/content" -port 8080

5. Once the server is running, it will listen for connections on the specified port. You can access the served content by opening a web browser and navigating to:

    http://127.0.0.1:[port]/

   Replace [port] with the port number you specified when starting the server.

Demonstration:
--------------
To demonstrate the server's functionality, after starting the server as described above, you can use a web browser or a tool like curl to request files from the server. For example:

    curl http://127.0.0.1:8080/index.html

This command should return the content of the index.html file located in your specified document root directory.

## To test HTTP 1.0

1. Open Firefox browser   
2. Enter network.http.version  
3. Change value from 1.1 to 1.0   
4. Then try http://127.0.0.1:[port]/ on the search bar.

Screenshots:
------------
Screenshots will be included in the  next commit

Note:
-----
This server is intended for educational purposes and does not implement the full HTTP specification.