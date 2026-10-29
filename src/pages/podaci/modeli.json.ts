import type { APIRoute } from 'astro';
import { fullData } from '../../lib/textdata';

export const GET: APIRoute = () => new Response(fullData().json, { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
