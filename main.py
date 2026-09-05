import os
import random
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from mss import mss

from regioes import LIMITE_PIXELS_VERDES, REGIAO_SEMAFORO

print("Iniciando bot de largada para Nitto Legends...")
print("0"*80)
print("""   █████ █████ ████   ███       █████ █   █ ████  █████ ████  ████  ███ █   █  ███
               █  █     █   █ █   █      █     ██ ██ █   █ █     █   █ █   █  █  ██  █ █
              █   ████  ████  █   █ ████ ████  █ █ █ ████  ████  █   █ █   █  █  █ █ █ █  ██
             █    █     █  █  █   █      █     █   █ █   █ █     █   █ █   █  █  █  ██ █   █
            █████ █████ █   █  ███       █████ █   █ ████  █████ ████  ████  ███ █   █  ███""")
print("0"*80)
print("Bot de largada para Nitto Legends")


def ydotool_env() -> dict[str, str]:
    env = os.environ.copy()
    if env.get("YDOTOOL_SOCKET"):
        return env

    runtime = env.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    for caminho in (f"{runtime}/.ydotool_socket", "/tmp/.ydotool_socket"):
        if os.path.exists(caminho):
            env["YDOTOOL_SOCKET"] = caminho
            break
    else:
        env["YDOTOOL_SOCKET"] = f"{runtime}/.ydotool_socket"
    return env


def garantir_ydotool() -> dict[str, str]:
    env = ydotool_env()
    socket = env.get("YDOTOOL_SOCKET", "")
    if not socket or not os.path.exists(socket):
        raise RuntimeError(
            "ydotoold não está no ar. Rode ./setup-bazzite.sh e, se o grupo "
            "input acabou de ser adicionado, saia e entre de novo no KDE."
        )
    return env


def iniciar_gabarito() -> subprocess.Popen:
    script = Path(__file__).resolve().parent / "gabarito.py"
    return subprocess.Popen(
        [sys.executable, str(script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def captura_semaforo(sct: mss) -> np.ndarray:
    frame = np.array(sct.grab(REGIAO_SEMAFORO))
    return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)


def largada_detectada(frame: np.ndarray) -> tuple[bool, int]:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mascara_verde = cv2.inRange(
        hsv,
        np.array([40, 110, 100]),
        np.array([95, 255, 255]),
    )

    pixels_verdes = cv2.countNonZero(mascara_verde)
    return pixels_verdes > LIMITE_PIXELS_VERDES, pixels_verdes


def tempo_reacao() -> tuple[float, bool]:
    sorteio = random.random()

    if sorteio < 0.08:
        return random.uniform(0.130, 0.280), True

    if sorteio < 0.28:
        return random.uniform(0.070, 0.115), False

    return random.uniform(0.038, 0.072), False


def pressionar_w(env: dict[str, str]) -> None:
    hold_s = random.uniform(0.045, 0.085)
    subprocess.run(["ydotool", "key", "17:1"], check=True, env=env)
    time.sleep(hold_s)
    subprocess.run(["ydotool", "key", "17:0"], check=True, env=env)


def executar_largada(pixels_verdes: int, env: dict[str, str]) -> None:
    atraso_s, largada_ruim = tempo_reacao()

    print(
        f"LARGADA DETECTADA ({pixels_verdes} pixels verdes) | "
        f"atraso: {atraso_s * 1000:.0f} ms"
        f"{' | largada ruim' if largada_ruim else ''}"
    )

    time.sleep(atraso_s)
    pressionar_w(env)


def main() -> None:
    env = garantir_ydotool()
    gabarito = iniciar_gabarito()
    print(
        f"Região do semáforo: {REGIAO_SEMAFORO} | "
        f"limiar verde: {LIMITE_PIXELS_VERDES}"
    )
    print(f"ydotool socket: {env['YDOTOOL_SOCKET']}")
    print("Gabarito vermelho aberto. Encaixe a janela do jogo e deixe-o visível.")
    print("Bot iniciado. Ctrl+C para encerrar.")
    print("Aguardando uma corrida nova para armar a detecção...")

    try:
        with mss() as sct:
            verde_anterior = False
            bot_armado = False
            debug_salvo = False

            while True:
                frame = captura_semaforo(sct)

                if not debug_salvo:
                    cv2.imwrite("/tmp/semaforo_debug.png", frame)
                    print(
                        "Recorte do semáforo salvo em /tmp/semaforo_debug.png "
                        "— confira se o farol está na imagem."
                    )
                    debug_salvo = True

                verde_atual, pixels_verdes = largada_detectada(frame)

                if not verde_atual:
                    if not bot_armado:
                        print("Bot armado. Aguardando o verde...")
                    bot_armado = True

                if bot_armado and verde_atual and not verde_anterior:
                    try:
                        executar_largada(pixels_verdes, env)
                    except subprocess.CalledProcessError as erro:
                        print(f"Erro ao enviar W pelo ydotool: {erro}")
                        break

                    bot_armado = False

                verde_anterior = verde_atual
                time.sleep(0.01)
    finally:
        if gabarito.poll() is None:
            gabarito.terminate()
            try:
                gabarito.wait(timeout=2)
            except subprocess.TimeoutExpired:
                gabarito.kill()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    except RuntimeError as erro:
        print(erro)
