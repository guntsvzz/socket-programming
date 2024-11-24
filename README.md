# Project 1: Socket Programming		

Propose the development of a network application program by writing the objectives of the program. What is the program for ? What characteristics does your application have? Which Transport Layer service (UDP or TCP) do your application require? Why? Justify your choice.

Design your application-layer protocol of your network application which you will develop. Please spend time thinking about the design of request/response and action for both clients and servers. This is the main objective of the project.
(For 1 and 2, submit a google docs file.)

Write your client and server programs that use your designed application-layer protocol. Note that the client and server programs should print messages and status that have been sent and received by the protocol for a viewing purpose as well. – Students are required to submit the source code of client and server programs.

Submit all the documents and your Client and Server programs. Towards the end of the semester, present your project in class.

### Due date: 2024/11/24

## Installation
### Install Dependencies
```
pip install -r requirements.txt
```

### Configure Environment Variables 
Create a .env file in the root directory and populate it with the following:
```
OPENAI_API_VERSION= 
AZURE_OPENAI_ENDPOINT= 
AZURE_OPENAI_API_KEY= 
AZURE_SPEECH_KEY= 
AZURE_SPEECH_REGION= 
```

## Project Structure

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

## Usage 
### Starting the Server
Run the server using the following command:
```
python3 server.py
```
### Starting the Client
Launch the client interface with Streamlit:
```
python3 -m streamlit run streamlit_client.py
```

## Modules Overview
### Server Modules
- client_handler.py: Manages individual client connections and handles their requests.
- user_management.py: Handles user authentication, registration, and session management.
### Client Modules
- client_utils.py: Provides utility functions for the client, such as message formatting and protocol handling.

## Todo
User Aspect
- [x] Writing Protocol
- [ ] Encryption password
LLM Aspect
- [x] Speech to Text and Text to Speech
- [ ] Text Only
- [ ] Add Memory
