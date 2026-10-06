"""
Box Run Club Heroica v1 — caixa de compensado naval sobre carrinho-plataforma (comprado pronto).

Referência: carrinho de DJ do run club do Lumin (vídeo enviado pelo Roberto em 06/10/2026).
A caixa é só marcenaria: 7 tipos de peça em compensado naval 15 mm, cortados em CNC
a partir dos DXF, montados com cola PU e parafusos nos furos-guia que a própria CNC fura.

Rodar:
    ESTUDIO_NODE_MODULES=<pasta com three>/node_modules python box_v1.py
Gera em ./saida: DXF por chapa, STEP, renders das etapas, validação e lista de peças.
Depois: python documentos_v1.py  (PDF da fábrica + guia de montagem)
"""
import json
import math
import os
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", ".."))
import biblioteca_heroica as bib  # noqa: E402
from biblioteca_heroica import Painel  # noqa: E402

# ======================================================================
# PARÂMETROS (mm)
# ======================================================================
# Carrinho-plataforma (comprado). CONFIRMAR COM TRENA antes de mandar cortar.
PLAT_L, PLAT_W, PLAT_Z = 1200, 600, 450   # comprimento, largura, altura do chão ao topo
FOLGA_PLAT = 5                             # recuo da caixa em cada borda da plataforma

T = 15                                     # compensado naval 15 mm (todas as peças)
L = PLAT_L - 2 * FOLGA_PLAT                # 1190 comprimento da caixa
W = PLAT_W - 2 * FOLGA_PLAT - 10           # 580 largura (cabe 2 chapas; ver plano de corte)
WI = W - 2 * T                             # 550 largura interna

Z0 = PLAT_Z                                # fundo da caixa apoiado na plataforma
Z_TAMPO = 1000                             # topo do tampo de trabalho, do chão
ABA_TRAS = 40                              # lateral sobe 40 acima do tampo no lado do DJ
Z_FACHADA = 1250                           # topo da fachada (lado oposto ao cabo do carrinho)

# porta de acesso no painel do DJ (sai do próprio painel: o corte da CNC vira a folga)
PORTA_MARGEM_LADO = 70
PORTA_BASE = 70                            # do pé do painel
PORTA_TOPO = 60                            # abaixo do topo do painel
BATENTE_LARG, BATENTE_SOBRE = 40, 15       # largura do batente e quanto invade o vão

PASSO_PARAFUSO = 150                       # furos-guia a cada ~150
PONTA_PARAFUSO = 40                        # primeiro furo a 40 da quina
D_GUIA = 3                                 # furo-guia (CNC); abrir 4,5 + escarear na montagem

# equipamento de referência (só para conferir espaço)
DJ_CONTROLADORA = (482, 273, 60)           # Pioneer DDJ-FLX4 (L × P × A)
CAIXA_SOM = (688, 368, 326)                # JBL PartyBox 310 deitada

DENS_COMPENSADO = 0.70                     # g/cm³ (chapa 2200×1600×15 ≈ 37 kg)

# cores (render)
MARROM, ROSA, NATURAL, PRETO, LED = "#5E2129", "#E3A1B5", "#D9B98C", "#2b2b2b", "#FFE9A8"

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
NX, NY = (-1, 0, 0), (0, -1, 0)


# ======================================================================
# Utilitários de geometria 2D
# ======================================================================
def poli(pts):
    return cq.Workplane("XY").polyline(pts).close()


def ret(u0, v0, u1, v1):
    return poli([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])


def linha_furos(p0, p1, d=D_GUIA):
    """Furos-guia ao longo de uma linha, ~PASSO_PARAFUSO, começando a PONTA_PARAFUSO das pontas."""
    (u0, v0), (u1, v1) = p0, p1
    comp = math.hypot(u1 - u0, v1 - v0)
    util = comp - 2 * PONTA_PARAFUSO
    n = max(2, math.ceil(util / PASSO_PARAFUSO) + 1)
    out = []
    for i in range(n):
        t = (PONTA_PARAFUSO + util * i / (n - 1)) / comp
        out.append((round(u0 + (u1 - u0) * t, 1), round(v0 + (v1 - v0) * t, 1), d))
    return out


def z_topo_lateral(x):
    """Altura do topo da lateral na posição x (reta do lado do DJ até a fachada)."""
    return (Z_TAMPO + ABA_TRAS) + (Z_FACHADA - Z_TAMPO - ABA_TRAS) * x / L


