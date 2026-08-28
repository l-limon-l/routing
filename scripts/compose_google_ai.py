#!/usr/bin/env python3
"""Собирает google_ai/domain.json из списка itdoginfo и наших дополнений.

Апстрим ведут за нас, поэтому копировать его в репозиторий разово смысла нет:
скопированное устареет. Список тянется на каждой сборке, к нему добавляется
google_ai/extra.lst, и результат компилируется в google_ai.srs. Обновления
itdoginfo продолжают приезжать сами, а наши правки живут отдельным файлом и
видны в истории.
"""

import json
import pathlib
import urllib.request

UPSTREAM = ("https://raw.githubusercontent.com/itdoginfo/allow-domains"
            "/main/Services/google_ai.lst")
ROOT = pathlib.Path(__file__).resolve().parent.parent


def domains(text):
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            yield line


with urllib.request.urlopen(UPSTREAM, timeout=60) as resp:
    upstream = list(domains(resp.read().decode("utf-8")))

extra = list(domains((ROOT / "google_ai" / "extra.lst").read_text("utf-8")))

merged = sorted(set(upstream) | set(extra))
if not upstream:
    raise SystemExit("апстрим вернул пустой список — сборка остановлена")

out = ROOT / "google_ai" / "domain.json"
out.write_text(json.dumps({"version": 1, "rules": [{"domain_suffix": merged}]},
                          ensure_ascii=False, indent=2) + "\n", "utf-8")

new = sorted(set(extra) - set(upstream))
print(f"итого {len(merged)}: {len(upstream)} от itdoginfo, наших сверх того {len(new)}")
for d in new:
    print(f"  + {d}")
