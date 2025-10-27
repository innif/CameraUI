#!/usr/bin/env bash
# setup_obs_headless.sh
# Ubuntu Server: Xfce + xrdp + OBS (ppa) + headless systemd Autostart + Template-Config
set -euo pipefail

# ----------------------------- Konfig -----------------------------
OBS_USER="${OBS_USER:-obsuser}"
OBS_PASS="${OBS_PASS:-}"
OBS_XRES="${OBS_XRES:-1920}"
OBS_YRES="${OBS_YRES:-1080}"

# Default-Startflags inkl. deiner Wünsche:
# --multi = mehrere Instanzen erlaubt
# --disable-shutdown-check = keine Crash-Abfrage
# --minimize-to-tray = nicht im Weg
OBS_ARGS_DEFAULT="${OBS_ARGS:---multi --disable-shutdown-check --minimize-to-tray}"

TEMPLATE_DIR="/opt/obs-config-template"
ENV_FILE="/etc/obs-headless/env"
SERVICE_FILE="/etc/systemd/system/obs.service"
WRAPPER="/usr/local/bin/obs-headless-start.sh"
SAVE_TEMPLATE="/usr/local/bin/obs-save-template.sh"

# Zufallspasswort, falls keins gesetzt
rand_pw () { tr -dc 'A-Za-z0-9' </dev/urandom | head -c 16; echo; }
if [[ -z "${OBS_PASS}" ]]; then
  OBS_PASS="$(rand_pw)"
fi

echo "==> Benutzer: ${OBS_USER}"
echo "==> Display (Xvfb): ${OBS_XRES}x${OBS_YRES}"
echo "==> OBS Start-Args: ${OBS_ARGS_DEFAULT}"

# ----------------------------- Pakete -----------------------------
export DEBIAN_FRONTEND=noninteractive
sudo apt update
sudo apt install -y \
  xfce4 xfce4-goodies \
  xrdp xorgxrdp dbus-x11 \
  software-properties-common rsync xvfb \
  ffmpeg libgl1 libxkbcommon-x11-0 libxcb-xinerama0 \
  pulseaudio v4l-utils \
  libpam-modules libpam-modules-bin

# OBS PPA
sudo add-apt-repository -y ppa:obsproject/obs-studio
sudo apt update
sudo apt install -y obs-studio

# xrdp-Rechte
sudo adduser xrdp ssl-cert || true

# ----------------------------- Benutzer -----------------------------
if ! id -u "${OBS_USER}" >/dev/null 2>&1; then
  echo "==> Lege Benutzer ${OBS_USER} an"
  sudo adduser --disabled-password --gecos "" "${OBS_USER}"
fi
echo "${OBS_USER}:${OBS_PASS}" | sudo chpasswd
sudo usermod -aG sudo,video,audio,plugdev "${OBS_USER}" || true

# Xfce als Standard-Session für RDP
echo xfce4-session | sudo tee "/home/${OBS_USER}/.xsession" >/dev/null
sudo chown "${OBS_USER}:${OBS_USER}" "/home/${OBS_USER}/.xsession"

# „Linger“ erlauben (hilft bei user-scoped Diensten/Runtime)
sudo loginctl enable-linger "${OBS_USER}" || true

# ----------------------------- RDP aktivieren -----------------------------
sudo systemctl enable --now xrdp

# Firewall (optional)
if command -v ufw >/dev/null 2>&1; then
  if sudo ufw status | grep -q "Status: active"; then
    sudo ufw allow 3389/tcp || true   # RDP
    sudo ufw allow 4455/tcp || true   # OBS-WebSocket (falls in OBS aktiv)
  fi
fi

# ----------------------------- Template-Ordner -----------------------------
sudo mkdir -p "${TEMPLATE_DIR}"
sudo chown -R "${OBS_USER}:${OBS_USER}" "${TEMPLATE_DIR}"

# ----------------------------- Env-Datei -----------------------------
sudo mkdir -p "$(dirname "${ENV_FILE}")"
sudo bash -c "cat > '${ENV_FILE}'" <<EOF
# /etc/obs-headless/env
OBS_XRES=${OBS_XRES}
OBS_YRES=${OBS_YRES}
OBS_ARGS="${OBS_ARGS_DEFAULT}"
EOF

# ----------------------------- Wrapper (Startlogik) -----------------------------
sudo bash -c "cat > '${WRAPPER}'" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${OBS_XRES:=1920}"
: "${OBS_YRES:=1080}"
: "${OBS_ARGS:=--multi --disable-shutdown-check --minimize-to-tray}"

