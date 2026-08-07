/**
 * HADEETH.ID — Cloudflare Workers AI Semantic Search & Assistant API
 * Leverages Cloudflare Workers AI free quota:
 * 1. Vector Embeddings with @cf/baai/bge-small-en-v1.5
 * 2. Conversational Hadith Q&A with @cf/meta/llama-3-8b-instruct
 */

export default {
  async fetch(request, env) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Content-Type': 'application/json; charset=utf-8'
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);

    // Endpoint 1: Semantic AI Search & Q&A
    if (url.pathname === '/api/ai-search' && request.method === 'POST') {
      try {
        const body = await request.json();
        const userQuery = body.query || '';

        if (!userQuery) {
          return new Response(JSON.stringify({ error: 'Query parameters required' }), { status: 400, headers: corsHeaders });
        }

        // 1. Generate Query Vector Embedding using Cloudflare Workers AI
        const embeddings = await env.AI.run('@cf/baai/bge-small-en-v1.5', { text: [userQuery] });

        // 2. Query Supabase RPC search for matching canonical hadiths
        const spRes = await fetch(`${env.SUPABASE_URL}/rest/v1/rpc/search_hadiths`, {
          method: 'POST',
          headers: {
            'apikey': env.SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${env.SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query_text: userQuery,
            target_lang: 'en',
            match_limit: 3,
            match_offset: 0
          })
        });

        const hadiths = await spRes.json();

        // 3. Generate AI Answer using Llama 3 on Workers AI
        const contextText = hadiths.map(h => `[Hadith #${h.hadith_number} (${h.book_id})]: ${h.text_en}`).join('\n\n');

        const systemPrompt = `You are a knowledgeable Islamic scholar assistant for HADEETH.ID. Answer the user's query clearly using the provided authentic Hadiths as primary context. Keep answers respectful, accurate, and concise.`;

        const aiResponse = await env.AI.run('@cf/meta/llama-3-8b-instruct', {
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: `Question: ${userQuery}\n\nContext Hadiths:\n${contextText}` }
          ]
        });

        return new Response(JSON.stringify({
          query: userQuery,
          matches: hadiths,
          ai_answer: aiResponse.response || 'No response generated.',
          embedding_vector_length: embeddings.data[0].length
        }), { headers: corsHeaders });

      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // Endpoint 2: Generate Sharh & Word Breakdown
    if (url.pathname === '/api/explain' && request.method === 'POST') {
      try {
        const body = await request.json();
        const text = body.text || '';
        const targetLang = body.language || 'English';

        const prompt = `Explain the following Hadith in ${targetLang}. Provide a 2-bullet summary of key learnings and explain key Arabic terms:\n\n${text}`;

        const aiResponse = await env.AI.run('@cf/meta/llama-3-8b-instruct', {
          messages: [{ role: 'user', content: prompt }]
        });

        return new Response(JSON.stringify({
          explanation: aiResponse.response
        }), { headers: corsHeaders });

      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // Health Check
    return new Response(JSON.stringify({
      name: 'HADEETH.ID Workers AI Search API',
      status: 'operational',
      endpoints: ['/api/ai-search', '/api/explain']
    }), { headers: corsHeaders });
  }
};
