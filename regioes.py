# Gabarito e leitura para monitor 2560x1440.
# Calibrado no print 1024x576 da área de trabalho (escala 2.5), jogo em janela.

LARGURA_TELA = 2560
ALTURA_TELA = 1440

# Contorno da janela "Nitto Legends (Beta)" — o usuário encaixa a janela aqui.
JANELA = {"left": 680, "top": 103, "width": 1198, "height": 1142}

# Leitura do semáforo (interior do círculo, sem a linha vermelha).
REGIAO_SEMAFORO = {"left": 1225, "top": 388, "width": 125, "height": 275}

# Círculo-guia do semáforo (PRE-STAGE até o vermelho).
SEMAFORO_CIRCULO = {"cx": 1280, "cy": 525, "r": 160}

VELOCIMETRO = {"left": 820, "top": 620, "width": 200, "height": 180}
PEDAIS = {"left": 1175, "top": 675, "width": 225, "height": 100}
TEMPOS = {"left": 1250, "top": 850, "width": 350, "height": 100}

_AREA_CALIB = 90 * 180
_AREA_ATUAL = REGIAO_SEMAFORO["width"] * REGIAO_SEMAFORO["height"]
LIMITE_PIXELS_VERDES = max(120, round(120 * _AREA_ATUAL / _AREA_CALIB))
