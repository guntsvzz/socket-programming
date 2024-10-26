## Project 1: Socket Programming		

Propose the development of a network application program by writing the objectives of the program. What is the program for ? What characteristics does your application have? Which Transport Layer service (UDP or TCP) do your application require? Why? Justify your choice.

Design your application-layer protocol of your network application which you will develop. Please spend time thinking about the design of request/response and action for both clients and servers. This is the main objective of the project.
(For 1 and 2, submit a google docs file.)

Write your client and server programs that use your designed application-layer protocol. Note that the client and server programs should print messages and status that have been sent and received by the protocol for a viewing purpose as well. – Students are required to submit the source code of client and server programs.

Submit all the documents and your Client and Server programs. Towards the end of the semester, present your project in class.

Due date: 2024/11/24

## Mymemo 
server.py
```
python3 server.py
```

client.py
```
python3 -m streamlit run streamlit_client.py
```

## Requirements

```
pip install -r requirements.txt
```

```
├── server.py
├── streamlit_client.py
├── modules/
│   ├── __init__.py
│   ├── server/
│   │   ├── __init__.py
│   │   ├── client_handler.py
│   │   ├── server_app.py
│   │   └── user_management.py
│   └── client/
│       ├── __init__.py
│       ├── client_app.py
│       └── client_utils.py
├── assets/
│   ├── audio/
│   │   └── return_voice.wav
│   └── database/
│       └── user_data.json
├── requirements.txt

```

## Todo
- [x] Writing Protocol
- [x] Speech to Text and Text to Speech
- [ ] User database 
- [ ] Add Memory
