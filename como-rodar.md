# Como rodar

Bazzite KDE, monitor **2560×1440**, jogo **em janela** (não tela cheia).

## Uma vez

```bash
./setup-bazzite.sh
```

Se o grupo `input` for adicionado, saia e entre de novo no KDE.

## Uso

1. Abra o jogo em janela
2. `./run.sh` — o gabarito vermelho aparece na tela
3. Encaixe a janela no retângulo e o semáforo no círculo
4. Clique no jogo para ele ficar em foco; deixe o gabarito aberto
5. `Ctrl+C` para sair

O recorte do farol vai para `/tmp/semaforo_debug.png`. Se o verde não estiver nele, ajuste a janela no gabarito.
