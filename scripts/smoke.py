"""模块 10 冒烟验收：按顺序验证核心 HTTP 链路。"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def call(base: str, path: str, method: str = "GET", body: object | None = None, headers: dict[str, str] | None = None) -> object:
    payload = None if body is None else json.dumps(body, ensure_ascii=False).encode()
    request = Request(f"{base.rstrip('/')}{path}", data=payload, method=method, headers={"Content-Type": "application/json", **(headers or {})})
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode())


def main() -> int:
    parser = argparse.ArgumentParser(description="电商 Agent HTTP 冒烟验收")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    try:
        health = call(args.base_url, "/health")
        assert health["status"] == "ok"
        ingestion = call(args.base_url, "/api/v1/knowledge/markdown", "POST", "# 退货制度\n支持七天无理由退货。", {"X-Filename": "smoke.md"})
        assert ingestion["chunk_count"] > 0
        query = call(args.base_url, "/api/v1/chat", "POST", {"message": "退货制度"})
        assert query.get("citations")
        proposal = call(args.base_url, "/api/v1/tools/propose", "POST", {"action": "product.update", "arguments": {"id": 1}})
        approval_id = proposal["approval_id"]
        call(args.base_url, f"/api/v1/approvals/{approval_id}/decision", "POST", {"decision": "rejected", "operator": "smoke"})
        audits = call(args.base_url, "/api/v1/approvals/audit/events")
        assert any(item["event"] == "approval.rejected" for item in audits)
    except (AssertionError, KeyError, HTTPError, URLError, TimeoutError) as exc:
        print(f"冒烟验收失败: {exc}", file=sys.stderr)
        return 1
    print("冒烟验收通过：健康、入库、查询、审批、审计")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