# ======================================================================
# PEÇAS
# Coordenadas globais: x = comprimento (0 = lado do cabo/DJ, L = fachada),
# y = largura (centro em 0), z = altura do chão.
# ======================================================================
def lateral(lado):
    """L1/L2: lateral trapezoidal. u = x, v = z (do chão)."""
    ztop0, ztopL = Z_TAMPO + ABA_TRAS, Z_FACHADA
    contorno = poli([(0, Z0), (L, Z0), (L, ztopL), (0, ztop0)])
    furos = []
    furos += linha_furos((T, Z0 + T / 2), (L - T, Z0 + T / 2))                 # fundo
    furos += linha_furos((0, Z_TAMPO - T / 2), (L - T, Z_TAMPO - T / 2))       # tampo
    furos += linha_furos((T / 2, Z0), (T / 2, Z_TAMPO - T))                    # painel do DJ
    furos += linha_furos((L - T / 2, Z0), (L - T / 2, Z_FACHADA))              # fachada
    # furos para gancho de elástico (prende o equipamento), na aba acima do tampo
    for x in (260, 700):
        furos.append((x, Z_TAMPO + 22, 12))
    y_face = W / 2 if lado == "esq" else -W / 2
    # espessura para dentro da caixa (−y na esquerda, +y na direita)
    ew = NY if lado == "esq" else Y
    pos = ((0, y_face, 0), X, Z, ew)
    return Painel("L", "lateral", contorno, T, pos, furos=furos,
                  obs="2 furos Ø12 na aba (elástico)")


def fachada():
    """F: painel alto da fachada (lado oposto ao cabo). u = y (−WI/2..WI/2), v = z."""
    contorno = ret(-WI / 2, Z0, WI / 2, Z_FACHADA)
    furos = linha_furos((-WI / 2, Z0 + T / 2), (WI / 2, Z0 + T / 2))            # fundo
    furos += linha_furos((-WI / 2, Z_TAMPO - T / 2), (WI / 2, Z_TAMPO - T / 2))  # tampo
    pos = ((L, 0, 0), NY, Z, NX)   # face externa em x = L, olhando para +x
    return Painel("F", "fachada", contorno, T, pos, furos=furos,
                  obs="área principal de marca (550 × 800)")


def painel_dj():
    """D: painel do lado do DJ, com a porta. u = y, v = z (do pé à base do tampo)."""
    v0, v1 = Z0, Z_TAMPO - T
    u0, u1 = -WI / 2 + PORTA_MARGEM_LADO, WI / 2 - PORTA_MARGEM_LADO
    pv0, pv1 = v0 + PORTA_BASE, v1 - PORTA_TOPO
    contorno = ret(-WI / 2, v0, WI / 2, v1)
    porta = ret(u0, pv0, u1, pv1)
    furos = linha_furos((-WI / 2, v0 + T / 2), (WI / 2, v0 + T / 2))            # fundo
    furos.append((WI / 2 - 30, v1 - 25, 8))                                     # cabo da fita LED
    pos = ((0, 0, 0), Y, Z, X)     # face externa em x = 0
    return Painel("D", "painel do DJ (com porta)", contorno, T, pos, recortes=[porta], furos=furos,
                  obs="recorte central = porta P (guardar)")


def fundo():
    """B: fundo. u = x (T..L−T), v = y."""
    contorno = ret(T, -WI / 2, L - T, WI / 2)
    furos = []
    for x in (T + 120, L - T - 120):               # fixação no carrinho (M8)
        for y in (-WI / 2 + 90, WI / 2 - 90):
            furos.append((x, y, 9))
    for x in (T + 40, L - T - 40):                 # dreno
        for y in (-WI / 2 + 40, WI / 2 - 40):
            furos.append((x, y, 10))
    pos = ((0, 0, Z0), X, Y, Z)
    return Painel("B", "fundo", contorno, T, pos, furos=furos,
                  obs="4 furos Ø9 = gabarito p/ furar carrinho")


def tampo():
    """K: tampo de trabalho. u = x (0..L−T), v = y."""
    contorno = ret(0, -WI / 2, L - T, WI / 2)
    furos = linha_furos((T / 2, -WI / 2), (T / 2, WI / 2))                      # painel do DJ
    furos.append((110, WI / 2 - 90, 60))                                        # passa-cabo
    pos = ((0, 0, Z_TAMPO - T), X, Y, Z)
    return Painel("K", "tampo de trabalho", contorno, T, pos, furos=furos,
                  obs="passa-fio Ø60 no canto do DJ")


