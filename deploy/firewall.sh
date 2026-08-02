#!/bin/bash
# Reglas de firewall para el SERVIDOR PÚBLICO (DMZ).
# Ejecutar como root/sudo. Deja abiertos únicamente los 6 puertos
# autorizados por la rúbrica: 22, 80, 443, 8404, 8405, 8080.
set -euo pipefail

sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw allow 8404/tcp   # Nginx stats
sudo ufw allow 8405/tcp   # Prometheus metrics
sudo ufw allow 8080/tcp   # API HTTP / App Móvil

sudo ufw --force enable
sudo ufw status verbose

echo ""
echo "Verificación recomendada antes de la exposición:"
echo "  nmap -Pn <IP_PUBLICA>"
echo "Solo deben aparecer abiertos: 22, 80, 443, 8080, 8404, 8405"
