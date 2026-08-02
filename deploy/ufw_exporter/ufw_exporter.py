"""Exportador Prometheus para intentos bloqueados por UFW en el servidor público.

Sigue /var/log/ufw.log (montado como solo lectura) y expone contadores de
paquetes bloqueados por protocolo y puerto destino, para que Grafana pueda
graficar y alertar sobre actividad de firewall (no solo tráfico permitido
de nginx).
"""
import re
import time

from prometheus_client import Counter, start_http_server

LOG_PATH = "/var/log/ufw.log"

BLOCKED_TOTAL = Counter(
    "ufw_blocked_total",
    "Paquetes bloqueados por UFW en el servidor público",
    ["proto"],
)
BLOCKED_BY_PORT = Counter(
    "ufw_blocked_by_port_total",
    "Paquetes bloqueados por UFW agrupados por puerto destino",
    ["dpt"],
)

PROTO_RE = re.compile(r"PROTO=(\w+)")
DPT_RE = re.compile(r"DPT=(\d+)")

# Puertos legítimos de la aplicación: no interesa graficarlos individualmente,
# se agrupan en "other" para no inflar la cardinalidad con puertos de escaneo.
KNOWN_PORTS = {"22", "80", "443", "8080", "8404", "8405"}


def follow(path):
    """Sigue un archivo de log como `tail -F` (tolera rotación)."""
    fh = open(path, "r")
    fh.seek(0, 2)  # ir al final, solo nuevas líneas
    while True:
        line = fh.readline()
        if not line:
            time.sleep(1)
            continue
        yield line


def main():
    start_http_server(9092)
    for line in follow(LOG_PATH):
        if "[UFW BLOCK]" not in line:
            continue

        proto_match = PROTO_RE.search(line)
        proto = proto_match.group(1) if proto_match else "OTHER"
        BLOCKED_TOTAL.labels(proto=proto).inc()

        dpt_match = DPT_RE.search(line)
        if dpt_match:
            dpt = dpt_match.group(1)
            BLOCKED_BY_PORT.labels(dpt=dpt if dpt in KNOWN_PORTS else "other").inc()


if __name__ == "__main__":
    main()
