"""
Pódio Heroica v3 — balcão de degustação em forma de pódio (1º = balcão, 2º e 3º = expositores).

Pedido (Roberto, 31/10/2026): conceito A da v4 do balcão de degustação. Tudo em peças retangulares
(serra) com pacote CNC em paralelo; as 3 caixas encaixam uma dentro da outra para transporte.
v2 (02/11): mais leve — compensado 9 mm (era 15) e quinas unidas por cantoneiras de alumínio
por DENTRO (9 mm não segura parafuso na borda). Travessa no alto do fundo da caixa 1. ~25 kg (era 45).
v3 (03/11): frentes e tampos voltam a 15 mm (pancada de carrinho de compras), resto 9 mm. Transporte:
conjunto encaixado de cabeça para baixo num carrinho de plataforma dobrável (comprado).

Rodar:  ESTUDIO_NODE_MODULES=<pasta com three>/node_modules python podio_v3.py [--sem-render]
Depois: python documentos_v3.py
"""
import json
import math
import os
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", ".."))
import biblioteca_heroica as bib  # noqa: E402
from biblioteca_heroica import Painel, poli_ret  # noqa: E402

# ======================================================================
# PARÂMETROS (mm)
# ======================================================================
TF = 15                                 # frentes e tampos: 15 mm (aguentam pancada de carrinho de compras)
T = 9                                   # laterais, fundos, travessas, bordas, prateleira: 9 mm
CANT = (20, 1.5)                        # cantoneira de alumínio 20 × 20 × 1,5 nas quinas, por dentro
DENS_ALU_KG_M = 0.155
FOLGA_NINHO = 10                        # folga de cada lado quando uma caixa entra na outra
W1, D1, H1 = 700, 500, 920              # H = altura até a face de cima do tampo
BEIRAL_F, BEIRAL_L = 40, 15
TRAVESSA_TRAS = 80
Z_PRAT1 = 460
H2, H3 = 620, 420
BORDA = 30
VAO_PODIO = 20
HASTE_D, FURO_HASTE = 25.4, 28.0
SELO_D = 520
Z_SELO = 1900
LED_PERFIL = (17, 8)
DENS = 0.52                             # compensado de pinus
PASSO, PONTA = 150, 40
# carrinho de plataforma dobrável (comprado), p.ex. Vonder 300 kg: plataforma 910 × 610
CARRINHO = (910, 610, 170)              # comprimento × largura × altura do piso (CONFERIR no comprado)

# caixas 2 e 3: dimensionadas para entrar uma na outra (frente 15, fundo/laterais 9)
W1i, D1i = W1 - 2 * T, D1 - TF - T
W2, D2 = W1i - 2 * FOLGA_NINHO, D1i - 2 * FOLGA_NINHO
W3, D3 = W2 - 2 * T - 2 * FOLGA_NINHO, D2 - TF - T - 2 * FOLGA_NINHO

MARROM, MADEIRA, CREME, ROSA, PRETO = "#5E2129", "#C9A06B", "#F4EFE9", "#E3A1B5", "#1b1b1b"
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
NX, NY = (-1, 0, 0), (0, -1, 0)

X1 = 0
X2 = -(W1 / 2 + VAO_PODIO + W2 / 2)
X3 = W1 / 2 + VAO_PODIO + W3 / 2


def furos_linha(p0, p1, d=3):
    (u0, v0), (u1, v1) = p0, p1
    comp = math.hypot(u1 - u0, v1 - v0)
    util = comp - 2 * PONTA
    n = max(2, math.ceil(util / PASSO) + 1)
    return [(round(u0 + (u1 - u0) * (PONTA + util * i / (n - 1)) / comp, 1),
             round(v0 + (v1 - v0) * (PONTA + util * i / (n - 1)) / comp, 1), d) for i in range(n)]


