"""
Balcão de degustação dobrável Heroica v3 — estética "expositor Red Bull" + só cortes retos (serra).

Pedido (Roberto, 30/10/2026): estética parecida com o expositor de geladeira da Red Bull (estrutura
preta, ripado preto, prateleiras de madeira, luz). O fornecedor (Luciano Lâminas) corta em
serra de precisão (esquadrejadeira): só retângulos. Por isso:
  • nada de espiga/rasgo: tampo e base travam o corpo com 4 TACOS colados por baixo/por cima;
  • prateleiras apoiam em TRAVESSAS coladas nas laterais;
  • furos (hastes, cabo) feitos na montagem, com furadeira/serra-copo, nas posições do desenho.

Rodar:  ESTUDIO_NODE_MODULES=<pasta com three>/node_modules python balcao_v3.py [--sem-render]
Depois: python documentos_v3.py
"""
import json
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
T = 12                        # compensado 12 mm
LARG, PROF = 840, 420         # corpo
Z_TAMPO = 920                 # mesa (face de cima do tampo)
BEIRAL, BEIRAL_FRENTE = 20, 40
Z_PRAT = (310, 610)           # face de cima das prateleiras
FOLGA = 2                     # folga de cada lado (prateleira × lateral, tacos × painéis)

TACO = (60, 60, 2 * T)        # taco de travamento: 2 camadas de compensado coladas
TRAVESSA = (2 * T, 30)        # apoio de prateleira: 2 camadas (24) × 30 de altura
COMP_TRAVESSA = PROF - T - 40

RIPA_L, RIPA_VAO = 30, 15     # ripado da frente: 19 ripas de 30 com vão de 15 = 840
PLACA = (560, 300)            # placa da marca, no centro do ripado
Z_PLACA = 560                 # centro da placa
ESPACADOR = (40, 40, T)       # 4 espaçadores atrás da placa (afasta 12 do ripado → halo de LED)

HASTE_D, FURO_HASTE = 25.4, 28.0   # tubo 1" preto; furo com serra-copo 1 1/8" (28)
HASTE_X, HASTE_Y = 330, PROF - 40
TESTEIRA = (840, 300)
Z_TOPO = 2000
CANTONEIRA = 20               # cantoneira de alumínio preta 20 × 20

LED_PERFIL = (17, 8)
DENS = 0.60

CHAPA_SERRA = {"comprimento": 2200, "largura": 1600, "margem": 10, "vao": 5}   # serra: 4 de corte

PRETO, MADEIRA, ROSA, CREME, ALU = "#1b1b1b", "#C9A06B", "#E3A1B5", "#F4EFE9", "#2a2a2a"
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
NX, NY = (-1, 0, 0), (0, -1, 0)

Z0, Z1 = T, Z_TAMPO - T       # corpo entre base e tampo
W_INT = LARG - 2 * T
L_LAT = PROF - T


# ======================================================================
# PEÇAS (todas retangulares)
# ======================================================================
def P(ref, nome, w, h, pos, esp=T, furos=(), obs="", material="compensado 12"):
    return Painel(ref, nome, poli_ret(0, 0, w, h), esp, pos, furos=furos, obs=obs, material=material)


