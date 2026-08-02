#!/bin/bash
# Reglas de firewall para el SERVIDOR PRIVADO.
# Solo debe aceptar tráfico del servidor público (Nginx) y SSH de administración.
# Uso: ./firewall-private.sh <IP_PUBLICA_DEL_SERVIDOR_PUBLICO>
set -euo pipefail

PUBLIC_IP="${1:?Uso: ./firewall-private.sh <IP_PUBLICA_DEL_SERVIDOR_PUBLICO>}"

sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow 22/tcp                                   # SSH de administración
sudo ufw allow from "$PUBLIC_IP" to any port 5001 proto tcp
sudo ufw allow from "$PUBLIC_IP" to any port 5002 proto tcp
sudo ufw allow from "$PUBLIC_IP" to any port 8001 proto tcp
sudo ufw allow from "$PUBLIC_IP" to any port 8002 proto tcp
sudo ufw allow from "$PUBLIC_IP" to any port 8000 proto tcp

sudo ufw --force enable
sudo ufw status verbose

echo ""
echo "Este servidor NO debe exponer 5432 (Postgres) ni 6379 (Redis) a nadie."
echo "Verificar con: nmap -Pn <IP_PRIVADA_DEL_SERVIDOR_PRIVADO> desde el servidor público."
