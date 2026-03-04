"""Agent monitoring endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from agent_monitor import get_full_agent_metrics, cluster_status, throughput
from security import verify_api_key

router = APIRouter(tags=["agents"])


@router.get("/api/agents/metrics")
async def get_agent_metrics(api_key: str = Depends(verify_api_key)):
    """Get comprehensive agent monitoring metrics."""
    return get_full_agent_metrics()


@router.get("/api/agents/metrics.html")
async def get_agent_metrics_html(api_key: str = Depends(verify_api_key)):
    """Get agent metrics as HTML fragment for htmx."""
    metrics = get_full_agent_metrics()
    cluster_class = "status-ok" if metrics["cluster"]["failover_ready"] else "status-warn"
    failover_text = "Ready \u2705" if metrics["cluster"]["failover_ready"] else "Single GPU \u26a0\ufe0f"
    last_update_time = metrics["agent"]["last_update"].split("T")[1][:8]
    tokens_k = metrics["tokens"]["total_tokens_24h"] // 1000
    top_models = metrics["tokens"]["top_models"]
    if top_models:
        rows = "".join(
            "<tr><td>{}</td><td>{}K</td><td>{}</td></tr>".format(
                m["model"], m["tokens"] // 1000, m["requests"]
            )
            for m in top_models
        )
        top_models_html = (
            "<article class='metric-card'><h4>Top Models (24h)</h4>"
            "<table><thead><tr><th>Model</th><th>Tokens</th><th>Requests</th></tr></thead>"
            "<tbody>" + rows + "</tbody></table></article>"
        )
    else:
        top_models_html = ""

    html = f"""
    <div class="grid">
        <article class="metric-card">
            <div class="metric-label">Cluster Status</div>
            <div class="metric-value {cluster_class}">{metrics["cluster"]["active_gpus"]}/{metrics["cluster"]["total_gpus"]} GPUs</div>
            <p style="margin: 0; font-size: 0.875rem;">Failover: {failover_text}</p>
        </article>
        <article class="metric-card">
            <div class="metric-label">Active Sessions</div>
            <div class="metric-value">{metrics["agent"]["session_count"]}</div>
            <p style="margin: 0; font-size: 0.875rem;">Updated: {last_update_time}</p>
        </article>
        <article class="metric-card">
            <div class="metric-label">Token Usage (24h)</div>
            <div class="metric-value">{tokens_k}K</div>
            <p style="margin: 0; font-size: 0.875rem;">${metrics["tokens"]["total_cost_24h"]:.4f} | {metrics["tokens"]["requests_24h"]} reqs</p>
        </article>
        <article class="metric-card">
            <div class="metric-label">Throughput</div>
            <div class="metric-value">{metrics["throughput"]["current"]:.1f}</div>
            <p style="margin: 0; font-size: 0.875rem;">tokens/sec (avg: {metrics["throughput"]["average"]:.1f})</p>
        </article>
    </div>
    {top_models_html}
    """
    return HTMLResponse(content=html)


@router.get("/api/agents/cluster")
async def get_cluster_status(api_key: str = Depends(verify_api_key)):
    """Get cluster health and node status."""
    await cluster_status.refresh()
    return cluster_status.to_dict()


@router.get("/api/agents/throughput")
async def get_throughput(api_key: str = Depends(verify_api_key)):
    """Get throughput metrics (tokens/sec)."""
    return throughput.get_stats()
