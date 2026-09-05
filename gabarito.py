#!/usr/bin/env python3
"""Gabarito vermelho sempre visível para encaixar a janela do jogo."""

from __future__ import annotations

import argparse
import sys

import cv2
import numpy as np

from regioes import (
    ALTURA_TELA,
    JANELA,
    LARGURA_TELA,
    PEDAIS,
    SEMAFORO_CIRCULO,
    TEMPOS,
    VELOCIMETRO,
)

COR_BGR = (0, 0, 255)
ESPESSURA = 2


def desenhar_gabarito(canvas: np.ndarray, escala: float = 1.0) -> np.ndarray:
    def p(valor: int) -> int:
        return int(round(valor * escala))

    janela = (
        (p(JANELA["left"]), p(JANELA["top"])),
        (
            p(JANELA["left"] + JANELA["width"]),
            p(JANELA["top"] + JANELA["height"]),
        ),
    )
    cv2.rectangle(canvas, janela[0], janela[1], COR_BGR, ESPESSURA)

    cx, cy, r = (
        p(SEMAFORO_CIRCULO["cx"]),
        p(SEMAFORO_CIRCULO["cy"]),
        p(SEMAFORO_CIRCULO["r"]),
    )
    cv2.circle(canvas, (cx, cy), r, COR_BGR, ESPESSURA)

    for caixa in (VELOCIMETRO, PEDAIS, TEMPOS):
        cv2.rectangle(
            canvas,
            (p(caixa["left"]), p(caixa["top"])),
            (p(caixa["left"] + caixa["width"]), p(caixa["top"] + caixa["height"])),
            COR_BGR,
            ESPESSURA,
        )
    return canvas


def gerar_preview(caminho_print: str, caminho_saida: str) -> None:
    imagem = cv2.imread(caminho_print)
    if imagem is None:
        raise RuntimeError(f"Não deu para ler {caminho_print}")
    altura, largura = imagem.shape[:2]
    escala = largura / LARGURA_TELA
    desenhar_gabarito(imagem, escala)
    cv2.imwrite(caminho_saida, imagem)


def abrir_overlay() -> None:
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen
    from PySide6.QtWidgets import QApplication, QWidget

    class Overlay(QWidget):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
                | Qt.WindowType.WindowTransparentForInput
                | Qt.WindowType.WindowDoesNotAcceptFocus
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
            tela = QGuiApplication.primaryScreen().geometry()
            self.setGeometry(tela)

        def paintEvent(self, _event) -> None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor(255, 0, 0), ESPESSURA))
            painter.drawRect(
                JANELA["left"],
                JANELA["top"],
                JANELA["width"],
                JANELA["height"],
            )
            painter.drawEllipse(
                QPoint(SEMAFORO_CIRCULO["cx"], SEMAFORO_CIRCULO["cy"]),
                SEMAFORO_CIRCULO["r"],
                SEMAFORO_CIRCULO["r"],
            )
            for caixa in (VELOCIMETRO, PEDAIS, TEMPOS):
                painter.drawRect(
                    caixa["left"],
                    caixa["top"],
                    caixa["width"],
                    caixa["height"],
                )

    app = QApplication(sys.argv)
    overlay = Overlay()
    overlay.show()
    # Evita aviso de variável não usada; a geometria confirma o monitor.
    _ = (LARGURA_TELA, ALTURA_TELA)
    sys.exit(app.exec())


def main() -> None:
    parser = argparse.ArgumentParser(description="Gabarito vermelho do Nitto Legends")
    parser.add_argument("--preview", metavar="PRINT", help="Desenha o gabarito em um print")
    parser.add_argument("--saida", default="/tmp/gabarito_preview.png")
    args = parser.parse_args()

    if args.preview:
        gerar_preview(args.preview, args.saida)
        print(f"Preview salvo em {args.saida}")
        return

    abrir_overlay()


if __name__ == "__main__":
    main()
