#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USUARIO="${SUDO_USER:-$USER}"
HOME_USUARIO="$(getent passwd "$USUARIO" | cut -d: -f6)"
UID_USUARIO="$(id -u "$USUARIO")"
RUNTIME_DIR="/run/user/$UID_USUARIO"
SOCKET="$RUNTIME_DIR/.ydotool_socket"
SERVICE_DIR="$HOME_USUARIO/.config/systemd/user"
ENV_DIR="$HOME_USUARIO/.config/environment.d"
UDEV_RULE="/etc/udev/rules.d/80-uinput-ydotool.rules"
MODULES_FILE="/etc/modules-load.d/uinput.conf"

precisa_sudo() {
  if [[ "$(id -u)" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

echo "==> Configurando ydotool no Bazzite/KDE"

if ! command -v ydotool >/dev/null 2>&1 || ! command -v ydotoold >/dev/null 2>&1; then
  if command -v rpm-ostree >/dev/null 2>&1; then
    echo "ydotool não encontrado. Instalando com rpm-ostree (Bazzite)..."
    precisa_sudo rpm-ostree install --apply-live --allow-inactive ydotool || {
      echo
      echo "Não deu para aplicar ao vivo. Rode de novo depois do reboot:"
      echo "  rpm-ostree install ydotool && systemctl reboot"
      echo "  $ROOT/setup-bazzite.sh"
      exit 1
    }
  else
    echo "Instale o ydotool com o gerenciador da distro e rode este script de novo."
    exit 1
  fi
fi

echo "==> Habilitando módulo uinput"
precisa_sudo tee "$MODULES_FILE" >/dev/null <<'EOF'
uinput
EOF
precisa_sudo modprobe uinput || true

echo "==> Liberando /dev/uinput para o usuário gráfico (KDE/Wayland)"
precisa_sudo tee "$UDEV_RULE" >/dev/null <<'EOF'
KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput", TAG+="uaccess"
EOF
precisa_sudo udevadm control --reload-rules
precisa_sudo udevadm trigger --name-match=uinput || true

if ! id -nG "$USUARIO" | tr ' ' '\n' | grep -qx input; then
  echo "==> Adicionando $USUARIO ao grupo input"
  precisa_sudo usermod -aG input "$USUARIO"
  echo "    Grupo alterado. É preciso sair e entrar de novo na sessão KDE."
fi

echo "==> Serviço systemd do usuário para o ydotoold"
mkdir -p "$SERVICE_DIR" "$ENV_DIR"

cat > "$SERVICE_DIR/ydotoold.service" <<EOF
[Unit]
Description=ydotoold (uinput) para automação no KDE/Wayland
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/ydotoold --socket-path ${SOCKET} --socket-perm 0600
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
EOF

cat > "$ENV_DIR/ydotool.conf" <<EOF
YDOTOOL_SOCKET=${SOCKET}
EOF

chown -R "$USUARIO:$USUARIO" "$HOME_USUARIO/.config/systemd" "$HOME_USUARIO/.config/environment.d"

systemctl_usuario() {
  local dbus="unix:path=$RUNTIME_DIR/bus"
  if [[ "$(id -u)" -eq 0 ]]; then
    sudo -u "$USUARIO" DBUS_SESSION_BUS_ADDRESS="$dbus" XDG_RUNTIME_DIR="$RUNTIME_DIR" \
      systemctl --user "$@"
  else
    systemctl --user "$@"
  fi
}

systemctl_usuario daemon-reload
systemctl_usuario enable --now ydotoold.service

echo "==> Ambiente Python do script"
if [[ ! -d "$ROOT/.venv" ]]; then
  python3 -m venv "$ROOT/.venv"
fi
"$ROOT/.venv/bin/pip" install --upgrade pip
"$ROOT/.venv/bin/pip" install -r "$ROOT/requirements.txt"

chmod +x "$ROOT/run.sh"

echo
echo "Pronto."
echo "  1. Se o grupo input acabou de ser adicionado, saia da sessão KDE e entre de novo."
echo "  2. Abra o jogo em tela cheia 2560x1440, deixe a janela em foco."
echo "  3. Rode: $ROOT/run.sh"
echo
echo "Teste do teclado virtual (deve imprimir ok no terminal em foco):"
echo "  export YDOTOOL_SOCKET=$SOCKET"
echo "  ydotool type ok"
