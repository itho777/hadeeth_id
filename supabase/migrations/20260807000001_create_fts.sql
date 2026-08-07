-- Full-Text Search (FTS) Configuration & Functions for Supabase

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_hadiths_fts ON public.hadiths USING gin(search_vector);
CREATE INDEX IF NOT EXISTS idx_hadiths_trgm_ar ON public.hadiths USING gin(text_ar_search gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_hadiths_trgm_en ON public.hadiths USING gin(text_en gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_hadiths_trgm_id ON public.hadiths USING gin(text_id gin_trgm_ops);

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

CREATE OR REPLACE FUNCTION public.search_hadiths(
    query_text TEXT,
    target_lang TEXT DEFAULT 'en',
    match_limit INT DEFAULT 20,
    match_offset INT DEFAULT 0
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
BEGIN
    IF target_lang = 'ar' THEN
        RETURN QUERY
        SELECT h.id, h.book_id, h.hadith_number, h.text_ar, h.text_en, h.text_id, h.grade,
               ts_rank(h.search_vector, to_tsquery('arabic', query_text)) AS rank
        FROM public.hadiths h
        WHERE h.search_vector @@ to_tsquery('arabic', query_text)
           OR h.text_ar_search ILIKE '%' || query_text || '%'
        ORDER BY rank DESC
        LIMIT match_limit OFFSET match_offset;
    ELSIF target_lang = 'id' THEN
        RETURN QUERY
        SELECT h.id, h.book_id, h.hadith_number, h.text_ar, h.text_en, h.text_id, h.grade,
               ts_rank(h.search_vector, to_tsquery('simple', query_text)) AS rank
        FROM public.hadiths h
        WHERE h.search_vector @@ to_tsquery('simple', query_text)
           OR h.text_id ILIKE '%' || query_text || '%'
        ORDER BY rank DESC
        LIMIT match_limit OFFSET match_offset;
    ELSE
        RETURN QUERY
        SELECT h.id, h.book_id, h.hadith_number, h.text_ar, h.text_en, h.text_id, h.grade,
               ts_rank(h.search_vector, to_tsquery('english', query_text)) AS rank
        FROM public.hadiths h
        WHERE h.search_vector @@ to_tsquery('english', query_text)
           OR h.text_en ILIKE '%' || query_text || '%'
        ORDER BY rank DESC
        LIMIT match_limit OFFSET match_offset;
    END IF;
END;
$$ LANGUAGE plpgsql;
