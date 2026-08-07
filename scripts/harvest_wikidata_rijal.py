# -*- coding: utf-8 -*-
"""
Phase 1 + 3: Wikidata Rijal Harvester
Queries Wikidata SPARQL for Islamic hadith scholars and builds a structured JSON dataset.
This runs via Python and saves to scratch/rijal_wikidata.json
"""

import requests
import json
import time
import re
import sys
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SPARQL_URL = "https://query.wikidata.org/sparql"
HEADERS = {
    "Accept": "application/sparql-results+json",
    # Wikidata requires a descriptive User-Agent per their policy
    "User-Agent": "Mozilla/5.0 (compatible; HADEETH_ID_RijalBot/1.0; +https://hadeeth.id; educational-research)"
}

# ── SPARQL Queries ──────────────────────────────────────────────────────────────

# Simpler query: hadith scholars (Q189459) only - no UNION to avoid timeouts
QUERY_HADITH_SCHOLARS = """
SELECT DISTINCT
  ?scholar ?scholarLabel
  ?birthDate ?deathDate
  ?birthPlaceLabel
  ?deathPlaceLabel
WHERE {
  ?scholar wdt:P106 wd:Q189459 .
  OPTIONAL { ?scholar wdt:P569 ?birthDate . }
  OPTIONAL { ?scholar wdt:P570 ?deathDate . }
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en,ar" .
    ?scholar rdfs:label ?scholarLabel .
  }
}
ORDER BY ?deathDate
LIMIT 300
"""

QUERY_SAHABA_ONLY = """
SELECT DISTINCT
  ?scholar ?scholarLabel
  ?birthDate ?deathDate
  ?birthPlace ?birthPlaceLabel
  ?deathPlace ?deathPlaceLabel
  ?nameAr
  ?gender ?genderLabel
  ?hadithCount
WHERE {
  # Companions of the Prophet (Q130754)
  ?scholar wdt:P31 wd:Q5 .
  { ?scholar wdt:P140 wd:Q432 . }  # religion = Islam
  { ?scholar wdt:P1066 wd:Q9458 . }  # student of Prophet Muhammad
  UNION
  { ?scholar wdt:P21 ?gender .
    ?scholar wdt:P1066 wd:Q9458 . }

  OPTIONAL { ?scholar wdt:P569 ?birthDate . }
  OPTIONAL { ?scholar wdt:P570 ?deathDate . }
  OPTIONAL { ?scholar wdt:P19 ?birthPlace . }
  OPTIONAL { ?scholar wdt:P20 ?deathPlace . }
  OPTIONAL { ?scholar wdt:P1705 ?nameAr . FILTER(LANG(?nameAr) = "ar") }
  OPTIONAL { ?scholar wdt:P21 ?gender . }

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
    ?scholar rdfs:label ?scholarLabel .
    ?birthPlace rdfs:label ?birthPlaceLabel .
    ?deathPlace rdfs:label ?deathPlaceLabel .
    ?gender rdfs:label ?genderLabel .
  }
}
ORDER BY ?deathDate
LIMIT 1000
"""

