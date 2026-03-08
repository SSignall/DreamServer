# LLM to Image Generation Workflow

Convert text prompts to generated images using LLM prompt enhancement + ComfyUI.

## How It Works

1. User sends a text prompt to the webhook
2. LLM enhances the prompt with artistic details (style, lighting, composition)
3. Enhanced prompt is sent to ComfyUI for image generation
4. Image generation starts and status is returned

## API Endpoint

**POST** `/llm-to-image`

### Headers
- `X-API-Key` — Optional API key if `LLM_TO_IMAGE_API_KEY` is set

### Body
```json
{
  "prompt": "A futuristic city with flying cars",
  "channel": "general"
}
```

### Response
```json
{
  "success": true,
  "prompt_id": "abc123",
  "queue_number": 5,
  "original_prompt": "A futuristic city with flying cars",
  "enhanced_prompt": "A futuristic cyberpunk city at sunset, neon lights, flying cars zooming through the sky, highly detailed, cinematic lighting, 8k resolution",
  "channel": "general"
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_TO_IMAGE_API_KEY` | (unset) | API key for webhook authentication |
| `LLM_HOST` | `localhost` | LLM service host |
| `LLM_PORT` | `8080` | LLM service port |
| `LLM_MODEL` | `default` | LLM model name |
| `COMFYUI_HOST` | `localhost` | ComfyUI service host |
| `COMFYUI_PORT` | `8188` | ComfyUI service port |
| `COMFYUI_MODEL_NAME` | `flux1-dev.safetensors` | ComfyUI model to use |

## Requirements

- LLM service running (Dream Server LLM endpoint)
- ComfyUI service running with FLUX.1 model loaded
- GPU with sufficient VRAM for image generation

## Security

- API key authentication via timing-safe comparison
- Prompt length validation (max 2000 chars)
- Channel validation (alphanumeric, dash, underscore only)
- All inputs sanitized before processing
