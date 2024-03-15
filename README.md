# Distributed-Computing-PA1

README
======

##### Name: Suryakangeyan kandasamy gowdaman  

##### Assignment: Programming Assignment 1   

##### Course : Distributed computing  

Description:
------------
This simple HTTP server is implemented in Python. It is capable of handling multiple simultaneous client connections on separate threads and serving static content from a specified document root directory. The server supports basic GET requests for files with a variety of MIME types. It also handles common HTTP response status codes such as 200 OK, 404 Not Found, 403 Forbidden, and 500 Internal Server Error.

The server is designed to be lightweight and does not require any external dependencies beyond the Python Standard Library. It utilizes multithreading to manage multiple connections, ensuring that the server can serve multiple clients simultaneously without significant performance degradation.


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