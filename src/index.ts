// Cloudflare Worker & Static Assets Entry Point
export default {
  async fetch(request: any, env: any) {
    return env.ASSETS.fetch(request);
  }
};
