import random
import subprocess
import time

import cv2
import numpy as np
import psutil
from mss import mss

print("Iniciando bot de largada para Nitto Legends...")
print("0"*80)
print("""   █████ █████ ████   ███       █████ █   █ ████  █████ ████  ████  ███ █   █  ███
               █  █     █   █ █   █      █     ██ ██ █   █ █     █   █ █   █  █  ██  █ █
              █   ████  ████  █   █ ████ ████  █ █ █ ████  ████  █   █ █   █  █  █ █ █ █  ██
             █    █     █  █  █   █      █     █   █ █   █ █     █   █ █   █  █  █  ██ █   █
            █████ █████ █   █  ███       █████ █   █ ████  █████ ████  ████  ███ █   █  ███""")
print("0"*80)
print("Bot de largada para Nitto Legends")

REGIAO_SEMAFORO = {
    "left": 320,
    "top": 100,
    "width": 90,
    "height": 180,
}

LIMITE_PIXELS_VERDES = 120


def jogo_aberto() -> bool:
    return any(
        "nittolegendscli" in (processo.info["name"] or "").lower()
        for processo in psutil.process_iter(["name"])
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
    # 90%: largada ótima.
    atraso_s = random.uniform(0.005, 0.030)
    largada_ruim = False

    # 10%: reação mais lenta.
    if random.random() < 0.10:
        atraso_s = random.uniform(0.080, 0.300)
        largada_ruim = True

    return atraso_s, largada_ruim


def pressionar_w() -> None:
    subprocess.run(
        ["ydotool", "key", "17:1", "17:0"],
        check=True,
    )


def executar_largada(pixels_verdes: int) -> None:
    atraso_s, largada_ruim = tempo_reacao()

    print(
        f"LARGADA DETECTADA ({pixels_verdes} pixels verdes) | "
        f"atraso: {atraso_s * 1000:.0f} ms"
        f"{' | largada ruim' if largada_ruim else ''}"
    )

    time.sleep(atraso_s)
    pressionar_w()


def main() -> None:
    print("Bot iniciado. Aguardando Nitto Legends...")
    print("Aguardando uma corrida nova para armar a detecção...")

    if not jogo_aberto():
        print("Nitto Legends não está aberto. Encerrando.")
        return

    with mss() as sct:
        verde_anterior = False
        bot_armado = False

        while jogo_aberto():
            frame = captura_semaforo(sct)
            verde_atual, pixels_verdes = largada_detectada(frame)

            if not verde_atual:
                if not bot_armado:
                    print("Bot armado. Aguardando o verde...")
                bot_armado = True

            if bot_armado and verde_atual and not verde_anterior:
                try:
                    executar_largada(pixels_verdes)
                except subprocess.CalledProcessError as erro:
                    print(f"Erro ao enviar W pelo ydotool: {erro}")
                    break

                bot_armado = False

            verde_anterior = verde_atual
            time.sleep(0.01)

    print("Jogo fechado ou bot encerrado.")


if __name__ == "__main__":
    main()