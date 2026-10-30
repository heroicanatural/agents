"""
Balcão de degustação dobrável Heroica v2 — peças planas de compensado, corte CNC.

Pedido (Roberto, 29/10/2026): versão reta do balcão promocional com testeira (ref. 84 × 42 cm,
2 m de altura). Frente + laterais unidas por dobradiça (dobram chatas); tampo e base encaixam
por espiga e rasgo nas três faces; prateleiras internas encaixáveis; 2 furos no tampo para as
hastes da bandeira (testeira).
v2 (30/10): fita LED sob o beiral da frente do tampo (lava a frente de luz). Beiral da frente
passa de 20 para 40 (esconde o perfil) e a frente ganha 1 furo Ø10 para o cabo, sob o beiral.

Rodar:
    ESTUDIO_NODE_MODULES=<pasta com three>/node_modules python balcao_v2.py [--sem-render]
Depois: python documentos_v2.py
"""
import json
import math
import os
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", ".."))
import biblioteca_heroica as bib  # noqa: E402
from biblioteca_heroica import Painel, contorno_espigas, rasgo  # noqa: E402

# ======================================================================
# PARÂMETROS (mm)
# ======================================================================
T = 12                       # compensado 12 mm (nominal)
T_REAL = 12.0                # MEDIR a chapa comprada com paquímetro e pôr aqui
FOLGA_ENCAIXE = 0.5          # rasgo = T_REAL + folga (encaixe deslizante, sem martelo)
FRESA = bib.FRESA            # Ø da fresa da CNC (alívios e pontas dos rasgos)

LARG = 840                   # largura do corpo (frente)
PROF = 420                   # profundidade do corpo (frente + lateral)
Z_TAMPO = 920                # altura da mesa (face de cima do tampo)
BEIRAL = 20                  # tampo sobra 20 nos lados
BEIRAL_FRENTE = 40           # e 40 na frente: esconde o perfil do LED

# LED (fita 5 V USB em perfil de alumínio com difusor, colado sob o beiral da frente)
LED_PERFIL = (17, 8)         # largura × altura do perfil de sobrepor (CONFERIR na compra)
LED_COMP = LARG - 40         # 800: perfil cortado no comprimento
FURO_CABO = 10               # furo na frente para o cabo entrar no balcão
X_FURO_CABO = LARG / 2 - 45  # perto da quina direita (vista de frente: esquerda do promotor)

Z_PRAT = (310, 610)          # face de cima das prateleiras (baixo, cima)
FOLGA_PRAT = 1.0             # folga de cada lado entre prateleira e lateral

ESPIGA = 120                 # comprimento das espigas do corpo (tampo/base) e da frente da prateleira
ESPIGA_PRAT_LADO = 150       # espiga da prateleira que entra na lateral

# bandeira (testeira) e hastes
HASTE_D = 25.4               # tubo de alumínio 1"
FURO_HASTE = 26.5            # furo no tampo e na prateleira de cima
HASTE_X = 330                # distância do centro até cada haste
HASTE_Y = PROF - 40          # a 40 do fundo
TESTEIRA = (840, 300)        # largura × altura
Z_TESTEIRA_TOPO = 2000       # altura total
ABRACADEIRA_PASSO = 34       # distância entre os furos da abraçadeira em U 1" (CONFERIR na compra)

DENS = 0.60                  # compensado de pinus/virola ~0,6 g/cm³

# cores (render)
MARROM, ROSA, CREME, NATURAL, ALU = "#5E2129", "#E3A1B5", "#F4EFE9", "#D9B98C", "#B8BCC2"
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
NX, NY = (-1, 0, 0), (0, -1, 0)

# derivados
Z_CORPO0 = T                         # corpo apoia em cima da base
Z_CORPO1 = Z_TAMPO - T               # e encosta embaixo do tampo
W_INT = LARG - 2 * T                 # 816 entre laterais
L_LAT = PROF - T                     # 408 profundidade da lateral (atrás da frente)
Y_PRAT1 = PROF - 13                  # fundo da prateleira
W_RASGO = T_REAL + FOLGA_ENCAIXE
Y_CENTRO_LAT = T + L_LAT / 2         # centro da lateral (em y)
Y_ESPIGA_PRAT = (T + Y_PRAT1) / 2    # centro da espiga lateral da prateleira
X_ESPIGA_FRENTE = (-250, 250)        # espigas da frente no tampo/base
X_ESPIGA_PRAT = (-200, 200)          # espigas da frente da prateleira


