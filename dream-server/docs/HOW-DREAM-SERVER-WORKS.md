# How Dream Server Works

A complete guide to understanding Dream Server — what it is, why it exists, how every piece fits together, and how to make it your own. No programming experience required.

---

## 1. The Idea Behind Dream Server

Dream Server is a local AI system that runs entirely on your computer. When you use ChatGPT or Claude in a browser, your messages travel to servers owned by OpenAI or Anthropic. Those companies process your request and send back a response. That works, but it means your data leaves your machine, you pay per message or per month, and you're limited to what those companies offer.

Dream Server flips that model. It downloads an AI brain — called a language model — directly onto your hardware, then wraps it with everything you need to actually use it: a chat interface, voice input and output, web search, document understanding, image generation, workflow automation, and autonomous AI agents. All of it runs on your machine. Nothing leaves your network unless you tell it to.

The design philosophy is simple: you should be able to buy a computer, run one command, and have a complete AI system running in minutes. No configuration files to write. No drivers to debug. No cloud accounts to create.

---

## 2. Why Dream Server Exists

Setting up local AI without Dream Server typically looks like this: you install a model runner like Ollama, then a separate chat interface like Open WebUI, then configure them to talk to each other, then realize you want voice so you install Whisper separately, then text-to-speech, then you want workflows so you install n8n, then a vector database for document search, then you spend a weekend debugging why things can't find each other on the network.

Dream Server exists because that process is painful and unnecessary. Every one of those tools is excellent on its own, but making them work together requires systems knowledge that most people don't have and shouldn't need.

Dream Server solves this by:

- **Auto-detecting your hardware.** The installer figures out what GPU you have, how much memory it has, and picks the right AI model automatically. An RTX 4060 Ti with 8 gigabytes of video memory gets a 7-billion-parameter model. An RTX 4090 with 24 gigabytes gets a 32-billion-parameter model. You don't choose — it just works.

- **Pre-wiring everything together.** The chat interface already knows how to reach the language model. The voice system is already connected to the chat. The web search engine is already feeding results to the AI. You open a browser and start talking.

- **Using Docker containers.** Each service runs in its own isolated container. If one breaks, the others keep running. Updates are clean. Uninstalling is clean. Nothing pollutes your system.

- **Making everything moddable.** Every service is a plug-in. Don't want image generation? Disable it. Want to add your own service? Drop in a folder and run one command. The whole system is built to be taken apart and reassembled.

---

## 3. The Overall Architecture — How It All Fits Together

Dream Server is made up of services. Each service is a separate program running in its own Docker container, and they all communicate over an internal network. Think of it like a team of specialists in an office — each one has a specific job, and they pass work to each other through a shared hallway.

### The Core Services (always running)

These four services are the foundation. They're always on and can't be disabled.

**llama-server** is the brain. It loads your AI model into GPU memory and responds to questions. When you type a message in the chat, it goes to llama-server, which runs it through the model and generates a response word by word. It speaks the OpenAI API format, which means any tool that works with ChatGPT's API can also talk to your local llama-server. It runs on port 8080 internally.

**Open WebUI** is the face. It's a web-based chat interface that looks and feels like ChatGPT. You open it in your browser at localhost:3000. It handles conversation history, file uploads, web search integration, image generation requests, and voice input/output. It talks to llama-server behind the scenes — you never interact with llama-server directly unless you want to.

**Dashboard** is the control center. It's a web interface at localhost:3001 that shows you system status: which services are running, GPU usage, memory, disk space, model information, and health checks. It's built with React and talks to the Dashboard API.

**Dashboard API** is the brain of the control center. It's a Python server that gathers metrics from all the other services and exposes them through a REST API. The Dashboard frontend reads from this API to display your system status.

### The Recommended Services (on by default)

These are enabled during installation by default because most people want them.

**LiteLLM** is a gateway that sits in front of your language model. It lets you switch between local inference, cloud APIs like Claude or GPT-4, or a hybrid mode where local is the default and cloud is the fallback. It runs on port 4000.

**SearXNG** is a self-hosted search engine. When you ask your AI a question that needs current information, Open WebUI sends the query to SearXNG, which searches Google, DuckDuckGo, Brave, Wikipedia, GitHub, and Stack Overflow — all without tracking you. It runs on port 8888.

**Token Spy** monitors how many tokens your AI is processing — useful for tracking usage, especially if you're also using cloud APIs where tokens cost money.

### The Optional Services (you choose during install)