def P(ref, nome, w, h, pos, furos=(), obs="", caixa=0, esp=T):
    p = Painel(ref, nome, poli_ret(0, 0, w, h), esp, pos, furos=furos, obs=obs)
    p.caixa = caixa
    return p


# ======================================================================
# CAIXAS
# ======================================================================
def caixa1(x0=X1, y0=0.0, dz=0.0):
    """Balcão (1º lugar): frente 15 + laterais 9 + 2 travessas de fundo 9 + tampo 15 + prateleira 9."""
    xe = x0 - W1 / 2
    h = H1 - TF
    out = []
    out.append(P("F1", "frente da 1", W1, h, ((xe, y0 + TF, dz), X, Z, NY), obs="15 mm; número 1 + QR",
                 caixa=1, esp=TF))
    pinos = [(60, Z_PRAT1 - T - 8, 5), (D1 - TF - 60, Z_PRAT1 - T - 8, 5)]
    for s in (-1, 1):
        x = x0 + s * W1 / 2
        out.append(P("L1", "lateral da 1", D1 - TF, h, ((x, y0 + TF, dz), Y, Z, X if s < 0 else NX),
                     furos=pinos, obs="2 furos Ø5 (pinos)", caixa=1))
    for zt, onde in ((dz, "embaixo"), (h - TRAVESSA_TRAS + dz, "em cima")):
        out.append(P("S1", "travessa de fundo da 1", W1 - 2 * T, TRAVESSA_TRAS,
                     ((xe + T, y0 + D1, zt), X, Z, NY), obs=f"entre as laterais, {onde}", caixa=1))
    wk, dk = W1 + 2 * BEIRAL_L, D1 + BEIRAL_F
    fk = furos_linha((BEIRAL_L, BEIRAL_F + TF / 2), (wk - BEIRAL_L, BEIRAL_F + TF / 2))
    fk += furos_linha((BEIRAL_L + T, dk - T / 2), (wk - BEIRAL_L - T, dk - T / 2))
    fk += furos_linha((BEIRAL_L + T / 2, BEIRAL_F + TF), (BEIRAL_L + T / 2, dk))
    fk += furos_linha((wk - BEIRAL_L - T / 2, BEIRAL_F + TF), (wk - BEIRAL_L - T / 2, dk))
    fk.append((wk / 2, dk - 90, FURO_HASTE))
    out.append(P("K1", "tampo da 1 (mesa)", wk, dk, ((xe - BEIRAL_L, y0 - BEIRAL_F, h + dz), X, Y, Z), furos=fk,
                 obs="15 mm; madeira; furo Ø28", caixa=1, esp=TF))
    wp, dp = W1 - 2 * T - 4, D1 - TF - T - 10
    out.append(P("P1", "prateleira da 1", wp, dp, ((xe + T + 2, y0 + TF + 2, Z_PRAT1 - T + dz), X, Y, Z),
                 furos=[(wp / 2, D1 - 90 - TF - 2, FURO_HASTE)], obs="removível (pinos)", caixa=1))
    return out


def caixa_fechada(n, W, D, H, x0, y0=0.0, dz=0.0):
    """Caixas 2 e 3: frente 15, fundo e laterais 9, tampo 15 por cima, borda 9 de 3 lados."""
    xe = x0 - W / 2
    h = H - TF
    out = []
    out.append(P(f"F{n}", f"frente da {n}", W, h, ((xe, y0 + TF, dz), X, Z, NY), obs=f"15 mm; número {n}",
                 caixa=n, esp=TF))
    out.append(P(f"T{n}", f"fundo da {n}", W, h, ((xe, y0 + D, dz), X, Z, NY), caixa=n))
    for s in (-1, 1):
        x = x0 + s * W / 2
        out.append(P(f"L{n}", f"lateral da {n}", D - TF - T, h,
                     ((x, y0 + TF, dz), Y, Z, X if s < 0 else NX), caixa=n))
    fk = furos_linha((0, TF / 2), (W, TF / 2)) + furos_linha((0, D - T / 2), (W, D - T / 2))
    fk += furos_linha((T / 2, TF), (T / 2, D - T)) + furos_linha((W - T / 2, TF), (W - T / 2, D - T))
    out.append(P(f"K{n}", f"tampo da {n}", W, D, ((xe, y0, h + dz), X, Y, Z), furos=fk,
                 obs="15 mm; madeira", caixa=n, esp=TF))
    out.append(P(f"B{n}", f"borda frente da {n}", W, BORDA, ((xe, y0 + T, H + dz), X, Z, NY), caixa=n))
    for s in (-1, 1):
        x = x0 + s * W / 2
        out.append(P(f"C{n}", f"borda lado da {n}", D - T, BORDA,
                     ((x, y0 + T, H + dz), Y, Z, X if s < 0 else NX), caixa=n))
    return out