def batentes(pdj):
    """S1 (cima/baixo) e S2 (laterais): moldura por dentro do painel do DJ, segura a porta."""
    (u0, pv0), (u1, pv1) = (-WI / 2 + PORTA_MARGEM_LADO, Z0 + PORTA_BASE), \
                           (WI / 2 - PORTA_MARGEM_LADO, Z_TAMPO - T - PORTA_TOPO)
    fora = BATENTE_LARG - BATENTE_SOBRE
    comp_h = (u1 - u0) + 2 * fora
    comp_v = (pv1 - pv0) - 2 * BATENTE_SOBRE
    pecas = []
    # horizontais: local u = comprimento, v = largura
    for nome, v_base in (("baixo", pv0 - fora), ("cima", pv1 - BATENTE_SOBRE)):
        c = ret(0, 0, comp_h, BATENTE_LARG)
        f = linha_furos((0, fora / 2), (comp_h, fora / 2))   # parafusos só na parte atrás do painel
        # fica atrás do painel (x de T a 2T): u ao longo de y, v ao longo de z
        pos = ((T, u0 - fora, v_base if nome == "baixo" else v_base), Y, Z, X)
        if nome == "cima":
            f = linha_furos((0, fora / 2 + BATENTE_SOBRE), (comp_h, fora / 2 + BATENTE_SOBRE))
        pecas.append(Painel("S1", "batente cima/baixo", c, T, pos, furos=f))
    for nome, u_base in (("esq", u0 - fora), ("dir", u1 - BATENTE_SOBRE)):
        c = ret(0, 0, BATENTE_LARG, comp_v)
        uf = fora / 2 if nome == "esq" else BATENTE_SOBRE + fora / 2
        f = linha_furos((uf, 0), (uf, comp_v))
        pos = ((T, u_base, pv0 + BATENTE_SOBRE), Y, Z, X)
        pecas.append(Painel("S2", "batente lateral", c, T, pos, furos=f))
    return pecas


def montar_paineis():
    pdj = painel_dj()
    return [lateral("esq"), lateral("dir"), fachada(), pdj, fundo(), tampo()] + batentes(pdj)


# ======================================================================
# Carrinho (só referência visual e checagem de encaixe)
# ======================================================================
def carrinho():
    itens = []
    plat = cq.Workplane("XY").box(PLAT_L, PLAT_W, 20, centered=(False, True, False)).translate(
        (-FOLGA_PLAT, 0, PLAT_Z - 20))
    itens.append((plat, {"cor": "#c9a978", "rugosidade": 0.8}))
    chassi = cq.Workplane("XY").box(PLAT_L - 200, PLAT_W - 160, 40, centered=(False, True, False)).translate(
        (100 - FOLGA_PLAT, 0, PLAT_Z - 60))
    itens.append((chassi, PRETO))
    r = 175
    for x in (150, PLAT_L - 200):
        for s in (-1, 1):
            roda = (cq.Workplane("XZ").circle(r).circle(r - 60).extrude(80, both=False)
                    .translate((x, s * (PLAT_W / 2 - 40) + (80 if s > 0 else 0), r)))
            aro = cq.Workplane("XZ").circle(r - 60).extrude(70).translate(
                (x, s * (PLAT_W / 2 - 40) + (75 if s > 0 else -5), r))
            itens += [(roda, {"cor": "#1e1e1e", "rugosidade": 0.9}), (aro, "#3a3a3a")]
    # cabo de tração em T (inclinado para cima, no lado x < 0)
    cabo = (cq.Workplane("XY").circle(14).extrude(950)
            .rotate((0, 0, 0), (0, 1, 0), -25).translate((-40, 0, 250)))
    punho = cq.Workplane("YZ").circle(16).extrude(160, both=True).translate((-40 - 950 * math.sin(math.radians(25)), 0,
                                                                              250 + 950 * math.cos(math.radians(25))))
    itens += [(cabo, PRETO), (punho, PRETO)]
    return itens


def equipamento():
    """Controladora (lado do DJ) e caixa de som deitada (encostada na fachada)."""
    c = DJ_CONTROLADORA
    ctrl = cq.Workplane("XY").box(c[1], c[0], c[2], centered=(False, True, False)).translate((60, 0, Z_TAMPO))
    s = CAIXA_SOM
    som = cq.Workplane("XY").box(s[0], s[1], s[2], centered=(False, True, False)).translate(
        (L - T - s[0] - 10, 0, Z_TAMPO))
    return [(ctrl, "#202020"), (som, "#111111")]


