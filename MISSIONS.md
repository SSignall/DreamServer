# MISSIONS.md — Dream Server Operations

*Light Heart Labs · Updated 2026-03-07*

---

## The Mission

**Build an ocean of confirmed, working extensions and keep them working forever.**

Dream Server's core stack is done. The product now lives or dies on how many tools a user can enable with one command. Every extension you add and maintain makes the platform more valuable. Every broken or missing extension is a reason for someone to go back to doing it manually.

You have seven workstreams. **Extensions (building and maintaining) is the primary job.** The other workstreams exist to support it. When choosing what to work on, default to extensions unless a real user is blocked on something else.

---

## What Dream Server Is Now

A working local AI stack: LLM inference (llama.cpp), chat UI (Open WebUI), image generation (ComfyUI), voice (Whisper + Kokoro), agents (OpenClaw), workflows (n8n), RAG (Qdrant), search (SearXNG + Perplexica), privacy tools, and monitoring — packaged into a single installer across NVIDIA, AMD, and Apple Silicon. Runs on everything from a 16GB Mac Mini to a multi-GPU server.

---

## Source of Truth

**All code work happens in the public repo:**
```
https://github.com/Light-Heart-Labs/DreamServer
```

Clone it. Branch from it. PR into it. That's where the code lives.

**This dev repo is for operations and coordination only** — MISSIONS.md, status tracking, and notes. Do not put code, configs, compose files, Dockerfiles, or scripts in this repo. If it runs, it belongs in DreamServer.

---

## Workstream 1: Extensions Library

**Goal:** Every major open-source AI project is one command away — `dream extensions enable <name>`.

### Extension Structure

```
extensions/services/<name>/
  manifest.yaml      # dream.services.v1 schema
  compose.yaml       # Docker Compose service definition
  config/            # Default config files (if needed)
  Dockerfile         # Only if no suitable upstream image exists
```

### Requirements

- `manifest.yaml` must include: `id`, `name`, `container_name`, `port`, `external_port_default`, `health` endpoint, `gpu_backends`, `depends_on`, `category`, and feature definitions with VRAM requirements.
- `compose.yaml`: pin image tags (no `:latest`), use `dream-network`, persist data under `./data/<name>/`, include healthcheck, set `security_opt: no-new-privileges:true`, run as non-root, wire to Dream Server's LLM endpoint via `${LLM_API_URL}`.
- Zero-touch configs. `dream extensions enable <name>` must work with no user editing.

### Patterns to Follow (Copy These Exactly)

Study these two reference extensions before building anything:
- **`extensions/services/open-webui/`** — full-featured extension with LLM integration, GPU backends, feature definitions, and VRAM requirements.
- **`extensions/services/searxng/`** — simpler service with config directory and no GPU requirement.

Specific patterns to match:

