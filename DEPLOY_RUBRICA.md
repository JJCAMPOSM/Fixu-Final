# Runbook de despliegue — Rúbrica 3er Ciclo (Fixu)

Sigue estos pasos en orden. Tiempo estimado total: 2-3 horas si no tienes cuenta cloud todavía.

## 0. Requisitos previos
- Tarjeta para verificación (DigitalOcean/Hetzner piden una, aunque uses créditos gratis).
- Cliente SSH (Windows: usa el mismo Git Bash/PowerShell que ya tienes).
- Tu teléfono con la app **Expo Go** instalada (Play Store / App Store) para probar rápido, o tiempo extra para generar un APK con `eas build`.

## 1. Crear cuenta y 2 servidores (VPS)
Recomendado: **DigitalOcean** (droplets baratos, red privada fácil) o **Hetzner** (más barato aún). Evita AWS si vas contrarreloj — tiene más pasos de configuración de red (VPC/Security Groups).

1. Crea la cuenta y activa el método de pago.
2. Crea **2 Droplets/Servers** Ubuntu 22.04, tamaño mínimo (2GB RAM recomendado):
   - `fixu-publico` — con IP pública.
   - `fixu-privado` — puede tener IP pública también (la vas a bloquear con firewall), pero lo importante es habilitar **red privada/VPC** entre ambos.
3. En DigitalOcean: al crear ambos droplets en la misma región y con "VPC Network" activado, automáticamente comparten una red privada (`10.x.x.x`). Anota la IP privada de `fixu-privado` (`ip a` dentro del droplet, interfaz `eth1` normalmente).

## 2. Preparar cada servidor
En **ambos** servidores:
```bash
ssh root@<IP>
apt update && apt install -y docker.io docker-compose-plugin git ufw nmap
git clone <URL_DE_TU_REPO> fixu && cd fixu
git checkout borrador-rubrica   # o la rama final una vez mergeado
cp .env.example .env
nano .env   # cambia todas las contraseñas/claves

# ENCRYPTION_KEY necesita un formato específico (Fernet), no puede ser
# cualquier cadena aleatoria como las demás claves. Generarla con:
#   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# y pegar el resultado en .env como ENCRYPTION_KEY=...
```

## 3. Certificado SSL (autofirmado, autorizado por la guía)
En el servidor público:
```bash
mkdir -p deploy/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout deploy/ssl/fixu.key -out deploy/ssl/fixu.crt \
  -subj "/CN=<IP_PUBLICA>"
```

## 4. Levantar el SERVIDOR PRIVADO
```bash
cd fixu
docker compose -f deploy/docker-compose.private.yml up -d --build
docker compose -f deploy/docker-compose.private.yml ps   # todo "Up"
```
Verifica que Flask levantó bien: `curl http://localhost:5001/api/health`

## 5. Levantar el SERVIDOR PÚBLICO
```bash
cd fixu
cp deploy/nginx.public.conf.template deploy/nginx.public.conf
sed -i "s/<IP_PRIVADA>/<IP_PRIVADA_REAL>/g" deploy/nginx.public.conf
cp deploy/prometheus.public.yml deploy/prometheus.public.yml   # ya existe, solo edítalo
sed -i "s/<IP_PRIVADA>/<IP_PRIVADA_REAL>/g" deploy/prometheus.public.yml
docker compose -f deploy/docker-compose.public.yml up -d
```

## 6. Firewalls
En el servidor privado:
```bash
chmod +x deploy/firewall-private.sh
./deploy/firewall-private.sh <IP_PUBLICA_DEL_SERVIDOR_PUBLICO>
```
En el servidor público:
```bash
chmod +x deploy/firewall.sh
./deploy/firewall.sh
```

## 7. Verificación con nmap (lo que el profesor va a correr)
Desde tu máquina local:
```bash
nmap -Pn <IP_PUBLICA>
```
Deben aparecer **solo**: `22, 80, 443, 8080, 8404, 8405`. Si aparece algo más, revisa `ufw status` en ese servidor.

