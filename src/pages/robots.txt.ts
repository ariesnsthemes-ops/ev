import type { APIRoute } from 'astro';
import { robots } from '../lib/textdata';

export const GET: APIRoute = () => new Response(robots(), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