These are available but not enabled unless you ask for them.

**Whisper** converts your voice into text. You speak into your microphone, Whisper transcribes it, and the text goes to the AI as if you had typed it. It runs on port 9000.

**Kokoro** does the reverse — it takes the AI's text response and reads it aloud in a natural-sounding voice. Together with Whisper, you get a full voice conversation loop. It runs on port 8880.

**n8n** is a workflow automation platform with over 400 integrations. You can build automations like: "When I get an email with an attachment, summarize the attachment using my local AI and save the summary to a Google Doc." It has a visual drag-and-drop editor at localhost:5678.

**OpenClaw** is an autonomous AI agent framework. Unlike the chat interface where you ask one question at a time, OpenClaw lets the AI plan multi-step tasks, use tools, browse the web, and execute actions on its own. It runs on port 7860.

**Qdrant** is a vector database used for retrieval-augmented generation, or RAG. You can feed it documents — PDFs, text files, code repositories — and it stores them in a way that lets the AI search through them semantically. When you ask a question, the AI can pull relevant passages from your documents to inform its answer. It runs on port 6333.

**Embeddings** is a companion to Qdrant. It converts text into numerical vectors that Qdrant can store and search. It runs on port 8090.

**ComfyUI** is a node-based image generation system. You can generate images from text prompts using the FLUX.1 model. Open WebUI is pre-configured to send image generation requests to ComfyUI. It runs on port 8188.

**Perplexica** is a deep research engine — think of it as an AI-powered research assistant that can search the web and synthesize findings. It runs on port 3004.

**Privacy Shield** is a proxy that sits between your AI and any external APIs. It scrubs personally identifiable information — names, emails, phone numbers, addresses — from outgoing requests. If you're using cloud APIs in hybrid mode, Privacy Shield makes sure your private data doesn't leave your network. It runs on port 8085.

### How They Talk to Each Other

All services sit on a shared Docker network called `dream-network`. They find each other by name — Open WebUI reaches llama-server at `http://llama-server:8080`, SearXNG is at `http://searxng:8080`, and so on. You access them from your browser using localhost ports: 3000 for chat, 3001 for the dashboard, 5678 for workflows, and so on.

Here's what happens when you send a chat message:

1. You type "What's the weather in Portland?" into Open WebUI at localhost:3000.
2. Open WebUI sees this might need current information, so it sends a search query to SearXNG.
3. SearXNG searches multiple search engines and returns results.
4. Open WebUI bundles the search results with your question and sends the whole thing to llama-server.
5. llama-server runs your question plus the search context through the AI model.
6. The AI generates a response, which streams back to Open WebUI word by word.
7. You see the answer appear in your chat window.

If voice is enabled, you can speak step 1 instead of typing (Whisper transcribes it), and the AI can read step 7 aloud (Kokoro synthesizes it).

---

## 4. What Running It Actually Looks Like

### Installation

You clone the repository and run the installer:

```
git clone https://github.com/Light-Heart-Labs/DreamServer.git
cd DreamServer/dream-server
./install.sh
```

The installer runs 13 phases. It checks your system, detects your GPU, asks which optional features you want (voice, workflows, RAG, agents), generates secure passwords, downloads the right AI model for your hardware, pulls all the Docker images, starts everything, and runs health checks. The whole process takes 5 to 30 minutes depending on your internet speed and which model it's downloading.

By default, it uses bootstrap mode: it downloads a small 1.5-billion-parameter model first so you can start chatting within two minutes, then downloads your full model in the background and hot-swaps it when ready.

### Day-to-Day Usage

Once installed, you manage everything through the `dream` command-line tool:

```
dream status          Show which services are running, their health, and GPU stats
dream list            See all available services and whether they're enabled
dream logs llm        Watch the live log output from the language model
dream logs stt        Watch the Whisper speech-to-text logs
dream restart         Restart all services
dream stop            Shut everything down
dream start           Start everything back up
```

Most of the time, you just open localhost:3000 in your browser and chat. The system runs in the background. You can also open the dashboard at localhost:3001 to see GPU usage, service health, and model information.

### Switching Modes

Dream Server supports three modes:

**Local mode** (default) — everything runs on your hardware. No internet connection needed after the initial setup.

**Cloud mode** — the language model runs on cloud APIs (Claude, GPT-4, etc.) instead of locally. Useful if you don't have a GPU but still want the full ecosystem (search, workflows, agents, RAG). You provide your API keys in the .env file.

