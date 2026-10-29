import type { APIRoute } from 'astro';
import { llms } from '../lib/textdata';

export const GET: APIRoute = () => new Response(llms(), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
