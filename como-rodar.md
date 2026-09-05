# Como rodar

Bot de largada para o Nitto Legends / Happy's V2 no **Bazzite KDE**, em **tela cheia 2560×1440**.

Ele lê o semáforo na tela e envia o `W` pelo `ydotool`. O `ydotool` é programa do sistema, não entra no `pip`.

## Requisitos

- Bazzite com KDE (Wayland)
- Monitor / jogo em tela cheia **2560×1440**
- Jogo aberto e **janela em foco** na hora da largada
- `sudo` na primeira configuração

## Primeira vez

Na pasta do projeto:

```bash
chmod +x setup-bazzite.sh run.sh
./setup-bazzite.sh
```

O setup:

1. Instala o `ydotool` com `rpm-ostree` se ainda não existir
2. Libera `/dev/uinput` (módulo + regra udev)
3. Coloca o usuário no grupo `input`
4. Sobe o `ydotoold` como serviço do usuário
5. Cria o `.venv` e instala o `requirements.txt`

Se o grupo `input` acabou de ser adicionado, **saia da sessão KDE e entre de novo**. Sem isso o daemon não consegue criar o teclado virtual.

Se o `rpm-ostree` pedir reboot:

```bash
rpm-ostree install ydotool
systemctl reboot
./setup-bazzite.sh
```

## Rodar

1. Abra o jogo em tela cheia 2560×1440
2. Deixe a pista / semáforo visível e a janela do jogo em foco
3. No terminal:

```bash
./run.sh
```

Na primeira captura o script grava `/tmp/semaforo_debug.png`. Abra essa imagem e confira se o farol (PRE STAGE / STAGE / amarelos / verde) aparece no recorte. Se estiver cortado ou fora, a região em `main.py` precisa ser recalibrada.

Para parar: `Ctrl+C`.

## Testar o ydotool

Com um editor ou terminal em foco:

```bash
export YDOTOOL_SOCKET="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/.ydotool_socket"
ydotool type ok
```

Tem que aparecer `ok` no campo em foco. Se falhar, o daemon não está no ar ou a sessão ainda não pegou o grupo `input`.

## Problemas comuns

**`ydotoold não está no ar`**

```bash
./setup-bazzite.sh
systemctl --user status ydotoold.service
```

Se o grupo `input` mudou agora, saia e entre de novo no KDE.

**`ydotool não está no PATH`**

Rode o setup de novo. No Bazzite ele costuma já vir na imagem; se não vier, o setup instala com `rpm-ostree`.

**Ambiente Python ainda não foi criado**

```bash
./setup-bazzite.sh
```

**O W não dispara no jogo**

A janela do jogo precisa estar em foco. O `ydotool` manda tecla para o que estiver ativo.

**O verde não é detectado**

Confira `/tmp/semaforo_debug.png`. A calibração assume tela cheia 2560×1440 no monitor principal, origem `(0, 0)`.