**Hybrid mode** — local inference is the default, but if your local model is busy or can't handle a request, it falls back to a cloud API automatically.

You switch modes with one command:

```
dream mode local
dream mode cloud
dream mode hybrid
```

### Switching Models

If you want a bigger or smaller model than what the installer chose:

```
dream model list         See available tiers
dream model swap T3      Switch to the Pro tier (bigger model)
dream model current      See what model you're running now
```

---

## 5. How Mods Work — Built to Be Taken Apart

Dream Server is designed from the ground up to be modified. Every service — even the core ones — follows the same extension pattern. There's no "special" code for built-in services versus add-ons. The chat interface, the search engine, the workflow tool — they're all extensions sitting in the same folder, following the same rules.

### The Extension Structure

Every service lives in its own folder under `extensions/services/`. Inside that folder, there are two files that matter:

**manifest.yaml** tells Dream Server about the service — what it's called, what port it uses, how to check if it's healthy, what other services it depends on, and whether it's a core service, a recommended one, or optional.

**compose.yaml** tells Docker how to run the service — which container image to use, what ports to expose, what environment variables it needs, and how much memory to allocate.

That's it. Those two files are all Dream Server needs to discover, manage, health-check, and display a service in the CLI, dashboard, and installer.

### A Real Example: Adding n8n

Here's what the n8n workflow automation extension looks like. Its folder is `extensions/services/n8n/` and it contains two files.

The manifest tells Dream Server: "I'm called n8n, my nickname is 'workflows', I run on port 5678, you can check my health at /healthz, I'm optional, and I need N8N_USER and N8N_PASS set in the environment."

The compose file tells Docker: "Pull the n8n image, run it with these environment variables, store its data in ./data/n8n, expose port 5678, limit it to 2 CPU cores and 4 gigabytes of RAM, and check health every 30 seconds."

When Dream Server starts, the service registry scans every folder under `extensions/services/`, reads each manifest, and builds a map of what's available. If a service has a `compose.yaml` file, it's enabled. If that file has been renamed to `compose.yaml.disabled`, it's disabled. That renaming is all that `dream enable` and `dream disable` do.

### Enabling and Disabling Services

```
dream enable n8n        Renames compose.yaml.disabled back to compose.yaml
dream disable n8n       Renames compose.yaml to compose.yaml.disabled
dream start n8n         Actually starts the container
dream stop n8n          Stops the container
```

When you enable a service, Dream Server also checks its dependencies. If n8n depended on another service that wasn't enabled, it would ask if you want to enable that too.

### Creating Your Own Extension

To add a completely new service to Dream Server:

1. Create a folder: `extensions/services/my-service/`
2. Write a `manifest.yaml` with your service's metadata
3. Write a `compose.yaml` with your Docker Compose definition
4. Run `dream enable my-service`
5. Run `dream start my-service`

Your service immediately shows up in `dream list`, `dream status`, the dashboard, and health checks. No code changes anywhere else. The system discovers it automatically.

A minimal manifest looks like this:

```yaml
schema_version: dream.services.v1

service:
  id: my-service
  name: My Custom Service
  aliases: [mine]
  container_name: dream-my-service
  port: 9999
  health: /health
  type: docker
  category: optional
  depends_on: []
```

And a minimal compose file:

