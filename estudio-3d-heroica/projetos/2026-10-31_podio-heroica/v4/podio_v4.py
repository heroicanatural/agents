"""
Pódio Heroica v4 — DESMONTÁVEL E CHATO (flat), sem ferramenta no PDV.

Pedido (Roberto, 09/11/2026): que o pódio desmonte e fique chato. Cada caixa vira 2 peças:
  • CORPO dobrável: frente (15) + 2 laterais (9) em dobradiças fixas; as laterais dobram para dentro.
    Uma lateral dobra por cima da outra (tira de 9 na frente afasta a dobradiça e é o batente dos 90°).
  • TAMPO (15) com 2 tacos na frente + travessa atrás, colados por baixo: encaixam por dentro do corpo e
    travam o esquadro (a lateral não abre além de 90° porque bate na frente/tira).
As 3 caixas ficam abertas atrás (estoque para a promotora). Só cortes retos (serra) + dobradiças compradas.

Rodar:  ESTUDIO_NODE_MODULES=<pasta com three>/node_modules python podio_v4.py [--sem-render]
Depois: python documentos_v4.py
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
TF, T = 15, 9                  # frentes e tampos 15; laterais, tiras, tacos, travessas, bordas, prateleira 9
FOLGA = 2                      # folga taco/travessa × painel
CAIXAS = {                      # largura, profundidade, altura (até a face de cima do tampo), centro x
    1: (700, 500, 920),
    2: (650, 450, 620),
    3: (600, 400, 420),
}
VAO_PODIO = 20
BEIRAL_F, BEIRAL_L = 40, 15    # só no tampo da 1
TACO = (60, 60, 2 * T)         # 2 camadas de 9 coladas
TRAVESSA = 40                  # travessa de trás, colada embaixo do tampo (40 basta p/ travar; empilha melhor)
TIRA = 30                      # tira (9 × 30) colada na frente, borda direita: afasta a 2ª lateral
BORDA = 30                     # borda no tampo da 2 e da 3 (frente + lados)
Z_PRAT1 = 460
HASTE_D, FURO_HASTE = 25.4, 28.0
SELO_D, Z_SELO = 520, 1900
LED_PERFIL = (17, 8)
DOBRADICA = (76, 35, 2)        # dobradiça reta 3" (altura × largura aberta × espessura)
Z_DOBRADICAS = (100, 0.5, -130)   # 100 do pé, no meio, 130 abaixo do topo do corpo
DENS = 0.52
CHAPA_SERRA = {"comprimento": 2200, "largura": 1600, "margem": 10, "vao": 5}

MARROM, MADEIRA, CREME, ROSA, PRETO = "#5E2129", "#C9A06B", "#F4EFE9", "#E3A1B5", "#1b1b1b"
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
NX, NY = (-1, 0, 0), (0, -1, 0)

W1, D1, H1 = CAIXAS[1]
W2, D2, H2 = CAIXAS[2]
W3, D3, H3 = CAIXAS[3]
XC = {1: 0, 2: -(W1 / 2 + VAO_PODIO + W2 / 2), 3: W1 / 2 + VAO_PODIO + W3 / 2}


def P(ref, nome, w, h, pos, esp=T, furos=(), obs="", caixa=0, grupo=""):
    p = Painel(ref, nome, poli_ret(0, 0, w, h), esp, pos, furos=furos, obs=obs)
    p.caixa, p.grupo = caixa, grupo          # grupo: "corpo", "tampo", "solta"
    return p


# ======================================================================
# CORPO (dobrável) e TAMPO (com tacos) de cada caixa
# ======================================================================
def corpo(n, x0=None):
    W, D, H = CAIXAS[n]
    x0 = XC[n] if x0 is None else x0
    xe = x0 - W / 2
    h = H - TF
    out = [P(f"F{n}", f"frente da {n}", W, h, ((xe, TF, 0), X, Z, NY), esp=TF, obs="15 mm",
             caixa=n, grupo="corpo")]
    # tira de 9 na borda direita (por dentro): afasta a lateral direita, que dobra por cima da esquerda
    out.append(P(f"R{n}", f"tira da frente da {n}", TIRA, h, ((x0 + W / 2 - TIRA, TF + T, 0), X, Z, NY),
                 obs="colada; batente da lateral direita", caixa=n, grupo="corpo"))
    pinos = [(60, Z_PRAT1 - T - 8, 5), (D - TF - T - 60 - 10, Z_PRAT1 - T - 8, 5)] if n == 1 else []
    out.append(P(f"L{n}", f"lateral esquerda da {n}", D - TF, h, ((xe, TF, 0), Y, Z, X), furos=pinos,
                 caixa=n, grupo="corpo", obs="dobra primeiro (rente à frente)"))
    pinos_d = [(60 - T, Z_PRAT1 - T - 8, 5), (D - TF - T - 60 - 10 - T, Z_PRAT1 - T - 8, 5)] if n == 1 else []
    out.append(P(f"M{n}", f"lateral direita da {n}", D - TF - T, h, ((x0 + W / 2, TF + T, 0), Y, Z, NX),
                 furos=pinos_d, caixa=n, grupo="corpo", obs="9 mais curta; dobra por cima"))
    return out


def tampo(n, x0=None):
    W, D, H = CAIXAS[n]
    x0 = XC[n] if x0 is None else x0
    xe = x0 - W / 2
    h = H - TF
    out = []
    if n == 1:
        wk, dk = W + 2 * BEIRAL_L, D + BEIRAL_F
        furo = [(wk / 2, dk - 90, FURO_HASTE)]
        out.append(P("K1", "tampo da 1 (mesa)", wk, dk, ((xe - BEIRAL_L, -BEIRAL_F, h), X, Y, Z), esp=TF,
                     furos=furo, obs="15 mm; furo Ø28 da haste", caixa=1, grupo="tampo"))
    else:
        out.append(P(f"K{n}", f"tampo da {n}", W, D, ((xe, 0, h), X, Y, Z), esp=TF, obs="15 mm",
                     caixa=n, grupo="tampo"))
        out.append(P(f"B{n}", f"borda frente da {n}", W, BORDA, ((xe, T, H), X, Z, NY), caixa=n, grupo="tampo"))
        for s in (-1, 1):
            x = x0 + s * W / 2
            out.append(P(f"C{n}", f"borda lado da {n}", D - T, BORDA, ((x, T, H), Y, Z, X if s < 0 else NX),
                         caixa=n, grupo="tampo"))
    # 2 tacos na frente (por dentro das quinas) + travessa atrás, colados embaixo do tampo
    tw, td, th = TACO
    xi0, xi1 = xe + T + FOLGA, x0 + W / 2 - T - FOLGA
    out.append(P(f"A{n}", f"taco do tampo da {n}", tw, td, ((xi0, TF + FOLGA, h - th), X, Y, Z), esp=th,
                 caixa=n, grupo="tampo", obs="2 camadas de 9"))
    out.append(P(f"A{n}", f"taco do tampo da {n}", tw, td, ((xi1 - tw, TF + T + FOLGA, h - th), X, Y, Z), esp=th,
                 caixa=n, grupo="tampo", obs="2 camadas de 9"))
    out.append(P(f"S{n}", f"travessa do tampo da {n}", W - 2 * T - 2 * FOLGA, TRAVESSA,
                 ((xi0, D, h - TRAVESSA), X, Z, NY), caixa=n, grupo="tampo", obs="entre as laterais, atrás"))
    return out


def prateleira():
    W, D, H = CAIXAS[1]
    xe = XC[1] - W / 2
    wp, dp = W - 2 * T - 4, D - TF - T - 30
    return [P("P1", "prateleira da 1", wp, dp, ((xe + T + 2, TF + T + 2, Z_PRAT1 - T), X, Y, Z),
              furos=[(wp / 2 - (XC[1] - XC[1]), D - 90 - TF - T - 2, FURO_HASTE)], caixa=1, grupo="solta",
              obs="removível, sobre 4 pinos")]


def montado():
    return [p for n in (1, 2, 3) for p in corpo(n) + tampo(n)] + prateleira()


# ======================================================================
# Comprados: dobradiças, haste, selo, LED
# ======================================================================
def dobradicas(n, x0=None):
    """3 por lateral, nas quinas de dentro (só para render e interferência)."""
    W, D, H = CAIXAS[n]
    x0 = XC[n] if x0 is None else x0
    h = H - TF
    a, b, e = DOBRADICA
    out = []
    # caixa baixa (< 500 de corpo): 2 dobradiças por lateral; senão 3
    zs = [Z_DOBRADICAS[0], h * Z_DOBRADICAS[1], h + Z_DOBRADICAS[2]] if h >= 500 else [90, h - 90]
    for z in zs:
        # esquerda: aba na frente (face de dentro, y=TF) e aba na lateral (x = xe+T)
        xe = x0 - W / 2
        out.append(cq.Workplane("XY").box(b / 2, e, a).translate((xe + T + b / 4, TF + e / 2, z)))
        out.append(cq.Workplane("XY").box(e, b / 2, a).translate((xe + T + e / 2, TF + e + b / 4 + 0.5, z)))
        # direita: na tira (y = TF+T) e na lateral (x = x0+W/2-T)
        xd = x0 + W / 2 - T
        out.append(cq.Workplane("XY").box(b / 2, e, a).translate((xd - b / 4 - 1, TF + T + e / 2, z)))
        out.append(cq.Workplane("XY").box(e, b / 2, a).translate((xd - e / 2, TF + T + e + b / 4 + 0.5, z)))
    return out


def comprados():
    h = H1 - TF
    haste = (cq.Workplane("XY").center(XC[1], D1 - 90).circle(HASTE_D / 2).circle(HASTE_D / 2 - 1.5)
             .extrude(Z_SELO - SELO_D / 2 + 40))
    selo = cq.Workplane("XZ").circle(SELO_D / 2).extrude(-10).translate((XC[1], D1 - 90 - HASTE_D / 2 - 11, Z_SELO))
    w, hh = LED_PERFIL
    led = cq.Workplane("XY").box(W1 - 40, w, hh).translate((XC[1], -BEIRAL_F + 4 + w / 2, h - hh / 2))
    return haste, selo, led


# ======================================================================
# Estados: dobrado e pilha (desmontado)
# ======================================================================
def corpo_dobrado(n):
    """Corpo da caixa n com as laterais dobradas (esquerda rente à frente, direita por cima)."""
    W, D, H = CAIXAS[n]
    x0 = XC[n]
    xe = x0 - W / 2
    sol = {}
    for p in corpo(n):
        s = p.solido()
        if p.ref == f"L{n}":
            eixo = cq.Vector(xe + T, TF, 0)
            s = s.rotate(eixo, eixo + cq.Vector(0, 0, 1), -90).translate((0, 0.5, 0))
        elif p.ref == f"M{n}":
            eixo = cq.Vector(x0 + W / 2 - T, TF + T, 0)
            s = s.rotate(eixo, eixo + cq.Vector(0, 0, 1), 90).translate((0, 1, 0))
        sol[p.ref] = s
    return sol


def pilha():
    """Desmontado: corpos dobrados deitados (frente para baixo) + tampos + prateleira, empilhados."""
    itens = []
    z = 0.0
    alt = {}
    for n in (1, 2, 3):
        partes = list(corpo_dobrado(n).values())
        un = bib.montar([bib.Peca("x", s, "", "", (), 0) for s in partes])
        # deita: frente no chão (gira −90° em X: y → z)
        un = un.rotate((0, 0, 0), (1, 0, 0), 90)
        bb = un.val().BoundingBox()
        un = un.translate((-bb.center.x, -bb.ymin, z - bb.zmin))
        itens.append((un, {1: MARROM, 2: ROSA, 3: CREME}[n]))
        alt[f"corpo {n}"] = round(bb.zlen)
        z += bb.zlen + 2
    for n in (1, 2, 3):
        partes = [p.solido() for p in tampo(n)]
        un = bib.montar([bib.Peca("x", s, "", "", (), 0) for s in partes])
        un = un.rotate((0, 0, 0), (1, 0, 0), 180)          # tampo de cabeça para baixo: tacos para cima
        bb = un.val().BoundingBox()
        un = un.translate((-bb.center.x, -bb.ymin, z - bb.zmin))
        itens.append((un, MADEIRA))
        alt[f"tampo {n}"] = round(bb.zlen)
        z += bb.zlen + 2
    pr = prateleira()[0].solido()
    bb = pr.val().BoundingBox()
    itens.append((pr.translate((-bb.center.x, -bb.ymin, z - bb.zmin)), MADEIRA))
    z += bb.zlen
    return itens, alt, z


# ======================================================================
# Validação
# ======================================================================
def validar():
    rel = {}
    ps = montado()
    sol = [bib.Peca(f"{p.ref}#{i}", p.solido(), "", "", (), DENS) for i, p in enumerate(ps)]
    for p, s in zip(ps, sol):
        v = bib.validar(s.solido, p.ref, mesa=(2200, 1600, 2200))
        if not (v["valido"] and v["watertight"] is True):
            rel.setdefault("pecas_invalidas", []).append(v)
    haste, selo, led = comprados()
    dob = [bib.Peca(f"dob{n}.{i}", d, "", "", (), 7.8) for n in (1, 2, 3) for i, d in enumerate(dobradicas(n))]
    rel["interferencias_montado_mm3"] = bib.interferencias(
        sol + dob + [bib.Peca("haste", haste, "", "", (), 1), bib.Peca("selo", selo, "", "", (), 1),
                     bib.Peca("led", led, "", "", (), 1)])
    rel["interferencias_dobrado_mm3"] = {}
    rel["corpo_dobrado_mm"] = {}
    for n in (1, 2, 3):
        d = corpo_dobrado(n)
        rel["interferencias_dobrado_mm3"][str(n)] = bib.interferencias(
            [bib.Peca(k, s, "", "", (), 0) for k, s in d.items()])
        bb = bib.montar([bib.Peca(k, s, "", "", (), 0) for k, s in d.items()]).val().BoundingBox()
        rel["corpo_dobrado_mm"][str(n)] = [round(bb.xlen), round(bb.zlen), round(bb.ylen)]
    itens, alt, zt = pilha()
    bb = bib.montar([bib.Peca("x", s, "", "", (), 0) for s, _ in itens]).val().BoundingBox()
    rel["pilha_mm"] = [round(bb.xlen), round(bb.ylen), round(bb.zlen)]
    rel["pilha_alturas_mm"] = alt
    # pesos por peça que a promotora carrega
    pesos = {}
    for p, s in zip(ps, sol):
        k = f"{p.grupo} {p.caixa}" if p.grupo != "solta" else "prateleira"
        pesos[k] = pesos.get(k, 0) + s.peso_kg()
    pesos_dob = {f"corpo {n}": 6 * 0.08 for n in (1, 2, 3)}    # 6 dobradiças ~80 g cada
    for k, v in pesos_dob.items():
        pesos[k] = pesos.get(k, 0) + v
    rel["pesos_kg"] = {k: round(v, 1) for k, v in sorted(pesos.items())}
    rel["maior_peca_kg"] = max(rel["pesos_kg"].values())
    rel["peso_total_kg"] = round(sum(pesos.values()) + 1.5, 1)      # + haste, selo, LED
    bm = bib.montar(sol).val().BoundingBox()
    rel["montado_mm"] = [round(bm.xlen), round(bm.ylen), round(max(bm.zmax, Z_SELO + SELO_D / 2))]
    return rel, ps


def lista_de_cortes(ps):
    g = {}
    for p in ps:
        x0, y0, x1, y1 = p.caixa2d()
        w, h = round(x1 - x0), round(y1 - y0)
        camadas = round(p.esp / T) if p.esp != TF else 1
        esp = TF if p.esp == TF else T
        k = (p.ref, max(w, h), min(w, h), esp)
        if k not in g:
            g[k] = {"ref": p.ref, "nome": p.nome, "comp": max(w, h), "larg": min(w, h), "qtd": 0, "esp": esp,
                    "obs": p.obs, "caixa": p.caixa}
        g[k]["qtd"] += camadas
    return sorted(g.values(), key=lambda e: (-e["esp"], e["caixa"], -e["comp"] * e["larg"]))


# ======================================================================
# Render
# ======================================================================
def cor(p):
    if p.ref[0] in "KP" or p.ref[0] in "AS":
        return {"cor": MADEIRA, "rugosidade": 0.6}
    return {"cor": MARROM, "rugosidade": 0.6}


def selo_smile():
    _, selo, _ = comprados()
    yf = D1 - 90 - HASTE_D / 2 - 11 - 10 - 0.6
    itens = [(selo, {"cor": ROSA})]
    itens.append((cq.Workplane("XZ").circle(SELO_D / 2 - 15).circle(SELO_D / 2 - 45).extrude(1.2)
                  .translate((XC[1], yf, Z_SELO)), MARROM))
    for ex in (-75, 75):
        itens.append((cq.Workplane("XZ").center(XC[1] + ex, Z_SELO + 60).ellipse(24, 44).extrude(1.2)
                      .translate((0, yf, 0)), MARROM))
    s = (cq.Workplane("XZ").moveTo(-120, Z_SELO - 30).threePointArc((0, Z_SELO - 150), (120, Z_SELO - 30))
         .lineTo(104, Z_SELO - 20).threePointArc((0, Z_SELO - 124), (-104, Z_SELO - 20)).close()
         .extrude(1.2).translate((XC[1], yf, 0)))
    return itens + [(s, MARROM)]


def numeros():
    out = []
    for n in (1, 2, 3):
        W, D, H = CAIXAS[n]
        out.append((cq.Workplane("XZ").text(str(n), (H - TF) * 0.5, 1.2, halign="center", valign="center",
                                            kind="bold").translate((XC[n], -0.1, (H - TF) * 0.47)), CREME))
    out.append((cq.Workplane("XZ").text("CELEBRE SUAS CONQUISTAS", 34, 1.2, halign="center", valign="center",
                                        kind="bold").translate((XC[1], -0.1, 130)), ROSA))
    return out


def render(saida):
    ps = montado()
    haste, selo, led = comprados()
    itens = [(p.solido(), cor(p)) for p in ps] + [(haste, {"cor": PRETO})] + selo_smile() + numeros()
    itens.append((led, {"cor": "#FFF0D8", "brilho": 2.2}))
    pngs = bib.renderizar(itens, [
        {"nome": "render_frente", "pos": (-1900, -3900, 1700), "alvo": (0, D1 / 2, 850), "fov": 36},
        {"nome": "render_tras", "pos": (1800, 3600, 1800), "alvo": (0, D1 / 2, 700), "fov": 36}],
        os.path.join(saida, "renders"), largura=1100, altura=900)
    # desmontado (pilha)
    pil, _, zt = pilha()
    pngs += bib.renderizar(pil, [{"nome": "desmontado", "pos": (-1600, -1900, 1500), "alvo": (0, 400, 90),
                                  "fov": 34}], os.path.join(saida, "renders"), largura=1100, altura=850)
    # peças lado a lado (o kit no chão)
    kit = []
    x = -1500
    for n in (1, 2, 3):
        d = corpo_dobrado(n)
        un = bib.montar([bib.Peca(k, s, "", "", (), 0) for k, s in d.items()])
        bb = un.val().BoundingBox()
        kit.append((un.translate((x - bb.xmin, 0, 0)), {1: MARROM, 2: ROSA, 3: CREME}[n]))
        tp = bib.montar([bib.Peca("t", p.solido(), "", "", (), 0) for p in tampo(n)])
        bt = tp.val().BoundingBox()
        kit.append((tp.translate((x - bt.xmin, 900, -bt.zmin)), MADEIRA))
        x += bb.xlen + 250
    pngs += bib.renderizar(kit, [{"nome": "kit", "pos": (-900, -3200, 2600), "alvo": (100, 600, 300),
                                  "fov": 40}], os.path.join(saida, "renders"), largura=1100, altura=850)
    return pngs


def render_etapas(saida):
    """Montagem no PDV: 1 abrir corpo 1 · 2 tampo 1 · 3 prateleira, haste, selo · 4 caixas 2 e 3 · 5 pronto."""
    out = []
    cinza = {"cor": "#8d8d8d"}
    c1 = corpo(1)
    t1 = tampo(1)
    haste, selo, led = comprados()
    d1 = corpo_dobrado(1)
    quadros = []
    # 1: corpo 1 meio aberto (laterais a 45°)
    meio = []
    W, D, H = CAIXAS[1]
    for p in c1:
        s = p.solido()
        if p.ref == "L1":
            e = cq.Vector(-W / 2 + T, TF, 0)
            s = s.rotate(e, e + cq.Vector(0, 0, 1), -45)
        if p.ref == "M1":
            e = cq.Vector(W / 2 - T, TF + T, 0)
            s = s.rotate(e, e + cq.Vector(0, 0, 1), 45)
        meio.append((s, {"cor": ROSA}))
    quadros.append(("etapa_1", meio, 450))
    quadros.append(("etapa_2", [(p.solido(), cinza) for p in c1] +
                    [(p.solido().translate((0, 0, 220)), {"cor": ROSA}) for p in t1], 600))
    q3 = [(p.solido(), cinza) for p in c1 + t1] + [(prateleira()[0].solido(), {"cor": ROSA}),
                                                     (haste, {"cor": ROSA})] + [(selo, {"cor": ROSA})]
    quadros.append(("etapa_3", q3, 950))
    q4 = [(p.solido(), cinza) for p in c1 + t1 + prateleira()] + [(haste, cinza), (selo, cinza)]
    for n in (2, 3):
        q4 += [(p.solido(), {"cor": ROSA}) for p in corpo(n) + tampo(n)]
    quadros.append(("etapa_4", q4, 700))
    for nome, itens, az in quadros:
        pos = (1600, 2800, 1900) if nome == "etapa_1" else (-1800, -3000, 2000)   # 1: de trás, vê as laterais
        v = {"nome": nome, "pos": pos, "alvo": (0, D1 / 2, az), "fov": 38}
        out += bib.renderizar(itens, [v], os.path.join(saida, "etapas"), largura=800, altura=800)
    # dobrar/desdobrar o corpo 1 visto de cima-trás (mostra a lateral por cima da outra)
    dob = [(s, {"cor": ROSA if k.startswith("M") else (MARROM if k.startswith("F") else CREME)})
           for k, s in d1.items()]
    out += bib.renderizar(dob, [{"nome": "corpo_dobrado", "pos": (900, 2400, 1700), "alvo": (0, 0, 450),
                                 "fov": 32}], os.path.join(saida, "etapas"), largura=800, altura=800)
    return out


if __name__ == "__main__":
    saida = os.path.join(AQUI, "saida")
    os.makedirs(saida, exist_ok=True)
    rel, ps = validar()
    lista = lista_de_cortes(ps)
    rel["serra_chapas"], rel["serra_plano"] = {}, {}
    for esp in (TF, T):
        lg = [g for g in lista if g["esp"] == esp]
        ch = bib.plano_de_corte([Painel(g["ref"], g["nome"], poli_ret(0, 0, g["comp"], g["larg"]), esp,
                                        ((0, 0, 0), X, Y, Z), qtd=g["qtd"]) for g in lg], chapa=CHAPA_SERRA)
        rel["serra_chapas"][str(esp)] = len(ch)
        rel["serra_plano"][str(esp)] = [[(p.ref, round(x, 1), round(y, 1), bib._angulo(g), round(p.caixa2d()[2]),
                                          round(p.caixa2d()[3])) for p, k, x, y, g in c] for c in ch]
    # pacote CNC: mesmas peças (tacos em camadas de 9), com os furos (pinos Ø5, haste Ø28)
    por = {}
    for p in ps:
        esp = TF if p.esp == TF else T
        n = 1 if p.esp == TF else round(p.esp / T)
        if p.ref in por:
            por[p.ref].qtd += n
        else:
            por[p.ref] = Painel(p.ref, p.nome, cq.Workplane("XY").add(p.fio), esp, ((0, 0, 0), X, Y, Z),
                                furos=p.furos, qtd=n)
    rel["cnc_chapas"], rel["cnc_plano"], rel["cnc_problemas"] = {}, {}, {}
    for esp in (TF, T):
        ch = bib.plano_de_corte([p for p in por.values() if p.esp == esp])
        rel["cnc_chapas"][str(esp)] = len(ch)
        rel["cnc_plano"][str(esp)] = [[(p.ref, round(x, 1), round(y, 1), bib._angulo(g)) for p, k, x, y, g in c]
                                      for c in ch]
        rel["cnc_problemas"][str(esp)] = bib.verificar_plano(ch)
        bib.dxf_chapas(ch, os.path.join(saida, "cnc_dxf"), prefixo=f"chapa_{esp}mm")
    with open(os.path.join(saida, "pecas.json"), "w") as f:
        json.dump([{"ref": p.ref, "nome": p.nome, "qtd": p.qtd, "furos": [list(x) for x in p.furos],
                    "contorno": [[round(v.X, 1), round(v.Y, 1)] for v in p.fio.Vertices()]} for p in por.values()],
                  f, indent=1, ensure_ascii=False)
    with open(os.path.join(saida, "lista_de_cortes.json"), "w") as f:
        json.dump(lista, f, indent=1, ensure_ascii=False)
    with open(os.path.join(saida, "validacao.json"), "w") as f:
        json.dump(rel, f, indent=1, ensure_ascii=False)
    import csv
    with open(os.path.join(saida, "Podio_v4_lista_de_cortes.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Ref", "Peça", "Qtd", "Comprimento (mm)", "Largura (mm)", "Espessura (mm)", "Material"])
        for g in lista:
            w.writerow([g["ref"], g["nome"], g["qtd"], g["comp"], g["larg"], g["esp"], "compensado de pinus"])
    print(json.dumps({k: v for k, v in rel.items() if "plano" not in k}, indent=1, ensure_ascii=False))
    if "--sem-render" not in sys.argv:
        print(render(saida))
        print(render_etapas(saida))
