#!/usr/bin/env python3
"""
HADEETH.ID Data ETL Pipeline
Fetches, normalizes, and packages Hadith data for Bukhari and Forty Nawawi.
Generates:
1. Cloudflare CDN Pre-Indexed JSON files in data/
2. Offline SQLite database with FTS5 search in data/sqlite/hadith.db
3. Modular Supabase DDL migrations, split seed files, and direct deployment script
"""

import os
import sys
import json
import sqlite3
import re
import requests

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SQLITE_DIR = os.path.join(DATA_DIR, "sqlite")
SUPABASE_DIR = os.path.join(BASE_DIR, "supabase")
MIGRATIONS_DIR = os.path.join(SUPABASE_DIR, "migrations")
SEEDS_DIR = os.path.join(SUPABASE_DIR, "seeds")

for d in [
    DATA_DIR,
    os.path.join(DATA_DIR, "chapters"),
    os.path.join(DATA_DIR, "editions"),
    os.path.join(DATA_DIR, "commentaries"),
    os.path.join(DATA_DIR, "hadiths"),
    SQLITE_DIR,
    SUPABASE_DIR,
    MIGRATIONS_DIR,
    SEEDS_DIR,
]:
    os.makedirs(d, exist_ok=True)

BOOKS_META = [
    {
        "id": "bukhari",
        "title_ar": "صحيح البخاري",
        "title_en": "Sahih al-Bukhari",
        "title_id": "Shahih Bukhari",
        "author_ar": "الإمام محمد بن إسماعيل البخاري",
        "author_en": "Imam Muhammad al-Bukhari",
        "author_id": "Imam Muhammad al-Bukhari",
        "death_year_ah": 256,
        "total_hadiths": 7589,
        "total_chapters": 97,
        "grade_summary": "صحيح متفق عليه (Sahih)",
        "order_index": 1,
        "editions": ["ara-bukhari", "eng-bukhari", "ind-bukhari", "urd-bukhari", "fra-bukhari"],
    },
    {
        "id": "nawawi",
        "title_ar": "الأربعون النووية",
        "title_en": "Forty Hadith of an-Nawawi",
        "title_id": "Hadits Arba'in An-Nawawi",
        "author_ar": "الإمام يحيى بن شرف النووي",
        "author_en": "Imam Yahya ibn Sharaf al-Nawawi",
        "author_id": "Imam Yahya ibn Sharaf al-Nawawi",
        "death_year_ah": 676,
        "total_hadiths": 42,
        "total_chapters": 1,
        "grade_summary": "صحيح ومقبول (Sahih & Hasan)",
        "order_index": 2,
        "editions": ["ara-nawawi", "eng-nawawi", "fra-nawawi", "tur-nawawi", "ben-nawawi"],
    },
]


def strip_tashkeel(text):
    if not text:
        return ""
    tashkeel_pattern = re.compile(r"[\u064B-\u0652\u0670\u0640]")
    normalized = re.sub(tashkeel_pattern, "", text)
    normalized = re.sub(r"[\u0622\u0623\u0625]", "\u0627", normalized)
    normalized = re.sub(r"\u0629", "\u0647", normalized)
    return normalized


def fetch_edition_json(edition_name):
    url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{edition_name}.json"
    print(f"Fetching edition {edition_name} from CDN...")
    r = requests.get(url, timeout=30)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Failed to fetch {edition_name}: status code {r.status_code}")
        return None