## 8. Probar todo end-to-end
```bash
# Web
curl -I http://<IP_PUBLICA>

# API pública / móvil (a través de Nginx en 8080 -> bridge_api)
curl -X POST http://<IP_PUBLICA>:8080/mobile/login \
  -H "Content-Type: application/json" \
  -d '{"email":"agent@fixu.local","password":"agent123"}'
```
Guarda el `token` que devuelve y crea un ticket de prueba:
```bash
curl -X POST http://<IP_PUBLICA>:8080/mobile/tickets \
  -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" \
  -d '{"title":"Prueba","body":"Ticket de prueba desde curl","priority":"low"}'
```
Confírmalo abriendo `http://<IP_PUBLICA>` (login web) → debe verse el ticket inmediatamente.

## 9. Demostración de Rate Limiting con Redis (429)
```bash
for i in $(seq 1 8); do
  curl -s -o /dev/null -w "Petición $i -> %{http_code}\n" \
    -X POST http://<IP_PUBLICA>:8080/mobile/login \
    -H "Content-Type: application/json" -d '{"email":"x","password":"x"}'
done
```
Las peticiones 7 y 8 deben devolver `429`.

## 10. Ráfaga de tráfico para Grafana (picos)
```bash
for i in $(seq 1 20); do curl -s -o /dev/null http://<IP_PUBLICA> & done; wait
```
Abre `http://<IP_PUBLICA>/grafana/` → agrega Prometheus (`http://prometheus:9090`) como datasource → crea un panel con la métrica `nginx_http_requests_total` (exportada por `nginx_exporter`) y otro con `fixu_http_requests_total` (para ver `allowed` vs `blocked` del rate limiter).

## 11. App móvil en el teléfono físico
Opción rápida (para exposición sin compilar APK):
```bash
cd mobile_app
npm install
cp .env.example .env
# Edita .env -> EXPO_PUBLIC_API_URL=http://<IP_PUBLICA>:8080
npx expo start
```
Escanea el QR con **Expo Go** en el teléfono (debe tener datos móviles o wifi con salida a internet, no necesita estar en la misma red que tu laptop porque ya apunta a la IP pública).

Opción para entregar el teléfono sin depender de tu laptop (APK instalado):
```bash
npm install -g eas-cli
eas login
eas build -p android --profile preview
```
Descarga el APK generado e instálalo directamente en el teléfono.

## 12. Checklist final (imprimir para el evaluador)
- [ ] IP pública: `___________________`
- [ ] URL Web: `http://<IP_PUBLICA>`
- [ ] URL API/Móvil: `http://<IP_PUBLICA>:8080`
- [ ] Grafana: `http://<IP_PUBLICA>/grafana/`
- [ ] Nginx stats: `http://<IP_PUBLICA>:8404/nginx_status`
- [ ] Prometheus: `http://<IP_PUBLICA>:8405`
- [ ] `nmap -Pn <IP_PUBLICA>` → solo 22/80/443/8080/8404/8405
- [ ] Usuario de prueba: `agent@fixu.local` / `agent123`
- [ ] Teléfono físico con la app instalada y funcionando

## Notas importantes / limitaciones honestas
- El asistente (Claude) no tiene acceso a proveedores cloud, a tu teléfono físico ni puede ejecutar `nmap` contra una IP real — todos los pasos de este documento debes ejecutarlos tú.
- Se decidió simplificar el alcance de la app móvil a **foto + formulario validado** (sin GPS ni firma táctil) para cumplir el plazo de 48h, por indicación explícita tuya.
- Prueba **todo en local con `docker compose up --build`** (usando el `docker-compose.yml` de la raíz, pensado para pruebas de un solo servidor) antes de replicar los pasos en los 2 servidores reales — así detectas errores de código sin gastar tiempo de VPS.
