"""
Tambor Heroica, v0: esboços dos 3 conceitos (baixa resolução, só para escolha).
Medidas do tambor: padrão ISO 15750 de 200 L, a confirmar no tambor real.
Rodar: ESTUDIO_NODE_MODULES=<pasta com three/node_modules> python conceitos_tambor.py
      -> render_A/B/C/*.png e prancha_conceitos.png
"""
import math
import sys
import os

import cadquery as cq
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
import biblioteca_heroica as biblioteca  # noqa: E402

# ------------------------------------------------------------------
# Medidas (mm)
# ------------------------------------------------------------------
diametro_ext = 585        # tambor 200 L (ISO 15750: Ø int 571,5 / ext máx 585)
altura_tambor = 880
chapa = 1.2               # parede do tambor (para o esboço)
aneis_z = (293, 587)      # frisos de rolagem, ~1/3 e 2/3 da altura
abertura_graus = 120      # largura do recorte frontal
abertura_z = (140, 720)   # do fundo ao topo do recorte; acima fica a faixa da marca (160 mm)
prateleiras_z = (140, 430)  # 2 prateleiras: vão livre ~275 mm (granola em pé = 240)
esp_prateleira = 15       # MDF 15

# Cores
MARROM = "#602221"
ROSA = "#E8A0B8"          # aproximado, confirmar no brandbook
BRANCO = "#F4EFE9"
MADEIRA = "#C8A27A"
CINZA = "#9AA3AA"
LED = "#FFE9A8"
PRETO = "#2A2A2A"

R = diametro_ext / 2


def setor(raio, graus, z0, z1, centro=-90):
    """Fatia de pizza (vista de cima) centrada na frente (-Y), entre z0 e z1."""
    a0, a1 = math.radians(centro - graus / 2), math.radians(centro + graus / 2)
    pts = [(0, 0)] + [(raio * math.cos(a), raio * math.sin(a))
                      for a in np.linspace(a0, a1, 24)]
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def casco(recortado=True):
    corpo = cq.Workplane("XY").circle(R).circle(R - chapa).extrude(altura_tambor)
    for z in aneis_z:
        corpo = corpo.union(cq.Workplane("XY").workplane(offset=z - 6)
                            .circle(R + 6).circle(R - chapa).extrude(12))
    if recortado:
        corpo = corpo.cut(setor(R + 20, abertura_graus, *abertura_z))
    return corpo


def interior(cor_raio=R - chapa - 0.5):
    """Pintura interna (só a parte de trás aparece pelo recorte)."""
    return (cq.Workplane("XY").workplane(offset=abertura_z[0])
            .circle(cor_raio).circle(cor_raio - 0.6).extrude(abertura_z[1] - abertura_z[0])
            .cut(setor(R + 20, abertura_graus, *abertura_z)))


def marca_frontal(texto="HEROICA", z=760, altura=70, profundidade=2):
    """Letreiro em arco na faixa acima do recorte (no real: adesivo ou pintura)."""
    letras = [cq.Workplane("XZ").text(ch, altura, profundidade, halign="center",
                                      valign="center", kind="bold") for ch in texto]
    larguras = [l.val().BoundingBox().xlen for l in letras]
    espaco = altura * 0.18
    total = sum(larguras) + espaco * (len(texto) - 1)
    s = -total / 2                      # comprimento de arco acumulado
    solido = None
    for letra, w in zip(letras, larguras):
        ang = math.degrees((s + w / 2) / R)
        letra = letra.translate((0, -R - 0.5, z)).rotate((0, 0, 0), (0, 0, 1), ang)
        solido = letra if solido is None else solido.union(letra)
        s += w + espaco
    return solido


def selo(angulo, z, diametro=200):
    """Selo 'Celebre suas conquistas' tangente ao tambor no ângulo dado."""
    s = cq.Workplane("XZ").circle(diametro / 2).extrude(2).translate((0, -R + 0.5, z))
    return s.rotate((0, 0, 0), (0, 0, 1), angulo + 90)


def disco(raio, z, esp):
    return cq.Workplane("XY").workplane(offset=z).circle(raio).extrude(esp)


