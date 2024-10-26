# How to run memorygpt-tcp

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
your_project/
├── server.py
├── client.py
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