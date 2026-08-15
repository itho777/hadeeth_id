// Cloudflare Worker & Static Assets Entry Point
export default {
  async fetch(request, env) {
    return env.ASSETS.fetch(request);
  }
};