def _cant(x, y, z0, z1, qx, qy):
    a, e = CANT
    pts = [(x + qx * u, y + qy * v) for u, v in [(0, 0), (a, 0), (a, e), (e, e), (e, a), (0, a)]]
    return cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0).translate((0, 0, z0))


def cantoneiras(caixa_n, x0, W, D, H, y0=0.0, dz=0.0):
    h = H - TF
    xi0, xi1 = x0 - W / 2 + T, x0 + W / 2 - T
    yf, yb = y0 + TF, y0 + D - T
    out = [_cant(xi0, yf, dz, h + dz, 1, 1), _cant(xi1, yf, dz, h + dz, -1, 1)]
    if caixa_n == 1:
        for z0 in (dz, h - TRAVESSA_TRAS + dz):
            out += [_cant(xi0, yb, z0, z0 + TRAVESSA_TRAS, 1, -1), _cant(xi1, yb, z0, z0 + TRAVESSA_TRAS, -1, -1)]
    else:
        out += [_cant(xi0, yb, dz, h + dz, 1, -1), _cant(xi1, yb, dz, h + dz, -1, -1)]
    return out


Y2_NINHO = TF + FOLGA_NINHO
Y3_NINHO = Y2_NINHO + TF + FOLGA_NINHO


def cant_montado():
    return (cantoneiras(1, X1, W1, D1, H1) + cantoneiras(2, X2, W2, D2, H2) + cantoneiras(3, X3, W3, D3, H3))


def cant_aninhado():
    return (cantoneiras(1, X1, W1, D1, H1) + cantoneiras(2, X1, W2, D2, H2, y0=Y2_NINHO)
            + cantoneiras(3, X1, W3, D3, H3, y0=Y3_NINHO))


def montado():
    return caixa1() + caixa_fechada(2, W2, D2, H2, X2) + caixa_fechada(3, W3, D3, H3, X3)


def aninhado():
    """Transporte: 3 dentro da 2, 2 dentro da 1 (sem prateleira; haste e selo à parte)."""
    c1 = [p for p in caixa1() if p.ref != "P1"]
    return c1 + caixa_fechada(2, W2, D2, H2, X1, y0=Y2_NINHO) + caixa_fechada(3, W3, D3, H3, X1, y0=Y3_NINHO)


def no_carrinho(solido):
    """Vira o conjunto de cabeça para baixo (tampo da 1 no piso do carrinho) e centraliza na plataforma."""
    cy = (D1 - BEIRAL_F) / 2
    s = solido.rotate((0, cy, H1 / 2), (1, cy, H1 / 2), 180)
    return s.translate((0, -cy, CARRINHO[2]))