def pecas():
    out = []
    # corpo dobrável
    # furos-guia Ø3 (CNC fura; na serra, marcar com o gabarito do guia):
    #   frente: 2 por ripa, para parafusar as ripas por DENTRO (nenhum parafuso aparece no ripado)
    #   lateral: 3 por travessa, para parafusar a travessa por fora (cabeça escareada e pintada)
    furos_f = [(LARG - 45, Z1 - Z0 - 14, 10)]
    for i in range(19):
        u = i * (RIPA_L + RIPA_VAO) + RIPA_L / 2
        furos_f += [(u, 150, 3), (u, Z1 - Z0 - 150, 3)]
    out.append(P("F", "frente", LARG, Z1 - Z0, ((-LARG / 2, T, Z0), X, Z, NY), furos=furos_f,
                 obs="preto; Ø10 do cabo + 38 guias das ripas"))
    furos_l = [(y - T, zp - T - TRAVESSA[1] / 2 - Z0, 3) for zp in Z_PRAT for y in (T + 60, T + 20 + COMP_TRAVESSA / 2,
                                                                                  T + COMP_TRAVESSA - 20)]
    for s, ref in ((-1, "esq"), (1, "dir")):
        x = -LARG / 2 if s < 0 else LARG / 2
        out.append(P("L", "lateral", L_LAT, Z1 - Z0, ((x, T, Z0), Y, Z, X if s < 0 else NX), furos=furos_l,
                     obs="preto; 6 guias das travessas; 3 dobradiças"))
    # tampo, base, prateleiras (madeira natural)
    furos_h = [(LARG / 2 + BEIRAL + sx * HASTE_X, BEIRAL_FRENTE + HASTE_Y, FURO_HASTE) for sx in (-1, 1)]
    out.append(P("K", "tampo (mesa)", LARG + 2 * BEIRAL, PROF + BEIRAL_FRENTE,
                 ((-LARG / 2 - BEIRAL, -BEIRAL_FRENTE, Z1), X, Y, Z), furos=furos_h,
                 obs="madeira natural; 2 furos Ø28 (serra-copo)"))
    out.append(P("B", "base", LARG, PROF, ((-LARG / 2, 0, 0), X, Y, Z), obs="preto"))
    for i, zp in enumerate(Z_PRAT, 1):
        w = W_INT - 2 * FOLGA
        f = [(w / 2 + sx * HASTE_X, HASTE_Y - T, FURO_HASTE) for sx in (-1, 1)] if i == 2 else []
        out.append(P(f"P{i}", f"prateleira {'de cima' if i == 2 else 'de baixo'}", w, PROF - T - 15,
                     ((-w / 2, T, zp - T), X, Y, Z), furos=f,
                     obs="madeira natural" + ("; furos Ø28" if i == 2 else "")))
    # tacos: 4 no tampo (por baixo) e 4 na base (por cima), nas quinas de dentro do corpo
    tw, td, th = TACO
    for z, nome in ((Z1 - th, "taco do tampo"), (Z0, "taco da base")):
        for sx in (-1, 1):
            for yy in (T + FOLGA, PROF - td - 10):
                x = sx * (W_INT / 2 - FOLGA) - (tw if sx > 0 else 0)
                out.append(P("A", "taco (2 camadas coladas)", tw, td, ((x, yy, z), X, Y, Z), esp=th,
                             obs="colar + 2 parafusos 3,5×30"))
    # travessas de apoio das prateleiras (2 camadas) nas laterais, por dentro
    tl, ta = TRAVESSA
    for zp in Z_PRAT:
        for sx in (-1, 1):
            x = sx * (W_INT / 2) - (tl if sx > 0 else 0)
            out.append(P("R", "travessa de prateleira (2 camadas)", COMP_TRAVESSA, ta,
                         ((x, T + 20, zp - T - ta), Y, Z, X), esp=tl,
                         obs="colar + parafusar na lateral, por dentro"))
    # ripado da frente
    for i in range(19):
        x = -LARG / 2 + i * (RIPA_L + RIPA_VAO)
        out.append(P("Rp", "ripa do ripado", RIPA_L, Z1 - Z0, ((x, 0, Z0), X, Z, NY), obs="preto"))
    # placa da marca + espaçadores
    pw, ph = PLACA
    out.append(P("M", "placa da marca", pw, ph, ((-pw / 2, -T - ESPACADOR[2], Z_PLACA - ph / 2), X, Z, NY),
                 obs="rosa/arte; LED em volta, por trás"))
    for sx in (-1, 1):
        for sz in (-1, 1):
            ex, ez, ee = ESPACADOR
            out.append(P("E", "espaçador da placa", ex, ez,
                         ((sx * (pw / 2 - 60) - ex / 2, -T, Z_PLACA + sz * (ph / 2 - 50) - ez / 2), X, Z, NY), esp=ee))
    # testeira
    w, h = TESTEIRA
    out.append(P("Q", "testeira (bandeira)", w, h, ((-w / 2, HASTE_Y - HASTE_D / 2, Z_TOPO - h), X, Z, NY),
                 obs="preto + arte; 4 abraçadeiras U"))
    return out


