// ev-srbija.rs on Cloudflare Workers (static assets in site/).
// Pages keep their .html addresses. This small script only:
//  - serves the homepage at "/" (from index.html),
//  - sends "/index.html" to "/" (one address for the homepage),
//  - shows site/404.html with status 404 for addresses that do not exist.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/index.html') {
      url.pathname = '/';
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname === '/') {
      url.pathname = '/index.html';
      return env.ASSETS.fetch(new Request(url.toString(), request));
    }
    const res = await env.ASSETS.fetch(request);
    if (res.status !== 404) return res;
    const nf = await env.ASSETS.fetch(new Request(new URL('/404.html', url).toString(), request));
    return new Response(nf.body, { status: 404, headers: nf.headers });
  }
};
