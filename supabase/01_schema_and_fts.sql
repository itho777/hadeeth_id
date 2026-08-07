-- HADEETH.ID Supabase PostgreSQL Master Schema & Universal Search Setup

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

-- Extensions & Search Indexes
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_hadiths_fts ON public.hadiths USING gin(search_vector);
CREATE INDEX IF NOT EXISTS idx_hadiths_trgm_ar ON public.hadiths USING gin(text_ar_search gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_hadiths_trgm_en ON public.hadiths USING gin(text_en gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_hadiths_trgm_id ON public.hadiths USING gin(text_id gin_trgm_ops);

-- Search Vector Auto-Trigger Function
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

-- Populate search_vector for any pre-seeded rows
UPDATE public.hadiths 
SET search_vector = 
    setweight(to_tsvector('arabic', COALESCE(text_ar_search, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(text_en, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(text_id, '')), 'C')
WHERE search_vector IS NULL;

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