def comprados():
    """Itens comprados (render + interferência): hastes, cantoneiras, LED."""
    z0, z1 = Z_PRAT[0], Z_TOPO - 15
    hastes = [cq.Workplane("XY").center(sx * HASTE_X, HASTE_Y).circle(HASTE_D / 2).circle(HASTE_D / 2 - 1.5)
              .extrude(z1 - z0).translate((0, 0, z0)) for sx in (-1, 1)]
    c = CANTONEIRA
    cant = []
    for sx in (-1, 1):
        # cantoneira na quina da frente: aba na face da ripa e aba cobrindo a borda frente+ripa
        perfil = cq.Workplane("XY").polyline([(0, 0), (c, 0), (c, 1.5), (1.5, 1.5), (1.5, c), (0, c)]).close()
        prof = perfil.extrude(Z1 - Z0)
        if sx < 0:
            prof = prof.translate((-LARG / 2 - 1.5, -T - 1.5, Z0))
        else:
            prof = prof.mirror("YZ").translate((LARG / 2 + 1.5, -T - 1.5, Z0))
        cant.append(prof)
    w, h = LED_PERFIL
    led_tampo = cq.Workplane("XY").box(LARG - 40, w, h).translate((0, -BEIRAL_FRENTE + 4 + w / 2, Z1 - h / 2))
    pw, ph = PLACA
    led_placa = (cq.Workplane("XY").box(pw - 30, 4, ph - 30).cut(cq.Workplane("XY").box(pw - 50, 6, ph - 50))
                 .translate((0, -T - ESPACADOR[2] / 2, Z_PLACA)))
    return hastes, cant, led_tampo, led_placa


# ======================================================================
# Validação e plano de corte (serra)
# ======================================================================
def validar(ps):
    rel = {}
    sol = []
    for i, p in enumerate(ps):
        s = p.solido()
        v = bib.validar(s, p.ref, mesa=(2200, 1600, 2200))
        if not (v["valido"] and v["watertight"] is True):
            rel.setdefault("pecas_invalidas", []).append(v)
        sol.append(bib.Peca(f"{p.ref}{i} {p.nome}", s, "", "chapa", (), DENS))
    hastes, cant, led_t, led_p = comprados()
    extra = [bib.Peca(f"haste{i}", h, "", "", (), 2.7) for i, h in enumerate(hastes)]
    extra += [bib.Peca(f"cantoneira{i}", c, "", "", (), 2.7) for i, c in enumerate(cant)]
    extra += [bib.Peca("led tampo", led_t, "", "", (), 2.7), bib.Peca("led placa", led_p, "", "", (), 1)]
    todas = sol + extra
    # interferência: ignora contato de face (volume ≤ 1 mm³)
    rel["interferencias_mm3"] = bib.interferencias(todas)
    bb = bib.montar(todas).val().BoundingBox()
    rel["dimensoes_mm"] = [round(bb.xlen), round(bb.ylen), round(bb.zmax)]
    rel["peso_compensado_kg"] = round(sum(s.peso_kg() for s in sol), 1)
    rel["haste_mm"] = round(Z_TOPO - 15 - Z_PRAT[0])
    # dobrado: frente + ripas + travessas + lateral
    rel["dobrado_espessura_mm"] = T + T + TRAVESSA[0] + T
    rel["vaos_livres_mm"] = [Z_PRAT[0] - T - Z0 - 0, Z_PRAT[1] - T - Z_PRAT[0], Z1 - Z_PRAT[1] - TACO[2]]
    return rel, sol


def lista_de_cortes(ps):
    """Agrupa por medida: o que a serra precisa (peça, qtd, comprimento × largura)."""
    grupos = {}
    for p in ps:
        x0, y0, x1, y1 = p.caixa2d()
        w, h = round(x1 - x0), round(y1 - y0)
        # taco/travessa/espaçador são 2 camadas (ou 1): conta as camadas de 12
        camadas = round(p.esp / T)
        chave = (p.ref, p.nome.split(" (")[0], max(w, h), min(w, h))
        g = grupos.setdefault(chave, {"ref": p.ref, "nome": chave[1], "comp": max(w, h), "larg": min(w, h),
                                      "qtd": 0, "obs": p.obs})
        g["qtd"] += camadas
    return list(grupos.values())


def paineis_cnc(ps):
    """Peças para o DXF da CNC: uma por referência (com furos), qtd = cópias × camadas de 12."""
    por_ref = {}
    for p in ps:
        if p.ref in por_ref:
            por_ref[p.ref][1] += round(p.esp / T)
        else:
            por_ref[p.ref] = [p, round(p.esp / T)]
    out = []
    for ref, (p, n) in por_ref.items():
        out.append(Painel(ref, p.nome.split(" (")[0], cq.Workplane("XY").add(p.fio), T, ((0, 0, 0), X, Y, Z),
                          furos=p.furos, qtd=n))
    return out


def paineis_corte(lista):
    out = []
    for g in lista:
        out.append(Painel(g["ref"], g["nome"], poli_ret(0, 0, g["comp"], g["larg"]), T,
                          ((0, 0, 0), X, Y, Z), qtd=g["qtd"]))
    return out


