from __future__ import annotations

import argparse
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def _fetch_json(url: str, timeout: float) -> dict:
    with urlopen(url, timeout=timeout) as response:  # noqa: S310 - internal test URL
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test the pod cart sim web app.")
    parser.add_argument("--base-url", default="http://pod-cart-sim:5002")
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--poll-interval-seconds", type=float, default=2.0)
    args = parser.parse_args()

    deadline = time.time() + args.timeout_seconds
    health_url = f"{args.base_url.rstrip('/')}/healthz"
    index_url = f"{args.base_url.rstrip('/')}/"

    while time.time() < deadline:
        try:
            payload = _fetch_json(health_url, timeout=5.0)
            if payload.get("ok") is True:
                break
        except (URLError, HTTPError, TimeoutError, json.JSONDecodeError):
            pass
        time.sleep(args.poll_interval_seconds)
    else:
        print(f"Health check timed out: {health_url}")
        return 1

    try:
        with urlopen(index_url, timeout=5.0) as response:  # noqa: S310 - internal test URL
            status = response.status
    except (URLError, HTTPError, TimeoutError) as exc:
        print(f"Index check failed: {exc}")
        return 1

    if status != 200:
        print(f"Index check returned unexpected status: {status}")
        return 1

    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