USER_NAME="${USER_NAME:-$(whoami)}"
USER_UID="$(id -u "${USER_NAME}")"
CFG_HOME="/home/${USER_NAME}/.config"
TEMPLATE_DIR="/opt/obs-config-template"

# Runtime-Verzeichnis für Audio/IPC bereitstellen
export XDG_RUNTIME_DIR="/run/user/${USER_UID}"
mkdir -p "${XDG_RUNTIME_DIR}" || true
chown "${USER_NAME}:${USER_NAME}" "${XDG_RUNTIME_DIR}" || true

# Saubere (goldene) Config einspielen – verhindert blockierende Dialoge
mkdir -p "${CFG_HOME}"
rm -rf "${CFG_HOME}/obs-studio" || true
rsync -a "${TEMPLATE_DIR}/" "${CFG_HOME}/obs-studio/" || true
chown -R "${USER_NAME}:${USER_NAME}" "${CFG_HOME}/obs-studio" || true

# Pulseaudio (falls vorhanden) starten, aber nicht hart verlangen
if command -v pulseaudio >/dev/null 2>&1; then
  pulseaudio --start --log-target=journal || true
fi

# Headless via Xvfb starten
exec /usr/bin/xvfb-run --auto-servernum \
  --server-args="-screen 0 ${OBS_XRES}x${OBS_YRES}x24" \
  /usr/bin/obs ${OBS_ARGS}
EOF
sudo chmod +x "${WRAPPER}"

# ----------------------------- Template speichern (Helper) -----------------------------
sudo bash -c "cat > '${SAVE_TEMPLATE}'" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
USER_NAME="${OBS_USER:-obsuser}"
SRC="/home/${USER_NAME}/.config/obs-studio/"
DST="/opt/obs-config-template/"
if [[ ! -d "${SRC}" ]]; then
  echo "OBS-Config unter ${SRC} nicht gefunden. Starte OBS einmal per RDP, konfiguriere und beende es sauber."
  exit 1
fi
sudo rsync -a --delete "${SRC}" "${DST}"
sudo chown -R "${USER_NAME}:${USER_NAME}" "${DST}"
echo "Template aktualisiert: ${DST}"
EOF
sudo chmod +x "${SAVE_TEMPLATE}"

# ----------------------------- systemd Service -----------------------------
# UID des Users ermitteln für XDG_RUNTIME_DIR
OBS_UID="$(id -u "${OBS_USER}")"

sudo bash -c "cat > '${SERVICE_FILE}'" <<EOF
[Unit]
Description=OBS Studio (headless autostart)
Wants=network-online.target
After=network-online.target systemd-logind.service

[Service]
Type=simple
User=${OBS_USER}

# Session-ähnliche Umgebung (ohne PAMName-Fehler)
Environment=XDG_RUNTIME_DIR=/run/user/${OBS_UID}
Environment=DISPLAY=:99
Environment=QT_X11_NO_MITSHM=1
EnvironmentFile=${ENV_FILE}

# Laufzeitverzeichnis sicherstellen
ExecStartPre=/bin/mkdir -p /run/user/${OBS_UID}
ExecStartPre=/bin/chown ${OBS_USER}:${OBS_USER} /run/user/${OBS_UID}

# Pulseaudio nur starten, wenn vorhanden (nicht fatal)
ExecStartPre=/bin/bash -lc 'command -v pulseaudio >/dev/null 2>&1 && pulseaudio --start --log-target=journal || true'

# Start-Wrapper erledigt: frische Config + XDG_RUNTIME_DIR + Xvfb + OBS
Environment=USER_NAME=${OBS_USER}
ExecStart=${WRAPPER}

Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now obs.service

# ----------------------------- Ausgabe -----------------------------
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo
echo "========================= FERTIG ========================="
echo "RDP:        ${IP:-<SERVER-IP>}:3389"
echo "Benutzer:   ${OBS_USER}"
echo "Passwort:   ${OBS_PASS}"
echo
echo "OBS läuft headless per systemd mit Flags: ${OBS_ARGS_DEFAULT}"
echo
echo "Erstkonfiguration (einmalig):"
echo "  1) Per RDP verbinden, OBS öffnen, Szenen/Quellen + WebSocket einrichten"
echo "  2) OBS sauber beenden"
echo "  3) Template speichern:      sudo ${SAVE_TEMPLATE}"
echo "  4) Dienst neu starten:      sudo systemctl restart obs.service"
echo
echo "Anpassen:"
echo "  - Auflösung/Args:           sudo nano ${ENV_FILE}   (OBS_XRES/OBS_YRES/OBS_ARGS)"
echo "  - Logs ansehen:             journalctl -u obs.service -f"
echo "=========================================================="
