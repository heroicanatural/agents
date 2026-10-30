"""
Balcão de degustação — v4: 3 conceitos "fora do óbvio" (esboço de volume, baixa resolução).
A · Pódio Heroica   B · Pouch gigante   C · Bar de granola (dispensers)
Rodar: ESTUDIO_NODE_MODULES=<...>/node_modules python conceitos_v4.py  → prancha_v4.png
"""
import os
import sys

import cadquery as cq
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", ".."))
import biblioteca_heroica as bib  # noqa: E402

MARROM, ROSA, CREME, MADEIRA, PRETO = "#5E2129", "#E3A1B5", "#F4EFE9", "#C9A06B", "#1b1b1b"


def caixa(w, d, h, x=0, y=0, z=0):
    return cq.Workplane("XY").box(w, d, h, centered=(True, True, False)).translate((x, y, z))


def texto(t, h, x, y, z, plano="XZ"):
    return cq.Workplane(plano).text(t, h, 1.5, halign="center", valign="center", kind="bold").translate((x, y, z))


def produtos(x0, z, n=4, y=0):
    """Pacotes de granola (160 × 80 × 240) em fila."""
    out = []
    for i in range(n):
        x = x0 + i * 175
        out.append((caixa(160, 80, 240, x, y, z), {"cor": CREME}))
        out.append((caixa(130, 2, 110, x, y - 41, z + 70), ROSA))
    return out


def podio():
    itens = []
    # 1º no centro (balcão de degustação, mesa a 920), 2º à esquerda, 3º à direita: as caixas se encaixam
    # uma dentro da outra para transporte (1 > 2 > 3)
    for x, w, d, h, n in ((0, 640, 460, 920, "1"), (-660, 600, 420, 620, "2"), (640, 560, 380, 420, "3")):
        itens.append((caixa(w, d, h, x, 0, 0), {"cor": MARROM, "rugosidade": 0.6}))
        itens.append((caixa(w + 30, d + 30, 18, x, 0, h), {"cor": MADEIRA}))
        itens.append((texto(n, h * 0.45, x, -d / 2 - 0.5, h * 0.48), CREME))
    itens += produtos(-660 - 260, 638, 4) + produtos(640 - 260, 438, 4)
    # topper: smile "Celebre suas conquistas" (disco) sobre haste
    itens.append((cq.Workplane("XY").circle(12).extrude(900).translate((0, 150, 938)), PRETO))
    itens.append((cq.Workplane("XZ").circle(260).extrude(-15).translate((0, 140, 1900)), {"cor": CREME}))
    itens.append((cq.Workplane("XZ").circle(240).circle(200).extrude(2).translate((0, 124, 1900)), MARROM))
    for ex in (-70, 70):                                                # olhos
        itens.append((cq.Workplane("XZ").center(ex, 1960).ellipse(22, 40).extrude(2).translate((0, 124, 0)), MARROM))
    sorriso = (cq.Workplane("XZ").moveTo(-110, 1870).threePointArc((0, 1760), (110, 1870))
               .lineTo(95, 1880).threePointArc((0, 1785), (-95, 1880)).close().extrude(2).translate((0, 124, 0)))
    itens.append((sorriso, MARROM))
    return itens


def pouch():
    itens = []
    # silhueta da embalagem stand-up, 2 m, em 2 partes (corte CNC), atrás de um balcão baixo
    w, h = 900, 1950
    perfil = (cq.Workplane("XZ").moveTo(-w / 2, 0).lineTo(w / 2, 0).lineTo(w / 2, h - 120)
              .threePointArc((w / 2 - 35, h - 35), (w / 2 - 120, h)).lineTo(-w / 2 + 120, h)
              .threePointArc((-w / 2 + 35, h - 35), (-w / 2, h - 120)).close().extrude(-18).translate((0, 200, 0)))
    itens.append((perfil, {"cor": ROSA, "rugosidade": 0.5}))
    itens.append((caixa(w - 60, 2, 14, 0, 181, h - 170), MARROM))          # zip
    itens.append((caixa(w - 160, 2, 520, 0, 181, 1150), {"cor": CREME}))  # janela/rótulo
    itens.append((texto("HEROICA", 120, 0, 180, 1500), MARROM))
    itens.append((texto("CLUSTER", 70, 0, 180, 1150), MARROM))
    # balcão de degustação na frente (mesa 920) em madeira
    itens.append((caixa(820, 380, 902, 0, -40, 0), {"cor": MARROM}))
    itens.append((caixa(860, 420, 18, 0, -40, 902), {"cor": MADEIRA}))
    itens += [(caixa(70, 70, 60, x, -60, 920), {"cor": CREME}) for x in (-200, -80, 40, 160)]  # copinhos
    return itens


