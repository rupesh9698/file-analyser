# 📂 File Analyser

> **AI-powered file analysis and translation — upload anything, ask anything.**

Built with [Chainlit](https://chainlit.io) + [Google Gemini](https://deepmind.google/technologies/gemini/) and deployed on Oracle Cloud (Ubuntu/Ampere), with [Firebase Hosting](https://firebase.google.com/docs/hosting) as the public entry point.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Chainlit](https://img.shields.io/badge/Chainlit-Latest-FF4B4B?style=flat-square)](https://chainlit.io)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Docker](https://img.shields.io/badge/Docker-Containerised-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Firebase](https://img.shields.io/badge/Firebase-Hosting-FFCA28?style=flat-square&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Oracle Cloud](https://img.shields.io/badge/Oracle_Cloud-Ampere-F80000?style=flat-square&logo=oracle&logoColor=white)](https://oracle.com/cloud)

---

## ✨ What It Does

Upload **any file** and let Gemini AI do the heavy lifting:

| Action | Description |
|---|---|
| 💬 **Ask Questions** | Chat with your document — get summaries, find specific data, explain content |
| 🌐 **Translate** | Translate the full document into 25 languages with formatting preserved |
| 🖼️ **Image Analysis** | Describe images, extract text from screenshots, identify objects via Gemini Vision |
| 📊 **Data Analysis** | Query CSV/Excel files — averages, trends, comparisons, statistics |

---

## 📁 Supported File Types

| Category | Extensions |
|---|---|
| 📄 Documents | `.docx`, `.doc`, `.pdf`, `.txt`, `.md`, `.rst` |
| 📊 Spreadsheets | `.csv`, `.xlsx`, `.xls`, `.ods`, `.tsv` |
| 📑 Presentations | `.pptx`, `.ppt` |
| 🌐 Web / Markup | `.html`, `.htm`, `.xml`, `.svg`, `.json`, `.jsonl` |
| 🖼️ Images | `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`, `.tiff` |
| 💻 Code & Config | `.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`, `.cpp`, `.cs`, `.rb`, `.php`, `.sh`, `.yaml`, `.toml`, `.sql`, and more |
| 🗂️ Data | `.geojson`, `.xsd`, `.xsl`, `.log`, `.ini`, `.cfg`, `.env` |

> **Any other text-based file** is also accepted and read automatically.

---

## 🏗️ Architecture

```
User
 │
 ▼
file-analyse.web.app          ← Firebase Hosting (302 redirect)
 │
 ▼
https://file-analyser.duckdns.org   ← Oracle Cloud public IP
 │
 ▼
Nginx (port 80/443)           ← Reverse proxy with WebSocket support
 │
 ▼
Docker Container (port 7860)  ← Chainlit Python app
 │
 ▼
Google Gemini 2.5 Flash       ← LLM for analysis, translation, vision
```

> **Why Firebase redirects instead of proxies:** Chainlit requires WebSocket connections for its real-time UI. Firebase Hosting cannot proxy WebSockets to external servers, so it performs a `302` redirect to the Oracle Cloud instance.

---

## 🚀 Getting Started

### Prerequisites

| Tool | Purpose |
|---|---|
| Python 3.11+ | Runtime |
| Docker | Containerisation |
| Google Gemini API Key | AI backend — [get one free](https://aistudio.google.com/apikey) |
| Git | Version control |

---

### 🖥️ Local Development (Windows / macOS / Linux)

**1. Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/file-analyser.git
cd file-analyser
```

**2. Create a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Copy the example file and fill in your real values:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
CHAINLIT_AUTH_SECRET=any_long_random_string_here
CHAINLIT_TELEMETRY_ENABLED=false
```

**5. Run the app**

```bash
chainlit run app.py --host 0.0.0.0 --port 7860
```

Open your browser at **http://localhost:7860**

---

### 🐳 Local Development with Docker

```bash
# Build
docker build -t file-analyser:latest .

# Run
docker run -d \
  --name file-analyser \
  --env-file .env \
  -p 7860:7860 \
  file-analyser:latest

# View logs
docker logs file-analyser --tail 30
```

---

## ☁️ Production Deployment — Oracle Cloud (Ubuntu/Ampere)

> **Development machine:** Windows 11
> **Server:** Oracle Cloud — Ubuntu 22.04 on Ampere (ARM64)

### Step 1 — SSH into the Oracle server

```bash
# From Windows PowerShell
ssh -i C:\Users\YourName\.ssh\oracle_key.pem ubuntu@YOUR_ORACLE_PUBLIC_IP
```

---

### Step 2 — Clone the repository on the server

```bash
sudo mkdir -p /opt/file-analyser
sudo chown ubuntu:ubuntu /opt/file-analyser
git clone https://github.com/YOUR_USERNAME/file-analyser.git /opt/file-analyser
cd /opt/file-analyser
```

---

### Step 3 — Create the `.env` file on the server

> ⚠️ **Never create `.env` on Windows and push it to GitHub.**
> Always create it directly on the server via SSH so secrets never touch your laptop or Git history.

**Generate the Chainlit secret (Ubuntu has OpenSSL built-in):**

```bash
openssl rand -hex 32
```

Copy the output, then create the `.env` file:

```bash
nano /opt/file-analyser/.env
```

Paste the following (replace with your real values):

```env
GOOGLE_API_KEY=your_gemini_api_key_here
CHAINLIT_AUTH_SECRET=paste_the_openssl_output_here
CHAINLIT_TELEMETRY_ENABLED=false
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

---

### Step 4 — Build and run the Docker container

```bash
cd /opt/file-analyser

# Build the image
docker build -t file-analyser:latest .

# Run the container
docker run -d \
  --name file-analyser \
  --restart unless-stopped \
  --env-file /opt/file-analyser/.env \
  -p 7860:7860 \
  file-analyser:latest

# Verify it started
docker logs file-analyser --tail 30
```

---

### Step 5 — Open the firewall

Oracle Cloud has **two separate firewalls** — both must be configured.

**Oracle Console (web):**

1. Go to **Networking → Virtual Cloud Networks → Security Lists**
2. Add **Ingress Rule**: Protocol `TCP`, Port `7860`, Source `0.0.0.0/0`
3. Also ensure port `80` and `443` are open

**OS-level iptables (on the server):**

```bash
sudo iptables -I INPUT -p tcp --dport 7860 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT

# Persist across reboots
sudo apt install iptables-persistent -y
sudo netfilter-persistent save
```

---

### Step 6 — Configure Nginx reverse proxy

```bash
sudo nano /etc/nginx/sites-available/file-analyser
```

Paste:

```nginx
server {
    listen 80;
    server_name file-analyser.duckdns.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name file-analyser.duckdns.org;

    ssl_certificate     /etc/letsencrypt/live/file-analyser.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/file-analyser.duckdns.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 55M;
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;

        # Required for Chainlit WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/file-analyser /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

### Step 7 — Get SSL certificate with Certbot

```bash
sudo certbot --nginx -d file-analyser.duckdns.org
```

---

### Step 8 — Configure Firebase Hosting redirect

In your local project on Windows, update `firebase.json`:

```json
{
  "hosting": {
    "site": "file-analyser",
    "public": "public",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      { "source": "**", "destination": "/index.html" }
    ]
  }
}
```

The `public/index.html` contains an animated splash screen that redirects to `https://file-analyser.duckdns.org` after a brief loading animation.

Deploy:

```bash
firebase deploy --only hosting
```

---

## 🔄 Redeploying After Code Changes

**On Windows — push changes:**

```bash
git add .
git commit -m "your change description"
git push origin master
```

**On Oracle server — pull and rebuild:**

```bash
cd /opt/file-analyser
git pull origin master
docker build -t file-analyser:latest .
docker stop file-analyser && docker rm file-analyser && docker run -d \
  --name file-analyser \
  --restart unless-stopped \
  --env-file /opt/file-analyser/.env \
  -p 7860:7860 \
  file-analyser:latest
docker logs file-analyser --tail 20
```

---

## 🧩 Project Structure

```
file-analyser/
├── app.py                 # Main Chainlit application
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container definition
├── chainlit.md            # Chainlit welcome message (shown in UI)
├── .env.example           # Environment variable template (safe to commit)
├── .env                   # Real secrets — NEVER commit this
├── .gitignore             # Excludes .env, __pycache__, etc.
├── public/
│   └── index.html         # Firebase splash/redirect page
└── firebase.json          # Firebase Hosting configuration
```

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | ✅ Yes | Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `CHAINLIT_AUTH_SECRET` | ✅ Yes | Random secret for session signing — generate with `openssl rand -hex 32` on Linux |
| `CHAINLIT_TELEMETRY_ENABLED` | Optional | Set to `false` to disable Chainlit analytics (recommended) |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `chainlit` | Conversational UI framework |
| `langchain-google-genai` | Gemini LLM integration |
| `langchain-core` + `langchain-community` | LangChain base + document loaders |
| `pymupdf` | PDF text extraction |
| `python-docx` | Word document parsing |
| `python-pptx` | PowerPoint parsing |
| `pandas` | Spreadsheet/CSV data handling |
| `openpyxl` | `.xlsx` read/write engine |
| `xlrd` | Legacy `.xls` read engine |
| `beautifulsoup4` + `lxml` | HTML and XML parsing |
| `chardet` | Auto-detect file character encoding |
| `httpx` | Async HTTP client (LangChain transport) |
| `anyio` | Async compatibility layer |

---

## 🖥️ Infrastructure Overview

| Component | Technology | Notes |
|---|---|---|
| App runtime | Chainlit + Python 3.11 | Async, streaming responses |
| AI model | Gemini 2.5 Flash | Text, vision, translation |
| Container | Docker | `--restart unless-stopped` |
| Reverse proxy | Nginx | WebSocket + SSL termination |
| SSL | Let's Encrypt / Certbot | Auto-renewing |
| DNS | DuckDNS | Free dynamic DNS |
| Server | Oracle Cloud Ampere | ARM64, always-free tier |
| Public URL | Firebase Hosting | Splash page + redirect |
| Co-hosted apps | chess24 (PM2) · customer-data-management (Docker) | Isolated by `server_name` |

---

## 🔐 Security Notes

- `.env` is listed in `.gitignore` and is **never committed**
- Secrets are created directly on the server — they never touch the development machine or Git
- The `CHAINLIT_AUTH_SECRET` signs user sessions to prevent tampering
- Nginx handles SSL termination; the app container runs HTTP internally only
- Docker's `--env-file` flag injects secrets at runtime without baking them into the image

---

## 🐛 Troubleshooting

**App not responding after deploy:**
```bash
docker logs file-analyser --tail 50
docker ps  # confirm container is running
```

**Nginx 502 Bad Gateway:**
```bash
# Check if container is actually up on port 7860
curl http://localhost:7860
sudo nginx -t
```

**WebSocket disconnects:**

Ensure your Nginx config includes both headers:
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

**File upload failing:**

Check `client_max_body_size` in Nginx matches or exceeds `MAX_FILE_SIZE_MB` in `app.py`.

**`openssl` not available on Windows:**

Generate the `CHAINLIT_AUTH_SECRET` on the Oracle server instead — Ubuntu has OpenSSL built in:
```bash
openssl rand -hex 32
```

**Chainlit `async with cl.Message()` error:**

Your Chainlit version does not support the async context manager. Use explicit `.send()` + `.stream_token()` pattern instead. See `app.py` — this is already handled correctly.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with ☕ and way too many <code>docker rm</code> commands</sub>
</div>
