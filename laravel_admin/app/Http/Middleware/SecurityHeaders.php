<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

/**
 * Cabeceras de seguridad HTTP para el panel /admin. No incluye CSP porque el
 * dashboard carga Chart.js y fuentes desde CDNs externos (cdn.jsdelivr.net,
 * fonts.googleapis.com) y una política estricta requeriría más pruebas antes
 * de la evaluación; X-Frame-Options/nosniff/Referrer-Policy no tienen ese riesgo.
 */
class SecurityHeaders
{
    public function handle(Request $request, Closure $next): Response
    {
        $response = $next($request);
        $response->headers->set('X-Content-Type-Options', 'nosniff');
        $response->headers->set('X-Frame-Options', 'DENY');
        $response->headers->set('Referrer-Policy', 'strict-origin-when-cross-origin');
        return $response;
    }
}
