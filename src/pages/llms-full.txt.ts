import type { APIRoute } from 'astro';
import { fullData } from '../lib/textdata';

export const GET: APIRoute = () => new Response(fullData().text, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