# ======================================================================
# Render
# ======================================================================
def render(ps, saida):
    cor = {"F": PRETO, "L": PRETO, "B": PRETO, "Q": PRETO, "Rp": "#141414", "K": MADEIRA, "P1": MADEIRA,
           "P2": MADEIRA, "A": MADEIRA, "R": MADEIRA, "M": ROSA, "E": PRETO}
    itens = [(p.solido(), {"cor": cor[p.ref], "rugosidade": 0.85 if cor[p.ref] in (PRETO, "#141414") else 0.6})
             for p in ps]
    hastes, cant, led_t, led_p = comprados()
    itens += [(h, {"cor": ALU, "metal": 0.6, "rugosidade": 0.35}) for h in hastes]
    itens += [(c, {"cor": ALU, "metal": 0.6, "rugosidade": 0.35}) for c in cant]
    pw, ph = PLACA
    logo = (cq.Workplane("XZ").text("HEROICA", 95, 1.2, halign="center", valign="center", kind="bold")
            .translate((0, -T - ESPACADOR[2] - T - 0.1, Z_PLACA)))
    w, h = TESTEIRA
    logo_q = (cq.Workplane("XZ").text("HEROICA", 120, 1.2, halign="center", valign="center", kind="bold")
              .translate((0, HASTE_Y - HASTE_D / 2 - T - 0.1, Z_TOPO - h / 2)))
    itens += [(logo, "#5E2129"), (logo_q, ROSA)]
    led_t_est = {"cor": "#FFF3DE", "brilho": 2.2}
    itens += [(led_t, led_t_est), (led_p, {"cor": "#FFE8F0", "brilho": 2.5})]
    # luzes: 4 sob o tampo e 4 em volta da placa (halo no ripado)
    luz = []
    for xl in (-300, -100, 100, 300):
        luz.append((xl, -BEIRAL_FRENTE + 12, Z1 - 40))
    for sx in (-1, 1):
        for sz in (-1, 1):
            luz.append((sx * (pw / 2 - 20), -T - 3, Z_PLACA + sz * (ph / 2 - 20)))
    for p in luz:
        itens.append((cq.Workplane("XY").box(1, 1, 1).translate(p),
                      {"cor": "#FFE9D6", "brilho": 0.1, "luz": 1.2, "luz_pos": p}))
    vistas = [{"nome": "render_frente", "pos": (-2500, -3300, 1500), "alvo": (0, PROF / 2, 1000), "fov": 34},
              {"nome": "render_promotor", "pos": (2200, 3400, 1700), "alvo": (0, PROF / 2, 900), "fov": 34}]
    pngs = bib.renderizar(itens, vistas, os.path.join(saida, "renders"), largura=900, altura=1100)
    noite = []
    for s, e in itens:
        if isinstance(e, dict) and e.get("luz"):
            e = dict(e, luz=700, luz_alcance=800)
        noite.append((s, e))
    pngs += bib.renderizar(noite, [{"nome": "render_led", "pos": (-1500, -3300, 1350), "alvo": (0, 0, 1050),
                                    "fov": 40}], os.path.join(saida, "renders"), largura=900, altura=1100,
                           fundo="#262321", ambiente=0.22)
    return pngs


def render_explodido(ps, saida):
    """Vista explodida com as letras das peças (para o guia)."""
    desloc = {"K": (0, 0, 350), "B": (0, 0, -250), "P2": (0, 450, 120), "P1": (0, 450, 0),
              "Q": (0, 0, 300), "M": (0, -350, 0), "E": (0, -200, 0)}
    cor = {"F": PRETO, "L": PRETO, "B": PRETO, "Q": PRETO, "Rp": "#141414", "K": MADEIRA, "P1": MADEIRA,
           "P2": MADEIRA, "A": ROSA, "R": ROSA, "M": ROSA, "E": PRETO}
    itens = []
    for p in ps:
        d = desloc.get(p.ref, (0, 0, 0))
        if p.ref == "A":
            d = (0, 0, 350) if p.posicao[0][2] > Z_TAMPO / 2 else (0, 0, -250)
        itens.append((p.solido().translate(d), {"cor": cor[p.ref], "rugosidade": 0.7}))
    v = [{"nome": "explodido", "pos": (2600, 3000, 2100), "alvo": (0, PROF / 2, 900), "fov": 40}]
    return bib.renderizar(itens, v, os.path.join(saida, "renders"), largura=900, altura=1100)


