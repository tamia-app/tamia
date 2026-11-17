#!/usr/bin/env python3
"""Check-up of data/destinations.json: structure, consistency of prices, freshness.

Usage: python3 tools/check_destinations.py [--today YYYY-MM-DD]
Prints a report, exits 1 if an error is found or if a destination is due for a price check.
"""
import json, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
STYLES = ("malin", "confort", "plaisir")
SEASONS = ("low", "mid", "high")
INFO = ("currency", "language", "formalities", "plug", "timeDiff", "flightTime", "bestMonths", "tip")

def main():
    today = datetime.date.today()
    if "--today" in sys.argv:
        today = datetime.date.fromisoformat(sys.argv[sys.argv.index("--today") + 1])
    data = json.loads((ROOT / "data" / "destinations.json").read_text(encoding="utf-8"))
    errors, due = [], []
    every = data.get("checkEveryMonths", 6)
    ids = set()

    def err(d, msg): errors.append(f"{d}: {msg}")
    def num(d, label, v, lo, hi):
        if not isinstance(v, (int, float)) or not lo <= v <= hi:
            err(d, f"{label} = {v!r}, attendu un nombre entre {lo} et {hi}")
            return False
        return True
    def rising(d, label, vals):
        if all(isinstance(v, (int, float)) for v in vals) and list(vals) != sorted(vals):
            err(d, f"{label} devrait être croissant : {vals}")

    if data.get("schemaVersion") != 1: errors.append("schemaVersion inconnue")
    if not any(x.get("id") == "PAR" for x in data.get("departures", [])): errors.append("départ PAR manquant")
    for x in data.get("departures", []):
        if not x.get("name") or not isinstance(x.get("factor"), (int, float)) or not 0.5 <= x["factor"] <= 2:
            errors.append(f"départ {x.get('id', '?')} : nom ou coefficient invalide")
    for k, lo, hi in (("margin", 0, 0.5), ("unexpectedRate", 0, 0.5)):
        if not isinstance(data.get(k), (int, float)) or not lo <= data[k] <= hi:
            errors.append(f"{k} doit être un nombre entre {lo} et {hi}")

    for x in data.get("destinations", []):
        d = x.get("id", "?")
        if d in ids: err(d, "identifiant en double")
        ids.add(d)
        for k in ("name", "country", "countryCode", "zone", "color"):
            if not x.get(k): err(d, f"champ {k} manquant")
        months = sorted(int(m) for m in x.get("seasons", {}))
        if months != list(range(1, 13)): err(d, "les 12 mois doivent avoir une saison")
        if any(v not in SEASONS for v in x.get("seasons", {}).values()): err(d, "saison inconnue")
        f = x.get("flights", {})
        for s in SEASONS: num(d, f"vol {s}", f.get(s), 30, 4000)
        rising(d, "vol low/mid/high", [f.get(s) for s in SEASONS])
        lo = x.get("lodging", {})
        for st in STYLES:
            for s in SEASONS: num(d, f"logement {st} {s}", lo.get(st, {}).get(s), 10, 2000)
            rising(d, f"logement {st} low/mid/high", [lo.get(st, {}).get(s) for s in SEASONS])
        for s in SEASONS: rising(d, f"logement {s} malin/confort/plaisir", [lo.get(st, {}).get(s) for st in STYLES])
        for k in ("food", "transport", "activities"):
            v = x.get("daily", {}).get(k, {})
            for st in STYLES: num(d, f"{k} {st}", v.get(st), 0, 600)
            rising(d, f"{k} malin/confort/plaisir", [v.get(st) for st in STYLES])
        fees = x.get("fees", {})
        for st in STYLES: num(d, f"taxe de séjour {st}", fees.get("cityTaxPerPersonNight", {}).get(st), 0, 50)
        num(d, "frais par personne", fees.get("perPerson"), 0, 500)
        if fees.get("perPerson") and not fees.get("perPersonLabel"): err(d, "perPersonLabel manquant")
        for k in INFO:
            if not x.get("info", {}).get(k): err(d, f"info {k} manquante")
        c = x.get("coords", [])
        if len(c) != 2 or not (-180 <= c[0] <= 180 and -90 <= c[1] <= 90): err(d, "coordonnées invalides")
        try:
            up = datetime.date.fromisoformat(x["meta"]["updatedAt"])
            age = (today.year - up.year) * 12 + today.month - up.month
            if age >= every: due.append(f"{x.get('name', d)} : prix vérifiés le {up}, il y a {age} mois")
        except Exception:
            err(d, "meta.updatedAt manquant ou invalide")

    print(f"Check-up des destinations du {today} : {len(ids)} destinations")
    print(f"- {len(errors)} erreur(s)")
    for e in errors: print("  ✗", e)
    print(f"- {len(due)} destination(s) à revérifier (plus de {every} mois)")
    for e in due: print("  ↻", e)
    if not errors and not due: print("Tout est à jour.")
    sys.exit(1 if errors or due else 0)

if __name__ == "__main__":
    main()
