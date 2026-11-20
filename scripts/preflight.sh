#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_comments.py
test -s index.html
test -s confirmacao.png
test -s assets/logo-ifmg.png
test -s registro.json
grep -Fq 'Comprovante de Matrícula confirmado!' index.html
grep -Fq 'Buscando a matrícula...' index.html
grep -Fq 'width="323" height="390"' index.html
python3 - <<'CHECK'
import json
from pathlib import Path
record = json.loads(Path("registro.json").read_text(encoding="utf-8"))
assert record["status"] == "confirmado"
assert record["mensagem"] == "Comprovante de Matrícula confirmado!"
CHECK