def bar():
    itens = []
    # balcão v3 + painel ripado alto com 3 dispensers de granola (Clássica, Cluster, Keto)
    itens.append((caixa(840, 420, 902, 0, 0, 0), {"cor": PRETO}))
    itens.append((caixa(880, 460, 18, 0, 0, 902), {"cor": MADEIRA}))
    itens.append((caixa(840, 24, 1000, 0, 180, 920), {"cor": PRETO}))      # painel de fundo
    for i, x in enumerate((-260, 0, 260)):
        # tubo transparente: só os aros aparecem; a granola é o que se vê
        for zc in (1250, 1755):
            itens.append((cq.Workplane("XY").circle(97).circle(90).extrude(15).translate((x, 70, zc)),
                          {"cor": "#cfd8dc", "metal": 0.5}))
        itens.append((cq.Workplane("XY").circle(90).extrude(400).translate((x, 70, 1265)),
                      {"cor": ("#C98A4B", "#7A4A24", "#E3CF98")[i], "rugosidade": 0.95}))
        itens.append((caixa(60, 60, 200, x, 70, 1050), {"cor": "#888888", "metal": 0.6}))  # alavanca/bico
        itens.append((caixa(200, 4, 60, x, 168, 1810), ROSA))
    itens.append((texto("MONTE SEU POTINHO", 70, 0, 166, 1880), CREME))
    itens += [(cq.Workplane("XY").circle(40).extrude(70).translate((x, -120, 920)), {"cor": CREME})
              for x in (-300, -200, 200, 300)]
    itens.append((caixa(560, 2, 260, 0, -211, 450), ROSA))
    itens.append((texto("HEROICA", 100, 0, -212, 450), MARROM))
    return itens


if __name__ == "__main__":
    saida = os.path.join(AQUI, "renders")
    conceitos = [("A", "Pódio Heroica", podio()), ("B", "Pouch gigante", pouch()), ("C", "Bar de granola", bar())]
    pngs = []
    for letra, nome, itens in conceitos:
        alvo_x = -100 if letra == "A" else 0
        v = {"nome": f"conceito_{letra}", "pos": (-2600, -4300, 2000), "alvo": (alvo_x, 0, 950), "fov": 36}
        pngs.append(bib.renderizar(itens, [v], saida, largura=900, altura=1000)[0])
    w, h, top = 900, 1000, 110
    prancha = Image.new("RGB", (w * 3, h + top), "#f3efe9")
    d = ImageDraw.Draw(prancha)
    f1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
    f2 = ImageFont.truetype("DejaVuSans.ttf", 22)
    d.text((30, 18), "Balcão de degustação · v4 · 3 conceitos fora do óbvio", fill=MARROM, font=f1)
    d.text((30, 64), "esboço de volume, sem acabamento · produto: granola 300 g (160 × 240 × 80)", fill="#555", font=f2)
    for i, ((letra, nome, _), p) in enumerate(zip(conceitos, pngs)):
        prancha.paste(Image.open(p), (i * w, top))
        d.text((i * w + 24, top + 14), f"{letra} · {nome}", fill=MARROM, font=f1)
    prancha.save(os.path.join(AQUI, "prancha_v4.png"), optimize=True)
    print("ok")
