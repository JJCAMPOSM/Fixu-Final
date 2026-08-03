<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Symfony\Component\HttpFoundation\Response;

/**
 * Protege el panel /admin: sin esto, cualquiera con la URL entraba sin
 * autenticarse. El acceso solo se concede si Flask entrega un token firmado
 * (HMAC compartido) tras validar login+rol admin, o si ya existe una sesión
 * de Laravel previamente establecida por ese mismo mecanismo.
 */
class EnsureAdminAccess
{
    public function handle(Request $request, Closure $next): Response
    {
        if ($request->session()->get('admin_authenticated')) {
            return $this->noStore($next($request));
        }

        $token = $request->query('admin_token');
        if ($token && $this->isValidAdminToken($token)) {
            $request->session()->put('admin_authenticated', true);
            $request->session()->regenerate();
            // Redirigir sin el token en la URL (no debe quedar en historial/logs)
            return redirect($request->url());
        }

        return redirect('/auth/login');
    }

    private function isValidAdminToken(string $token): bool
    {
        $parts = explode('.', $token, 2);
        if (count($parts) !== 2) {
            return false;
        }
        [$payloadB64, $signature] = $parts;

        $secret = env('HMAC_SECRET_KEY');
        if (!$secret) {
            // Sin secreto compartido no hay forma de validar el handoff:
            // fallar cerrado en vez de aceptar un valor público conocido.
            return false;
        }
        $expected = hash_hmac('sha256', $payloadB64, $secret);
        if (!hash_equals($expected, $signature)) {
            return false;
        }

        $normalized = strtr($payloadB64, '-_', '+/');
        $normalized .= str_repeat('=', (4 - strlen($normalized) % 4) % 4);
        $payloadJson = base64_decode($normalized);
        $payload = json_decode($payloadJson, true);
        if (!is_array($payload)) {
            return false;
        }

        if (($payload['role'] ?? null) !== 'admin') {
            return false;
        }

        if (!isset($payload['exp']) || time() > (int) $payload['exp']) {
            return false;
        }

        // Nonce de un solo uso: si ya se consumió (ej. la URL quedó en logs
        // de nginx/proxy y alguien más la reutiliza dentro de la ventana de
        // 60s), rechazar el segundo intento.
        $nonce = $payload['nonce'] ?? null;
        if (!$nonce) {
            return false;
        }
        $cacheKey = 'admin_handoff_nonce:' . $nonce;
        if (Cache::has($cacheKey)) {
            return false;
        }
        Cache::put($cacheKey, true, 65);

        return true;
    }

    private function noStore(Response $response): Response
    {
        $response->headers->set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
        $response->headers->set('Pragma', 'no-cache');
        return $response;
    }
}