def sparql_query(query, label="query"):
    """Execute a SPARQL query and return results."""
    print(f"  Querying Wikidata: {label}...")
    try:
        resp = requests.get(
            SPARQL_URL,
            params={"query": query, "format": "json"},
            headers=HEADERS,
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", {}).get("bindings", [])
        print(f"  → {len(results)} results")
        return results
    except Exception as e:
        print(f"  ERROR: {e}")
        return []

def extract_year(date_str):
    """Extract year from ISO date string like '1850-01-01T00:00:00Z'."""
    if not date_str:
        return None
    m = re.match(r'^(-?\d{1,4})', date_str)
    if m:
        try:
            return int(m.group(1))
        except:
            return None
    return None

def ce_to_ah(ce_year):
    """Approximate CE to AH conversion."""
    if ce_year is None:
        return None
    # AH ≈ (CE - 622) * 1.031
    ah = round((ce_year - 622) * 1.031)
    return ah if ah > 0 else None

def wikidata_id(url):
    """Extract Q-ID from Wikidata URL."""
    if not url:
        return None
    m = re.search(r'Q(\d+)', url)
    return int(m.group(1)) if m else None

def name_to_id(name_en):
    """Convert English name to a URL-safe ID."""
    clean = name_en.lower()
    clean = re.sub(r"['\u2018\u2019\u02bc\u02be\u02bf`]", "", clean)
    clean = re.sub(r'[^a-z0-9]+', '_', clean)
    clean = clean.strip('_')
    return f"rawi_{clean}"

def parse_result(r):
    """Parse a single SPARQL binding into a structured dict."""
    name_en = r.get("scholarLabel", {}).get("value", "")
    if not name_en:
        return None

    name_ar = r.get("nameAr", {}).get("value", "") or r.get("labelAr", {}).get("value", "")

    birth_ce = extract_year(r.get("birthDate", {}).get("value", ""))
    death_ce = extract_year(r.get("deathDate", {}).get("value", ""))

    rawi = {
        "id": name_to_id(name_en),
        "name_en": name_en,
        "name_ar": name_ar,
        "born_ce": birth_ce,
        "died_ce": death_ce,
        "born_ah": ce_to_ah(birth_ce),
        "died_ah": ce_to_ah(death_ce),
        "city_of_birth": r.get("birthPlaceLabel", {}).get("value", ""),
        "city_of_death": r.get("deathPlaceLabel", {}).get("value", ""),
        "gender": "female" if "female" in r.get("genderLabel", {}).get("value", "").lower() else "male",
        "external_ids": {
            "wikidata": wikidata_id(r.get("scholar", {}).get("value", ""))
        },
        "source": "wikidata"
    }
    return rawi

def main():
    print("=" * 60)
    print("HADEETH.ID — Wikidata Rijal Harvester")
    print("=" * 60)

    all_rawis = {}

    # Query 1: All hadith scholars
    time.sleep(1)
    scholars = sparql_query(QUERY_HADITH_SCHOLARS, "Hadith Scholars")
    for r in scholars:
        parsed = parse_result(r)
        if parsed and parsed["name_en"]:
            # Avoid duplicates by name
            if parsed["id"] not in all_rawis:
                all_rawis[parsed["id"]] = parsed
            else:
                # Merge: fill in missing fields
                existing = all_rawis[parsed["id"]]
                for k, v in parsed.items():
                    if not existing.get(k) and v:
                        existing[k] = v

    print(f"\nAfter hadith scholars query: {len(all_rawis)} unique narrators")

    # Query 2: Sahabah specifically
    time.sleep(2)
    sahaba = sparql_query(QUERY_SAHABA_ONLY, "Sahabah (Companions)")
    sahaba_count = 0
    for r in sahaba:
        parsed = parse_result(r)
        if parsed and parsed["name_en"]:
            parsed["is_sahabi"] = True
            parsed["generation"] = "Sahabi"
            parsed["tabaqat_number"] = 1
            parsed["is_thiqah"] = True  # All Sahabah are 'Adl by ijma'
            if parsed["id"] not in all_rawis:
                all_rawis[parsed["id"]] = parsed
                sahaba_count += 1
            else:
                all_rawis[parsed["id"]]["is_sahabi"] = True
                all_rawis[parsed["id"]]["generation"] = "Sahabi"
                all_rawis[parsed["id"]]["tabaqat_number"] = 1
                all_rawis[parsed["id"]]["is_thiqah"] = True

    print(f"Sahabah added/updated: {sahaba_count}")
    print(f"Total unique narrators: {len(all_rawis)}")

    # Save results
    output = list(all_rawis.values())
    outpath = "scratch/rijal_wikidata.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(output)} narrator records to {outpath}")

    # Print summary
    sahabi_count = sum(1 for r in output if r.get("is_sahabi"))
    with_ar = sum(1 for r in output if r.get("name_ar"))
    with_dates = sum(1 for r in output if r.get("died_ah"))
    print(f"\nSummary:")
    print(f"  Sahabah:          {sahabi_count}")
    print(f"  With Arabic name: {with_ar}")
    print(f"  With death date:  {with_dates}")

if __name__ == "__main__":
    main()