def carrinho():
    l, w, z = CARRINHO
    piso = cq.Workplane("XY").box(l, w, 30, centered=(True, True, False)).translate((0, 0, z - 30))
    rodas = [cq.Workplane("XZ").circle(50).extrude(30, both=True).translate((sx * (l / 2 - 80), sy * (w / 2 - 70), 60))
             for sx in (-1, 1) for sy in (-1, 1)]
    cabo = (cq.Workplane("XY").box(30, w - 40, 30).translate((-l / 2 + 15, 0, z + 700))
            .union(cq.Workplane("XY").box(30, 25, 700).translate((-l / 2 + 15, w / 2 - 35, z + 350)))
            .union(cq.Workplane("XY").box(30, 25, 700).translate((-l / 2 + 15, -w / 2 + 35, z + 350))))
    return piso, rodas, cabo


def comprados(dx=0.0):
    h = H1 - TF
    haste = (cq.Workplane("XY").center(X1, D1 - 90).circle(HASTE_D / 2).circle(HASTE_D / 2 - 1.5)
             .extrude(Z_SELO - SELO_D / 2 + 40).translate((0, 0, 0)))
    selo = cq.Workplane("XZ").circle(SELO_D / 2).extrude(-10).translate((X1, D1 - 90 - HASTE_D / 2 - 11, Z_SELO))
    w, hh = LED_PERFIL
    led = cq.Workplane("XY").box(W1 - 40, w, hh).translate((X1, -BEIRAL_F + 4 + w / 2, h - hh / 2))
    return haste, selo, led