# ======================================================================
# Validação
# ======================================================================
def validar(paineis):
    rel = {}
    solidos = []
    for p in paineis:
        s = p.solido()
        v = bib.validar(s, p.ref + " " + p.nome, mesa=(2200, 1600, 2200))
        solidos.append(bib.Peca(p.ref + " " + p.nome, s, p.material, "chapa", (), DENS_COMPENSADO))
        if not (v["valido"] and v["watertight"] is True):
            rel.setdefault("pecas_invalidas", []).append(v)
    rel["interferencias_mm3"] = bib.interferencias(solidos)
    # porta: o recorte do painel D precisa passar pelo vão entre batentes? (abre para fora: ok)
    caixa = bib.montar(solidos).val().BoundingBox()
    rel["caixa_externa_mm"] = [round(caixa.xlen), round(caixa.ylen), round(caixa.zlen)]
    rel["altura_total_do_chao_mm"] = round(caixa.zmax)
    rel["cabe_na_plataforma"] = caixa.xlen <= PLAT_L and caixa.ylen <= PLAT_W
    porta = paineis[3].recorte_solido(0)
    rel["peso_caixa_kg"] = round(sum(s.peso_kg() for s in solidos)
                                 + porta.val().Volume() / 1000 * DENS_COMPENSADO / 1000, 1)
    # espaço do equipamento
    c, s = DJ_CONTROLADORA, CAIXA_SOM
    rel["tampo_util_mm"] = [L - T, WI]
    rel["cabe_controladora_e_som_deitado"] = (c[1] + s[0] + 70 <= L - T) and max(c[0], s[1]) <= WI
    rel["porta_vao_mm"] = [WI - 2 * PORTA_MARGEM_LADO,
                           (Z_TAMPO - T - Z0) - PORTA_BASE - PORTA_TOPO]
    rel["interno_bau_mm"] = [L - 2 * T, WI, Z_TAMPO - T - Z0 - T]
    # interferência caixa × carrinho (só plataforma)
    plat = cq.Workplane("XY").box(PLAT_L, PLAT_W, 20, centered=(False, True, False)).translate(
        (-FOLGA_PLAT, 0, PLAT_Z - 20))
    rel["caixa_x_plataforma_mm3"] = round(bib.montar(solidos).intersect(plat).val().Volume()) \
        if bib.montar(solidos).intersect(plat).vals() else 0
    return rel, solidos, porta


# ======================================================================
# Etapas de montagem (renders)
# ======================================================================
ETAPAS = [
    # (id, título, refs já montadas, refs novas)
    ("1", "Batentes no painel do DJ", ["D"], ["S1", "S2"]),
    ("2", "Fundo + painel do DJ + fachada", ["D", "S1", "S2"], ["B", "F"]),
    ("3", "Tampo de trabalho", ["D", "S1", "S2", "B", "F"], ["K"]),
    ("4", "Lateral esquerda", ["D", "S1", "S2", "B", "F", "K"], ["L1"]),
    ("5", "Lateral direita", ["D", "S1", "S2", "B", "F", "K", "L1"], ["L2"]),
    ("6", "Porta", ["D", "S1", "S2", "B", "F", "K", "L1", "L2"], ["P"]),
    ("7", "Sobre o carrinho", ["D", "S1", "S2", "B", "F", "K", "L1", "L2", "P"], ["CARRINHO"]),
]


def render_etapas(paineis, porta, saida):
    por_ref = {}
    for i, p in enumerate(paineis):
        chave = p.ref if p.ref != "L" else ("L1" if i == 0 else "L2")
        por_ref.setdefault(chave, []).append(p.solido())
    por_ref["P"] = [porta]
    pngs = {}
    vista = {"pos": (-1900, 2300, 1900), "alvo": (L / 2, 0, 800), "fov": 30}
    for eid, titulo, feitas, novas in ETAPAS:
        itens = []
        for r in feitas:
            for s in por_ref[r]:
                itens.append((s, {"cor": NATURAL, "rugosidade": 0.75}))
        for r in novas:
            if r == "CARRINHO":
                itens += carrinho()
                continue
            for s in por_ref[r]:
                itens.append((s, {"cor": ROSA, "rugosidade": 0.6}))
        if eid == "1":
            vista_e = {"pos": (-1500, 900, 1250), "alvo": (0, 0, 720), "fov": 30}
        elif eid == "7":
            vista_e = {"pos": (-2400, 2700, 1700), "alvo": (L / 2, 0, 650), "fov": 30}
        else:
            vista_e = vista
        pngs[eid] = bib.renderizar(itens, [dict(vista_e, nome=f"etapa_{eid}")],
                                   os.path.join(saida, "etapas"), largura=900, altura=800)[0]
    return pngs


