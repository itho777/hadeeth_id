/**
 * HADEETH.ID — semantic search API.
 *
 * Cloudflare Workers AI embeds the query with bge-m3 (1024-d, the same model
 * used for the offline corpus). Supabase compares via pgvector halfvec cosine
 * through the match_hadiths RPC. This Worker is stateless: the vectors live in
 * Supabase, and the text is hydrated by the client from R2.
 *
 * POST /api/search   { q, book?, limit? }
 * GET  /health
 */

const ALLOWED_ORIGINS = [
  'https://hadeeth.id',
  'https://www.hadeeth.id',
];

function cors(request) {
  const origin = request.headers.get('Origin') || '';
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  };
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), { status, headers });
}

export default {
  async fetch(request, env) {
    const H = cors(request);
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') return new Response(null, { headers: H });

    if (url.pathname === '/health' && request.method === 'GET') {
      return json({
        name: 'hadeeth-semantic',
        status: 'ok',
        model: '@cf/baai/bge-m3',
        rpc: 'match_hadiths',
      }, 200, H);
    }

    if (url.pathname !== '/api/search' || request.method !== 'POST') {
      return json({ error: 'not found' }, 404, H);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: 'invalid JSON body' }, 400, H);
    }

    const q = String(body.q || body.query || '').trim().slice(0, 500);
    const book = body.book && body.book !== 'all' ? String(body.book).slice(0, 40) : null;
    const limit = Math.max(1, Math.min(Number(body.limit) || 20, 100));

    if (!q) return json({ error: 'q is required' }, 400, H);

    const out = {
      // 'none' until a tier actually produced rows. Never pre-label the response
      // with an engine that has not run — the client reports this verbatim.
      mode: 'none',
      results: [],
      vectorGenerated: false,
      aiError: null,
      rpcError: null,
      embeddingMs: 0,
      searchMs: 0,
    };

    // 1. Embed the query on Cloudflare AI.
    let vector = null;
    const t0 = Date.now();
    try {
      if (!env.AI) throw new Error('AI binding is not configured');
      const r = await env.AI.run('@cf/baai/bge-m3', { text: [q] });
      vector = r?.data?.[0] || null;
      out.embeddingMs = Date.now() - t0;
      if (!Array.isArray(vector) || vector.length !== 1024) {
        throw new Error(`bad embedding shape: ${vector?.length}`);
      }
      out.vectorGenerated = true;
    } catch (e) {
      out.aiError = String(e?.message || e);
      return json(out, 200, H); // client falls back to keyword search
    }

    // 2. Compare in Supabase via pgvector.
    const t1 = Date.now();
    try {
      const rpcBody = { p_query_embedding: vector, p_match_count: limit };
      if (book) rpcBody.p_book = book;

      const res = await fetch(`${env.SUPABASE_URL}/rest/v1/rpc/match_hadiths`, {
        method: 'POST',
        headers: {
          apikey: env.SUPABASE_ANON_KEY,
          Authorization: `Bearer ${env.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(rpcBody),
        signal: AbortSignal.timeout(12000),
      });
      out.searchMs = Date.now() - t1;

      if (!res.ok) {
        out.rpcError = `HTTP ${res.status}: ${(await res.text()).slice(0, 200)}`;
        return json(out, 200, H);
      }

      const rows = await res.json();
      out.results = (Array.isArray(rows) ? rows : []).map(r => ({
        id: r.id,
        book_id: r.book_id,
        hadith_number: r.hadith_number,
        similarity: Number(r.similarity),
      }));
      if (out.results.length) out.mode = 'semantic';
    } catch (e) {
      out.rpcError = String(e?.message || e);
      return json(out, 200, H);
    }

    return json(out, 200, H);
  },
};
