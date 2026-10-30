"""
Balcão v3 — documentos: pacote SERRA (lista de cortes), pacote CNC (DXF + desenho) e GUIA de montagem.
Rode antes: balcao_v3.py.     python documentos_v3.py
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
import balcao_v3 as m  # noqa: E402

SAIDA = os.path.join(AQUI, "saida")
VAL = json.load(open(os.path.join(SAIDA, "validacao.json")))
LISTA = json.load(open(os.path.join(SAIDA, "lista_de_cortes.json")))
PECAS = {p["ref"]: p for p in json.load(open(os.path.join(SAIDA, "pecas.json")))}
DATA = "30/10/2026"
MARROM, ROSA, AZUL, VERDE = "#5E2129", "#C9607F", "#2346b0", "#1a8a3a"
TIT = "BALCÃO DE DEGUSTAÇÃO HEROICA · v3"
ACAB = {"F": "preto fosco", "L": "preto fosco", "B": "preto fosco", "Q": "preto fosco", "Rp": "preto fosco",
        "E": "preto fosco", "K": "madeira + verniz", "P1": "madeira + verniz", "P2": "madeira + verniz",
        "A": "madeira (oculto)", "R": "madeira + verniz", "M": "rosa / arte"}


def cab(fig, sub, folha, tot, doc):
    dz.cabecalho(fig, TIT, sub, f"{doc} · folha {folha}/{tot} · medidas em mm", f"Heroica · {DATA}")


def img(fig, arq, caixa, titulo=None):
    ax = fig.add_axes(caixa)
    ax.imshow(plt.imread(os.path.join(SAIDA, arq)))
    ax.axis("off")
    if titulo:
        ax.set_title(titulo, fontsize=8, color="#555")


def capa_comum(fig):
    img(fig, "renders/render_frente.png", [0.01, 0.30, 0.24, 0.62], "frente")
    img(fig, "renders/render_led.png", [0.24, 0.30, 0.24, 0.62], "com LED")
    img(fig, "renders/render_promotor.png", [0.47, 0.30, 0.24, 0.62], "lado do promotor")
    d = VAL["dimensoes_mm"]
    fig.text(0.03, 0.25, "O BALCÃO", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.03, 0.235,
             f"{d[0]} × {d[1]} × {d[2]} com bandeira · mesa a {m.Z_TAMPO} · corpo {m.LARG} × {m.PROF}\n"
             "Estética de expositor: estrutura e ripado pretos, tampo e prateleiras em madeira natural,\n"
             "placa da marca com halo de LED, LED sob o tampo, cantoneiras de alumínio pretas nas quinas.\n"
             f"Compensado 12 mm · ~{VAL['peso_compensado_kg']:.0f} kg · corpo dobra (~{VAL['dobrado_espessura_mm']} mm).",
             fontsize=8.2, va="top", linespacing=1.6)


# ---------------------------------------------------------------------------
# SERRA
# ---------------------------------------------------------------------------
def serra(pdf):
    tot = 2 + VAL["chapas_2200x1600"]
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Pacote SERRA (esquadrejadeira) · só cortes retos", 1, tot, "SERRA")
    capa_comum(fig)
    fig.text(0.73, 0.89,
             "PARA O FORNECEDOR\n"
             "Compensado 12 mm (pinus/virola A/B),\n"
             f"chapa 2200 × 1600: {VAL['chapas_2200x1600']} chapas.\n\n"
             "Todas as peças são RETANGULARES.\n"
             "Nenhum furo, rasgo ou encaixe na serra:\n"
             "os furos são feitos na montagem.\n\n"
             "• Medidas finais (já descontada a serra).\n"
             "• Plano de corte nas folhas seguintes,\n"
             "   em faixas (corte de ponta a ponta).\n"
             "• Tolerância ±0,5. Esquadro conferido.\n"
             "• Identificar cada peça com a letra\n"
             "   (lápis ou etiqueta) no verso.",
             fontsize=7.8, va="top", linespacing=1.45)
    pdf.savefig(fig)
    plt.close(fig)

    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Lista de cortes", 2, tot, "SERRA")
    ax = fig.add_axes([0.04, 0.12, 0.92, 0.76])
    linhas = []
    total = 0
    for g in sorted(LISTA, key=lambda g: -g["comp"] * g["larg"]):
        linhas.append([g["ref"], g["nome"], str(g["qtd"]), f"{g['comp']} × {g['larg']}", ACAB.get(g["ref"], "")])
        total += g["qtd"]
    dz.tabela(ax, linhas, ["Ref", "Peça", "Qtd", "Comprimento × largura (mm)", "Acabamento (Heroica)"],
              [0.07, 0.34, 0.08, 0.26, 0.25], fs=8)
    fig.text(0.04, 0.07, f"Total: {total} peças em {VAL['chapas_2200x1600']} chapas de 12 mm. "
             "Tacos (A) e travessas (R) são coladas em pares na montagem (por isso a quantidade dobrada).",
             fontsize=8)
    pdf.savefig(fig)
    plt.close(fig)

    for n, ch in enumerate(VAL["plano"], 1):
        fig = plt.figure(figsize=dz.A4_PAISAGEM)
        cab(fig, f"Plano de corte · chapa {n} (2200 × 1600 × 12) · corte de serra ~4", 2 + n, tot, "SERRA")
        ax = fig.add_axes([0.04, 0.08, 0.92, 0.80])
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(Rectangle((0, 0), 2200, 1600, fc="#faf7f2", ec="#999"))
        for ref, x, y, ang, w, h in ch:
            bw, bh = (h, w) if ang in (90, 270) else (w, h)
            ax.add_patch(Rectangle((x, y), bw, bh, fc="#efe0cc", ec="#9b7b55", lw=0.8))
            fs = 7 if min(bw, bh) > 80 else 4.5
            ax.text(x + bw / 2, y + bh / 2, f"{ref}\n{max(bw, bh):.0f}×{min(bw, bh):.0f}" if min(bw, bh) > 50 else ref,
                    ha="center", va="center", fontsize=fs, color="#5a4630", rotation=90 if bh > bw * 3 else 0)
        dz.cota_h(ax, 0, 2200, 1600, "2200", off=30)
        dz.cota_v(ax, 0, 1600, 0, "1600", off=-30)
        ax.set_xlim(-80, 2260)
        ax.set_ylim(-60, 1700)
        pdf.savefig(fig)
        plt.close(fig)


# ---------------------------------------------------------------------------
# CNC
# ---------------------------------------------------------------------------
def peca_local(ref):
    p = PECAS[ref]
    xs = [q[0] for q in p["contorno"]]
    ys = [q[1] for q in p["contorno"]]
    x0, y0 = min(xs), min(ys)
    return [(u - x0, v - y0) for u, v in p["contorno"]], [(u - x0, v - y0, d) for u, v, d in p["furos"]]


def cnc(pdf):
    tot = 1 + VAL["cnc_chapas"]
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Pacote CNC · arquivos chapa_1.dxf e chapa_2.dxf", 1, tot, "CNC")
    capa_comum(fig)
    fig.text(0.73, 0.89,
             "PARA O FORNECEDOR\n"
             f"Compensado 12 mm, 2200 × 1600: {VAL['cnc_chapas']} chapas.\n"
             "DXF em mm, escala 1:1.\n\n"
             "CAMADAS\n"
             "■ CORTE_INTERNO (azul): furos Ø28 das\n"
             "   hastes (4) e Ø10 do cabo (1). Primeiro.\n"
             "■ CORTE_EXTERNO (vermelho): contornos.\n"
             "■ FURO_GUIA_3 (verde): 50 furos Ø3\n"
             "   passantes (ripas e travessas).\n"
             "■ TEXTO_NAO_CORTAR: letra da peça.\n\n"
             "• Fresa Ø6, microjuntas ok, ±0,3.\n"
             "• Peças miúdas (tacos 60×60, espaçadores\n"
             "   40×40): usar microjunta para não soltar.",
             fontsize=7.8, va="top", linespacing=1.45)
    pdf.savefig(fig)
    plt.close(fig)
    for n, ch in enumerate(VAL["cnc_plano"], 1):
        fig = plt.figure(figsize=dz.A4_PAISAGEM)
        cab(fig, f"Plano de corte CNC · chapa {n} (2200 × 1600 × 12)", 1 + n, tot, "CNC")
        ax = fig.add_axes([0.04, 0.08, 0.92, 0.80])
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(Rectangle((0, 0), 2200, 1600, fc="#faf7f2", ec="#999"))
        for ref, x, y, ang in ch:
            c, f = peca_local(ref)
            ca, sa = round(math.cos(math.radians(ang))), round(math.sin(math.radians(ang)))
            rot = [(u * ca - v * sa, u * sa + v * ca) for u, v in c]
            mx, my = min(q[0] for q in rot), min(q[1] for q in rot)
            bw, bh = max(q[0] for q in rot) - mx, max(q[1] for q in rot) - my
            mapa = (lambda u, v, x=x, y=y, ca=ca, sa=sa, mx=mx, my=my:
                    (x + u * ca - v * sa - mx, y + u * sa + v * ca - my))
            dz.desenhar_peca(ax, c, [], f, mapa=mapa)
            if min(bw, bh) > 50:
                ax.text(x + bw / 2, y + bh / 2, ref, ha="center", va="center", fontsize=7, color="#5a4630",
                        rotation=90 if bh > bw * 3 else 0)
        dz.cota_h(ax, 0, 2200, 1600, "2200", off=30)
        dz.cota_v(ax, 0, 1600, 0, "1600", off=-30)
        ax.set_xlim(-80, 2260)
        ax.set_ylim(-60, 1700)
        pdf.savefig(fig)
        plt.close(fig)


# ---------------------------------------------------------------------------
# GUIA
# ---------------------------------------------------------------------------
H = VAL["haste_mm"] // 2
MAT = [
    ["Peças cortadas (serra ou CNC) — ver lista de cortes", "fornecedor", "1 kit"],
    ["Dobradiça reta 3\" preta + parafusos 3,5 × 16", "ferragens", "6"],
    [f"Cantoneira de alumínio preta 20 × 20 × {m.Z1 - m.Z0} (quinas da frente)", "alumínio", "2"],
    [f"Tubo de alumínio 1\" preto (ou pintado) — 4 × {H} + 2 luvas internas + 2 ponteiras", "alumínio", "1 barra 6 m"],
    ["Abraçadeira U 1\" com borboleta M6 (testeira)", "ferragens", "4"],
    ["Fita LED 5 V USB 4000 K: 800 (tampo) + ~1600 (volta da placa) + 2 perfis c/ difusor", "elétrica", "1 rolo 3 m"],
    ["Power bank 20 000 mAh + cabo USB em Y", "elétrica", "1"],
    ["Cola PU/branca, parafusos 3,5 × 30 (tacos, travessas) e 3,5 × 20 (ripas, por dentro)", "ferragens", "~80"],
    ["Fundo + preto fosco (spray ou rolo) · verniz para as peças em madeira", "tintas", "—"],
    ["Arte da placa (560 × 300) e da testeira (840 × 300)", "gráfica", "—"],
]
PREP = [
    ("Pintura", "Preto fosco: F, L, B, Q, ripas (Rp) e espaçadores (E). Verniz: K, P1, P2, travessas (R).\n"
     "Placa M: rosa ou adesivo da arte. Pintar antes de montar (ripas soltas pintam mais rápido)."),
    ("Ripado", f"19 ripas na frente, vão de {m.RIPA_VAO} entre elas (use um taco de 15 como gabarito), a 1ª\n"
     "rente à borda. Cola + 2 parafusos 3,5 × 20 POR DENTRO da frente (CNC: pelos furos-guia;\n"
     "serra: marque a 150 do pé e a 150 do topo, no centro de cada ripa)."),
    ("Placa + halo", "4 espaçadores colados atrás da placa (a 60 das laterais e 50 de cima/baixo). Fita LED\n"
     "em volta, por trás, virada para fora. Placa centralizada no ripado, centro a "
     f"{m.Z_PLACA - m.Z0} do pé da frente."),
    ("Travessas", f"Cole as travessas em pares (2 × 12 = 24). Nas laterais, por dentro, face de cima a "
     f"{m.Z_PRAT[0] - m.T - m.Z0} e {m.Z_PRAT[1] - m.T - m.Z0}\ndo pé, começando a 20 da borda da frente. Parafuse por fora (CNC: furos-guia).\n"),
    ("Dobradiças e quinas", "3 dobradiças por lateral (~100, ~450, ~800 do pé), lateral ENCOSTADA na frente (é o\n"
     "batente dos 90°). Cantoneiras pretas coladas nas 2 quinas da frente (sobre a ripa da ponta)."),
    ("Tacos (sem medir)", "Cole os tacos em pares. Monte o corpo aberto sobre a base: cole 4 tacos na base, nas\n"
     "quinas de DENTRO, encostados nos painéis (2 mm de folga). Faça o mesmo embaixo do tampo.\n"
     "Assim eles ficam exatamente no lugar, qualquer que seja o corte."),
    ("Furos (só se for SERRA)", f"Tampo: 2 furos Ø28 (serra-copo 1 1/8\") a {m.HASTE_X} do centro e a "
     f"{m.HASTE_Y + m.BEIRAL_FRENTE} da borda da frente.\nPrateleira de cima: os mesmos 2, a {m.HASTE_X} do centro "
     f"e a {m.HASTE_Y - m.T} da borda da frente.\nFrente: Ø10 a 45 da borda direita e 14 do topo (cabo do LED)."),
    ("LED do tampo", "Perfil sob o beiral da frente, a 4 da borda. Cabo pelo Ø10 até o power bank (prateleira\n"
     "de baixo), junto com o cabo do halo da placa (passa pelo mesmo furo)."),
]
PASSOS = [
    ("1", "Base no chão", "etapas/etapa_1.png", "Base B no chão, tacos para cima."),
    ("2", "Corpo aberto sobre a base", "etapas/etapa_2.png",
     "Abra as laterais até encostarem (90°) e desça o corpo sobre a base: os 4 tacos\n"
     "ficam por dentro das quinas e travam as laterais."),
    ("3", "Prateleiras", "etapas/etapa_3.png",
     "P1 embaixo e P2 (com furos, para trás) em cima, apoiadas nas travessas.\nLigue o power bank na de baixo."),
    ("4", "Tampo", "etapas/etapa_4.png",
     "Tampo com o beiral para a frente: os tacos de baixo dele entram nas quinas.\n"
     "O corpo fica travado em cima e embaixo."),
    ("5", "Hastes e bandeira", "etapas/etapa_5.png",
     f"Emende cada haste ({H} + {H}), passe pelo tampo e pela prateleira de cima até apoiar\n"
     "na de baixo. Testeira na frente das hastes, abraçadeiras, topo a 2 m.\n\n"
     "DESMONTAR: ao contrário. Transporte: corpo dobrado, tampo, base, 2 prateleiras,\n"
     "testeira, 4 tubos e o power bank."),
]


def guia(pdf):
    tot = 2 + math.ceil(len(PASSOS) / 2) + 1
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Guia de montagem · materiais", 1, tot, "MONTAGEM")
    img(fig, "renders/explodido.png", [0.01, 0.08, 0.30, 0.84], "peças (rosa = tacos, travessas e placa)")
    ax = fig.add_axes([0.33, 0.40, 0.65, 0.48])
    dz.tabela(ax, MAT, ["Item", "Onde", "Qtd"], [0.70, 0.15, 0.15], fs=7)
    fig.text(0.33, 0.35, "FERRAMENTAS", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.33, 0.33, "Parafusadeira, brocas 3 e 10, serra-copo 1 1/8\" (só no pacote serra), grampos, "
             "taco de 15 (gabarito do ripado).\nMontagem no PDV: sem ferramenta, ~5 min, 1 pessoa.",
             fontsize=8, va="top", linespacing=1.5)
    fig.text(0.33, 0.25, "MAPA", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.33, 0.23,
             "F frente  L lateral (2)  B base  K tampo  P1/P2 prateleiras  Q testeira\n"
             "Rp ripas (19)  M placa da marca  E espaçadores (4)  A tacos (8 pares)  R travessas (4 pares)",
             fontsize=8, va="top", family="DejaVu Sans Mono", linespacing=1.6)
    pdf.savefig(fig)
    plt.close(fig)

    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Preparação · uma vez só (oficina)", 2, tot, "MONTAGEM")
    y = 0.89
    for titulo, texto in PREP:
        texto = texto.rstrip("\n")
        fig.text(0.04, y, titulo.upper(), fontsize=9, fontweight="bold", color=MARROM, va="top")
        fig.text(0.25, y, texto, fontsize=8, va="top", linespacing=1.4)
        y -= 0.025 + 0.026 * (texto.count("\n") + 1)
    pdf.savefig(fig)
    plt.close(fig)

    folha = 3
    for i in range(0, len(PASSOS), 2):
        fig = plt.figure(figsize=dz.A4_PAISAGEM)
        cab(fig, "No PDV · montar em 5 passos", folha, tot, "MONTAGEM")
        for j, (n, t, im, tx) in enumerate(PASSOS[i:i + 2]):
            yy = 0.50 - j * 0.45
            img(fig, im, [0.03, yy, 0.30, 0.40])
            fig.text(0.37, yy + 0.37, f"PASSO {n} · {t.upper()}", fontsize=11, fontweight="bold", color=MARROM)
            fig.text(0.37, yy + 0.33, tx, fontsize=8.6, va="top", linespacing=1.55)
            fig.text(0.03, yy - 0.005, "rosa = peças deste passo", fontsize=7, color=ROSA)
        pdf.savefig(fig)
        plt.close(fig)
        folha += 1

    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Áreas de arte (gráfica)", folha, tot, "MONTAGEM")
    ax = fig.add_axes([0.05, 0.15, 0.90, 0.70])
    ax.set_aspect("equal")
    ax.axis("off")
    x = 0
    for nome, w, h, txt in (("PLACA DA MARCA (M)", *m.PLACA, "Heroica / produto\nfundo rosa"),
                            ("TESTEIRA (Q)", *m.TESTEIRA, "logo em rosa/branco\nsobre preto"),
                            ("LATERAL (L) × 2", m.L_LAT, m.Z1 - m.Z0, "preto liso ou\nadesivo patrocinador")):
        ax.add_patch(Rectangle((x, 0), w, h, fc="#f1e1e5", ec=MARROM))
        ax.text(x + w / 2, h / 2, txt, ha="center", va="center", fontsize=8, color=MARROM)
        dz.cota_h(ax, x, x + w, 0, off=-50)
        dz.cota_v(ax, 0, h, x + w, off=30)
        ax.text(x + w / 2, -130, nome, ha="center", fontsize=8, fontweight="bold")
        x += w + 200
    ax.set_xlim(-80, x)
    ax.set_ylim(-200, m.Z1 - m.Z0 + 60)
    fig.text(0.05, 0.08, "A frente é o ripado preto: sem adesivo. A marca fica na placa iluminada e na testeira.",
             fontsize=8)
    pdf.savefig(fig)
    plt.close(fig)


if __name__ == "__main__":
    with PdfPages(os.path.join(SAIDA, "Balcao_v3_SERRA_lista_de_cortes.pdf")) as pdf:
        serra(pdf)
    with PdfPages(os.path.join(SAIDA, "Balcao_v3_CNC.pdf")) as pdf:
        cnc(pdf)
    with PdfPages(os.path.join(SAIDA, "Balcao_v3_GUIA_DE_MONTAGEM.pdf")) as pdf:
        guia(pdf)
    print("ok")
