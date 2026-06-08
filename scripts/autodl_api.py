#!/usr/bin/env python3
"""Small CLI for AutoDL developer APIs.

Reads token from AUTODL_TOKEN or AUTODL_API_TOKEN by default.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


HOST = "https://api.autodl.com"
TOKEN_ENV_NAMES = ("AUTODL_TOKEN", "AUTODL_API_TOKEN")


def get_token(args: argparse.Namespace) -> str:
    if args.token:
        return args.token
    for name in TOKEN_ENV_NAMES:
        value = os.environ.get(name)
        if value:
            return value
    raise SystemExit("Missing token. Set AUTODL_TOKEN or AUTODL_API_TOKEN.")


def call_api(method: str, path: str, token: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Authorization": token}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        HOST + path,
        data=data,
        method=method,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {raw}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Request failed: {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Non-JSON response: {raw}") from exc


def call_get_query(path: str, token: str, params: dict) -> dict:
    query = urllib.parse.urlencode(params)
    return call_api("GET", f"{path}?{query}", token)


def print_json(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True))


def require_success(response: dict) -> None:
    if response.get("code") != "Success":
        print_json(response)
        raise SystemExit(1)


def command_balance(args: argparse.Namespace) -> None:
    token = get_token(args)
    response = call_api("POST", "/api/v1/dev/wallet/balance", token)
    require_success(response)
    data = response.get("data") or {}
    summary = {
        "assets_yuan": (data.get("assets") or 0) / 1000,
        "accumulate_yuan": (data.get("accumulate") or 0) / 1000,
        "voucher_balance_yuan": (data.get("voucher_balance") or 0) / 1000,
        "raw": data,
    }
    print_json(summary if args.summary else response)


def command_instances(args: argparse.Namespace) -> None:
    token = get_token(args)
    body = {"page_index": args.page_index, "page_size": args.page_size}
    response = call_api("POST", "/api/v1/dev/instance/pro/list", token, body)
    require_success(response)
    print_json(response)


def command_status(args: argparse.Namespace) -> None:
    token = get_token(args)
    response = call_get_query(
        "/api/v1/dev/instance/pro/status",
        token,
        {"instance_uuid": args.instance_uuid},
    )
    require_success(response)
    print_json(response)


def command_snapshot(args: argparse.Namespace) -> None:
    token = get_token(args)
    response = call_get_query(
        "/api/v1/dev/instance/pro/snapshot",
        token,
        {"instance_uuid": args.instance_uuid},
    )
    require_success(response)
    if args.redact:
        data = response.get("data") or {}
        for key in (
            "root_password",
            "jupyter_token",
            "jupyter_domain",
            "service_6006_domain",
            "service_6008_domain",
        ):
            if key in data and data[key]:
                data[key] = "<redacted>"
    print_json(response)


def command_create(args: argparse.Namespace) -> None:
    token = get_token(args)
    body = {
        "req_gpu_amount": args.gpu_count,
        "expand_system_disk_by_gb": args.disk_gb,
        "gpu_spec_uuid": args.gpu_spec,
        "image_uuid": args.image,
        "cuda_v_from": args.cuda_from,
    }
    if args.data_center:
        body["data_center_list"] = args.data_center
    if args.name:
        body["instance_name"] = args.name
    if args.start_command:
        body["start_command"] = args.start_command
    response = call_api("POST", "/api/v1/dev/instance/pro/create", token, body)
    require_success(response)
    print_json(response)


def command_power_on(args: argparse.Namespace) -> None:
    token = get_token(args)
    body = {"instance_uuid": args.instance_uuid, "payload": "gpu"}
    if args.start_command:
        body["start_command"] = args.start_command
    response = call_api("POST", "/api/v1/dev/instance/pro/power_on", token, body)
    require_success(response)
    print_json(response)


def command_simple_instance_post(args: argparse.Namespace, path: str) -> None:
    token = get_token(args)
    response = call_api("POST", path, token, {"instance_uuid": args.instance_uuid})
    require_success(response)
    print_json(response)


def command_images(args: argparse.Namespace) -> None:
    token = get_token(args)
    body = {"page_index": args.page_index, "page_size": args.page_size}
    response = call_api("POST", "/api/v1/dev/instance/pro/image/private/list", token, body)
    require_success(response)
    print_json(response)


def command_save_image(args: argparse.Namespace) -> None:
    token = get_token(args)
    body = {"instance_uuid": args.instance_uuid, "image_name": args.image_name}
    response = call_api("POST", "/api/v1/dev/instance/pro/image/save", token, body)
    require_success(response)
    print_json(response)


def add_token_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--token", help="AutoDL developer token. Prefer env vars.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call AutoDL developer APIs.")
    add_token_arg(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    balance = subparsers.add_parser("balance", help="Get account balance.")
    balance.add_argument("--summary", action="store_true", default=True)
    balance.set_defaults(func=command_balance)

    instances = subparsers.add_parser("instances", help="List Pro instances.")
    instances.add_argument("--page-index", type=int, default=1)
    instances.add_argument("--page-size", type=int, default=20)
    instances.set_defaults(func=command_instances)

    status = subparsers.add_parser("status", help="Get instance status.")
    status.add_argument("instance_uuid")
    status.set_defaults(func=command_status)

    snapshot = subparsers.add_parser("snapshot", help="Get instance snapshot.")
    snapshot.add_argument("instance_uuid")
    snapshot.add_argument("--redact", action=argparse.BooleanOptionalAction, default=True)
    snapshot.set_defaults(func=command_snapshot)

    create = subparsers.add_parser("create", help="Create a paid Pro instance.")
    create.add_argument("--gpu-spec", required=True)
    create.add_argument("--gpu-count", type=int, required=True)
    create.add_argument("--image", required=True)
    create.add_argument("--cuda-from", type=int, required=True)
    create.add_argument("--disk-gb", type=int, default=0)
    create.add_argument("--data-center", action="append")
    create.add_argument("--name")
    create.add_argument("--start-command")
    create.set_defaults(func=command_create)

    power_on = subparsers.add_parser("power-on", help="Power on an instance in GPU mode.")
    power_on.add_argument("instance_uuid")
    power_on.add_argument("--start-command")
    power_on.set_defaults(func=command_power_on)

    power_off = subparsers.add_parser("power-off", help="Power off an instance.")
    power_off.add_argument("instance_uuid")
    power_off.set_defaults(
        func=lambda args: command_simple_instance_post(
            args, "/api/v1/dev/instance/pro/power_off"
        )
    )

    release = subparsers.add_parser("release", help="Release a stopped instance.")
    release.add_argument("instance_uuid")
    release.set_defaults(
        func=lambda args: command_simple_instance_post(
            args, "/api/v1/dev/instance/pro/release"
        )
    )

    images = subparsers.add_parser("images", help="List private images.")
    images.add_argument("--page-index", type=int, default=1)
    images.add_argument("--page-size", type=int, default=20)
    images.set_defaults(func=command_images)

    save_image = subparsers.add_parser("save-image", help="Save an instance as an image.")
    save_image.add_argument("instance_uuid")
    save_image.add_argument("image_name")
    save_image.set_defaults(func=command_save_image)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