def tampo(raio, z, esp, borda=0):
    t = disco(raio, z, esp)
    if borda:
        t = t.union(cq.Workplane("XY").workplane(offset=z + esp)
                    .circle(raio).circle(raio - 12).extrude(borda))
    return t


def barra_led(z):
    """Barra LED magnética sob a prateleira, no fundo do nicho."""
    return cq.Workplane("XY").box(300, 12, 6).translate((0, -40, z - 4))


# ------------------------------------------------------------------
# Conceitos
# ------------------------------------------------------------------
def conceito_a():
    """A. Vitrine essencial: recorte + 2 prateleiras + tampo de madeira."""
    pecas = [(casco(), MARROM), (interior(), ROSA)]
    for z in prateleiras_z:
        pecas.append((disco(R - chapa - 1, z, esp_prateleira), MADEIRA))
    pecas.append((tampo(R + 10, altura_tambor, 18), MADEIRA))
    pecas += [(marca_frontal(), BRANCO), (selo(-178, 470), BRANCO), (selo(-2, 470), BRANCO)]
    pecas += [(barra_led(prateleiras_z[1]), LED), (barra_led(abertura_z[1]), LED)]
    return pecas


def conceito_b():
    """B. Premium/impacto: moldura rosa, fundo espelhado, tampo-bandeja e topper."""
    pecas = [(casco(), MARROM), (interior(), CINZA)]
    # moldura do recorte: faixa rosa de 30 mm contornando a abertura
    moldura = (setor(R + 3, abertura_graus + 8, abertura_z[0] - 30, abertura_z[1] + 30)
               .cut(setor(R + 20, abertura_graus, *abertura_z))
               .cut(cq.Workplane("XY").circle(R - 1).extrude(altura_tambor + 50)))
    pecas.append((moldura, ROSA))
    for z in prateleiras_z:
        pecas.append((disco(R - chapa - 1, z, esp_prateleira), BRANCO))
    pecas.append((tampo(R + 20, altura_tambor, 18, borda=30), ROSA))
    # topper: disco vertical com o smile "Celebre suas conquistas"
    haste = cq.Workplane("XY").box(20, 20, 420).translate((0, 200, altura_tambor + 48 + 210))
    placa = (cq.Workplane("XZ").circle(170).extrude(-8)
             .translate((0, 190, altura_tambor + 48 + 420 + 120)))
    pecas += [(haste, PRETO), (placa, BRANCO), (marca_frontal(), BRANCO),
              (selo(-178, 470), ROSA), (selo(-2, 470), ROSA)]
    pecas += [(barra_led(prateleiras_z[1]), LED), (barra_led(abertura_z[1]), LED)]
    return pecas


def conceito_c():
    """C. Itinerante: recorte vira porta com visor, rodízios, prateleiras removíveis."""
    elev = 70  # altura da base com rodízios
    pecas = []
    for peca, cor in conceito_a()[:-6]:
        pecas.append((peca.translate((0, 0, elev)), cor))
    pecas.append((tampo(R + 10, altura_tambor + elev, 18), MADEIRA))
    # porta: o próprio pedaço recortado, girado 100° na dobradiça lateral esquerda
    porta = (cq.Workplane("XY").workplane(offset=abertura_z[0] + elev)
             .circle(R).circle(R - chapa).extrude(abertura_z[1] - abertura_z[0])
             .intersect(setor(R + 20, abertura_graus, abertura_z[0] + elev, abertura_z[1] + elev)))
    a = math.radians(-90 - abertura_graus / 2)
    eixo = (R * math.cos(a), R * math.sin(a), 0)
    porta = porta.rotate(eixo, (eixo[0], eixo[1], 1), -100)
    pecas.append((porta, MARROM))
    pecas += [(marca_frontal().translate((0, 0, elev)), BRANCO),
              (selo(-2, 470 + elev), BRANCO)]
    # base: anel de metalon com 4 rodízios
    pecas.append((cq.Workplane("XY").workplane(offset=elev - 25).circle(R - 20).circle(R - 45)
                  .extrude(25), PRETO))
    for ang in (45, 135, 225, 315):
        x, y = (R - 60) * math.cos(math.radians(ang)), (R - 60) * math.sin(math.radians(ang))
        pecas.append((cq.Workplane("YZ").circle(22).extrude(20).translate((x - 10, y, 22)), PRETO))
    pecas += [(barra_led(prateleiras_z[1] + elev), LED), (barra_led(abertura_z[1] + elev), LED)]
    return pecas