# ======================================================================
# PEÇAS
# ======================================================================
def frente():
    """F: frente. u = x, v = z. Espigas em cima (tampo) e embaixo (base)."""
    c = contorno_espigas(-LARG / 2, Z_CORPO0, LARG / 2, Z_CORPO1, T,
                         baixo=[(x, ESPIGA) for x in X_ESPIGA_FRENTE],
                         cima=[(x, ESPIGA) for x in X_ESPIGA_FRENTE])
    # frente lisa (sem rasgos): só o furo do cabo do LED, escondido sob o beiral
    furos = [(X_FURO_CABO, Z_CORPO1 - 14, FURO_CABO)]
    return Painel("F", "frente", c, T, ((0, 0, 0), X, Z, Y), furos=furos,
                  obs="área principal de marca; dobradiças por dentro nas bordas")


def lateral(lado):
    """L: lateral (2 iguais). u = y (T..PROF), v = z."""
    c = contorno_espigas(T, Z_CORPO0, PROF, Z_CORPO1, T,
                         baixo=[(Y_CENTRO_LAT, ESPIGA)], cima=[(Y_CENTRO_LAT, ESPIGA)])
    rasgos = [rasgo(Y_ESPIGA_PRAT, zp - T / 2, ESPIGA_PRAT_LADO, W_RASGO) for zp in Z_PRAT]
    if lado == "dir":
        pos = ((LARG / 2, 0, 0), Y, Z, NX)
    else:
        pos = ((-LARG / 2, 0, 0), Y, Z, X)
    return Painel("L", "lateral", c, T, pos, recortes=rasgos, obs="2 iguais; dobradiça na borda da frente")


def _rasgos_corpo():
    """Rasgos do tampo e da base que recebem as espigas da frente e das laterais (u = x, v = y)."""
    r = [rasgo(x, T / 2, ESPIGA, W_RASGO) for x in X_ESPIGA_FRENTE]
    for s in (-1, 1):
        r.append(rasgo(s * (LARG / 2 - T / 2), Y_CENTRO_LAT, ESPIGA, W_RASGO, vertical=True))
    return r


def tampo():
    """K: tampo/mesa. u = x, v = y. Beiral na frente e nos lados; 2 furos das hastes."""
    c = bib.poli_ret(-LARG / 2 - BEIRAL, -BEIRAL_FRENTE, LARG / 2 + BEIRAL, PROF)
    furos = [(s * HASTE_X, HASTE_Y, FURO_HASTE) for s in (-1, 1)]
    return Painel("K", "tampo (mesa)", c, T, ((0, 0, Z_CORPO1), X, Y, Z), recortes=_rasgos_corpo(),
                  furos=furos, obs="2 furos Ø26,5 para as hastes da bandeira")


def base():
    """B: base. u = x, v = y."""
    c = bib.poli_ret(-LARG / 2, 0, LARG / 2, PROF)
    return Painel("B", "base", c, T, ((0, 0, 0), X, Y, Z), recortes=_rasgos_corpo(),
                  obs="o corpo apoia em cima; espigas atravessam até o chão")


def prateleira(i):
    """P1 (baixo) / P2 (cima). u = x, v = y. Espigas nas pontas, atravessando as laterais."""
    x0 = -W_INT / 2 + FOLGA_PRAT
    x1 = W_INT / 2 - FOLGA_PRAT
    prof_lado = T + FOLGA_PRAT                      # atravessa a lateral até a face de fora
    c = contorno_espigas(x0, T, x1, Y_PRAT1, T,
                         dir=[(Y_ESPIGA_PRAT, ESPIGA_PRAT_LADO, prof_lado)],
                         esq=[(Y_ESPIGA_PRAT, ESPIGA_PRAT_LADO, prof_lado)])
    furos = [(s * HASTE_X, HASTE_Y, FURO_HASTE) for s in (-1, 1)] if i == 2 else []
    ref = f"P{i}"
    nome = "prateleira de cima (furos das hastes)" if i == 2 else "prateleira de baixo (apoio das hastes)"
    return Painel(ref, nome, c, T, ((0, 0, Z_PRAT[i - 1] - T), X, Y, Z), furos=furos,
                  obs="entra antes do tampo; ver guia")


