/**
 * Razi bridge — exact-match cache for the ten starter questions the app and
 * the web widget put on screen themselves. Those answers are prepared once,
 * reviewed, and shipped as `seed_answers.json`; the Worker returns them before
 * any model session is created, so the first tap is instant on BOTH clients.
 *
 * Drop into the Worker that serves https://razi.hadeeth.id/api/chat:
 *
 *   import { withSeedCache } from './seed_cache.js';
 *   export default {
 *     fetch(request, env, ctx) {
 *       return withSeedCache(request, env, ctx, () => handleChat(request, env, ctx));
 *     }
 *   };
 *
 * The fallback runs unchanged for every other question.
 */
import seedAnswers from './seed_answers.json';

const normalise = (s) =>
  s
    .normalize('NFKC')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();

const INDEX = new Map();
for (const entry of seedAnswers) {
  INDEX.set(`${entry.lang}|${normalise(entry.question)}`, entry.reply);
}

export async function withSeedCache(request, env, ctx, next) {
  if (request.method !== 'POST') return next();
  let body;
  try {
    body = await request.clone().json();
  } catch (_) {
    return next();
  }
  const lang = String(body.lang || 'id').toLowerCase().startsWith('en') ? 'en' : 'id';
  const reply = INDEX.get(`${lang}|${normalise(String(body.message || ''))}`);
  if (!reply) return next();

  // Same envelope as the live endpoint; the marker makes cache hits visible
  // in the network tab without changing anything clients already read.
  return new Response(
    JSON.stringify({ reply, cached: true, source: 'prepared-answer' }),
    {
      status: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=3600',
        'X-Razi-Cache': 'seed',
      },
    },
  );
}