| Pattern | What to Copy | Don't Do |
|---------|-------------|----------|
| **Manifest schema** | `schema_version: dream.services.v1` — use exactly this | Don't invent your own schema fields |
| **Port allocation** | Pick an unused port, set both `port` and `external_port_default` | Don't reuse ports from existing services |
| **Health endpoint** | Set `health: /` or `health: /api/health` — whatever the upstream app exposes | Don't set a health path that doesn't exist |
| **GPU backends** | List only backends you've tested: `[nvidia]`, `[amd, nvidia]`, `[amd, nvidia, apple]` | Don't list `apple` if the image is x86-only |
| **Network** | `networks: [dream-network]` using the external network | Don't create service-specific networks |
| **Data volumes** | `./data/<name>/:/app/data` (match upstream's data path) | Don't use named volumes — use bind mounts under `./data/` |
| **Environment** | Wire LLM via `LLM_API_URL: ${LLM_API_URL}` | Don't hardcode `http://llama-server:8080` |
| **Container name** | Set `container_name: <name>` matching the manifest `id` | Don't leave container name auto-generated |
| **Depends on** | List services this requires (e.g., `depends_on: [llama-server]`) | Don't list optional dependencies as required |
| **Category** | Use existing categories: `optional`, `core`, etc. | Don't create new categories without approval |

### Definition of Done (Every Extension Must Pass ALL of These)

An extension is not done until every box is checked:

1. **Starts clean.** `docker compose up <name>` runs with no errors, no warnings that indicate misconfiguration.
2. **Healthcheck passes.** The service becomes healthy within its declared start period. If it takes longer than 120 seconds, investigate — users will think it's broken.
3. **LLM integration works** (if applicable). Send a real request through the service to Dream Server's LLM endpoint. Get a real response back. Don't just check that the port is open — verify the actual workflow end-to-end.
4. **Zero-touch config.** `dream extensions enable <name>` works with no user editing. No manual `.env` entries, no "edit this config file first" steps. If the extension needs environment variables, they must have working defaults or be auto-generated at enable time.
5. **Enable AND disable cleanly.** `dream extensions disable <name>` removes the service without breaking other services or leaving orphaned volumes/networks.
6. **Dashboard integration.** The service appears correctly in the Dream Server dashboard with accurate status, correct port, and working links.
7. **Tested on all declared GPU backends.** If `manifest.yaml` says `gpu_backends: [nvidia, amd]`, it must be tested on both. Don't declare support you haven't verified.
8. **Graceful degradation.** If the extension requires a GPU and there isn't one, it should either: (a) run in CPU mode with a clear performance warning, or (b) refuse to enable with a clear error message. No silent crashes.
9. **No floating tags.** Every image, git clone, and pip package is pinned to a specific version.
10. **Data persists.** User data survives `docker compose down && docker compose up`. Volumes are correctly mapped to `./data/<name>/`.

### How to Test an Extension (Step-by-Step)

Follow this exact sequence every time you build or update an extension. Don't skip steps.

```
1. CLEAN STATE
   - Remove any previous containers, volumes, and configs for this extension
   - Start from a fresh Dream Server install state

2. ENABLE
   - Run: dream extensions enable <name>
   - Verify: no errors, no prompts for manual config

3. START
   - Run: docker compose up <name>
   - Watch logs for errors, warnings, deprecation notices
   - Time how long it takes to become healthy

4. HEALTH
   - Verify container shows "healthy" in docker ps
   - Hit the health endpoint directly: curl http://localhost:<port><health_path>
   - If it takes > 120 seconds, investigate and optimize

5. FUNCTION
   - Open the service in a browser (if it has a UI)
   - Perform the core action: send a prompt, generate an image, run a query — whatever the tool does
   - If it connects to the LLM, verify a real response comes back (not just a connection)

6. INTEGRATION
   - Test with dependent services (e.g., if it uses SearXNG, verify search results flow through)
   - Test any n8n workflow templates associated with this extension

7. PERSISTENCE
   - docker compose down
   - docker compose up
   - Verify user data (conversations, generated files, settings) survived the restart

8. DISABLE
   - Run: dream extensions disable <name>
   - Verify: service stops, other services unaffected, no orphaned resources
   - Re-enable and verify it comes back clean

9. GPU VARIANTS (if applicable)
   - Repeat steps 2-8 on each declared GPU backend
   - Test CPU-only fallback behavior
```

### Extension Catalog

Build in this order. Each is independent — work in parallel.

**Wave 1 — High Demand**

| # | Extension | What It Is | Upstream Image |
|---|-----------|-----------|----------------|
| 1 | Ollama | Alternative LLM backend | `ollama/ollama` |
| 2 | SillyTavern | Character/roleplay chat UI | `ghcr.io/sillytavern/sillytavern` |
| 3 | Dify | AI workflow builder | `langgenius/dify-*` |
| 4 | Fooocus | Simple image generation UI | `ghcr.io/lllyasviel/fooocus` |
| 5 | ChromaDB | Lightweight vector database | `chromadb/chroma` |
| 6 | Piper TTS | Fast text-to-speech | `rhasspy/wyoming-piper` |
| 7 | Aider | AI coding assistant (terminal) | Build from pip |
| 8 | RVC | Voice cloning | Community image |
| 9 | Jupyter | Notebook environment | `jupyter/scipy-notebook` |
| 10 | Immich | AI photo management | `ghcr.io/immich-app/immich-server` |

**Wave 2 — Ecosystem Growth**

| # | Extension | What It Is |
|---|-----------|-----------|
| 11 | LibreChat | Alternative chat UI |
| 12 | AnythingLLM | RAG-focused chat |
| 13 | Flowise | Visual LLM workflow builder |
| 14 | Langflow | LangChain visual builder |
| 15 | Open Interpreter | Natural language computer control |
| 16 | InvokeAI | Advanced image generation |
| 17 | Forge/A1111 | Stable Diffusion ecosystem |
| 18 | AudioCraft | Music generation |
| 19 | Weaviate | Enterprise vector DB |
| 20 | Paperless-ngx | AI document management |

**Wave 3 — Full Catalog**

| # | Extension | What It Is |
|---|-----------|-----------|
| 21 | Jan | Desktop LLM client |
| 22 | GPT4All | Offline chat |
| 23 | Text Generation WebUI | Oobabooga |
| 24 | Milvus | Scalable vector DB |
| 25 | Label Studio | Data annotation |
| 26 | Frigate | AI security cameras |
| 27 | Bark | Expressive TTS |
| 28 | XTTS/Coqui | Multilingual TTS |
| 29 | CrewAI | Multi-agent framework |
| 30 | Continue.dev | IDE AI assistant |

**Wave 4+ — Ongoing Discovery**

When Waves 1-3 are done, actively scan for new projects to add:
- Browse GitHub trending for AI/ML repositories
- Check r/LocalLLaMA, r/selfhosted, r/StableDiffusion for tools people are asking about
- Monitor Hugging Face Spaces for popular apps that could run locally
- Watch for new releases from projects already in the catalog (new tools from the same teams)
- Check Product Hunt AI category for emerging open-source tools
- Search Docker Hub and GHCR for AI-related images with high pull counts
- Read "awesome-selfhosted" and "awesome-llm" lists for projects not yet in the catalog

**How to Evaluate a Candidate Extension**

Not every project belongs in Dream Server. Before building, check:

| Criteria | Yes = Add It | No = Skip It |
|----------|-------------|-------------|
| **Has a Docker image or Dockerfile?** | Ready to containerize | Would need heavy custom packaging — skip unless high demand |
| **Actively maintained?** (commits in last 3 months) | Sustainable | Risk of abandonment — skip unless it's the only option in its category |
| **Has 500+ GitHub stars?** | Proven demand | Niche — only add if users specifically request it |
| **Runs locally without cloud dependencies?** | Fits Dream Server's mission | Cloud-only tool — skip |
| **Adds a capability Dream Server doesn't have?** | Fills a gap | Redundant with existing extension — skip unless it's clearly better |
| **Can connect to Dream Server's LLM endpoint?** | Integrates with the stack | Standalone tool — lower priority but still valid if useful |
| **Works on consumer hardware (8-16GB VRAM)?** | Accessible to target users | Requires enterprise GPUs — skip |

When in doubt, add it. A big catalog with some niche tools is better than a small catalog missing something a user needs.

**There is no end to this workstream.** New OSS AI projects ship every week. The catalog should always be growing.

---

## Workstream 2: Community Issues & Bug Fixes

**Goal:** Every GitHub issue gets a response, a diagnosis, or a fix.

### Process

1. Check the [Dream Server GitHub issues](https://github.com/Light-Heart-Labs/DreamServer/issues) regularly.
2. For each new issue:
   - Reproduce it if possible.
   - Diagnose the root cause.
   - If it's a quick fix (< 1 hour), fix it and submit a PR.
   - If it's complex, comment with your diagnosis and tag Michael.
   - If it's a user config problem, respond with clear instructions.
3. For feature requests:
   - If it's an extension request, add it to the catalog and build it.
   - If it's a core architecture change, tag Michael for decision.
4. Keep response time under 24 hours. A user who files an issue and hears nothing will leave.

### What You Can Fix Without Approval

- Bug fixes that don't change architecture or public APIs
- Documentation corrections
- Config defaults that are clearly wrong
- Missing healthchecks or broken health endpoints
- Typos, broken links, formatting issues

### What Needs Michael's Approval

- Changes to core services (llama-server, open-webui, dashboard)
- New dependencies or major version bumps
- Security-related changes
- Anything that changes the install flow
- Architectural decisions

---

## Workstream 3: Installer & Distribution Testing

**Goal:** The install works perfectly on every target platform.

### Ongoing Test Matrix

Run full install-to-first-chat tests on every release and PR that touches the installer:

**Linux (coordinate with Bilal for coverage)**
- Ubuntu 24.04 / 22.04
- Fedora 40 / 41
- Debian 12
- Arch Linux

**Windows**
- Windows 11 (NVIDIA)
- Windows 11 (AMD)
- Windows 11 (CPU-only)

**macOS**
- Apple Silicon (16GB minimum)
- Apple Silicon (32GB+)

### What to Test

1. Fresh install from zero — does the script complete without errors?
2. All services come up healthy within expected timeframes.
3. First chat works — user can send a message and get a response.
4. Model download/bootstrap works correctly.
5. Dashboard shows accurate service status.
6. Extensions can be enabled and disabled cleanly.
7. Update from previous version preserves data.

### What to File

For each failure, file a GitHub issue with:
- Exact OS version and hardware specs
- Full install log (sanitize secrets)
- Screenshot of the failure state
- Steps to reproduce

---

## Workstream 4: Hardening & Quality

**Goal:** Make the existing stack more robust, secure, and polished.

### Security Fixes (Do These First)

- [ ] Generate SearXNG secret key at install time instead of using the hardcoded one in the repo
- [ ] Tighten OpenClaw auth defaults — `dangerouslyDisableDeviceAuth` should not be `true` by default
- [ ] Remove API key embedding from token-spy HTML dashboard — use session-based auth instead
- [ ] Pin all container images to specific versions — replace `:latest` tags on SearXNG, OpenClaw, Whisper (speaches), Perplexica
- [ ] Pin ComfyUI git clone to a specific commit/tag in the Dockerfile
- [ ] Remove `seccomp:unconfined` and `SYS_PTRACE` from ComfyUI AMD compose unless strictly required

### Ongoing Quality Work

- Add rate limiting to API endpoints (dashboard-api, privacy-shield, token-spy)
- Fix the agent monitor `KeyError` — `get_agent_metrics_html()` references `metrics["tokens"]` which doesn't exist in `get_full_agent_metrics()`
- Add Python lock files (`pip-compile`) for reproducible builds
- Replace deprecated `@app.on_event("startup")` with lifespan context manager in FastAPI services
- Split token-spy's monolithic `main.py` — extract the embedded HTML dashboard into template files
- Add structured (JSON) logging format option for all Python services
- Test and fix mobile responsiveness on the dashboard

---

## Workstream 5: Pre-Built Workflow Templates

**Goal:** Every extension that supports workflows ships with ready-to-use templates so users see value immediately.

### What This Means

n8n is already in the stack. Every extension that can be automated should have at least one n8n workflow template that shows it working with Dream Server's LLM and other services.

### Examples

- **Whisper + LLM + TTS:** Voice-in → transcribe → LLM response → speak back. End-to-end voice assistant workflow.
- **SearXNG + LLM:** User question → web search → LLM summarizes results. Research assistant.
- **ComfyUI + LLM:** User describes an image in chat → LLM generates a ComfyUI prompt → image is generated and returned.
- **Qdrant + Embeddings + LLM:** Drop a PDF → auto-chunk → embed → store. Then ask questions against it. Full RAG pipeline.
- **Immich + LLM:** New photo uploaded → auto-tag with LLM vision → searchable by description.
- **n8n + Email + LLM:** Incoming email → LLM summarizes → sends digest.
- **Paperless-ngx + LLM:** New document scanned → OCR → LLM extracts metadata → auto-categorized.

### Process

1. Build the workflow in n8n on a running Dream Server instance.
2. Export as JSON.
3. Place in `extensions/workflows/<name>/` with a README describing what it does and which extensions it requires.
4. Test that importing the workflow on a fresh instance works with zero config.

**Every extension you build in Workstream 1 should get at least one workflow here.** This is what turns "I installed a tool" into "I have a working AI pipeline."

---

## Workstream 6: Content & Community Growth

**Goal:** Make Dream Server visible to the people who need it.

### What Agents Can Build

- **Tutorial scripts:** Step-by-step guides for common use cases. "How to set up a local RAG pipeline with Dream Server." "How to run voice chat with Whisper + Kokoro." Written as markdown, publishable to docs or blog.
- **Comparison pages:** "Dream Server vs. running Ollama + Open WebUI + ComfyUI manually." "Dream Server vs. paying for ChatGPT + Midjourney." Factual, not salesy.
- **Extension showcase pages:** For each extension in the catalog, write a short page: what it does, why someone would want it, screenshot of it running in Dream Server.
- **Community responses:** Draft responses to Reddit posts, HN comments, GitHub discussions where people are asking about local AI stacks. Michael reviews and posts.
- **FAQ expansion:** Every GitHub issue that reveals a common user confusion should become a FAQ entry.
- **Changelog drafts:** When new extensions or features ship, draft a changelog entry for the website/GitHub releases.

### What Agents Should NOT Do

- Don't post directly to social media or forums. Draft for Michael to review and post.
- Don't write marketing fluff. Be factual and technical. The audience is tinkerers, not executives.
- Don't create video content (agents can't). Write scripts that Michael or contributors can record.

---

## Workstream 7: Upstream Monitoring, Updates & Regression Testing

**Goal:** Keep every extension current, tested, and working as upstream projects evolve.

### Why This Is Critical

Every extension depends on an upstream open-source project. Those projects release new versions, change APIs, deprecate features, and break things. A user who enables an extension and gets a crash because the upstream image changed is a user who leaves. This workstream prevents that.

### The Update Cycle

For every extension in the catalog, repeat this cycle continuously:

**1. Detect**
- Check the upstream project's GitHub releases, Docker Hub tags, or GHCR tags for new stable versions.
- Read the release notes and changelog. Flag breaking changes, new dependencies, deprecated features, and new capabilities.

**2. Bump**
- Update the pinned image tag in `compose.yaml`.
- Update any config files that reference version-specific settings, paths, or APIs.
- Update the `manifest.yaml` if ports, health endpoints, or GPU requirements changed.

**3. Test (Full Regression)**
- Pull the new image.
- `docker compose up <name>` — does it start clean?
- Healthcheck passes?
- Service responds on its expected port?
- Integration with Dream Server's LLM endpoint still works? (Send a real request, check the response.)
- Integration with dependent extensions still works? (e.g., Perplexica → SearXNG, RAG workflow → Qdrant + embeddings)
- Existing user data (volumes from previous version) survives the upgrade without corruption or migration errors?
- Any associated n8n workflow templates still function with the updated service?

**4. Fix**
- If anything breaks, fix the config, Dockerfile, manifest, or workflow template to accommodate the new version.
- If the break is fundamental (upstream completely changed their API), document the migration path.

**5. Ship**
- Commit the version bump with a clear message: `bump <name> from v1.2.3 to v1.3.0`
- Update the changelog.
- If the update added significant new capabilities, create a new workflow template (feeds Workstream 5) and update the extension showcase (feeds Workstream 6).

### Monitoring Schedule

| Tier | Extensions | Scan Frequency |
|------|-----------|----------------|
| **Wave 1** (high demand) | Ollama, SillyTavern, Dify, Fooocus, ChromaDB, Piper, Aider, RVC, Jupyter, Immich | Weekly |
| **Wave 2** (ecosystem) | LibreChat, AnythingLLM, Flowise, Langflow, Open Interpreter, InvokeAI, Forge, AudioCraft, Weaviate, Paperless-ngx | Biweekly |
| **Wave 3+** (catalog) | Everything else | Monthly |
| **Core stack** | llama.cpp, Open WebUI, ComfyUI, Whisper, Kokoro, n8n, Qdrant, SearXNG, Perplexica, LiteLLM, OpenClaw | Weekly |

### Dependency Chain Map

When updating one extension, always test its dependents:

- **LLM endpoint changes** → test ALL extensions that call the LLM (most of them)
- **SearXNG update** → test Perplexica, any search-based workflows
- **Qdrant update** → test embeddings integration, RAG workflows
- **Embeddings update** → test Qdrant ingestion, RAG workflows
- **n8n update** → test ALL workflow templates

### What to Watch For

- **Image tag disappears.** Upstream deletes old tags. If our pinned tag gets pulled, builds break silently. Always verify the pinned tag still exists.
- **Base image changes.** Upstream switches from Ubuntu to Alpine, from Python 3.11 to 3.12, from amd64-only to multi-arch. Config paths and available packages may change.
- **Default port changes.** Upstream moves from port 8080 to 3000. Manifest and compose need to match.
- **Auth added.** Upstream adds authentication that wasn't there before. Configs need default credentials or a way to disable for local use.
- **Project archived/abandoned.** If no commits in 6+ months, flag it and research replacement options.
- **Project forked/renamed.** Community forks happen. Track which fork is now the active one.

**This is the largest ongoing workstream.** At 50+ extensions with weekly/biweekly scans, full regression testing, and dependency chain validation, this alone keeps an agent team busy indefinitely. Every extension you build in Workstream 1 adds to the maintenance load here.

---

## Priority Order

**The default activity is building and maintaining extensions.** That's the job. The other items below interrupt it when they come up, then you go back to extensions.

When choosing what to work on:

1. **GitHub issues from real users** — drop everything and respond. A user waiting on a response is the only thing more urgent than building extensions. But most issues will BE about extensions (broken, missing, requested), so this feeds right back into the main work.
2. **Upstream updates breaking existing extensions** — a broken extension in the catalog is worse than a missing one. Fix regressions immediately.
3. **Building new extensions (current wave)** — this is the primary job. Grow the catalog.
4. **Maintaining existing extensions** — run the update cycle (Workstream 7). Keep everything current and tested.
5. **Workflow templates** for completed extensions — ship a workflow with every extension. This is what turns "installed a tool" into "running an AI pipeline."
6. **Security fixes** from the hardening list — these block public credibility.
7. **Installer testing** — coordinate with Bilal's schedule so you're not duplicating work.
8. **Content & community drafts** — fill time between the above.
9. **Quality/hardening items** — always available as background work.

**If you're not sure what to do, build an extension.** If all extensions are built, update and test existing ones. If everything is current, find new projects to add to the catalog. The catalog never stops growing.

---

## Rules (All Workstreams)

1. **Pin versions.** Images, git clones, pip packages. No floating tags.
2. **Don't modify core without approval.** Extensions, bug fixes, and hardening — yes. Architecture changes — ask Michael.
3. **Copy existing patterns.** The codebase has established conventions. Match them.
4. **No stubs.** Don't commit anything you haven't tested running.
5. **One logical change per commit.** Clean, reviewable, revertable.
6. **Test as a stranger.** After building anything, test it as if you've never seen Dream Server before.
7. **File what you find.** If you discover a bug while working on something else, file a GitHub issue immediately. Don't let it slip.
8. **Unblock before you build.** If another agent or team member is stuck on something you could help with, do that first.

---

## Team & Ownership

| Person | Owns |
|--------|------|
| **Michael** | Core architecture, installer, landing page, business decisions |
| **Youness** | Multi-GPU detection, hardware orchestration, driver pinning, edge devices |
| **Bilal** | QA testing across Linux distros, Windows, macOS — hardware compatibility matrix |
| **Agent Team** | Extensions library, GitHub issues, installer testing, hardening |

If something falls in another team member's area, handle what you can and loop them in. Don't wait for permission to fix things.

---

## How to Find More Work

If all current tasks are done:

1. **Scan GitHub issues** — there are always new ones.
2. **Search for new OSS AI projects** — the catalog should never stop growing.
3. **Run a full install test** — there are always bugs you haven't found.
4. **Audit existing extensions** — upstream images get updated, configs drift, new features appear. Keep them current.
5. **Check the hardening list** — there's always more to secure and polish.
6. **Read community forums** (Reddit, Discord, HN) — what are people complaining about with local AI? Can Dream Server solve it?

**There is always work. If you think you're done, you're not looking hard enough.**
