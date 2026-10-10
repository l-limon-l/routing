#!/usr/bin/env python3
"""Собирает aws/ip.json из официального списка адресов Amazon.

Amazon публикует свои диапазоны в ip-ranges.json и часто их меняет, поэтому
список тянется на каждой сборке. Берутся EC2 (на нём стоят игровые серверы,
в том числе GameLift) и Global Accelerator, через который игры подключают
игроков. Весь сервис AMAZON не берётся: в него входят S3 и CloudFront, то есть
заметная часть обычных сайтов.
"""

import ipaddress
import json
import pathlib
import urllib.request

UPSTREAM = "https://ip-ranges.amazonaws.com/ip-ranges.json"
SERVICES = {"EC2", "GLOBALACCELERATOR"}
ROOT = pathlib.Path(__file__).resolve().parent.parent

with urllib.request.urlopen(UPSTREAM, timeout=60) as resp:
    data = json.load(resp)

v4 = [ipaddress.ip_network(p["ip_prefix"]) for p in data.get("prefixes", [])
      if p.get("service") in SERVICES]
v6 = [ipaddress.ip_network(p["ipv6_prefix"]) for p in data.get("ipv6_prefixes", [])
      if p.get("service") in SERVICES]
if len(v4) < 500:
    raise SystemExit(f"апстрим вернул слишком мало адресов ({len(v4)}) — сборка остановлена")

cidrs = [str(n) for n in ipaddress.collapse_addresses(v4)] + \
        [str(n) for n in ipaddress.collapse_addresses(v6)]

out = ROOT / "aws" / "ip.json"
out.write_text(json.dumps({"version": 1, "rules": [{"ip_cidr": cidrs}]},
                          indent=2) + "\n", "utf-8")
print(f"aws: {len(cidrs)} подсетей (IPv4 {len(v4)}, IPv6 {len(v6)} до слияния)")
