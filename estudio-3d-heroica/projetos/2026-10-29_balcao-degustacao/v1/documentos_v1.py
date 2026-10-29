"""
Balcão de degustação v1 — documentos: PDF da fábrica (corte CNC) e guia de montagem.
Rode antes: balcao_v1.py (gera saida/pecas.json, validacao.json e renders).

    python documentos_v1.py
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "..", "ferramentas"))
sys.path.insert(0, os.path.join(AQUI, "..", "..", ".."))
import desenho as dz  # noqa: E402
import balcao_v1 as m  # noqa: E402

SAIDA = os.path.join(AQUI, "saida")
PECAS = {p["ref"]: p for p in json.load(open(os.path.join(SAIDA, "pecas.json")))}
VAL = json.load(open(os.path.join(SAIDA, "validacao.json")))
DATA = "29/10/2026"
MARROM, ROSA, AZUL = "#5E2129", "#C9607F", "#2346b0"
TITULO = "BALCÃO DE DEGUSTAÇÃO HEROICA · v1"


def cab(fig, sub, folha, total, doc):
    dz.cabecalho(fig, TITULO, sub, f"{doc} · folha {folha}/{total} · medidas em mm", f"Heroica · {DATA}")


def img(fig, arq, caixa, titulo=None):
    ax = fig.add_axes(caixa)
    ax.imshow(plt.imread(os.path.join(SAIDA, arq)))
    ax.axis("off")
    if titulo:
        ax.set_title(titulo, fontsize=8, color="#555")


def caixa(ref):
    xs = [p[0] for p in PECAS[ref]["contorno"]]
    ys = [p[1] for p in PECAS[ref]["contorno"]]
    return min(xs), min(ys), max(xs), max(ys)


def peca_local(ref):
    x0, y0, _, _ = caixa(ref)
    p = PECAS[ref]
    return ([(u - x0, v - y0) for u, v in p["contorno"]],
            [[(u - x0, v - y0) for u, v in r] for r in p["recortes"]],
            [(u - x0, v - y0, d) for u, v, d in p["furos"]])


def cotar(ax, ref, titulo, extras=None):
    c, r, f = peca_local(ref)
    x0, y0, x1, y1 = caixa(ref)
    w, h = x1 - x0, y1 - y0
    ax.set_aspect("equal")
    ax.axis("off")
    q = PECAS[ref]["qtd"]
    ax.set_title(f"{ref} · {titulo} · {q} peça{'s' if q > 1 else ''}", fontsize=9, color=MARROM,
                 fontweight="bold", loc="left")
    dz.desenhar_peca(ax, c, r, f)
    dz.cota_h(ax, 0, w, 0, f"{w:.0f} (com espigas)" if r or len(c) > 4 else None, off=-max(w, h) * 0.07)
    dz.cota_v(ax, 0, h, 0, off=-max(w, h) * 0.07)
    if extras:
        extras(ax, w, h, x0, y0)
    pad = max(w, h) * 0.17
    ax.set_xlim(-pad, w + pad * 0.6)
    ax.set_ylim(-pad, h + pad * 0.45)


# ---------------------------------------------------------------------------
# FÁBRICA
# ---------------------------------------------------------------------------
def fab_capa(pdf, tot):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Balcão dobrável para PDV · peças planas em compensado 12 mm · corte CNC", 1, tot, "FÁBRICA")
    img(fig, "renders/render_frente.png", [0.01, 0.30, 0.25, 0.62], "frente (cliente)")
    img(fig, "renders/render_promotor.png", [0.25, 0.30, 0.25, 0.62], "fundo aberto (promotor)")
    img(fig, "renders/dobrado.png", [0.49, 0.42, 0.20, 0.40], "corpo dobrado (transporte)")
    fig.text(0.71, 0.89,
             "MATERIAL\n"
             "Compensado 12 mm (pinus ou virola, A/B),\n"
             "chapa 2200 × 1600: "
             f"{VAL['chapas_2200x1600']} chapas\n(2 balcões = 3 chapas).\n\n"
             "ARQUIVOS (mm, 1:1): chapa_1.dxf · chapa_2.dxf\n\n"
             "CAMADAS\n"
             "■ CORTE_INTERNO (azul): rasgos e furos. Cortar\n"
             "   PRIMEIRO, ferramenta por dentro da linha.\n"
             "■ CORTE_EXTERNO (vermelho): contorno, por fora.\n"
             "■ TEXTO_NAO_CORTAR: letra da peça.\n\n"
             "ENCAIXES (importante)\n"
             f"• Rasgos com {m.W_RASGO:.1f} de largura =\n"
             f"   chapa de {m.T_REAL:.1f} + {m.FOLGA_ENCAIXE} de folga.\n"
             "   MEDIR a chapa antes: se não for 12,0,\n"
             "   avisar para ajustar o arquivo.\n"
             f"• Feito para fresa Ø{m.FRESA:.0f}: os rasgos já têm sobra\n"
             "   nas pontas e as espigas têm alívio na base.\n"
             "• Tolerância ±0,3. Microjuntas ok.",
             fontsize=7.6, va="top", linespacing=1.45)
    d = VAL["dimensoes_mm"]
    fig.text(0.03, 0.25, "MEDIDAS GERAIS", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.03, 0.235,
             f"Montado: {d[0]} × {d[1]} × {d[2]} (largura × profundidade × altura com bandeira)\n"
             f"Mesa a {VAL['altura_mesa_mm']} do chão · corpo {m.LARG} × {m.PROF}\n"
             f"Prateleiras {VAL['prateleira_mm'][0]:.0f} × {VAL['prateleira_mm'][1]} · vãos "
             f"{' / '.join(str(v) for v in VAL['vaos_livres_mm'].values())}\n"
             f"Bandeira {m.TESTEIRA[0]} × {m.TESTEIRA[1]} · compensado ~{VAL['peso_compensado_kg']:.0f} kg",
             fontsize=8.2, va="top", linespacing=1.6)
    fig.text(0.50, 0.25, "COMO FUNCIONA", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.50, 0.235,
             "Frente + 2 laterais unidas por dobradiças: dobram chatas (~25 mm).\n"
             "Base e tampo encaixam nas espigas das 3 faces e travam o esquadro.\n"
             "Prateleiras encaixam pelas espigas nas laterais. Nenhum parafuso\n"
             "na montagem do dia a dia: só as dobradiças (fixas) e as abraçadeiras.",
             fontsize=8.2, va="top", linespacing=1.6)
    pdf.savefig(fig)
    plt.close(fig)


def fab_chapa(pdf, n, folha, tot):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, f"Plano de corte · chapa {n} de {VAL['chapas_2200x1600']} (2200 × 1600 × 12)", folha, tot, "FÁBRICA")
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.80])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 2200, 1600, fc="#faf7f2", ec="#999", lw=1))
    for ref, x, y, ang in VAL["plano"][n - 1]:
        c, r, f = peca_local(ref)
        ca, sa = round(math.cos(math.radians(ang))), round(math.sin(math.radians(ang)))
        rot = [(u * ca - v * sa, u * sa + v * ca) for u, v in c]
        mx, my = min(p[0] for p in rot), min(p[1] for p in rot)
        bw, bh = max(p[0] for p in rot) - mx, max(p[1] for p in rot) - my
        mapa = (lambda u, v, x=x, y=y, ca=ca, sa=sa, mx=mx, my=my:
                (x + u * ca - v * sa - mx, y + u * sa + v * ca - my))
        dz.desenhar_peca(ax, c, r, f, mapa=mapa)
        x0, y0, x1, y1 = caixa(ref)
        ax.text(x + bw / 2, y + bh / 2, f"{ref}\n{PECAS[ref]['nome']}\n{x1 - x0:.0f} × {y1 - y0:.0f}",
                ha="center", va="center", fontsize=7, color="#5a4630", fontweight="bold")
    dz.cota_h(ax, 0, 2200, 1600, "2200", off=30)
    dz.cota_v(ax, 0, 1600, 0, "1600", off=-30)
    ax.set_xlim(-80, 2260)
    ax.set_ylim(-60, 1700)
    fig.text(0.04, 0.04, "azul = corte interno (rasgos e furos)   contorno marrom = corte externo", fontsize=7.5)
    pdf.savefig(fig)
    plt.close(fig)


def fab_pecas1(pdf, folha, tot):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Peças cotadas (1/2) · vistas de fora", folha, tot, "FÁBRICA")

    def ext_f(ax, w, h, x0, y0):
        for xe in m.X_ESPIGA_FRENTE:
            u = xe - x0
            dz.cota_h(ax, u - m.ESPIGA / 2, u + m.ESPIGA / 2, h, f"espiga {m.ESPIGA}", off=25, fs=6.5)
        dz.cota_h(ax, 0, m.X_ESPIGA_FRENTE[0] - x0 - m.ESPIGA / 2, h - m.T, off=-30, fs=6.5)
        ax.text(w / 2, h / 2, "FRENTE LISA\n(área de marca)", ha="center", va="center", fontsize=9, color=ROSA)

    ax = fig.add_axes([0.02, 0.07, 0.40, 0.83])
    cotar(ax, "F", "FRENTE", ext_f)

    def ext_l(ax, w, h, x0, y0):
        for zp in m.Z_PRAT:
            v = zp - m.T / 2 - y0
            ax.annotate(f"rasgo {m.ESPIGA_PRAT_LADO}+{m.FRESA:.0f} × {m.W_RASGO:.1f}\n(z={zp - m.T} a {zp})",
                        (m.Y_ESPIGA_PRAT - x0, v), (w * 0.62, v + 70), fontsize=6.5,
                        arrowprops=dict(arrowstyle="-", lw=0.5))
        ax.text(5, -h * 0.13, "← borda da frente (dobradiças)", fontsize=6.5)

    ax = fig.add_axes([0.43, 0.07, 0.25, 0.83])
    cotar(ax, "L", "LATERAL", ext_l)

    def ext_k(ax, w, h, x0, y0):
        for s in (-1, 1):
            u, v = s * m.HASTE_X - x0, m.HASTE_Y - y0
            ax.annotate(f"Ø{m.FURO_HASTE} haste", (u, v), (u + (-150 if s < 0 else 20), v + 70), fontsize=6.5,
                        arrowprops=dict(arrowstyle="-", lw=0.5))
        dz.cota_v(ax, 0, m.HASTE_Y - y0, w, f"{m.HASTE_Y - y0:.0f}", off=30, fs=6.5)
        ax.text(w / 2, -60, "frente (beiral 20)", ha="center", fontsize=6.5)

    ax = fig.add_axes([0.69, 0.50, 0.30, 0.40])
    cotar(ax, "K", "TAMPO (MESA)", ext_k)
    ax = fig.add_axes([0.69, 0.08, 0.30, 0.36])
    cotar(ax, "B", "BASE")
    pdf.savefig(fig)
    plt.close(fig)


def fab_pecas2(pdf, folha, tot):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Peças cotadas (2/2) e lista de peças", folha, tot, "FÁBRICA")
    ax = fig.add_axes([0.02, 0.55, 0.46, 0.35])
    cotar(ax, "P1", "PRATELEIRA DE BAIXO")

    def ext_p2(ax, w, h, x0, y0):
        u = m.HASTE_X - x0
        ax.annotate(f"Ø{m.FURO_HASTE}", (u, m.HASTE_Y - y0), (u + 30, m.HASTE_Y - y0 - 120), fontsize=6.5,
                    arrowprops=dict(arrowstyle="-", lw=0.5))

    ax = fig.add_axes([0.51, 0.55, 0.46, 0.35])
    cotar(ax, "P2", "PRATELEIRA DE CIMA", ext_p2)

    def ext_q(ax, w, h, x0, y0):
        ax.text(w / 2, h / 2, "furos Ø7 para 4 abraçadeiras U 1\"", ha="center", fontsize=6.5, color=AZUL)

    ax = fig.add_axes([0.02, 0.10, 0.40, 0.36])
    cotar(ax, "Q", "TESTEIRA (BANDEIRA)", ext_q)
    ax = fig.add_axes([0.45, 0.10, 0.53, 0.36])
    linhas = []
    for ref in ("F", "L", "K", "B", "P1", "P2", "Q"):
        p = PECAS[ref]
        linhas.append([ref, p["nome"], str(p["qtd"]), f"{p['medida'][0]} × {p['medida'][1]} × 12", p["obs"][:38]])
    dz.tabela(ax, linhas, ["Ref", "Peça", "Qtd", "Medida (c/ espigas)", "Obs."], [0.06, 0.33, 0.06, 0.20, 0.35],
              fs=6.6)
    pdf.savefig(fig)
    plt.close(fig)


# ---------------------------------------------------------------------------
# GUIA
# ---------------------------------------------------------------------------
H2 = VAL["haste_partes_mm"][0]
MATERIAIS = [
    ["Peças cortadas: F, L×2, K, B, P1, P2, Q", "fábrica", "1 kit"],
    ["Dobradiça reta (de sobrepor) 3\" com parafusos 3,5 × 16", "ferragens", "6 (3 por lateral)"],
    [f"Tubo de alumínio redondo 1\" (25,4), parede 1,5 — cortar em 4 × {H2}", "alumínio", "4 pedaços*"],
    ["Luva de emenda interna para tubo 1\" (ou tubo 7/8\" × 100)", "alumínio/ferragens", "2"],
    ["Ponteira de borracha interna 1\"", "ferragens", "2 (pé das hastes)"],
    ["Abraçadeira em U 1\" com porcas borboleta M6", "ferragens", "4"],
    ["Fundo + tinta esmalte (ou laca) e verniz no tampo", "tintas", "—"],
    ["Adesivo impresso (frente, laterais, testeira)", "gráfica", "—"],
]
PASSOS = [
    ("0", "Uma vez só: dobradiças e acabamento", None,
     "1. Lixar as bordas (lixa 120), selar e pintar todas as peças. Tampo com verniz\n"
     "   (é onde vai alimento embalado; para alimento aberto, usar bandeja/forro próprio).\n"
     "2. Dobradiças: deite a frente F com a face de dentro para cima. Encoste cada\n"
     "   lateral L em pé na borda (a lateral fica ATRÁS da frente, alinhada pela\n"
     "   borda de fora). 3 dobradiças por lado, a ~100, ~460 e ~820 do pé, com as\n"
     "   abas nas faces de DENTRO. Confira que a lateral dobra para dentro e deita\n"
     "   sobre a frente (as duas se encontram no meio).\n"
     "3. Abraçadeiras: parafusos U pelos 8 furos Ø7 da testeira (por trás)."),
    ("1", "Abrir o corpo", "etapas/etapa_1.png",
     "Abra as duas laterais até 90° (o corpo fica em pé sozinho, em U).\n"
     "Ainda NÃO coloque sobre a base: as laterais precisam abrir um pouco\n"
     "para receber as prateleiras."),
    ("2", "Prateleiras", "etapas/etapa_2.png",
     "Prateleira de baixo P1 (sem furos) e de cima P2 (com 2 furos, furos para trás).\n"
     "Encaixe a espiga de um lado no rasgo de uma lateral; abra a outra lateral\n"
     "uns 10°, alinhe o rasgo com a outra espiga e feche. Repita com a outra."),
    ("3", "Corpo sobre a base", "etapas/etapa_3.png",
     "Base B no chão. Levante o corpo e desça sobre a base: as 4 espigas de baixo\n"
     "(2 da frente, 1 de cada lateral) entram nos rasgos da base."),
    ("4", "Tampo", "etapas/etapa_4.png",
     "Desça o tampo K com o beiral para a frente e os furos para trás: as 4 espigas\n"
     "de cima entram nos rasgos. Pronto: o balcão está travado no esquadro."),
    ("5", "Hastes", "etapas/etapa_5.png",
     f"Emende as duas partes de cada haste com a luva ({H2} + {H2}).\n"
     "Ponteira de borracha no pé. Passe pelos furos do tampo e da prateleira de\n"
     "cima até apoiar na prateleira de baixo."),
    ("6", "Bandeira", "etapas/etapa_6.png",
     "Encoste a testeira Q na frente das hastes, com as abraçadeiras em volta\n"
     "dos tubos, suba até a altura (topo a 2 m) e aperte as borboletas.\n\n"
     "DESMONTAR: na ordem inversa. Para transporte: corpo dobrado (~25 mm),\n"
     "tampo, base, 2 prateleiras, testeira e 4 tubos."),
]


def guia_capa(pdf, tot):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Guia de montagem e desmontagem · o que você vai precisar", 1, tot, "MONTAGEM")
    img(fig, "renders/render_frente.png", [0.01, 0.33, 0.27, 0.58])
    ax = fig.add_axes([0.31, 0.50, 0.67, 0.38])
    dz.tabela(ax, MATERIAIS, ["Item", "Onde comprar", "Qtd"], [0.62, 0.18, 0.20], fs=7)
    fig.text(0.31, 0.46, f"* 4 × {H2} mm = {4 * H2 / 1000:.2f} m: compre 1 barra de 6 m (sobra) e peça cortado na loja,"
             " em esquadro.", fontsize=7, color="#555")
    fig.text(0.31, 0.41, "FERRAMENTAS", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.31, 0.39, "Parafusadeira e broca 3 (só para as dobradiças, uma vez). "
             "Montagem do dia a dia: sem ferramenta.", fontsize=8, va="top")
    fig.text(0.31, 0.33, "MAPA DAS PEÇAS", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.31, 0.31,
             "F  frente (com as laterais nas dobradiças)   L  lateral (2)\n"
             "B  base                                      K  tampo / mesa (furos atrás)\n"
             "P1 prateleira de baixo                       P2 prateleira de cima (furos)\n"
             "Q  testeira (bandeira)                       H  hastes de alumínio (2, em 2 partes)",
             fontsize=8, va="top", family="DejaVu Sans Mono", linespacing=1.6)
    fig.text(0.03, 0.25, "TEMPO", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.03, 0.23, "Montar no PDV: ~5 min, 1 pessoa.\nDesmontar: ~3 min.\n"
             f"Peso: ~{VAL['peso_compensado_kg']:.0f} kg de compensado + hastes.", fontsize=8.2, va="top",
             linespacing=1.6)
    pdf.savefig(fig)
    plt.close(fig)


def guia_passos(pdf, inicio, tot):
    folha = inicio
    for i in range(0, len(PASSOS), 2):
        fig = plt.figure(figsize=dz.A4_PAISAGEM)
        cab(fig, "Guia de montagem · passo a passo", folha, tot, "MONTAGEM")
        for j, (n, titulo, imagem, texto) in enumerate(PASSOS[i:i + 2]):
            y = 0.50 - j * 0.45
            img(fig, imagem or "renders/dobrado.png", [0.03, y, 0.30, 0.40])
            fig.text(0.37, y + 0.37, f"PASSO {n} · {titulo.upper()}", fontsize=11, fontweight="bold", color=MARROM)
            fig.text(0.37, y + 0.33, texto, fontsize=8.6, va="top", linespacing=1.55)
            if imagem:
                fig.text(0.03, y - 0.005, "rosa = peças deste passo", fontsize=7, color=ROSA)
        pdf.savefig(fig)
        plt.close(fig)
        folha += 1
    return folha


def guia_marca(pdf, folha, tot):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Áreas de impressão (para a gráfica)", folha, tot, "MONTAGEM")
    ax = fig.add_axes([0.03, 0.12, 0.94, 0.76])
    ax.set_aspect("equal")
    ax.axis("off")
    hc = m.Z_CORPO1 - m.Z_CORPO0
    itens = [("FRENTE", m.LARG, hc, "Heroica + produto + QR"), ("LATERAL × 2", m.L_LAT, hc, "patrocinador / selo"),
             ("TESTEIRA", m.TESTEIRA[0], m.TESTEIRA[1], "Heroica / campanha")]
    x = 0
    for nome, w, h, txt in itens:
        ax.add_patch(Rectangle((x, 0), w, h, fc="#f1e1e5", ec=MARROM))
        ax.text(x + w / 2, h / 2, txt, ha="center", va="center", fontsize=8, color=MARROM)
        dz.cota_h(ax, x, x + w, 0, off=-50)
        dz.cota_v(ax, 0, h, x + w, off=30)
        ax.text(x + w / 2, -130, nome, ha="center", fontsize=8, fontweight="bold")
        x += w + 180
    ax.add_patch(Rectangle((m.LARG + 180 + 20, 0), m.L_LAT - 40, hc, fill=False, ec=AZUL, ls=":"))
    ax.set_xlim(-100, x)
    ax.set_ylim(-200, hc + 80)
    fig.text(0.03, 0.07, "Lateral: deixar livre (sem adesivo) a faixa dos 2 rasgos das prateleiras, a 298–310 e 598–610 "
             "do pé, numa largura de 170 centrada. Frente: totalmente lisa. Vinil fosco laminado sobre pintura curada.",
             fontsize=7.8)
    pdf.savefig(fig)
    plt.close(fig)


if __name__ == "__main__":
    nf = 3 + VAL["chapas_2200x1600"]
    with PdfPages(os.path.join(SAIDA, "Balcao_Degustacao_v1_FABRICA.pdf")) as pdf:
        fab_capa(pdf, nf)
        for n in range(1, VAL["chapas_2200x1600"] + 1):
            fab_chapa(pdf, n, 1 + n, nf)
        fab_pecas1(pdf, nf - 1, nf)
        fab_pecas2(pdf, nf, nf)
    ng = 1 + (len(PASSOS) + 1) // 2 + 1
    with PdfPages(os.path.join(SAIDA, "Balcao_Degustacao_v1_GUIA_DE_MONTAGEM.pdf")) as pdf:
        guia_capa(pdf, ng)
        f = guia_passos(pdf, 2, ng)
        guia_marca(pdf, f, ng)
    print("ok")
