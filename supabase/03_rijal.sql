-- ============================================================
-- HADEETH.ID — Rijal al-Hadith (علم الرجال) Schema
-- Migration: 03_rijal.sql
-- Run this in Supabase Studio → SQL Editor
-- ============================================================

-- Enable fuzzy text search extension (may already exist)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- ============================================================
-- TABLE 1: rijal — Narrator biographical records
-- ============================================================
CREATE TABLE IF NOT EXISTS public.rijal (
    -- Primary identity
    id                  TEXT PRIMARY KEY,            -- e.g. "rawi_abu_hurairah", "rawi_ibn_umar"
    name_ar             TEXT NOT NULL,               -- Full Arabic name
    name_en             TEXT NOT NULL,               -- Latin transliteration (primary)
    name_id             TEXT,                        -- Indonesian transliteration

    -- Name components
    kunya               TEXT,                        -- Teknonym e.g. "أبو هريرة" (Father of X)
    kunya_en            TEXT,                        -- Kunya in Latin e.g. "Abu Hurairah"
    laqab               TEXT,                        -- Epithet/nickname (Arabic)
    laqab_en            TEXT,                        -- Epithet in Latin
    nasab               TEXT,                        -- Lineage e.g. "ibn al-Khattab"
    nasab_en            TEXT,
    nisba               TEXT,                        -- Attribution e.g. "al-Ansari", "al-Qurashi"
    nisba_en            TEXT,

    -- Variant spellings (array of alternative transliterations)
    name_variants       TEXT[],                      -- {"Abu Huraira", "Abu Hureyra", "Aba Hurairah"}

    -- Generation / era
    generation          TEXT,                        -- "Sahabi", "Tabi'i", "Tabi' al-Tabi'in", "Collector", "Later"
    generation_ar       TEXT,                        -- "صحابي", "تابعي", "تابع التابعين"
    tabaqat_number      SMALLINT,                    -- Generation tier 1–10+ (1=Sahaba, 2=Senior Tabi'un...)
    gender              TEXT DEFAULT 'male',         -- 'male' / 'female'

    -- Timeline
    born_ah             SMALLINT,                    -- Birth year in AH (Hijri)
    died_ah             SMALLINT,                    -- Death year in AH
    born_ce             SMALLINT,                    -- Birth year CE
    died_ce             SMALLINT,                    -- Death year CE
    age_at_death        SMALLINT,

    -- Geography
    city_of_birth       TEXT,
    city_of_death       TEXT,
    city_of_residence   TEXT,
    region              TEXT,                        -- "Hijaz", "Iraq", "Egypt", "Sham", "Khorasan"

    -- Reliability / Grade
    is_sahabi           BOOLEAN DEFAULT FALSE,       -- All Sahabah are 'Adl (just) by consensus
    is_thiqah           BOOLEAN,                     -- Unanimously trustworthy
    grade               TEXT,                        -- Primary grade: "Thiqah", "Sadooq", "Da'if", "Muttaham", "Matruk"
    grade_ar            TEXT,                        -- "ثقة", "صدوق", "ضعيف"
    grade_detail        TEXT,                        -- More nuanced e.g. "Thiqah Thabt" or "Layyin al-Hadith"
    grade_source        TEXT,                        -- Who assigned the primary grade e.g. "Ibn Hajar"

    -- Hadith statistics
    hadith_count        INTEGER DEFAULT 0,           -- Hadiths attributed in our DB
    books               TEXT[],                      -- Which books they appear in {"bukhari","muslim",...}

    -- Biographies (multilingual)
    bio_en              TEXT,
    bio_ar              TEXT,
    bio_id              TEXT,

    -- Relationships (stored as ID arrays for performance; JOINable)
    teacher_ids         TEXT[],                      -- rijal.id values of their teachers
    student_ids         TEXT[],                      -- rijal.id values of their students

    -- Source references
    sources             JSONB,                       -- {"tahdhib_kamal": "vol 34 p 260", "mizan": "vol 4 p 581"}
    external_ids        JSONB,                       -- {"wikidata": "Q315436", "muslimscholars_id": 10}
    muslimscholars_id   INTEGER UNIQUE,              -- Direct reference to muslimscholars.info ID

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE 2: hadith_rijal — Junction: Narrators in each Hadith chain
-- ============================================================
CREATE TABLE IF NOT EXISTS public.hadith_rijal (
    id                  SERIAL PRIMARY KEY,
    hadith_id           TEXT NOT NULL REFERENCES public.hadiths(id) ON DELETE CASCADE,
    rawi_id             TEXT NOT NULL REFERENCES public.rijal(id) ON DELETE CASCADE,

    -- Position in chain (ascending from Prophet ﷺ)
    -- position 1 = closest to Prophet (usually a Sahabi)
    -- position N = closest to the compiler/collector
    position            SMALLINT NOT NULL,

    -- How they transmitted it
    transmission_verb   TEXT,                        -- "حَدَّثَنَا", "أَخْبَرَنَا", "عَنْ", "سَمِعْتُ"
    transmission_en     TEXT,                        -- "narrated to us", "informed us", "from", "I heard"
    is_direct           BOOLEAN DEFAULT FALSE,       -- Direct narration from Prophet ﷺ?

    UNIQUE(hadith_id, rawi_id, position)
);

-- ============================================================
-- TABLE 3: rijal_evaluations — Scholarly verdicts on each narrator
-- ============================================================
CREATE TABLE IF NOT EXISTS public.rijal_evaluations (
    id              SERIAL PRIMARY KEY,
    rawi_id         TEXT NOT NULL REFERENCES public.rijal(id) ON DELETE CASCADE,

    -- The scholar giving the verdict
    evaluator_en    TEXT NOT NULL,                   -- "Ibn Hajar al-Asqalani"
    evaluator_ar    TEXT,                            -- "ابن حجر العسقلاني"
    evaluator_died  SMALLINT,                        -- Death year AH of evaluator (for context)

    -- The verdict itself
    verdict_en      TEXT NOT NULL,                   -- "Thiqah", "Sadooq", "Weak", "Liar"
    verdict_ar      TEXT,                            -- "ثقة", "صدوق", "ضعيف"
    quote_en        TEXT,                            -- Their exact statement in English
    quote_ar        TEXT,                            -- Their exact statement in Arabic

    -- Source reference
    source_book_en  TEXT,                            -- "Taqrib al-Tahdhib"
    source_book_ar  TEXT,                            -- "تقريب التهذيب"
    source_vol      TEXT,
    source_page     TEXT,

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDEXES for performance
-- ============================================================

-- Full-text search on narrator names
CREATE INDEX IF NOT EXISTS idx_rijal_name_en_trgm
    ON public.rijal USING GIN (name_en gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_rijal_name_ar_trgm
    ON public.rijal USING GIN (name_ar gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_rijal_kunya_trgm
    ON public.rijal USING GIN (kunya_en gin_trgm_ops);

-- Generation / grade filter indexes
CREATE INDEX IF NOT EXISTS idx_rijal_generation
    ON public.rijal (generation, tabaqat_number);

CREATE INDEX IF NOT EXISTS idx_rijal_grade
    ON public.rijal (grade, is_thiqah, is_sahabi);

CREATE INDEX IF NOT EXISTS idx_rijal_died_ah
    ON public.rijal (died_ah);

-- Junction table indexes
CREATE INDEX IF NOT EXISTS idx_hadith_rijal_hadith
    ON public.hadith_rijal (hadith_id);

CREATE INDEX IF NOT EXISTS idx_hadith_rijal_rawi
    ON public.hadith_rijal (rawi_id);

-- Evaluations index
CREATE INDEX IF NOT EXISTS idx_rijal_eval_rawi
    ON public.rijal_evaluations (rawi_id);

-- ============================================================
-- FULL-TEXT SEARCH vector for rijal
-- ============================================================
ALTER TABLE public.rijal ADD COLUMN IF NOT EXISTS search_vector tsvector;

CREATE OR REPLACE FUNCTION public.rijal_update_search_vector() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('simple', COALESCE(NEW.name_en, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(NEW.kunya_en, '')), 'A') ||
    setweight(to_tsvector('arabic', COALESCE(NEW.name_ar, '')), 'B') ||
    setweight(to_tsvector('arabic', COALESCE(NEW.kunya, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(NEW.laqab_en, '')), 'C') ||
    setweight(to_tsvector('simple', COALESCE(NEW.nisba_en, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_rijal_search_vector ON public.rijal;
CREATE TRIGGER trigger_rijal_search_vector
BEFORE INSERT OR UPDATE ON public.rijal
FOR EACH ROW EXECUTE FUNCTION public.rijal_update_search_vector();

CREATE INDEX IF NOT EXISTS idx_rijal_fts
    ON public.rijal USING GIN (search_vector);

-- ============================================================
-- RPC: Search rijal by name (supports fuzzy + exact)
-- ============================================================
DROP FUNCTION IF EXISTS public.search_rijal(text, integer, integer);

CREATE OR REPLACE FUNCTION public.search_rijal(
    query_text  TEXT,
    match_limit INTEGER DEFAULT 20,
    match_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id          TEXT,
    name_en     TEXT,
    name_ar     TEXT,
    kunya_en    TEXT,
    generation  TEXT,
    grade       TEXT,
    is_sahabi   BOOLEAN,
    hadith_count INTEGER,
    rank        REAL
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.name_en,
        r.name_ar,
        r.kunya_en,
        r.generation,
        r.grade,
        r.is_sahabi,
        r.hadith_count,
        (
            CASE
                WHEN r.name_en ILIKE '%' || query_text || '%' THEN 2.0
                WHEN r.kunya_en ILIKE '%' || query_text || '%' THEN 1.8
                WHEN r.name_ar ILIKE '%' || query_text || '%' THEN 1.5
                ELSE similarity(r.name_en, query_text)
            END
        )::real AS rank
    FROM public.rijal r
    WHERE
        r.name_en ILIKE '%' || query_text || '%'
        OR r.kunya_en ILIKE '%' || query_text || '%'
        OR r.name_ar ILIKE '%' || query_text || '%'
        OR r.search_vector @@ websearch_to_tsquery('simple', query_text)
        OR similarity(r.name_en, query_text) > 0.3
    ORDER BY rank DESC, r.hadith_count DESC
    LIMIT match_limit OFFSET match_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- RPC: Get full sanad chain for a hadith from DB
-- ============================================================
DROP FUNCTION IF EXISTS public.get_sanad_chain(text);

CREATE OR REPLACE FUNCTION public.get_sanad_chain(p_hadith_id TEXT)
RETURNS TABLE (
    narrator_position   SMALLINT,
    transmission_en     TEXT,
    transmission_verb   TEXT,
    rawi_id             TEXT,
    name_en             TEXT,
    name_ar             TEXT,
    kunya_en            TEXT,
    generation          TEXT,
    grade               TEXT,
    died_ah             SMALLINT,
    is_sahabi           BOOLEAN,
    is_thiqah           BOOLEAN
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        hr.position AS narrator_position,
        hr.transmission_en,
        hr.transmission_verb,
        r.id,
        r.name_en,
        r.name_ar,
        r.kunya_en,
        r.generation,
        r.grade,
        r.died_ah,
        r.is_sahabi,
        r.is_thiqah
    FROM public.hadith_rijal hr
    JOIN public.rijal r ON r.id = hr.rawi_id
    WHERE hr.hadith_id = p_hadith_id
    ORDER BY hr.position ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- RLS Policies (read-only public access)
-- ============================================================
ALTER TABLE public.rijal ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hadith_rijal ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rijal_evaluations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read rijal" ON public.rijal
    FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "Public read hadith_rijal" ON public.hadith_rijal
    FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "Public read rijal_evaluations" ON public.rijal_evaluations
    FOR SELECT TO anon, authenticated USING (true);

-- Grant RPC access
GRANT EXECUTE ON FUNCTION public.search_rijal(text, integer, integer) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.get_sanad_chain(text) TO anon, authenticated, service_role;

-- Updated_at auto-trigger for rijal
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_rijal_updated_at ON public.rijal;
CREATE TRIGGER trigger_rijal_updated_at
BEFORE UPDATE ON public.rijal
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
