#!/usr/bin/env python3
"""
Gera o arquivo campaigns.json na raiz do repositório, lendo o campanha.json
de cada pasta de campanha na raiz.

Uma pasta é considerada "campanha" se contiver um arquivo campanha.json
válido. Pastas sem esse arquivo (ex: scripts/, campaign-template/, .github/)
são ignoradas automaticamente.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "campaigns.json"

REQUIRED_FIELDS = ["nome", "periodo", "publico", "categoria", "data_publicacao"]
VALID_CATEGORIAS = {"expansao", "retencao"}


def load_campaign(folder: Path):
    meta_path = folder / "campanha.json"
    if not meta_path.exists():
        return None

    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"AVISO: {meta_path} tem JSON inválido ({e}) — pasta ignorada.", file=sys.stderr)
        return None

    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    if missing:
        print(f"AVISO: {meta_path} está faltando campo(s) {missing} — pasta ignorada.", file=sys.stderr)
        return None

    categoria = str(data["categoria"]).strip().lower()
    if categoria not in VALID_CATEGORIAS:
        print(
            f"AVISO: {meta_path} tem categoria inválida '{data['categoria']}' "
            f"(use 'expansao' ou 'retencao') — pasta ignorada.",
            file=sys.stderr,
        )
        return None

    return {
        "nome": str(data["nome"]).strip(),
        "periodo": str(data["periodo"]).strip(),
        "publico": str(data["publico"]).strip(),
        "categoria": categoria,
        "data_publicacao": str(data["data_publicacao"]).strip(),
        "link": f"{folder.name}/",
    }


def main():
    ignore = {"scripts", "campaign-template", ".github", ".git"}
    campaigns = []

    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in ignore or entry.name.startswith("."):
            continue
        campaign = load_campaign(entry)
        if campaign:
            campaigns.append(campaign)

    # mais recente primeiro
    campaigns.sort(key=lambda c: c["data_publicacao"], reverse=True)

    OUTPUT_FILE.write_text(
        json.dumps(campaigns, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"campaigns.json gerado com {len(campaigns)} campanha(s).")


if __name__ == "__main__":
    main()
