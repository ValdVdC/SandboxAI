#!/usr/bin/env python3
"""
SandboxAI CI/CD CLI Client
Trigger tests and poll for Rule Engine evaluation.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

import yaml


def main():
    api_key = os.getenv("SANDBOXAI_API_KEY")
    if not api_key:
        print("ERROR: SANDBOXAI_API_KEY environment variable not set.")
        sys.exit(1)

    config_path = "sandboxai-ci.yml"
    if not os.path.exists(config_path):
        print(f"ERROR: {config_path} not found in current directory.")
        sys.exit(1)

    with open(config_path, "r") as f:
        try:
            config = yaml.safe_load(f)
            if (
                not isinstance(config, dict)
                or "prompts" not in config
                or not isinstance(config["prompts"], list)
            ):
                print(
                    f"ERROR: {config_path} has an invalid structure. Expected a dictionary with a 'prompts' list."
                )
                sys.exit(1)
        except yaml.YAMLError as e:
            print(f"ERROR parsing {config_path}: {e}")
            sys.exit(1)

    prompt_ids = config.get("prompts", [])
    if not prompt_ids:
        print("ERROR: No prompts specified in sandboxai-ci.yml")
        sys.exit(1)

    base_url = os.getenv("SANDBOXAI_API_URL", "http://localhost:8000")
    from urllib.parse import urlparse

    parsed = urlparse(base_url)
    if parsed.scheme not in ["http", "https"] or not parsed.netloc:
        print("ERROR: SANDBOXAI_API_URL inválida. Use uma URL http/https completa.")
        sys.exit(1)

    run_url = f"{base_url}/api/v1/ci/run"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    data = json.dumps({"prompt_ids": prompt_ids}).encode("utf-8")

    print(f"Triggering CI tests for prompts: {prompt_ids}")
    try:
        req = urllib.request.Request(run_url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            resp_body = response.read().decode("utf-8")
            resp_data = json.loads(resp_body)
            job_id = resp_data["job_id"]
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"ERROR triggering tests (HTTP {e.code}): {err_msg}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR triggering tests: {e}")
        sys.exit(1)

    print(f"Tests triggered successfully. Job ID: {job_id}")
    print("Polling for results...")

    status_url = f"{base_url}/api/v1/ci/run/{job_id}"

    timeout_seconds = 600
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout_seconds:
            print("ERROR: Timeout waiting for CI tests to complete.")
            sys.exit(1)
        try:
            req = urllib.request.Request(status_url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as response:
                resp_body = response.read().decode("utf-8")
                data = json.loads(resp_body)

                status = data["status"]
                if status == "RUNNING":
                    time.sleep(5)
                    continue

                final_status = data.get("final_status", "UNKNOWN")
                justification = data.get("justification", "No justification provided.")

                print("\n" + "=" * 50)
                print(f"SandboxAI CI/CD Result: {final_status}")
                print("=" * 50)
                print("Justification:")
                print(justification)
                print("=" * 50 + "\n")

                if final_status == "FAIL":
                    sys.exit(1)
                else:
                    sys.exit(0)

        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            print(f"ERROR polling status (HTTP {e.code}): {err_msg}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR polling status: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