# ------------------------------------------------------------------
# Produto (granola 300 g, 160 × 240 × 80 mm) para mostrar a função
# ------------------------------------------------------------------
def granolas(z, n=3, y=-20):
    """n pacotes em pé lado a lado (embalagem genérica, só volume)."""
    l, a, p = biblioteca.PRODUTOS["granola_300g"]
    passo = l + 12
    itens = []
    for i in range(n):
        x = (i - (n - 1) / 2) * passo
        pacote = cq.Workplane("XY").box(l, p, a, centered=(True, True, False)).edges("|Z").fillet(12)
        rotulo = cq.Workplane("XY").box(l * 0.8, 2, a * 0.45).translate((0, -p / 2 - 1, a * 0.45))
        itens += [(pacote.translate((x, y, z)), {"cor": "#E9DDCF", "rugosidade": 0.8}),
                  (rotulo.translate((x, y, z)), ROSA)]
    return itens


def com_produto(pecas, elev=0):
    topo = altura_tambor + 18 + elev
    return (pecas + granolas(prateleiras_z[0] + esp_prateleira + elev)
            + granolas(prateleiras_z[1] + esp_prateleira + elev) + granolas(topo, y=0))


def estilos(pecas):
    """Acabamentos: LED emissivo com luz pontual; tambor em pintura semibrilho."""
    saida = []
    for solido, cor in pecas:
        if cor == LED:
            c = solido.val().Center()
            cor = {"cor": LED, "brilho": 1.5, "luz": 0.9, "luz_pos": (c.x, c.y - 30, c.z - 40)}
        elif cor == MARROM:
            cor = {"cor": MARROM, "rugosidade": 0.5, "metal": 0.0}
        saida.append((solido, cor))
    return saida


if __name__ == "__main__":
    from PIL import Image, ImageDraw, ImageFont

    aqui = os.path.dirname(os.path.abspath(__file__))
    vistas = [
        {"nome": "frente", "pos": (0, -3800, 950), "alvo": (0, 0, 680), "fov": 27},
        {"nome": "iso", "pos": (-2400, -2900, 1750), "alvo": (0, 0, 620), "fov": 27},
    ]
    conceitos = [("A", "Vitrine essencial", com_produto(conceito_a())),
                 ("B", "Premium / impacto", com_produto(conceito_b())),
                 ("C", "Itinerante com porta", com_produto(conceito_c(), elev=70))]
    renders = []
    for letra, nome, pecas in conceitos:
        renders.append(biblioteca.renderizar(estilos(pecas), vistas,
                                             os.path.join(aqui, f"render_{letra}"),
                                             largura=700, altura=900))

    # prancha: 3 colunas (conceitos) × 2 linhas (frente, iso)
    w, h, topo_px = 700, 900, 110
    prancha = Image.new("RGB", (w * 3, h * 2 + topo_px), "#f3efe9")
    d = ImageDraw.Draw(prancha)
    try:
        f1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        f2 = ImageFont.truetype("DejaVuSans.ttf", 22)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((30, 18), "Tambor Heroica · v0 · conceitos", fill=MARROM, font=f1)
    d.text((30, 62), "Tambor 200 L Ø585 × 880 mm (padrão ISO, a confirmar) · granola 160 × 240 × 80 mm "
           "· embalagem genérica, só volume", fill="#555", font=f2)
    for i, ((letra, nome, _), (frente, iso)) in enumerate(zip(conceitos, renders)):
        prancha.paste(Image.open(frente), (i * w, topo_px))
        prancha.paste(Image.open(iso), (i * w, topo_px + h))
        d.text((i * w + 24, topo_px + 16), f"{letra} · {nome}", fill=MARROM, font=f1)
    prancha.save(os.path.join(aqui, "prancha_conceitos.png"), optimize=True)
    print("ok prancha")