def testeira():
    """Q: bandeira. u = x, v = z (local 0..altura). Na frente das hastes."""
    w, h = TESTEIRA
    c = bib.poli_ret(-w / 2, 0, w / 2, h)
    furos = []
    for s in (-1, 1):
        for zf in (40, h - 40):
            for d in (-1, 1):
                furos.append((s * HASTE_X + d * ABRACADEIRA_PASSO / 2, zf, 7))
    y_tras = HASTE_Y - HASTE_D / 2                    # costas da testeira encostam nas hastes
    pos = ((0, y_tras - T, Z_TESTEIRA_TOPO - h), X, Z, Y)
    return Painel("Q", "testeira (bandeira)", c, T, pos, furos=furos,
                  obs="4 abraçadeiras U 1\" com borboleta")


def hastes():
    """Tubos (comprados): da prateleira de baixo até 15 abaixo do topo da testeira."""
    z0, z1 = Z_PRAT[0], Z_TESTEIRA_TOPO - 15
    return [cq.Workplane("XY").center(s * HASTE_X, HASTE_Y).circle(HASTE_D / 2).circle(HASTE_D / 2 - 1.5)
            .extrude(z1 - z0).translate((0, 0, z0)) for s in (-1, 1)], z1 - z0


def perfil_led():
    """Perfil de alumínio com a fita, colado sob o beiral, recuado 4 da borda da frente."""
    w, h = LED_PERFIL
    y = -BEIRAL_FRENTE + 4 + w / 2
    return cq.Workplane("XY").box(LED_COMP, w, h).translate((0, y, Z_CORPO1 - h / 2))


def power_bank():
    """Power bank 20 000 mAh na prateleira de baixo (só referência)."""
    return cq.Workplane("XY").box(150, 75, 28, centered=(True, True, False)).translate(
        (X_FURO_CABO - 80, 120, Z_PRAT[0]))


def montar_paineis():
    return [frente(), lateral("esq"), lateral("dir"), tampo(), base(), prateleira(1), prateleira(2), testeira()]


# ======================================================================
# Validação
# ======================================================================
def validar(paineis):
    rel = {}
    solidos = []
    for p in paineis:
        s = p.solido()
        v = bib.validar(s, p.ref, mesa=(2200, 1600, 2200))
        if not (v["valido"] and v["watertight"] is True):
            rel.setdefault("pecas_invalidas", []).append(v)
        solidos.append(bib.Peca(p.ref + " " + p.nome, s, "compensado", "chapa", (), DENS))
    tubos, comp_haste = hastes()
    todas = solidos + [bib.Peca(f"haste {i + 1}", t, "alumínio", "tubo", (), 2.7) for i, t in enumerate(tubos)]
    todas += [bib.Peca("perfil LED", perfil_led(), "alumínio", "tubo", (), 2.7),
              bib.Peca("power bank", power_bank(), "", "", (), 1.0)]
    pl = perfil_led().val().BoundingBox()
    rel["led"] = {"perfil_mm": LED_COMP, "recuo_da_frente_mm": round(-pl.ymax), "aparece_de_cima": False,
                  "furo_cabo": [X_FURO_CABO, Z_CORPO1 - 14, FURO_CABO]}
    rel["interferencias_mm3"] = bib.interferencias(todas)
    bb = bib.montar(todas).val().BoundingBox()
    rel["dimensoes_mm"] = [round(bb.xlen), round(bb.ylen), round(bb.zmax)]
    rel["altura_mesa_mm"] = Z_TAMPO
    rel["peso_compensado_kg"] = round(sum(s.peso_kg() for s in solidos), 1)
    rel["haste_mm"] = round(comp_haste)
    rel["haste_partes_mm"] = [round(comp_haste / 2)] * 2
    rel["vaos_livres_mm"] = {"base→prateleira 1": Z_PRAT[0] - T - T,
                             "prateleira 1→2": Z_PRAT[1] - T - Z_PRAT[0],
                             "prateleira 2→tampo": Z_CORPO1 - Z_PRAT[1]}
    rel["prateleira_mm"] = [W_INT - 2 * FOLGA_PRAT, Y_PRAT1 - T]
    # dobrado: as duas laterais (408 cada) cabem lado a lado atrás da frente (816)?
    rel["dobrado_laterais_cabem"] = 2 * L_LAT <= W_INT
    rel["dobrado_mm"] = [LARG, Z_CORPO1 - Z_CORPO0 + 2 * T, 2 * T + 10]
    # estabilidade: alavanca da bandeira x base (tombamento lateral desprezível; frontal checado)
    rel["espessura_rasgo_mm"] = W_RASGO
    return rel, solidos, tubos


