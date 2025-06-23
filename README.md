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

```bash
    git clone https://github.com/coronatusvi/Chatterhub.git
    cd Chatterhub
```

### Run the app locally

You can install the requirements locally using the following command

```bash
    conda create -n chatterhub-py310 python=3.10

    conda activate chatterhub-py310

    pip install -r requirements.txt
```

If you can install [https://anaconda.org/anaconda/conda](conda)
If your computer is on python version != 3.10, you can download 3.10 in parallel using the method below. I still recommend you to use [https://anaconda.org/anaconda/conda](conda)

or building with venv

```bash
    python3 -m venv venv 
    source venv/bin/activate  
    pip install -r requirements.txt
```

You can install Database

```bash
    sudo apt-get update
    sudo apt-get install -y libsqlite3-dev
```

SQLite is chosen for its lightweight, serverless nature, making deployment and maintenance effortless for our project. While perceived as small-scale, it efficiently handles large datasets into terabytes, with SQL syntax mirroring that of larger databases.

Then finally, run the app with the following command

```bash
    # Host reload
    uvicorn main:app --reload

    # Save process
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
```

### Run the application in Docker

You can run the app using Docker with the following commands:

```bash
    docker build -t chatterhub .
```

```bash
                docker run -p 8000:8000 chatterhub
```

After running, access the app at [http://localhost:8000](http://127.0.0.1:8000)
