# Dify (AI Workflow Builder)

Dify is a visual AI workflow builder that lets you create complex AI applications with drag-and-drop nodes. Connect LLMs, knowledge bases, tools, and decision logic to build custom AI agents, chatbots, and automation pipelines.

## What It Does

- Visual workflow designer with drag-and-drop nodes
- Connect any LLM (including Dream Server's local models)
- Build RAG pipelines with vector database integration
- Create multi-step agent workflows with memory and tools
- Deploy as web apps or APIs

## Integration with Dream Server

Dify connects directly to Dream Server's LLM endpoint at `${LLM_API_URL}` (typically `http://llama-server:8080/v1`). You can use any model hosted in Dream Server without configuring API keys.

## Quick Start

After running `dream extensions enable dify`, access Dify at:

```
http://localhost:8002
```

Default login (auto-generated):
- Email: `admin@dify.ai`
- Password: Check `dream-server/.env` for `DIFY_INIT_PASSWORD`

## Features

| Feature | Status |
|---------|--------|
| Local LLM integration | ✅ Works with Dream Server models |
| Vector database | ✅ Supports Qdrant, ChromaDB |
| Multi-model support | ✅ Switch between any LLM in Dream Server |
| Workflow persistence | ✅ Data stored in `./data/dify/` |
| GPU acceleration | ✅ Uses host GPU for embeddings |
| Mobile responsive | ✅ Works on all screen sizes |

## Architecture

```
User Browser → Dify (:8002) → Dream Server LLM (:8080)
                            ↓
                      Qdrant (:6333) [optional]
```

## Requirements

- **VRAM:** 4GB minimum (for embedding models)
- **RAM:** 8GB+ recommended
- **CPU:** 2+ cores

## Troubleshooting

**Service won't start**
- Check Docker logs: `docker compose logs dify`
- Verify port 8002 is not in use: `lsof -i :8002`
- Ensure `llama-server` is running first

**Can't connect to LLM**
- Verify Dream Server LLM is accessible at `${LLM_API_URL}`
- Check `llama-server` logs for errors
- Ensure `depends_on: [llama-server]` is set in compose.yaml

## Configuration

Edit `dream-server/.env` to customize:

```bash
# Dify configuration
DIFY_PORT=8002
DIFY_INIT_PASSWORD=your-secure-password
SECRET_KEY=your-random-secret-key
```

## Dependencies

- `langgenius/dify` (Docker image)
- `llama-server` (Dream Server LLM endpoint)
- `qdrant` (optional, for vector search)

## Updates

When upstream releases a new version:

1. Update `image: langgenius/dify:<tag>` in `compose.yaml`
2. Pull and restart: `docker compose pull dify && docker compose up -d dify`
3. Verify health: `docker compose ps dify`

## Support

- **Dify Docs:** https://docs.dify.ai
- **GitHub:** https://github.com/langgenius/dify
- **Community:** https://discord.gg/8vQ6GXWZ (Dify Discord)
