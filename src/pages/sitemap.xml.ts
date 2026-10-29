import type { APIRoute } from 'astro';
import { sitemap } from '../lib/textdata';

export const GET: APIRoute = () => new Response(sitemap(), { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