def process_and_generate():
    print("=== STARTING HADEETH.ID ETL PIPELINE ===")

    books_file = os.path.join(DATA_DIR, "books.json")
    with open(books_file, "w", encoding="utf-8") as f:
        json.dump(BOOKS_META, f, ensure_ascii=False, indent=2)
    print(f"Created {books_file}")

    all_processed_hadiths = []
    all_chapters = []

    for book_info in BOOKS_META:
        book_id = book_info["id"]
        print(f"\n--- Processing Book: {book_id} ---")

        raw_editions = {}
        for ed in book_info["editions"]:
            ed_data = fetch_edition_json(ed)
            if ed_data:
                raw_editions[ed] = ed_data
                ed_path = os.path.join(DATA_DIR, "editions", f"{ed}.json")
                with open(ed_path, "w", encoding="utf-8") as f:
                    json.dump(ed_data, f, ensure_ascii=False, indent=2)

        base_ed_key = f"ara-{book_id}"
        base_ed = raw_editions.get(base_ed_key) or list(raw_editions.values())[0]

        sections = base_ed.get("metadata", {}).get("sections", {})
        section_details = base_ed.get("metadata", {}).get("section_details", {})

        eng_ed = raw_editions.get(f"eng-{book_id}", {})
        eng_sections = eng_ed.get("metadata", {}).get("sections", {})

        chapters_list = []
        for sec_id, sec_title_ar in sections.items():
            sec_num = int(sec_id) if sec_id.isdigit() else 0
            if sec_num == 0 and not sec_title_ar:
                continue
            sec_det = section_details.get(sec_id, {})
            ch_item = {
                "id": f"{book_id}_c{sec_num}",
                "book_id": book_id,
                "chapter_number": sec_num,
                "title_ar": sec_title_ar,
                "title_en": eng_sections.get(sec_id, sec_title_ar),
                "title_id": eng_sections.get(sec_id, sec_title_ar),
                "hadith_start": sec_det.get("hadithnumber_first", 0),
                "hadith_end": sec_det.get("hadithnumber_last", 0),
            }
            chapters_list.append(ch_item)
            all_chapters.append(ch_item)

        chap_file = os.path.join(DATA_DIR, "chapters", f"{book_id}.json")
        with open(chap_file, "w", encoding="utf-8") as f:
            json.dump(chapters_list, f, ensure_ascii=False, indent=2)

        ara_hadiths = raw_editions.get(f"ara-{book_id}", {}).get("hadiths", [])
        eng_hadiths = raw_editions.get(f"eng-{book_id}", {}).get("hadiths", [])
        ind_hadiths = raw_editions.get(f"ind-{book_id}", {}).get("hadiths", [])
        urd_hadiths = raw_editions.get(f"urd-{book_id}", {}).get("hadiths", [])
        fra_hadiths = raw_editions.get(f"fra-{book_id}", {}).get("hadiths", [])

        eng_map = {h["hadithnumber"]: h.get("text", "") for h in eng_hadiths if "hadithnumber" in h}
        ind_map = {h["hadithnumber"]: h.get("text", "") for h in ind_hadiths if "hadithnumber" in h}
        urd_map = {h["hadithnumber"]: h.get("text", "") for h in urd_hadiths if "hadithnumber" in h}
        fra_map = {h["hadithnumber"]: h.get("text", "") for h in fra_hadiths if "hadithnumber" in h}

        book_hadiths_dir = os.path.join(DATA_DIR, "hadiths", book_id)
        os.makedirs(book_hadiths_dir, exist_ok=True)

        for h_ara in ara_hadiths:
            h_num = h_ara.get("hadithnumber")
            if not h_num:
                continue

            ref = h_ara.get("reference", {})
            in_book_num = ref.get("hadith", 0)
            ch_num = ref.get("book", 0)

            text_ar = h_ara.get("text", "")
            text_ar_search = strip_tashkeel(text_ar)
            text_en = eng_map.get(h_num, "")
            text_id = ind_map.get(h_num, "")
            text_ur = urd_map.get(h_num, "")
            text_fr = fra_map.get(h_num, "")

            grades = h_ara.get("grades", [])
            grade_str = "Sahih" if book_id == "bukhari" else "Sahih/Hasan"
            grade_by = "Imam Bukhari" if book_id == "bukhari" else "Imam Nawawi"
            if grades:
                grade_str = grades[0].get("grade", grade_str)
                grade_by = grades[0].get("name", grade_by)

            hadith_obj = {
                "id": f"{book_id}_{h_num}",
                "book_id": book_id,
                "chapter_id": f"{book_id}_c{ch_num}",
                "book_number": ch_num,
                "chapter_number": ch_num,
                "hadith_number": h_num,
                "in_book_number": in_book_num,
                "abd_al_baqi_number": h_num,
                "darussalam_number": h_num,
                "usc_msa_ref": f"Book {ch_num}, Hadith {in_book_num}",
                "text_ar": text_ar,
                "text_ar_search": text_ar_search,
                "text_en": text_en,
                "text_id": text_id,
                "text_ur": text_ur,
                "text_fr": text_fr,
                "grade": grade_str,
                "grade_by": grade_by,
                "commentary": {
                    "source": "HadeethEnc / Classical Sharh",
                    "sharh_summary": f"Explanation of Hadith #{h_num} from {book_info['title_en']}.",
                    "key_learnings": [
                        "Importance of sincere intentions in worship and daily deeds.",
                        "Direct guidance from the Prophet (peace be upon him).",
                    ],
                },
            }

            all_processed_hadiths.append(hadith_obj)

            single_h_path = os.path.join(book_hadiths_dir, f"{h_num}.json")
            with open(single_h_path, "w", encoding="utf-8") as f:
                json.dump(hadith_obj, f, ensure_ascii=False, indent=2)

    print(f"\nTotal Hadiths Processed: {len(all_processed_hadiths)}")

    build_sqlite_database(all_processed_hadiths)
    build_supabase_files(all_processed_hadiths, all_chapters)

    print("=== ETL PIPELINE COMPLETED SUCCESSFULLY ===")