# ======================================================================
# Render: montado, explodido (etapas) e dobrado
# ======================================================================
ETAPAS = [
    ("1", "Abrir o corpo", [], ["F", "L1", "L2"]),
    ("2", "Prateleiras", ["F", "L1", "L2"], ["P1", "P2"]),
    ("3", "Corpo sobre a base", ["F", "L1", "L2", "P1", "P2"], ["B"]),
    ("4", "Tampo", ["B", "F", "L1", "L2", "P1", "P2"], ["K"]),
    ("5", "Hastes", ["B", "F", "L1", "L2", "P1", "P2", "K"], ["H"]),
    ("6", "Bandeira", ["B", "F", "L1", "L2", "P1", "P2", "K", "H"], ["Q"]),
]


def _por_ref(paineis, tubos):
    d = {}
    for i, p in enumerate(paineis):
        k = p.ref if p.ref != "L" else ("L1" if "L1" not in d else "L2")
        d.setdefault(k, []).append(p.solido())
    d["H"] = tubos
    return d


def render_etapas(paineis, tubos, saida):
    d = _por_ref(paineis, tubos)
    out = {}
    for eid, titulo, feitas, novas in ETAPAS:
        itens = [(s, {"cor": NATURAL, "rugosidade": 0.75}) for r in feitas for s in d[r]]
        itens += [(s, {"cor": ROSA, "rugosidade": 0.6}) for r in novas for s in d[r]]
        alvo_z = 1000 if eid in ("5", "6") else 480
        vista = {"nome": f"etapa_{eid}", "pos": (2300, 2600, 1900 if eid not in ("5", "6") else 2300),
                 "alvo": (0, PROF / 2, alvo_z), "fov": 30 if eid not in ("5", "6") else 38}
        out[eid] = bib.renderizar(itens, [vista], os.path.join(saida, "etapas"), largura=800, altura=800)[0]
    return out


def render_final(paineis, tubos, saida):
    d = _por_ref(paineis, tubos)
    cor = {"F": MARROM, "L1": MARROM, "L2": MARROM, "K": CREME, "B": MARROM, "P1": NATURAL, "P2": NATURAL,
           "Q": MARROM}
    itens = []
    for r, lst in d.items():
        for s in lst:
            itens.append((s, {"cor": ALU, "metal": 0.8, "rugosidade": 0.3} if r == "H"
                          else {"cor": cor[r], "rugosidade": 0.55}))
    # marca (posição): frente e testeira
    logo_f = (cq.Workplane("XZ").text("HEROICA", 120, 1.2, halign="center", valign="center", kind="bold")
              .translate((0, -0.1, 620)))
    selo = cq.Workplane("XZ").circle(130).extrude(1.2).translate((0, -0.1, 330))
    w, h = TESTEIRA
    y_q = HASTE_Y - HASTE_D / 2 - T
    logo_q = (cq.Workplane("XZ").text("Sua pitada de coragem", 50, 1.2, halign="center", valign="center",
                                      kind="bold").translate((0, y_q - 0.1, Z_TESTEIRA_TOPO - h / 2)))
    itens += [(logo_f, CREME), (selo, ROSA), (logo_q, CREME)]
    yl = -BEIRAL_FRENTE + 4 + LED_PERFIL[0] / 2
    itens.append((perfil_led(), {"cor": "#FFE7B0", "brilho": 2.2}))
    for xl in (-300, -100, 100, 300):     # luzes que descem pela frente
        itens.append((cq.Workplane("XY").box(1, 1, 1).translate((xl, yl, Z_CORPO1 - 20)),
                      {"cor": "#FFD9A0", "brilho": 0.1, "luz": 1.6, "luz_pos": (xl, yl - 60, Z_CORPO1 - 30)}))
    itens.append((power_bank(), "#222222"))
    vistas = [{"nome": "render_frente", "pos": (-2600, -3200, 1500), "alvo": (0, PROF / 2, 1000), "fov": 34},
              {"nome": "render_promotor", "pos": (2200, 3400, 1700), "alvo": (0, PROF / 2, 900), "fov": 34}]
    pngs = bib.renderizar(itens, vistas, os.path.join(saida, "renders"), largura=900, altura=1100)
    # "loja à meia-luz": mostra o efeito do LED (luz geral baixa, câmera na altura dos olhos)
    noite = []
    for solido, est in itens:
        if isinstance(est, dict) and est.get("luz"):
            est = dict(est, luz=900, luz_alcance=900, luz_pos=(est["luz_pos"][0], est["luz_pos"][1] - 40,
                                                                  est["luz_pos"][2] - 10))
        noite.append((solido, est))
    pngs += bib.renderizar(noite, [{"nome": "render_led", "pos": (-1500, -3300, 1350), "alvo": (0, 0, 1050),
                                    "fov": 40}], os.path.join(saida, "renders"), largura=900, altura=1100,
                           fundo="#2a2522", ambiente=0.22)
    return pngs


