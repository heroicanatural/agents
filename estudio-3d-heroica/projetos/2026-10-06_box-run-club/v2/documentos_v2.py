"""
Box Run Club v2 — documentos: PDF para a fábrica (corte CNC) e guia de montagem.
Lê saida/pecas.json e saida/validacao.json gerados por box_v2.py (rode ele antes).

    python documentos_v2.py
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, Rectangle

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "..", "ferramentas"))
sys.path.insert(0, os.path.join(AQUI, "..", "..", ".."))
import desenho as dz  # noqa: E402
import box_v2 as m  # noqa: E402

SAIDA = os.path.join(AQUI, "saida")
PECAS = {p["ref"]: p for p in json.load(open(os.path.join(SAIDA, "pecas.json")))}
VAL = json.load(open(os.path.join(SAIDA, "validacao.json")))
DATA = "06/10/2026"
MARROM, ROSA, VERDE, AZUL = "#5E2129", "#C9607F", "#1a8a3a", "#2346b0"
N_GUIA = sum(p["furos_guia"] * p["qtd"] for p in PECAS.values())


def img(fig, arq, caixa, titulo=None):
    ax = fig.add_axes(caixa)
    ax.imshow(plt.imread(os.path.join(SAIDA, arq)))
    ax.axis("off")
    if titulo:
        ax.set_title(titulo, fontsize=8, color="#555")


def cab(fig, sub, folha, total, doc="FÁBRICA"):
    dz.cabecalho(fig, "BOX RUN CLUB HEROICA · v2", sub,
                 f"{doc} · folha {folha}/{total} · medidas em mm", f"Heroica · {DATA}")


def caixa(ref):
    xs = [p[0] for p in PECAS[ref]["contorno"]]
    ys = [p[1] for p in PECAS[ref]["contorno"]]
    return min(xs), min(ys), max(xs), max(ys)


def peca_local(ref):
    """Contorno, recortes e furos da peça deslocados para começar em (0, 0)."""
    x0, y0, _, _ = caixa(ref)
    p = PECAS[ref]
    c = [(u - x0, v - y0) for u, v in p["contorno"]]
    r = [[(u - x0, v - y0) for u, v in rr] for rr in p["recortes"]]
    f = [(u - x0, v - y0, d) for u, v, d in p["furos"]]
    return c, r, f


# ---------------------------------------------------------------------------
# FÁBRICA
# ---------------------------------------------------------------------------
def fabrica_capa(pdf, total):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Caixa em compensado naval 15 mm para carrinho-plataforma · corte CNC", 1, total)
    img(fig, "renders/render_dj.png", [0.02, 0.36, 0.33, 0.55], "lado do DJ (cabo do carrinho)")
    img(fig, "renders/render_fachada.png", [0.34, 0.36, 0.33, 0.55], "fachada (marca / patrocinador)")
    cx = VAL["caixa_externa_mm"]
    fig.text(0.69, 0.89,
             "MATERIAL\n"
             f"Compensado naval 15 mm, chapa 2200 × 1600: {VAL['chapas_2200x1600']} chapas.\n"
             "Pode ser virola/pinus naval A/B (cola fenólica WBP).\n\n"
             "ARQUIVOS (mm, escala 1:1)\n"
             "chapa_1.dxf · chapa_2.dxf\n\n"
             "CAMADAS DO DXF\n"
             "■ CORTE_INTERNO (azul): cortar PRIMEIRO,\n"
             "   ferramenta por dentro da linha.\n"
             "■ CORTE_EXTERNO (vermelho): por fora da linha.\n"
             f"■ FURO_GUIA_3 (verde): {N_GUIA} furos Ø3 passantes\n"
             "   (sem broca Ø3: marcar com 3 mm de profundidade).\n"
             "■ TEXTO_NAO_CORTAR: letra da peça. Gravar\n"
             "   leve (1 mm) ou só escrever a lápis.\n\n"
             "OBSERVAÇÕES\n"
             "• Fresa sugerida Ø6. Microjuntas (tabs) ok.\n"
             "• Os 2 recortes retangulares da peça D são as\n"
             "   PORTAS: não descartar.\n"
             "• Tolerância ±0,5 mm. Não lixar as bordas.",
             fontsize=7.8, va="top", linespacing=1.45)
    fig.text(0.03, 0.30, "MEDIDAS GERAIS (caixa montada)", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.03, 0.285,
             f"Externo: {cx[0]} × {cx[1]} × {cx[2]} (comprimento × largura × altura)\n"
             f"Altura do chão: tampo de trabalho a {m.Z_TAMPO}, fachada a {m.Z_FACHADA} "
             f"(sobre plataforma a {m.Z0})\n"
             f"Tampo útil: {VAL['tampo_util_mm'][0]} × {VAL['tampo_util_mm'][1]}  ·  "
             f"Baú interno: {' × '.join(str(v) for v in VAL['interno_bau_mm'])}\n"
             f"2 portas: vão {VAL['porta_vao_mm'][0]} × {VAL['porta_vao_mm'][1]} cada  ·  "
             f"Peso da caixa: ~{VAL['peso_caixa_kg']:.0f} kg",
             fontsize=8.2, va="top", linespacing=1.6)
    fig.text(0.50, 0.30, "ATENÇÃO", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.50, 0.285,
             f"Projeto para plataforma de {m.PLAT_L} × {m.PLAT_W}, a {m.PLAT_Z} do chão;\n"
             f"a caixa passa {VAL['balanco_lateral_mm']} de cada lado (fundo {VAL['folga_roda_sob_balanco_mm']} acima das rodas).\n"
             "Medir o carrinho antes de cortar. Se mudar, o arquivo é\n"
             "regerado (todas as medidas saem de um script).\n"
             f"Aproveitamento das chapas: {VAL['aproveitamento_%']}% (laterais encaixadas invertidas).",
             fontsize=8.2, va="top", linespacing=1.6)
    pdf.savefig(fig)
    plt.close(fig)


def fabrica_chapa(pdf, n, folha, total):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, f"Plano de corte · chapa {n} de {VAL['chapas_2200x1600']} (2200 × 1600 × 15)", folha, total)
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.80])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 2200, 1600, fc="#faf7f2", ec="#999", lw=1))
    import math
    for ref, x, y, ang in VAL["plano"][n - 1]:
        c, r, f = peca_local(ref)
        x0, y0, x1, y1 = caixa(ref)
        w, h = x1 - x0, y1 - y0
        ca, sa = round(math.cos(math.radians(ang))), round(math.sin(math.radians(ang)))
        rot = [(u * ca - v * sa, u * sa + v * ca) for u, v in c]
        mx, my = min(p[0] for p in rot), min(p[1] for p in rot)
        bw = max(p[0] for p in rot) - mx
        bh = max(p[1] for p in rot) - my
        mapa = (lambda u, v, x=x, y=y, ca=ca, sa=sa, mx=mx, my=my:
                (x + u * ca - v * sa - mx, y + u * sa + v * ca - my))
        dz.desenhar_peca(ax, c, r, f, mapa=mapa)
        nome = PECAS[ref]["nome"]
        ax.text(x + bw / 2, y + bh / 2, f"{ref}\n{nome}\n{w:.0f} × {h:.0f}", ha="center", va="center",
                fontsize=7 if min(bw, bh) > 120 else 5, color="#5a4630", fontweight="bold",
                rotation=90 if bw < 100 else 0)
    dz.cota_h(ax, 0, 2200, 1600, "2200", off=30)
    dz.cota_v(ax, 0, 1600, 0, "1600", off=-30)
    ax.set_xlim(-80, 2260)
    ax.set_ylim(-60, 1700)
    fig.text(0.04, 0.04, "● verde = furo-guia Ø3 passante   ○ azul = corte interno (furos Ø8 a Ø60 e portas)   "
             "contorno marrom = corte externo", fontsize=7.5, color="#333")
    pdf.savefig(fig)
    plt.close(fig)


def cotar_peca(ax, ref, titulo, extras=None):
    c, r, f = peca_local(ref)
    x0, y0, x1, y1 = caixa(ref)
    w, h = x1 - x0, y1 - y0
    ax.set_aspect("equal")
    ax.axis("off")
    q = PECAS[ref]["qtd"]
    ax.set_title(f"{ref} · {titulo} · {q} peça{'s' if q > 1 else ''}", fontsize=9, color=MARROM,
                 fontweight="bold", loc="left")
    dz.desenhar_peca(ax, c, r, f)
    dz.cota_h(ax, 0, w, 0, off=-max(w, h) * 0.06)
    dz.cota_v(ax, 0, h, 0, off=-max(w, h) * 0.06)
    if extras:
        extras(ax, w, h, f)
    pad = max(w, h) * 0.16
    ax.set_xlim(-pad, w + pad * 0.7)
    ax.set_ylim(-pad, h + pad * 0.5)


def fabrica_pecas(pdf, folha, total):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Peças cotadas (1/2) · vistas pelo lado de fora", folha, total)

    def ext_l(ax, w, h, f):
        h_dj = m.Z_TAMPO + m.ABA_TRAS - m.Z0
        dz.cota_v(ax, 0, h_dj, w * 0.0, f"{h_dj:.0f}", off=40, fs=7)
        dz.cota_v(ax, 0, h, w, f"{h:.0f}", off=40, fs=7)
        ax.plot([0, w], [m.Z_TAMPO - m.Z0 - m.T, m.Z_TAMPO - m.Z0 - m.T], ls=":", color="#999", lw=0.6)
        ax.text(w / 2, m.Z_TAMPO - m.Z0 - m.T - 35, "linha do tampo (por dentro)", ha="center", fontsize=6.5,
                color="#777")
        for u, v, d in f:
            if d == 12:
                ax.annotate(f"Ø12 (x={u:.0f}, y={v:.0f})", (u, v), (u + 40, v + 110), fontsize=6.5,
                            arrowprops=dict(arrowstyle="-", lw=0.5))
        ax.text(10, -95, "lado do DJ", fontsize=7)
        ax.text(w - 10, -95, "lado da fachada", fontsize=7, ha="right")

    ax = fig.add_axes([0.02, 0.45, 0.62, 0.44])
    cotar_peca(ax, "L", "LATERAL (2 iguais)", ext_l)

    def ext_f(ax, w, h, f):
        ax.plot([0, w], [m.Z_TAMPO - m.Z0 - m.T] * 2, ls=":", color="#999", lw=0.6)
        ax.text(w / 2, m.Z_TAMPO - m.Z0 + 10, "tampo", ha="center", fontsize=6.5, color="#777")

    ax = fig.add_axes([0.66, 0.40, 0.32, 0.50])
    cotar_peca(ax, "F", "FACHADA", ext_f)

    def ext_d(ax, w, h, f):
        x0, y0, _, _ = caixa("D")
        for i, rc in enumerate(PECAS["D"]["recortes"]):
            us = [p[0] - x0 for p in rc]
            vs = [p[1] - y0 for p in rc]
            dz.cota_h(ax, min(us), max(us), max(vs), f"{max(us) - min(us):.0f}", off=25, fs=7, cor=AZUL)
            if i == 1:
                dz.cota_v(ax, min(vs), max(vs), max(us), f"{max(vs) - min(vs):.0f}", off=25, fs=7, cor=AZUL)
            ax.text((min(us) + max(us)) / 2, (min(vs) + max(vs)) / 2, f"PORTA P\n(guardar)", ha="center",
                    va="center", fontsize=7, color=AZUL)
        ax.text(w / 2, -110, f"vãos a {m.PORTA_MARGEM_LADO} das bordas, {2 * m.PORTA_MEIO} de montante central, "
                f"{m.PORTA_BASE} do pé e {m.PORTA_TOPO} do topo", ha="center", fontsize=6.5, color=AZUL)

    ax = fig.add_axes([0.02, 0.05, 0.36, 0.36])
    cotar_peca(ax, "D", "PAINEL DO DJ", ext_d)
    fig.text(0.42, 0.33,
             "COMO LER\n"
             "• Medidas externas de cada peça; espessura 15.\n"
             "• Furos-guia (verde) ficam no centro da espessura\n"
             "   da peça vizinha: 7,5 da borda.\n"
             "• Linhas de furos começam a 40 da quina e seguem\n"
             f"   a cada ~{m.PASSO_PARAFUSO}.\n"
             "• Furos azuis: Ø8 cabo de LED, Ø9 fixação no\n"
             "   carrinho, Ø10 dreno, Ø12 elástico, Ø60 passa-fio.",
             fontsize=7.6, va="top", linespacing=1.5)
    pdf.savefig(fig)
    plt.close(fig)


def fabrica_pecas2(pdf, folha, total):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Peças cotadas (2/2) e lista de peças", folha, total)

    def ext_b(ax, w, h, f):
        for u, v, d in f:
            if d == 9:
                ax.annotate("Ø9", (u, v), (u + 30, v + 40), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5))
        us = sorted({u for u, v, d in f if d == 9})
        vs = sorted({v for u, v, d in f if d == 9})
        dz.cota_h(ax, 0, us[0], vs[0], off=-30, fs=6.5)
        dz.cota_v(ax, 0, vs[0], us[0], off=-25, fs=6.5)

    ax = fig.add_axes([0.02, 0.56, 0.47, 0.33])
    cotar_peca(ax, "B", "FUNDO", ext_b)

    def ext_k(ax, w, h, f):
        for u, v, d in f:
            if d == 60:
                ax.annotate(f"passa-fio Ø60\n({u:.0f}; {v:.0f})", (u, v), (u + 120, v - 160), fontsize=6.5,
                            arrowprops=dict(arrowstyle="-", lw=0.5))
        ax.text(5, h + 20, "lado do DJ ←", fontsize=6.5)

    ax = fig.add_axes([0.51, 0.56, 0.47, 0.33])
    cotar_peca(ax, "K", "TAMPO DE TRABALHO", ext_k)
    ax = fig.add_axes([0.02, 0.06, 0.42, 0.24])
    cotar_peca(ax, "M", "DIVISÓRIA CENTRAL")
    ax = fig.add_axes([0.02, 0.36, 0.28, 0.14])
    cotar_peca(ax, "S1", "BATENTE CIMA/BAIXO")
    ax = fig.add_axes([0.32, 0.31, 0.10, 0.22])
    cotar_peca(ax, "S2", "BATENTE LAT.")

    ax = fig.add_axes([0.46, 0.08, 0.52, 0.40])
    linhas = []
    for ref in ("L", "F", "D", "B", "K", "M", "S1", "S2"):
        p = PECAS[ref]
        linhas.append([ref, p["nome"], str(p["qtd"]), f"{p['medida'][0]} × {p['medida'][1]} × 15",
                       str(p["furos_guia"] * p["qtd"]), p["obs"][:40]])
    linhas.append(["P", "porta (sai dos recortes de D)", "2", f"{VAL['porta_vao_mm'][0]} × {VAL['porta_vao_mm'][1]} × 15",
                   "—", "não é corte extra"])
    dz.tabela(ax, linhas, ["Ref", "Peça", "Qtd", "Medida", "Furos-guia", "Obs."],
              [0.05, 0.24, 0.05, 0.17, 0.10, 0.39], fs=6.3)
    pdf.savefig(fig)
    plt.close(fig)


# ---------------------------------------------------------------------------
# GUIA DE MONTAGEM
# ---------------------------------------------------------------------------
N_PARAF_PAINEL = N_GUIA - (PECAS["S1"]["furos_guia"] * 2 + PECAS["S2"]["furos_guia"] * 2)
N_PARAF_BATENTE = PECAS["S1"]["furos_guia"] * 2 + PECAS["S2"]["furos_guia"] * 2

MATERIAIS = [
    ["Peças cortadas (L×2, F, D, B, K, M, S1×4, S2×4 + 2 portas P)", "fábrica", "1 kit"],
    ["Cola PU para madeira, uso externo (ex.: Titebond III)", "marcenaria", "1 frasco 500 g"],
    [f"Parafuso p/ madeira cabeça chata 4,0 × 40 inox ou bicromatizado", "ferragens",
     f"{N_PARAF_PAINEL} + 20 de sobra"],
    ["Parafuso p/ madeira cabeça chata 3,5 × 25", "ferragens", f"{N_PARAF_BATENTE} + 6"],
    ["Dobradiça piano (contínua) inox, 400 mm + parafusos 3,5 × 16", "ferragens", "2"],
    ["Fecho de pressão (tipo maleta) com porta-cadeado + cadeado", "ferragens", "2"],
    ["Puxador pequeno (concha ou alça)", "ferragens", "2"],
    ["Passa-fio de mesa Ø60", "ferragens", "1"],
    ["Parafuso francês M8 × 70 + arruela larga M8 + porca borboleta M8", "ferragens", "4 conjuntos"],
    ["Elástico extensor com gancho, 60 cm", "ferragens", "2 a 4"],
    ["Fita LED COB 5 V USB 1 m + perfil de alumínio c/ difusor + power bank", "elétrica", "1"],
    ["Massa para madeira, lixas 80/120/220, fundo/primer, esmalte PU ou sintético", "tintas", "—"],
    ["Verniz marítimo (tampo e interior) ", "tintas", "—"],
    ["Adesivos de marca (laterais, fachada, portas) — ver última folha", "gráfica", "—"],
]
FERRAMENTAS = ("Parafusadeira, brocas 3 · 4,5 · 9 mm, escareador, 4 grampos/sargentos, esquadro, trena, "
               "lixadeira ou taco de lixa, rolo de espuma e pincel.")

PASSOS = [
    ("0", "Preparar as peças", None,
     "1. Conferir as peças pela letra gravada (tabela da folha 1).\n"
     "2. Lixar as bordas com lixa 120 (quebrar a quina, R≈2).\n"
     "3. Em todos os furos-guia Ø3 (verdes) das peças L, F, D, K, S1 e S2:\n"
     "   abrir com broca 4,5 e escarear pelo LADO DE FORA (o lado da marca).\n"
     "   As laterais L são iguais: escolha o lado mais bonito de cada uma\n"
     "   para ser o de fora, e lembre que uma vira a esquerda e a outra a direita.\n"
     "4. REGRA DO PARAFUSO: em cada união, passe cola PU na borda, encoste,\n"
     "   prenda com grampo, e pré-fure a borda da peça vizinha com broca 3\n"
     "   (35 mm de fundo) pelo furo já aberto. Só então parafuse 4,0 × 40.\n"
     "   Sem o pré-furo, o compensado racha na borda."),
    ("1", "Batentes no painel do DJ", "etapas/etapa_1.png",
     "Deite o painel D com a face de dentro para cima.\n"
     "Cada vão de porta ganha 4 batentes (S1 em cima e embaixo, S2 dos lados)\n"
     f"formando uma moldura que invade {m.BATENTE_SOBRE} mm o vão: é onde a porta encosta.\n"
     "Use as próprias portas P como gabarito: encaixe no vão por cima e\n"
     "confira que apoiam nos 4 batentes. Cola + parafusos 3,5 × 25\n"
     "pelos furos dos batentes."),
    ("2", "Fundo + painel do DJ + fachada + divisória", "etapas/etapa_2.png",
     "Fundo B no chão. Painel D numa ponta e fachada F na outra, em pé, por\n"
     "FORA do fundo (o fundo fica entre os dois). Bases alinhadas.\n"
     "Cola nas bordas do fundo, grampos, pré-furo e parafusos pelos furos\n"
     "da linha de baixo de D e de F.\n"
     "Divisória M em pé sobre o fundo, no centro: parafusos de baixo pelo\n"
     "fundo (linha do meio) e pelas linhas verticais do meio de D e de F.\n"
     "Conferir esquadro (medir as diagonais: têm que ser iguais)."),
    ("3", "Tampo de trabalho", "etapas/etapa_3.png",
     f"O tampo K apoia em cima do painel D e encosta por dentro na fachada.\n"
     f"Altura: a face de cima fica a {m.Z_TAMPO - m.Z0} do fundo da caixa; a linha de\n"
     "furos de cima da fachada marca o lugar.\n"
     "Parafusos: pelo tampo (furos na borda do lado do DJ) para dentro do\n"
     "painel D, pela linha do meio para dentro da divisória, e pela\n"
     "fachada para dentro da borda do tampo.\n"
     "O passa-fio Ø60 fica no canto do lado do DJ."),
    ("4", "Lateral esquerda", "etapas/etapa_4.png",
     "Cola em todas as bordas que tocam a lateral: fundo, painel D,\n"
     "tampo e fachada. Encoste a lateral L com a base e o lado do DJ\n"
     "alinhados (o lado baixo da lateral fica no lado do DJ).\n"
     "Grampos, pré-furo e parafusos em todas as linhas de furos.\n"
     "Dica: deite a caixa de lado para parafusar de cima."),
    ("5", "Lateral direita e cura", "etapas/etapa_5.png",
     "Mesma coisa do outro lado. Limpe o excesso de cola PU (ela\n"
     "espuma) antes de secar.\n"
     "Deixe curar 24 h antes de pintar ou de colocar peso."),
    ("6", "Acabamento", "renders/render_fachada.png",
     "1. Massa nas cabeças dos parafusos e nas falhas; lixa 120.\n"
     "2. Selar TODAS as bordas do compensado (é por onde entra água).\n"
     "3. Fundo/primer + 2 demãos de esmalte por fora (marrom Heroica,\n"
     "   ref. RAL 3005). Tampo e interior: verniz marítimo ou a mesma tinta.\n"
     "4. Pintar as portas P separadas, nas duas faces."),
    ("7", "Portas", "etapas/etapa_6.png",
     "Cada porta: dobradiça piano de 400 mm na borda de FORA (perto da\n"
     "lateral), por fora (aba na porta e aba no painel), folga igual em volta.\n"
     "Fecho de pressão na borda do meio (no montante central); puxador.\n"
     "As portas abrem para os lados e fecham contra os batentes.\n"
     "Esquerda: equipamento e cabos. Direita: produto (sugestão)."),
    ("8", "Sobre o carrinho", "etapas/etapa_7.png",
     "Coloque a caixa centrada na plataforma, com o lado do DJ (lado baixo)\n"
     "no lado do cabo do carrinho.\n"
     "Antes de furar, olhe por baixo: os 4 furos Ø9 do fundo não podem cair\n"
     "em cima de tubo do chassi (se cair, desloque o furo na plataforma).\n"
     "Use os furos do fundo como gabarito: broca 9 atravessando a plataforma.\n"
     "Parafuso francês M8 de dentro para fora, arruela larga e porca\n"
     "borboleta por baixo. Sem ferramenta para tirar a caixa depois."),
    ("9", "Acabamentos finais e marca", "renders/render_dj.png",
     "• Passa-fio no furo Ø60 do tampo.\n"
     "• LED: perfil de alumínio colado no painel D, logo abaixo do tampo;\n"
     "  cabo pelo furo Ø8 até o power bank dentro do baú.\n"
     "• Elásticos: ganchos nos furos Ø12 das laterais, prendendo a\n"
     "  controladora e a caixa de som. SEMPRE prender antes de andar.\n"
     "• Adesivos nas áreas da última folha.\n"
     "• Teste: carregar, puxar em curva e numa rampa. Nada pode escorregar."),
]


def guia_capa(pdf, total):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Guia de montagem · o que você vai precisar", 1, total, doc="MONTAGEM")
    img(fig, "renders/render_dj.png", [0.02, 0.42, 0.30, 0.48])
    ax = fig.add_axes([0.34, 0.42, 0.64, 0.48])
    dz.tabela(ax, MATERIAIS, ["Item", "Onde comprar", "Qtd"], [0.68, 0.14, 0.18], fs=6.8)
    fig.text(0.03, 0.37, "FERRAMENTAS", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.03, 0.35, FERRAMENTAS, fontsize=8, va="top")
    fig.text(0.03, 0.29, "MAPA DAS PEÇAS", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.03, 0.27,
             "L  lateral (2, iguais)        F  fachada (painel alto, lado oposto ao cabo)\n"
             "D  painel do DJ (2 portas)    P  portas (os recortes de D, 2)\n"
             "B  fundo                      K  tampo de trabalho\n"
             "M  divisória central          S1 batente cima/baixo (4)\n"
             "S2 batente lateral (4)",
             fontsize=8.2, va="top", family="DejaVu Sans Mono", linespacing=1.6)
    fig.text(0.55, 0.29, "TEMPO E PESSOAS", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.55, 0.27,
             "Marcenaria: 1 dia com 2 pessoas (+24 h de cura da cola).\n"
             "Pintura: 2 dias (secagem entre demãos).\n"
             "Montagem no carrinho e acabamentos: 2 h.\n"
             f"Caixa pronta: ~{VAL['peso_caixa_kg']:.0f} kg. Levantar sempre em 2 pessoas.",
             fontsize=8.2, va="top", linespacing=1.6)
    pdf.savefig(fig)
    plt.close(fig)


def guia_passos(pdf, inicio, total):
    folha = inicio
    for i in range(0, len(PASSOS), 2):
        fig = plt.figure(figsize=dz.A4_PAISAGEM)
        cab(fig, "Guia de montagem · passo a passo", folha, total, doc="MONTAGEM")
        for j, (n, titulo, imagem, texto) in enumerate(PASSOS[i:i + 2]):
            y = 0.50 - j * 0.45
            if imagem:
                img(fig, imagem, [0.03, y, 0.36, 0.40])
            else:
                desenhar_regra_parafuso(fig, [0.05, y + 0.03, 0.32, 0.34])
            fig.text(0.42, y + 0.37, f"PASSO {n} · {titulo.upper()}", fontsize=11, fontweight="bold",
                     color=MARROM)
            fig.text(0.42, y + 0.33, texto, fontsize=8.6, va="top", linespacing=1.55)
            if imagem and imagem.startswith("etapas"):
                fig.text(0.03, y - 0.005, "rosa = peças deste passo", fontsize=7, color=ROSA)
        pdf.savefig(fig)
        plt.close(fig)
        folha += 1
    return folha


def desenhar_regra_parafuso(fig, caixa_ax):
    ax = fig.add_axes(caixa_ax)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("regra do parafuso (corte)", fontsize=8, color="#555")
    ax.add_patch(Rectangle((0, 0), 15, 120, fc="#efe0cc", ec="#9b7b55"))      # painel que passa o parafuso
    ax.add_patch(Rectangle((15, 45), 110, 15, fc="#e2cfb3", ec="#9b7b55"))   # peça vizinha (borda)
    ax.add_patch(Polygon([(-1, 49.5), (5, 50.2), (5, 54.8), (-1, 55.5)], fc="#888"))   # cabeça escareada
    ax.add_patch(Rectangle((5, 51), 40, 3, fc="#888"))
    ax.plot([15, 50], [52.5, 52.5], ls="--", color=VERDE, lw=1.2)
    ax.text(-4, 75, "furo 4,5\n+ escareador", fontsize=7, ha="right")
    ax.text(55, 66, "pré-furo Ø3 × 35\nna borda", fontsize=7, color=VERDE)
    ax.text(7, 125, "peça de fora\n(L, F, D ou K)", fontsize=7, ha="center")
    ax.text(70, 30, "peça vizinha (borda)", fontsize=7, ha="center")
    ax.text(70, 5, "cola PU na borda", fontsize=7, ha="center", color=MARROM)
    ax.set_xlim(-60, 140)
    ax.set_ylim(-5, 150)


def guia_marca(pdf, folha, total):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Áreas de marca (para a gráfica) · Heroica + patrocinador", folha, total, doc="MONTAGEM")
    ax = fig.add_axes([0.03, 0.10, 0.94, 0.78])
    ax.set_aspect("equal")
    ax.axis("off")
    h_dj = m.Z_TAMPO + m.ABA_TRAS - m.Z0
    h_f = m.Z_FACHADA - m.Z0
    lat = [(0, 0), (m.L, 0), (m.L, h_f), (0, h_dj)]
    ax.add_patch(Polygon(lat, fc="#f1e1e5", ec=MARROM))
    ax.text(m.L / 2, h_dj * 0.62, "HEROICA", ha="center", fontsize=22, color=MARROM, fontweight="bold")
    ax.add_patch(Rectangle((m.L / 2 - 300, 120), 600, 160, fc="white", ec=ROSA, ls="--"))
    ax.text(m.L / 2, 200, "patrocinador\n600 × 160", ha="center", va="center", fontsize=8, color=ROSA)
    dz.cota_h(ax, 0, m.L, 0, off=-60)
    dz.cota_v(ax, 0, h_dj, 0, off=-50)
    dz.cota_v(ax, 0, h_f, m.L, off=40)
    ax.text(m.L / 2, -150, "LATERAL × 2 (vista de fora; a área acima do tampo é a aba)", ha="center", fontsize=8)
    x0 = m.L + 260
    ax.add_patch(Rectangle((x0, 0), m.WI, h_f, fc="#f1e1e5", ec=MARROM))
    ax.text(x0 + m.WI / 2, h_f * 0.70, "HEROICA", ha="center", fontsize=16, color=MARROM, fontweight="bold")
    ax.add_patch(Rectangle((x0 + 65, 120), m.WI - 130, 200, fc="white", ec=ROSA, ls="--"))
    ax.text(x0 + m.WI / 2, 220, f"patrocinador\n{m.WI - 130} × 200", ha="center", va="center", fontsize=8,
            color=ROSA)
    dz.cota_h(ax, x0, x0 + m.WI, 0, off=-60)
    dz.cota_v(ax, 0, h_f, x0 + m.WI, off=40)
    ax.text(x0 + m.WI / 2, -150, "FACHADA (frente para quem vem atrás)", ha="center", fontsize=8)
    x1 = x0 + m.WI + 200
    hd = m.Z_TAMPO - m.T - m.Z0
    pv = VAL["porta_vao_mm"]
    ax.add_patch(Rectangle((x1, 0), m.WI, hd, fc="#f1e1e5", ec=MARROM))
    for u0, u1, v0, v1 in m.vaos_porta():
        ax.add_patch(Rectangle((x1 + m.WI / 2 + u0, v0 - m.Z0), u1 - u0, v1 - v0, fc="white", ec=AZUL))
        ax.text(x1 + m.WI / 2 + (u0 + u1) / 2, (v0 + v1) / 2 - m.Z0, f"porta\n{pv[0]} × {pv[1]}",
                ha="center", va="center", fontsize=7, color=AZUL)
    dz.cota_h(ax, x1, x1 + m.WI, 0, off=-60)
    dz.cota_v(ax, 0, hd, x1 + m.WI, off=40)
    ax.text(x1 + m.WI / 2, -150, "PAINEL DO DJ", ha="center", fontsize=8)
    ax.set_xlim(-150, x1 + m.WI + 150)
    ax.set_ylim(-220, h_f + 80)
    fig.text(0.03, 0.06, "Vinil adesivo impresso e laminado (fosco), aplicado sobre a pintura curada (7 dias). "
             "Deixar 20 mm de margem das bordas e cabeças de parafuso. Áreas de patrocinador são sugestão.",
             fontsize=7.8)
    pdf.savefig(fig)
    plt.close(fig)


if __name__ == "__main__":
    tot_f = 3 + VAL["chapas_2200x1600"]
    arq_f = os.path.join(SAIDA, "Box_RunClub_v2_FABRICA.pdf")
    with PdfPages(arq_f) as pdf:
        fabrica_capa(pdf, tot_f)
        for n in range(1, VAL["chapas_2200x1600"] + 1):
            fabrica_chapa(pdf, n, 1 + n, tot_f)
        fabrica_pecas(pdf, tot_f - 1, tot_f)
        fabrica_pecas2(pdf, tot_f, tot_f)
    tot_g = 1 + (len(PASSOS) + 1) // 2 + 1
    arq_g = os.path.join(SAIDA, "Box_RunClub_v2_GUIA_DE_MONTAGEM.pdf")
    with PdfPages(arq_g) as pdf:
        guia_capa(pdf, tot_g)
        f = guia_passos(pdf, 2, tot_g)
        guia_marca(pdf, f, tot_g)
    print("ok", arq_f, arq_g)