```yaml
services:
  my-service:
    image: some-docker-image:latest
    container_name: dream-my-service
    restart: unless-stopped
    ports:
      - "9999:9999"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9999/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

### Aliases

Every service can have nicknames. Whisper's manifest defines aliases `stt` and `voice`. So `dream logs whisper`, `dream logs stt`, and `dream logs voice` all do the same thing. When you run any dream command with a service name, the service registry resolves aliases automatically.

### GPU Overlays

Some services need different Docker configurations depending on your GPU. ComfyUI, for example, has three compose files: `compose.yaml` for the base config, `compose.nvidia.yaml` for NVIDIA-specific GPU passthrough, and `compose.amd.yaml` for AMD ROCm settings. The installer detects your GPU and merges the right overlay automatically.

---

## 6. The File Map — Where to Find Things

Here's a practical reference for the most common things you might want to look at or change.

### Configuration

| What you want to change | Where to find it |
|--------------------------|-----------------|
| All settings (ports, model, mode, passwords) | `.env` in your install directory |
| See what settings are available | `.env.example` in the repo |
| LiteLLM routing (local/cloud/hybrid models) | `config/litellm/local.yaml`, `cloud.yaml`, or `hybrid.yaml` |
| SearXNG search engines | `config/searxng/settings.yml` |
| AI model file | `data/models/` (GGUF files live here) |
| OpenClaw agent config | `config/openclaw/openclaw.json` |

The `.env` file is the single most important configuration file. It controls which model to load, how much context the AI can handle, what ports everything runs on, your secrets and passwords, and whether you're in local, cloud, or hybrid mode. You can view it safely (with secrets hidden) using:

```
dream config show
```

Or edit it directly:

```
dream config edit
```

### Service Files

| What you want to do | Where to look |
|----------------------|--------------|
| See all available services | `extensions/services/` (one folder per service) |
| Check a service's settings | `extensions/services/<name>/manifest.yaml` |
| Check how a service runs in Docker | `extensions/services/<name>/compose.yaml` |
| See the core Docker setup | `docker-compose.base.yml` |
| See GPU-specific Docker settings | `docker-compose.nvidia.yml` or `docker-compose.amd.yml` |

### Installer

| What you want to understand | Where to look |
|-----------------------------|--------------|
| What the installer does, step by step | `installers/phases/01-preflight.sh` through `13-summary.sh` |
| How GPU detection works | `installers/lib/detection.sh` |
| How models are mapped to hardware tiers | `installers/lib/tier-map.sh` |
| Shared utility functions (colors, logging) | `installers/lib/constants.sh`, `logging.sh`, `ui.sh` |
| The main installer script | `install-core.sh` |

### Data and Storage

| What's stored where | Path |
|--------------------|------|
| AI model files (GGUF) | `data/models/` |
| Open WebUI conversations and settings | `data/open-webui/` |
| n8n workflow data | `data/n8n/` |
| Qdrant vector database | `data/qdrant/` |
| Saved configuration presets | `presets/` |

### Management

| What you want to do | Command |
|--------------------|---------|
| Check system health | `dream status` |
| Run full diagnostics | `dream doctor` |
| Save your current config | `dream preset save my-setup` |
| Restore a saved config | `dream preset load my-setup` |
| Quick chat from the terminal | `dream chat "What is the capital of France?"` |
| Run a performance benchmark | `dream benchmark` |
| Open a shell inside a container | `dream shell llm` |

---

## 7. Summary

Dream Server is a local AI stack that gives you ChatGPT-level capabilities on your own hardware. It runs 13 to 16 services — language model inference, chat interface, dashboard, voice, search, workflows, agents, vector database, image generation, and privacy tools — all pre-configured to work together out of the box.

Everything is built on Docker containers and managed through the `dream` CLI. Every service is a modular extension that can be enabled, disabled, or replaced. Configuration lives in one `.env` file. The installer handles hardware detection, model selection, and service orchestration automatically.

The system is designed so that you never have to touch a terminal if you don't want to — just open localhost:3000 and chat. But if you do want to go deeper, every layer is accessible: the configuration, the Docker setup, the service manifests, the installer phases, and the source code itself.

---

## 8. Where to Go From Here

Once you're comfortable with the basics, here are topics that will make you even more effective with Dream Server as a platform.

**Learn Docker basics.** Dream Server handles Docker for you, but understanding containers, images, volumes, and networks will make troubleshooting much easier. The official Docker "Get Started" guide is excellent.

**Explore the n8n workflow editor.** Open localhost:5678 and look through the template library. You can build automations that use your local AI without writing code — summarize emails, process documents, generate reports, monitor RSS feeds, and hundreds of other tasks.

**Try RAG with your own documents.** Enable Qdrant and the embeddings service, then upload PDFs or text files through Open WebUI. The AI will search your documents when answering questions, turning your local model into an expert on your specific content.

**Experiment with cloud/hybrid mode.** If you have API keys for Claude or GPT-4, try `dream mode hybrid`. Your local model handles most requests, but complex tasks can fall back to more powerful cloud models automatically.

**Build a custom extension.** Follow the extension pattern described in section 5. If there's a Docker-based tool you like — a code editor, a database interface, a monitoring tool — you can wrap it as a Dream Server extension in about 15 minutes.

**Read the other docs.** The full documentation index is at `docs/README.md` in the repo. The hardware guide helps you pick the right GPU. The extensions guide has advanced patterns like GPU overlays and dashboard plugins. The integration guide shows how to connect external applications to your local AI API.

---

*Part of the [Dream Server](https://github.com/Light-Heart-Labs/DreamServer) project by Light Heart Labs.*