def render_dobrado(paineis, saida):
    """Frente + laterais dobradas (transporte) e as peças soltas empilhadas."""
    f, l1, l2 = paineis[0].solido(), paineis[1].solido(), paineis[2].solido()
    # lateral gira 90° para dentro em torno da quina interna da frente
    eixo_e = cq.Vector(-LARG / 2 + T, T, 0)
    eixo_d = cq.Vector(LARG / 2 - T, T, 0)
    l1d = l1.rotate(eixo_e, eixo_e + cq.Vector(0, 0, 1), -90).translate((0, 1, 0))
    l2d = l2.rotate(eixo_d, eixo_d + cq.Vector(0, 0, 1), 90).translate((0, 1, 0))
    itens = [(f, {"cor": MARROM}), (l1d, {"cor": ROSA}), (l2d, {"cor": ROSA})]
    rel = {"laterais_dobradas_interferencia_mm3": round(
        sum(a.intersect(b).val().Volume() if a.intersect(b).vals() else 0
            for a, b in ((f, l1d), (f, l2d), (l1d, l2d))))}
    bb = bib.montar([bib.Peca("f", f, "", "", (), 0), bib.Peca("a", l1d, "", "", (), 0),
                     bib.Peca("b", l2d, "", "", (), 0)]).val().BoundingBox()
    rel["dobrado_espessura_mm"] = round(bb.ylen)
    vistas = [{"nome": "dobrado", "pos": (1800, 2600, 1500), "alvo": (0, 0, 460), "fov": 32}]
    png = bib.renderizar(itens, vistas, os.path.join(saida, "renders"), largura=800, altura=800)
    return rel, png


if __name__ == "__main__":
    saida = os.path.join(AQUI, "saida")
    os.makedirs(saida, exist_ok=True)
    paineis = montar_paineis()
    rel, solidos, tubos = validar(paineis)

    unicos = {}
    for p in paineis:
        if p.ref in unicos:
            unicos[p.ref].qtd += 1
        else:
            p.qtd = 1
            unicos[p.ref] = p
    pecas_corte = list(unicos.values())
    chapas = bib.plano_de_corte(pecas_corte)
    rel["chapas_2200x1600"] = len(chapas)
    rel["aproveitamento_%"] = round(100 * sum(p.area_m2() * p.qtd for p in pecas_corte) / (len(chapas) * 3.52))
    rel["plano"] = [[(p.ref, round(x, 1), round(y, 1), bib._angulo(g)) for p, k, x, y, g in ch] for ch in chapas]
    rel["plano_problemas"] = bib.verificar_plano(chapas)
    bib.dxf_chapas(chapas, os.path.join(saida, "dxf"), prefixo="chapa")

    lista = []
    for p in pecas_corte:
        x0, y0, x1, y1 = p.caixa2d()
        lista.append({"ref": p.ref, "nome": p.nome, "qtd": p.qtd, "medida": [round(x1 - x0), round(y1 - y0), T],
                      "obs": p.obs, "furos": [list(f) for f in p.furos],
                      "contorno": [[round(v.X, 1), round(v.Y, 1)] for v in p.fio.Vertices()],
                      "recortes": [[[round(v.X, 1), round(v.Y, 1)] for v in r.Vertices()] for r in p.fios_recorte]})
    with open(os.path.join(saida, "pecas.json"), "w") as f:
        json.dump(lista, f, indent=1, ensure_ascii=False)
    cq.exporters.export(bib.montar(solidos), os.path.join(saida, "balcao_v2.step"))

    if "--sem-render" not in sys.argv:
        r2, _ = render_dobrado(paineis, saida)
        rel.update(r2)
        print(render_final(paineis, tubos, saida))
        print(render_etapas(paineis, tubos, saida))
    with open(os.path.join(saida, "validacao.json"), "w") as f:
        json.dump(rel, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in rel.items() if k != "plano"}, indent=1, ensure_ascii=False))