ETAPAS = [
    ("1", "Base no chão", [], ["B", "Ab"]),
    ("2", "Corpo aberto sobre a base", ["B", "Ab"], ["F", "L", "Rp", "M", "E", "R"]),
    ("3", "Prateleiras", ["B", "Ab", "F", "L", "Rp", "M", "E", "R"], ["P1", "P2"]),
    ("4", "Tampo", ["B", "Ab", "F", "L", "Rp", "M", "E", "R", "P1", "P2"], ["K", "At"]),
    ("5", "Hastes e bandeira", ["B", "Ab", "F", "L", "Rp", "M", "E", "R", "P1", "P2", "K", "At"], ["H", "Q"]),
]


def render_etapas(ps, saida):
    d = {}
    for p in ps:
        k = p.ref
        if k == "A":
            k = "At" if p.posicao[0][2] > Z_TAMPO / 2 else "Ab"
        d.setdefault(k, []).append(p.solido())
    d["H"] = comprados()[0]
    out = {}
    for eid, _, feitas, novas in ETAPAS:
        itens = [(s, {"cor": "#8d8d8d", "rugosidade": 0.8}) for r in feitas for s in d[r]]
        itens += [(s, {"cor": ROSA, "rugosidade": 0.6}) for r in novas for s in d[r]]
        alto = eid == "5"
        v = {"nome": f"etapa_{eid}", "pos": (2300, 2700, 2300 if alto else 1900),
             "alvo": (0, PROF / 2, 1000 if alto else 450), "fov": 40 if alto else 32}
        out[eid] = bib.renderizar(itens, [v], os.path.join(saida, "etapas"), largura=800, altura=800)[0]
    return out


if __name__ == "__main__":
    saida = os.path.join(AQUI, "saida")
    os.makedirs(saida, exist_ok=True)
    ps = pecas()
    rel, sol = validar(ps)
    lista = lista_de_cortes(ps)
    chapas = bib.plano_de_corte(paineis_corte(lista), chapa=CHAPA_SERRA)
    rel["chapas_2200x1600"] = len(chapas)
    rel["plano"] = [[(p.ref, round(x, 1), round(y, 1), bib._angulo(g), round(p.caixa2d()[2]), round(p.caixa2d()[3]))
                     for p, k, x, y, g in ch] for ch in chapas]
    rel["plano_problemas"] = bib.verificar_plano(chapas, chapa=CHAPA_SERRA)
    # pacote CNC: mesmas peças, com furos; vão 12 entre peças (fresa Ø6)
    cnc = paineis_cnc(ps)
    ch_cnc = bib.plano_de_corte(cnc)
    rel["cnc_chapas"] = len(ch_cnc)
    rel["cnc_plano"] = [[(p.ref, round(x, 1), round(y, 1), bib._angulo(g)) for p, k, x, y, g in ch] for ch in ch_cnc]
    rel["cnc_plano_problemas"] = bib.verificar_plano(ch_cnc)
    bib.dxf_chapas(ch_cnc, os.path.join(saida, "cnc_dxf"), prefixo="chapa")
    pecas_json = []
    for p in cnc:
        x0, y0, x1, y1 = p.caixa2d()
        pecas_json.append({"ref": p.ref, "nome": p.nome, "qtd": p.qtd, "medida": [round(x1 - x0), round(y1 - y0)],
                           "furos": [list(f) for f in p.furos],
                           "contorno": [[round(v.X, 1), round(v.Y, 1)] for v in p.fio.Vertices()]})
    with open(os.path.join(saida, "pecas.json"), "w") as f:
        json.dump(pecas_json, f, indent=1, ensure_ascii=False)
    with open(os.path.join(saida, "lista_de_cortes.json"), "w") as f:
        json.dump(lista, f, indent=1, ensure_ascii=False)
    with open(os.path.join(saida, "validacao.json"), "w") as f:
        json.dump(rel, f, indent=1, ensure_ascii=False)
    cq.exporters.export(bib.montar(sol), os.path.join(saida, "balcao_v3.step"))
    print(json.dumps({k: v for k, v in rel.items() if k != "plano"}, indent=1, ensure_ascii=False))
    for g in lista:
        print(g["ref"], g["nome"], g["qtd"], g["comp"], "x", g["larg"])
    if "--sem-render" not in sys.argv:
        print(render(ps, saida))
        print(render_explodido(ps, saida))
        print(render_etapas(ps, saida))
