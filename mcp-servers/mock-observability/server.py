#!/usr/bin/env python3
"""
Read-only mock observability MCP for demo installs.
Replace .mcp.json with your org's OpenSearch/Grafana servers for production use.
Requires: pip install mcp
"""
from __future__ import annotations

import json

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    import sys

    print(
        "mock-observability: install the MCP SDK — pip install mcp",
        file=sys.stderr,
    )
    raise

mcp = FastMCP(
    "mock-observability",
    instructions="Demo read-only log and metrics tools. Responses are canned for workshops.",
)


@mcp.tool()
def search_logs(
    cluster: str,
    query: str = "*",
    severity: str = "ERROR",
    time_range: str = "30m",
    limit: int = 20,
    hours: int | None = None,
) -> str:
    """Search cluster logs (read-only). Demo returns grouped signatures.

    Use time_range (e.g. \"30m\", \"2h\"). Passing hours= is a legacy footgun and
    returns unknown_args_warning instead of silently defaulting.
    """
    unknown_args_warning = None
    if hours is not None:
        unknown_args_warning = (
            'Ignored parameters: hours. Use time_range="30m" (or "2h") instead; '
            "do not assume a silent default lookback."
        )

    payload = {
        "cluster": cluster,
        "effective_lookback": time_range,
        "query": query,
        "severity_filter": severity,
        "mode": "mock",
        "unknown_args_warning": unknown_args_warning,
        "groups": [
            {
                "signature": "ConnectionTimeoutException: upstream db-primary:5432",
                "count": 47,
                "sample_message": f"[{cluster}] pool exhausted waiting for connection",
                "last_seen": "2m ago",
            },
            {
                "signature": "HTTP 503 /api/v1/orders — circuit open",
                "count": 12,
                "sample_message": f"[{cluster}] resilience4j circuit breaker OPEN",
                "last_seen": "5m ago",
            },
        ],
        "truncated": False,
        "returned": 2,
    }
    return json.dumps(payload, indent=2)


@mcp.tool()
def cluster_overview(cluster: str, namespace: str | None = None) -> str:
    """One-shot cluster health: nodes, pod phases, restarts, CPU/memory highlights."""
    ns = namespace or cluster
    payload = {
        "cluster": cluster,
        "namespace_scoped": ns,
        "mode": "mock",
        "nodes": {"ready": 8, "total": 8},
        "pod_phases": {
            "Running": 142,
            "Pending": 3,
            "CrashLoopBackOff": 1,
        },
        "namespace_pod_phases": {
            ns: {"Running": 24, "Pending": 3, "CrashLoopBackOff": 1},
        },
        "top_restart_pods": [
            {"pod": f"{cluster}-api-7d4f9b-kl2m9", "restarts": 14, "namespace": ns},
        ],
        "cluster_cpu_avg_percent": 71.2,
        "managed_postgres": [
            {
                "host": "db-primary",
                "azure_cpu_percent": 88.4,
                "note": "Demo metric name mirrors azure_metrics_flex_server_cpu_percent_percent",
            }
        ],
        "notes": [
            "Pending pods often correlate with node pressure—check events next.",
            "managed_postgres.azure_cpu_percent: on Azure, host CPU may live under a non-obvious metric name—verify in Prometheus before concluding 'no signal'.",
            "Swap mock-observability for real Grafana/Prometheus MCP in .mcp.json for production.",
        ],
    }
    return json.dumps(payload, indent=2)


if __name__ == "__main__":
    mcp.run()
