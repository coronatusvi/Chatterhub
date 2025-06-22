# Chatterhub

---

### 🔷 **Chatterhub – Connecting every conversation, seamlessly and instantly.**

**Chatterhub** is a lightweight, scalable real-time messaging system designed to support group chat and future extensibility to 1-1 conversations. Built on top of WebSocket technology and RESTful APIs, Chatterhub provides seamless bi-directional communication for both web and mobile clients.

Key features include:

- Real-time group chat with persistent message history
- WebSocket-based communication layer
- RESTful API for message retrieval and user management
- Modular architecture ready for 1-1 messaging and notifications
- Dockerized environment with CI-ready setup
- Well-documented API and architecture for easy integration

Whether you're building a chat-enabled application, an internal team tool, or a learning project, **Chatterhub** gives you the foundation for fast, secure, and extensible messaging infrastructure.

---

---

## How to run the app

### Run the app locally

You can install the requirements locally using the following command

```bash
    conda create -n chatterhub-py310 python=3.10

    conda activate chatterhub-py310

    pip install -r requirements.txt

    sudo apt-get update
    sudo apt-get install -y libsqlite3-dev
```

or building with venv

```bash
    python3.12 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

Then finally, run the app with the following command

```bash
    uvicorn main:app --reload
```

### Run the application in Docker

You can run the app using Docker with the following commands:

```bash
    docker build -t chatterhub .
```

```bash
                docker run -p 8000:8000 chatterhub
```

After running, access the app at [http://localhost:8000](http://localhost:8000)