# ======================================================================
# VALIDAÇÃO
# ======================================================================
def validar():
    rel = {}
    ps = montado()
    sol = [bib.Peca(f"{p.ref}#{i}", p.solido(), "", "chapa", (), DENS) for i, p in enumerate(ps)]
    for p, s in zip(ps, sol):
        v = bib.validar(s.solido, p.ref, mesa=(2200, 1600, 2200))
        if not (v["valido"] and v["watertight"] is True):
            rel.setdefault("pecas_invalidas", []).append(v)
    haste, selo, led = comprados()
    extra = [bib.Peca("haste", haste, "", "", (), 2.7), bib.Peca("selo", selo, "", "", (), 1.4),
             bib.Peca("led", led, "", "", (), 2.7)]
    cm = [bib.Peca(f"cant{i}", c, "", "", (), 2.7) for i, c in enumerate(cant_montado())]
    rel["interferencias_montado_mm3"] = bib.interferencias(sol + extra + cm)
    ns = aninhado()
    sol_n = [bib.Peca(f"{p.ref}#{i}", p.solido(), "", "chapa", (), DENS) for i, p in enumerate(ns)]
    cn = [bib.Peca(f"cant{i}", c, "", "", (), 2.7) for i, c in enumerate(cant_aninhado())]
    rel["interferencias_aninhado_mm3"] = bib.interferencias(sol_n + cn)
    comp_c = sum(c.val().BoundingBox().zlen for c in cant_montado())
    rel["cantoneiras"] = {"pecas": len(cant_montado()), "metros": round(comp_c / 1000, 2),
                          "kg": round(comp_c / 1000 * DENS_ALU_KG_M, 1)}
    bb = bib.montar(sol + extra).val().BoundingBox()
    rel["montado_mm"] = [round(bb.xlen), round(bb.ylen), round(bb.zmax)]
    bn = bib.montar(sol_n).val().BoundingBox()
    rel["aninhado_mm"] = [round(bn.xlen), round(bn.ylen), round(bn.zlen)]
    peso = {}
    for p, s in zip(ps, sol):
        peso[p.caixa] = peso.get(p.caixa, 0) + s.peso_kg()
    rel["peso_kg"] = {f"caixa {k}": round(v, 1) for k, v in sorted(peso.items())}
    rel["peso_madeira_kg"] = round(sum(peso.values()), 1)
    rel["peso_total_kg"] = round(sum(peso.values()) + rel["cantoneiras"]["kg"] + 1.5, 1)   # + haste/selo/LED
    rel["caixas_mm"] = {"1": [W1, D1, H1], "2": [W2, D2, H2], "3": [W3, D3, H3]}
    rel["area_exposicao_mm"] = {"2": [W2 - 2 * T, D2 - T], "3": [W3 - 2 * T, D3 - T]}
    g = bib.PRODUTOS["granola_300g"]
    rel["granolas_em_pe_por_tampo"] = {"2": int((W2 - 2 * T) // (g[0] + 10)) * int((D2 - T) // (g[2] + 10)),
                                       "3": int((W3 - 2 * T) // (g[0] + 10)) * int((D3 - T) // (g[2] + 10))}
    # transporte no carrinho: conjunto encaixado de cabeça para baixo sobre o piso
    piso, rodas, cabo = carrinho()
    inv = [bib.Peca(p.nome, no_carrinho(p.solido()), "", "", (), DENS) for p in ns]
    inv += [bib.Peca(f"cant{i}", no_carrinho(c), "", "", (), 2.7) for i, c in enumerate(cant_aninhado())]
    rel["carrinho_interferencias_mm3"] = bib.interferencias(inv + [bib.Peca("piso", piso, "", "", (), 1),
                                                                   bib.Peca("cabo", cabo, "", "", (), 1)])
    bc = bib.montar(inv).val().BoundingBox()
    rel["carrinho"] = {"plataforma_mm": list(CARRINHO[:2]), "conjunto_mm": [round(bc.xlen), round(bc.ylen)],
                       "cabe": bc.xlen <= CARRINHO[0] and bc.ylen <= CARRINHO[1],
                       "altura_total_mm": round(bc.zmax), "peso_carga_kg": rel["peso_total_kg"]}
    # maior peso que a promotora levanta de uma vez
    rel["maior_volume_kg"] = max(rel["peso_kg"].values())
    return rel, ps


def lista_de_cortes(ps):
    g = {}
    for p in ps:
        x0, y0, x1, y1 = p.caixa2d()
        w, h = round(x1 - x0), round(y1 - y0)
        k = (p.ref, max(w, h), min(w, h), p.esp)
        if k not in g:
            g[k] = {"ref": p.ref, "nome": p.nome, "comp": max(w, h), "larg": min(w, h), "qtd": 0, "obs": p.obs,
                    "caixa": p.caixa, "esp": p.esp}
        g[k]["qtd"] += 1
    return sorted(g.values(), key=lambda e: (-e["esp"], e["caixa"], -e["comp"] * e["larg"]))


def paineis_cnc(ps):
    por = {}
    for p in ps:
        if p.ref in por:
            por[p.ref].qtd += 1
        else:
            por[p.ref] = Painel(p.ref, p.nome, cq.Workplane("XY").add(p.fio), p.esp, ((0, 0, 0), X, Y, Z),
                                furos=p.furos, qtd=1)
    return list(por.values())


# ======================================================================
# RENDER
# ======================================================================
def cor(p):
    if p.ref.startswith("K") or p.ref.startswith("P"):
        return {"cor": MADEIRA, "rugosidade": 0.6}
    return {"cor": MARROM, "rugosidade": 0.6}


def numeros_e_marca():
    itens = []
    for n, x, h, d in (("1", X1, H1, 0), ("2", X2, H2, 0), ("3", X3, H3, 0)):
        tam = (h - TF) * 0.5
        itens.append((cq.Workplane("XZ").text(n, tam, 1.2, halign="center", valign="center", kind="bold")
                      .translate((x, -0.1, (h - TF) * 0.47)), CREME))
    itens.append((cq.Workplane("XZ").text("CELEBRE SUAS CONQUISTAS", 34, 1.2, halign="center", valign="center",
                                          kind="bold").translate((X1, -0.1, 130)), ROSA))
    for x, w in ((X2, W2), (X3, W3)):   # pacotes na borda das caixas 2 e 3
        pass
    return itens


def granolas_sobre(x0, W, z, y0, n):
    l, a, p = bib.PRODUTOS["granola_300g"]
    out = []
    for i in range(n):
        x = x0 - (n - 1) * (l + 12) / 2 + i * (l + 12)
        out.append((cq.Workplane("XY").box(l, p, a, centered=(True, True, False)).translate((x, y0 + 80, z)),
                    {"cor": CREME}))
        out.append((cq.Workplane("XY").box(l * 0.8, 1.5, a * 0.45).translate((x, y0 + 80 - p / 2 - 0.8, z + a * 0.45)),
                    ROSA))
    return out


def selo_smile():
    _, selo, _ = comprados()
    yf = D1 - 90 - HASTE_D / 2 - 11 - 10 - 0.6
    itens = [(selo, {"cor": ROSA})]
    itens.append((cq.Workplane("XZ").circle(SELO_D / 2 - 15).circle(SELO_D / 2 - 45).extrude(1.2)
                  .translate((X1, yf, Z_SELO)), MARROM))
    for ex in (-75, 75):
        itens.append((cq.Workplane("XZ").center(X1 + ex, Z_SELO + 60).ellipse(24, 44).extrude(1.2)
                      .translate((0, yf, 0)), MARROM))
    s = (cq.Workplane("XZ").moveTo(X1 - 120, Z_SELO - 30).threePointArc((X1, Z_SELO - 150), (X1 + 120, Z_SELO - 30))
         .lineTo(X1 + 104, Z_SELO - 20).threePointArc((X1, Z_SELO - 124), (X1 - 104, Z_SELO - 20)).close()
         .extrude(1.2).translate((0, yf, 0)))
    itens.append((s, MARROM))
    return itens


def render(ps, saida):
    haste, selo, led = comprados()
    itens = [(p.solido(), cor(p)) for p in ps]
    itens += [(haste, {"cor": PRETO, "metal": 0.5})] + selo_smile() + numeros_e_marca()
    itens += granolas_sobre(X2, W2, H2, 0, 3) + granolas_sobre(X3, W3, H3, 0, 3)
    itens.append((led, {"cor": "#FFF0D8", "brilho": 2.2}))
    luzes = []
    for xl in (-220, 0, 220):
        p = (xl, -BEIRAL_F + 12, H1 - TF - 40)
        luzes.append((cq.Workplane("XY").box(1, 1, 1).translate(p), {"cor": "#FFE7C8", "brilho": 0.1, "luz": 1.2,
                                                                        "luz_pos": p}))
    itens += luzes
    vistas = [{"nome": "render_frente", "pos": (-1900, -3900, 1700), "alvo": (0, D1 / 2, 850), "fov": 36},
              {"nome": "render_promotor", "pos": (1800, 3600, 1800), "alvo": (0, D1 / 2, 800), "fov": 36}]
    pngs = bib.renderizar(itens, vistas, os.path.join(saida, "renders"), largura=1100, altura=900)
    noite = [(s, dict(e, luz=700, luz_alcance=800) if isinstance(e, dict) and e.get("luz") else e) for s, e in itens]
    pngs += bib.renderizar(noite, [{"nome": "render_led", "pos": (-1200, -3600, 1300), "alvo": (0, 0, 950),
                                    "fov": 38}], os.path.join(saida, "renders"), largura=1100, altura=900,
                           fundo="#262321", ambiente=0.22)
    # transporte (aninhado), com a caixa 1 meio transparente: mostrar as 3 por corte
    ns = aninhado()
    corte = cq.Workplane("XY").box(3000, 3000, 3000).translate((1500 + X1, 0, 0))   # corta metade (x > 0)
    itens_n = []
    for p in ns:
        s = p.solido()
        if p.caixa in (1, 2):           # corta a 1 e a 2 ao meio para ver as 3 encaixadas
            s = s.cut(corte)
        itens_n.append((s, {"cor": {1: MARROM, 2: ROSA, 3: CREME}[p.caixa], "rugosidade": 0.6}))
    pngs += bib.renderizar(itens_n, [{"nome": "transporte", "pos": (2300, -2700, 1700), "alvo": (0, D1 / 2, 450),
                                      "fov": 32}], os.path.join(saida, "renders"), largura=900, altura=900)
    return pngs


ETAPAS = [
    ("1", "Tirar as caixas", "Ab", None),
    ("2", "Posicionar 2 – 1 – 3", "Pos", None),
    ("3", "Prateleira, haste e selo", "Sel", None),
    ("4", "Produto e LED", "Fim", None),
]


def render_etapas(saida):
    ps = montado()
    haste, _, _ = comprados()
    out = {}
    base = [(p.solido(), {"cor": "#8d8d8d"}) for p in ps if p.ref != "P1"]
    # 1: caixa 1 levantada, 2 e 3 saindo
    c1 = [p for p in caixa1() if p.ref != "P1"]
    i1 = [(p.solido().translate((0, 0, 700)), {"cor": "#8d8d8d"}) for p in c1]
    i1 += [(p.solido(), {"cor": ROSA}) for p in caixa_fechada(2, W2, D2, H2, X1, y0=Y2_NINHO)]
    i1 += [(p.solido().translate((900, 0, 0)), {"cor": ROSA}) for p in
           caixa_fechada(3, W3, D3, H3, X1, y0=Y3_NINHO)]
    i2 = [(p.solido(), {"cor": ROSA if p.caixa != 1 else "#8d8d8d"}) for p in ps if p.ref != "P1"]
    i3 = base + [(p.solido(), {"cor": ROSA}) for p in ps if p.ref == "P1"] + [(haste, {"cor": ROSA})] + \
        [(s, {"cor": ROSA}) for s, _ in selo_smile()[:1]]
    i4 = [(p.solido(), {"cor": "#8d8d8d"}) for p in ps] + [(haste, {"cor": "#8d8d8d"})] + \
        [(s, {"cor": "#8d8d8d"}) for s, _ in selo_smile()[:1]] + \
        [(s, {"cor": ROSA}) for s, _ in granolas_sobre(X2, W2, H2, 0, 3) + granolas_sobre(X3, W3, H3, 0, 3)] + \
        [(comprados()[2], {"cor": ROSA})]
    for eid, itens in (("1", i1), ("2", i2), ("3", i3), ("4", i4)):
        alto = eid in ("1", "3", "4")
        v = {"nome": f"etapa_{eid}", "pos": (-2100, -3300, 2100), "alvo": (0, D1 / 2, 900 if alto else 500),
             "fov": 40 if alto else 34}
        out[eid] = bib.renderizar(itens, [v], os.path.join(saida, "etapas"), largura=800, altura=800)[0]
    return out


def render_carrinho(saida):
    """3 quadros do carregamento: 1 virada no carrinho → +2 → +3 (o que entra no passo fica rosa)."""
    piso, rodas, cabo = carrinho()
    base = [(piso, {"cor": "#3a3a3a"}), (cabo, {"cor": "#3a3a3a", "metal": 0.5})] + \
        [(r, {"cor": "#111111"}) for r in rodas]
    c1 = [p for p in caixa1() if p.ref != "P1"]
    c2 = caixa_fechada(2, W2, D2, H2, X1, y0=Y2_NINHO)
    c3 = caixa_fechada(3, W3, D3, H3, X1, y0=Y3_NINHO)
    out = []
    quadros = [("carregar_1", [(c1, ROSA)]),
               ("carregar_2", [(c1, MARROM), (c2, ROSA)]),
               ("carregar_3", [(c1, MARROM), (c2, MARROM), (c3, ROSA)])]
    for nome, grupos in quadros:
        itens = list(base)
        for grupo, cor_g in grupos:
            for p in grupo:
                sol = no_carrinho(p.solido())
                if grupo is c1 and len(grupos) > 1:
                    sol = sol.cut(cq.Workplane("XY").box(3000, 3000, 3000).translate((1500, 0, 0)))
                if grupo is c2 and len(grupos) > 2:
                    sol = sol.cut(cq.Workplane("XY").box(3000, 3000, 3000).translate((1500, 0, 0)))
                if cor_g == ROSA and len(grupos) > 1:
                    sol = sol.translate((0, 0, 250))           # entrando, ainda acima
                itens.append((sol, {"cor": cor_g, "rugosidade": 0.6}))
        v = {"nome": nome, "pos": (2400, -2600, 2000), "alvo": (0, 0, 650), "fov": 34}
        out += bib.renderizar(itens, [v], os.path.join(saida, "etapas"), largura=800, altura=800)
    return out


if __name__ == "__main__":
    saida = os.path.join(AQUI, "saida")
    os.makedirs(saida, exist_ok=True)
    rel, ps = validar()
    lista = lista_de_cortes(ps)
    # um plano por espessura (chapas diferentes)
    rel["serra_chapas"], rel["serra_plano"], rel["cnc_chapas"], rel["cnc_plano"], rel["cnc_plano_problemas"] = \
        {}, {}, {}, {}, {}
    cnc_todos = paineis_cnc(ps)
    for esp in (TF, T):
        lg = [g for g in lista if g["esp"] == esp]
        serra = bib.plano_de_corte([Painel(g["ref"], g["nome"], poli_ret(0, 0, g["comp"], g["larg"]), esp,
                                           ((0, 0, 0), X, Y, Z), qtd=g["qtd"]) for g in lg],
                                   chapa={"comprimento": 2200, "largura": 1600, "margem": 10, "vao": 5})
        k = str(esp)
        rel["serra_chapas"][k] = len(serra)
        rel["serra_plano"][k] = [[(p.ref, round(x, 1), round(y, 1), bib._angulo(g), round(p.caixa2d()[2]),
                                   round(p.caixa2d()[3])) for p, kk, x, y, g in c] for c in serra]
        cnc = [p for p in cnc_todos if p.esp == esp]
        ch = bib.plano_de_corte(cnc)
        rel["cnc_chapas"][k] = len(ch)
        rel["cnc_plano"][k] = [[(p.ref, round(x, 1), round(y, 1), bib._angulo(g)) for p, kk, x, y, g in c]
                               for c in ch]
        rel["cnc_plano_problemas"][k] = bib.verificar_plano(ch)
        bib.dxf_chapas(ch, os.path.join(saida, "cnc_dxf"), prefixo=f"chapa_{esp}mm")
    cnc = cnc_todos
    with open(os.path.join(saida, "lista_de_cortes.json"), "w") as f:
        json.dump(lista, f, indent=1, ensure_ascii=False)
    with open(os.path.join(saida, "pecas.json"), "w") as f:
        json.dump([{"ref": p.ref, "nome": p.nome, "qtd": p.qtd, "furos": [list(x) for x in p.furos],
                    "contorno": [[round(v.X, 1), round(v.Y, 1)] for v in p.fio.Vertices()]} for p in cnc], f,
                  indent=1, ensure_ascii=False)
    with open(os.path.join(saida, "validacao.json"), "w") as f:
        json.dump(rel, f, indent=1, ensure_ascii=False)
    cq.exporters.export(bib.montar([bib.Peca("x", p.solido(), "", "", (), 0) for p in ps]),
                        os.path.join(saida, "podio_v3.step"))
    print(json.dumps({k: v for k, v in rel.items() if "plano" not in k}, indent=1, ensure_ascii=False))
    for g in lista:
        print(g["ref"], g["nome"], g["qtd"], g["comp"], "x", g["larg"])
    if "--sem-render" not in sys.argv:
        print(render(ps, saida))
        print(render_etapas(saida))
        print(render_carrinho(saida))