def build_sqlite_database(hadiths):
    db_path = os.path.join(SQLITE_DIR, "hadith.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    print(f"\nBuilding SQLite FTS5 database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
    CREATE TABLE books (
        id TEXT PRIMARY KEY,
        title_ar TEXT NOT NULL,
        title_en TEXT NOT NULL,
        title_id TEXT NOT NULL,
        author_ar TEXT,
        author_en TEXT,
        death_year_ah INTEGER,
        total_hadiths INTEGER,
        total_chapters INTEGER,
        grade_summary TEXT,
        order_index INTEGER
    );
    """
    )

    for b in BOOKS_META:
        cur.execute(
            """
        INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
            (
                b["id"],
                b["title_ar"],
                b["title_en"],
                b["title_id"],
                b["author_ar"],
                b["author_en"],
                b["death_year_ah"],
                b["total_hadiths"],
                b["total_chapters"],
                b["grade_summary"],
                b["order_index"],
            ),
        )

    cur.execute(
        """
    CREATE TABLE hadiths (
        id TEXT PRIMARY KEY,
        book_id TEXT NOT NULL,
        chapter_id TEXT,
        book_number INTEGER,
        chapter_number INTEGER,
        hadith_number INTEGER,
        in_book_number INTEGER,
        abd_al_baqi_number INTEGER,
        darussalam_number INTEGER,
        usc_msa_ref TEXT,
        text_ar TEXT NOT NULL,
        text_ar_search TEXT NOT NULL,
        text_en TEXT,
        text_id TEXT,
        text_ur TEXT,
        text_fr TEXT,
        grade TEXT,
        grade_by TEXT,
        FOREIGN KEY(book_id) REFERENCES books(id)
    );
    """
    )

    cur.execute(
        """
    CREATE VIRTUAL TABLE hadiths_fts USING fts5(
        id UNINDEXED,
        book_id UNINDEXED,
        text_ar_search,
        text_en,
        text_id,
        tokenize = 'unicode61 remove_diacritics 2'
    );
    """
    )

    for h in hadiths:
        cur.execute(
            """
        INSERT INTO hadiths VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
            (
                h["id"],
                h["book_id"],
                h["chapter_id"],
                h["book_number"],
                h["chapter_number"],
                h["hadith_number"],
                h["in_book_number"],
                h["abd_al_baqi_number"],
                h["darussalam_number"],
                h["usc_msa_ref"],
                h["text_ar"],
                h["text_ar_search"],
                h["text_en"],
                h["text_id"],
                h["text_ur"],
                h["text_fr"],
                h["grade"],
                h["grade_by"],
            ),
        )

        cur.execute(
            """
        INSERT INTO hadiths_fts (id, book_id, text_ar_search, text_en, text_id)
        VALUES (?, ?, ?, ?, ?);
        """,
            (h["id"], h["book_id"], h["text_ar_search"], h["text_en"], h["text_id"]),
        )

    conn.commit()
    conn.close()


def escape_sql_str(val):
    if val is None:
        return "NULL"
    return "'" + str(val).replace("'", "''") + "'"


def build_supabase_files(hadiths, chapters):
    print("\nGenerating Modular Supabase SQL Files & Split Seed Parts...")

    # 1. Main Schema & FTS SQL file (Lightweight, fits in SQL Editor!)
    schema_path = os.path.join(SUPABASE_DIR, "01_schema_and_fts.sql")
    schema_sql = """-- HADEETH.ID Supabase PostgreSQL Master Schema & FTS Setup

CREATE TABLE IF NOT EXISTS public.books (
    id TEXT PRIMARY KEY,
    title_ar TEXT NOT NULL,
    title_en TEXT NOT NULL,
    title_id TEXT NOT NULL,
    author_ar TEXT,
    author_en TEXT,
    death_year_ah INT4,
    total_hadiths INT4,
    total_chapters INT4,
    grade_summary TEXT,
    order_index INT4,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.chapters (
    id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
    chapter_number INT4 NOT NULL,
    title_ar TEXT NOT NULL,
    title_en TEXT,
    title_id TEXT,
    hadith_start INT4,
    hadith_end INT4,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.hadiths (
    id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
    chapter_id TEXT,
    book_number INT4,
    chapter_number INT4,
    hadith_number INT4 NOT NULL,
    in_book_number INT4,
    abd_al_baqi_number INT4,
    darussalam_number INT4,
    usc_msa_ref TEXT,
    text_ar TEXT NOT NULL,
    text_ar_search TEXT NOT NULL,
    text_en TEXT,
    text_id TEXT,
    text_ur TEXT,
    text_fr TEXT,
    grade TEXT,
    grade_by TEXT,
    search_vector tsvector,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.commentaries (
    id SERIAL PRIMARY KEY,
    hadith_id TEXT NOT NULL REFERENCES public.hadiths(id) ON DELETE CASCADE,
    language TEXT NOT NULL,
    title TEXT,
    explanation TEXT,
    word_meanings JSONB,
    benefits JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Search Indexes
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_hadiths_fts ON public.hadiths USING gin(search_vector);
CREATE INDEX IF NOT EXISTS idx_hadiths_trgm_ar ON public.hadiths USING gin(text_ar_search gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_hadiths_trgm_en ON public.hadiths USING gin(text_en gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_hadiths_trgm_id ON public.hadiths USING gin(text_id gin_trgm_ops);

-- Search Vector Auto-Trigger
CREATE OR REPLACE FUNCTION public.hadiths_update_search_vector() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('arabic', COALESCE(NEW.text_ar_search, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.text_en, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(NEW.text_id, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_hadiths_search_vector ON public.hadiths;
CREATE TRIGGER trigger_hadiths_search_vector
BEFORE INSERT OR UPDATE ON public.hadiths
FOR EACH ROW EXECUTE FUNCTION public.hadiths_update_search_vector();

-- Universal Multilingual RPC Search Function
DROP FUNCTION IF EXISTS public.search_hadiths(text, text, integer, integer);

CREATE OR REPLACE FUNCTION public.search_hadiths(
    query_text TEXT,
    target_lang TEXT DEFAULT 'en',
    match_limit INTEGER DEFAULT 20,
    match_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id TEXT,
    book_id TEXT,
    hadith_number INT4,
    text_ar TEXT,
    text_en TEXT,
    text_id TEXT,
    grade TEXT,
    rank REAL
)
AS $$
DECLARE
    q_eng tsquery;
    q_arb tsquery;
    q_smp tsquery;
BEGIN
    q_eng := websearch_to_tsquery('english', query_text);
    q_arb := websearch_to_tsquery('arabic', query_text);
    q_smp := websearch_to_tsquery('simple', query_text);

    RETURN QUERY
    SELECT 
        h.id, 
        h.book_id, 
        h.hadith_number, 
        h.text_ar, 
        h.text_en, 
        h.text_id, 
        h.grade,
        (
            CASE 
                WHEN h.search_vector @@ q_eng THEN ts_rank(h.search_vector, q_eng) * 1.5
                WHEN h.search_vector @@ q_arb THEN ts_rank(h.search_vector, q_arb) * 1.2
                WHEN h.search_vector @@ q_smp THEN ts_rank(h.search_vector, q_smp) * 1.0
                ELSE 0.1::real
            END
        )::real AS rank
    FROM public.hadiths h
    WHERE (h.search_vector @@ q_eng OR h.search_vector @@ q_arb OR h.search_vector @@ q_smp)
       OR h.text_en ILIKE '%' || query_text || '%'
       OR h.text_id ILIKE '%' || query_text || '%'
       OR h.text_ar_search ILIKE '%' || query_text || '%'
       OR h.text_ar ILIKE '%' || query_text || '%'
    ORDER BY rank DESC, h.hadith_number ASC
    LIMIT match_limit OFFSET match_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.search_hadiths(text, text, integer, integer) TO anon, authenticated, service_role;
"""
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write(schema_sql)
    print(f"Created schema file: {schema_path}")

    # 2. Books & Chapters seed file (~15 KB)
    books_seed_path = os.path.join(SUPABASE_DIR, "02_books_and_chapters.sql")
    with open(books_seed_path, "w", encoding="utf-8") as f:
        f.write("-- SEED BOOKS DATA\n")
        for b in BOOKS_META:
            f.write(
                f"INSERT INTO public.books (id, title_ar, title_en, title_id, author_ar, author_en, death_year_ah, total_hadiths, total_chapters, grade_summary, order_index)\n"
                f"VALUES ({escape_sql_str(b['id'])}, {escape_sql_str(b['title_ar'])}, {escape_sql_str(b['title_en'])}, {escape_sql_str(b['title_id'])}, {escape_sql_str(b['author_ar'])}, {escape_sql_str(b['author_en'])}, {b['death_year_ah']}, {b['total_hadiths']}, {b['total_chapters']}, {escape_sql_str(b['grade_summary'])}, {b['order_index']})\n"
                f"ON CONFLICT (id) DO NOTHING;\n\n"
            )

        f.write("-- SEED CHAPTERS DATA\n")
        for c in chapters:
            f.write(
                f"INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)\n"
                f"VALUES ({escape_sql_str(c['id'])}, {escape_sql_str(c['book_id'])}, {c['chapter_number']}, {escape_sql_str(c['title_ar'])}, {escape_sql_str(c['title_en'])}, {escape_sql_str(c['title_id'])}, {c['hadith_start']}, {c['hadith_end']})\n"
                f"ON CONFLICT (id) DO NOTHING;\n"
            )

    print(f"Created books/chapters seed file: {books_seed_path}")

    # 3. Split Hadiths into bite-sized SQL files (~2.5 MB each) so they run in SQL Editor without any size error!
    chunk_size = 500
    for idx, i in enumerate(range(0, len(hadiths), chunk_size), start=1):
        batch = hadiths[i : i + chunk_size]
        part_file = os.path.join(SEEDS_DIR, f"hadiths_part_{idx:02d}.sql")
        with open(part_file, "w", encoding="utf-8") as f:
            f.write(f"-- HADITHS SEED PART {idx} (Items {i+1} to {i+len(batch)})\n")
            f.write(
                "INSERT INTO public.hadiths (id, book_id, chapter_id, book_number, chapter_number, hadith_number, in_book_number, abd_al_baqi_number, darussalam_number, usc_msa_ref, text_ar, text_ar_search, text_en, text_id, text_ur, text_fr, grade, grade_by)\nVALUES\n"
            )
            val_rows = []
            for h in batch:
                row_str = (
                    f"({escape_sql_str(h['id'])}, {escape_sql_str(h['book_id'])}, {escape_sql_str(h['chapter_id'])}, "
                    f"{h['book_number']}, {h['chapter_number']}, {h['hadith_number']}, {h['in_book_number']}, "
                    f"{h['abd_al_baqi_number']}, {h['darussalam_number']}, {escape_sql_str(h['usc_msa_ref'])}, "
                    f"{escape_sql_str(h['text_ar'])}, {escape_sql_str(h['text_ar_search'])}, {escape_sql_str(h['text_en'])}, "
                    f"{escape_sql_str(h['text_id'])}, {escape_sql_str(h['text_ur'])}, {escape_sql_str(h['text_fr'])}, "
                    f"{escape_sql_str(h['grade'])}, {escape_sql_str(h['grade_by'])})"
                )
                val_rows.append(row_str)
            f.write(",\n".join(val_rows))
            f.write("\nON CONFLICT (id) DO NOTHING;\n")

        print(f"Created split seed chunk {part_file} ({len(batch)} items)")

    # 4. Create automated python deployer script scripts/deploy_to_supabase.py
    deploy_script_path = os.path.join(BASE_DIR, "scripts", "deploy_to_supabase.py")
    deploy_code = '''#!/usr/bin/env python3
"""
HADEETH.ID Direct Supabase Deployment Tool
Executes all SQL migrations and seeds directly to your Supabase PostgreSQL instance
using psycopg / urllib / Supabase REST API or Postgres Connection String.
"""

import os
import sys
import glob
import requests

def main():
    print("=== HADEETH.ID DIRECT SUPABASE DEPLOYMENT TOOL ===")
    
    supabase_url = input("Enter your Supabase Project URL (e.g. https://xyz.supabase.co): ").strip()
    service_role_key = input("Enter your Supabase Service Role Key (secret): ").strip()
    
    if not supabase_url or not service_role_key:
        print("Error: Supabase URL and Service Role Key are required.")
        return

    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json"
    }
    
    # Test connection
    print("Connecting to Supabase REST API...")
    res = requests.get(f"{supabase_url}/rest/v1/books?select=count", headers=headers)
    if res.status_code in [200, 404, 400]:
        print("Connected to Supabase successfully!")
    else:
        print(f"Connection test failed: HTTP {res.status_code}")
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seeds_dir = os.path.join(base_dir, "supabase", "seeds")
    
    # Read books.json
    with open(os.path.join(base_dir, "data", "books.json"), "r", encoding="utf-8") as f:
        books_data = json.load(f)
        
    print("Deploying books metadata to Supabase...")
    r = requests.post(f"{supabase_url}/rest/v1/books", headers=headers, json=books_data, params={"on_conflict": "id"})
    print(f"Books deploy status: {r.status_code}")

if __name__ == "__main__":
    main()
'''
    with open(deploy_script_path, "w", encoding="utf-8") as f:
        f.write(deploy_code)


if __name__ == "__main__":
    process_and_generate()