def render_final(paineis, porta, saida):
    estilo = {"L": MARROM, "F": MARROM, "D": MARROM, "K": NATURAL,
              "B": NATURAL, "S1": NATURAL, "S2": NATURAL}
    itens = [(p.solido(), {"cor": estilo[p.ref], "rugosidade": 0.6}) for p in paineis]
    itens.append((porta.translate((-1, 0, 0)), {"cor": MARROM, "rugosidade": 0.6}))
    # marcas (posição): HEROICA nas laterais e fachada; faixa do patrocinador
    marca = []
    for s in (1, -1):
        y = s * (W / 2 + 0.6)
        txt = (cq.Workplane("XZ").text("HEROICA", 120, 1.2, halign="center", valign="center", kind="bold")
               .translate((L / 2, y if s < 0 else y + 1.2, 840)))
        if s > 0:
            txt = txt.mirror("YZ", basePointVector=(L / 2, 0, 0))
        faixa = cq.Workplane("XY").box(520, 1.2, 110).translate((L / 2, y, 610))
        marca += [(txt, "#F4EFE9"), (faixa, "#F4EFE9")]
    patrocinio = cq.Workplane("XY").box(1.2, 420, 160).translate((L + 0.6, 0, 640))
    logo_f = (cq.Workplane("YZ").text("HEROICA", 85, 1.2, halign="center", valign="center", kind="bold")
              .translate((L + 0.6, 0, 1050)))
    led = cq.Workplane("XY").box(8, WI - 20, 12).translate((-4, 0, Z_TAMPO - T - 10))
    marca += [(patrocinio, "#F4EFE9"), (logo_f, ROSA),
              (led, {"cor": LED, "brilho": 1.8, "luz": 0.8, "luz_pos": (-80, 0, Z_TAMPO - 60)})]
    itens += marca + carrinho() + equipamento()
    vistas = [
        {"nome": "render_dj", "pos": (-2600, 1900, 1900), "alvo": (L / 2, 0, 750), "fov": 30},
        {"nome": "render_fachada", "pos": (3300, -2000, 1600), "alvo": (L / 2, 0, 750), "fov": 30},
    ]
    return bib.renderizar(itens, vistas, os.path.join(saida, "renders"), largura=1100, altura=900)


if __name__ == "__main__":
    saida = os.path.join(AQUI, "saida")
    os.makedirs(saida, exist_ok=True)
    paineis = montar_paineis()
    rel, solidos, porta = validar(paineis)

    # plano de corte (a porta sai do painel D, não entra como peça)
    unicos = {}
    for p in paineis:
        if p.ref in unicos:
            unicos[p.ref].qtd += 1
        else:
            unicos[p.ref] = p
            p.qtd = 1
    pecas_corte = list(unicos.values())
    chapas = bib.plano_de_corte(pecas_corte)
    rel["chapas_2200x1600"] = len(chapas)
    area_pecas = sum(p.area_m2() * p.qtd for p in pecas_corte)
    rel["aproveitamento_%"] = round(100 * area_pecas / (len(chapas) * 2.2 * 1.6))
    rel["plano"] = [[(p.ref, round(x), round(y), g) for p, k, x, y, g in ch] for ch in chapas]
    dxfs = bib.dxf_chapas(chapas, os.path.join(saida, "dxf"), prefixo="chapa")
    print(json.dumps(rel, indent=1, ensure_ascii=False))
    with open(os.path.join(saida, "validacao.json"), "w") as f:
        json.dump(rel, f, indent=1, ensure_ascii=False)

    # lista de peças (para o PDF)
    lista = []
    for p in pecas_corte:
        x0, y0, x1, y1 = p.caixa2d()
        lista.append({"ref": p.ref, "nome": p.nome,
                      "qtd": p.qtd, "medida": [round(x1 - x0), round(y1 - y0), T], "obs": p.obs,
                      "furos_guia": sum(1 for f in p.furos if f[2] <= 3),
                      "furos": [list(f) for f in p.furos],
                      "contorno": [[round(v.X, 1), round(v.Y, 1)] for v in p.fio.Vertices()],
                      "recortes": [[[round(v.X, 1), round(v.Y, 1)] for v in r.Vertices()]
                                   for r in p.fios_recorte]})
    with open(os.path.join(saida, "pecas.json"), "w") as f:
        json.dump(lista, f, indent=1, ensure_ascii=False)

    cq.exporters.export(bib.montar(solidos + [bib.Peca("P", porta, "", "chapa", (), 0.7)]),
                        os.path.join(saida, "box_run_club_v1.step"))
    if "--sem-render" not in sys.argv:
        print(render_final(paineis, porta, saida))
        print(render_etapas(paineis, porta, saida))
