-- Supabase PostgreSQL Schema for HADEETH.ID

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
