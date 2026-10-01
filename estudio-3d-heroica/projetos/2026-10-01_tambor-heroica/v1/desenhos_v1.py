"""
Tambor Heroica v1 — pacote do fornecedor: PDF com vistas cotadas + DXF 1:1 das peças de MDF.
Lê os parâmetros de tambor_v1.py (mude lá, rode os dois de novo).

Rodar (depois de tambor_v1.py):  python desenhos_v1.py
"""
import math
import os

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Arc, Circle, Polygon, Rectangle

import tambor_v1 as m

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "saida")
QTD = 4
import json
PESO = json.load(open(os.path.join(SAIDA, "validacao.json")))["peso_kg"]
MARROM, ROSA, CINZA = "#5E2129", "#C9607F", "#666666"
A4 = (11.69, 8.27)

# ---------------------------------------------------------------------------
# Medidas derivadas (todas vêm do modelo)
# ---------------------------------------------------------------------------
R_EXT = m.R_INT + m.T["chapa"]
CORDA_VAO = 2 * R_EXT * math.sin(math.radians(m.RECORTE_GRAUS / 2))
ARCO_VAO = math.radians(m.RECORTE_GRAUS) * R_EXT          # medida na fita, por fora
R_PRAT = m.R_INT - m.FOLGA_PAREDE
PROF_PRAT = R_PRAT - m.Y_FRENTE_PRAT
FRENTE_PRAT = 2 * math.sqrt(R_PRAT ** 2 - m.Y_FRENTE_PRAT ** 2)
Y_TEST = m.Y_FRENTE_PRAT - m.ESP_TEST
COMP_TEST = 2 * math.sqrt((R_PRAT - 1) ** 2 - Y_TEST ** 2)
Z_ARCO_SUP = m.RECORTE_Z[1] + m.AFASTAMENTO_REFORCO
Z_ARCO_INF = m.RECORTE_Z[0] - m.AFASTAMENTO_REFORCO - m.BARRA[0]
GRAUS_ARCO = m.RECORTE_GRAUS + 2 * m.SOBRA_ARCO_GRAUS
COMP_ARCO = math.radians(GRAUS_ARCO) * (m.R_INT - m.BARRA[1] / 2)
COMP_MONT = Z_ARCO_SUP - (Z_ARCO_INF + m.BARRA[0])
PERIM_VAO = 2 * (m.RECORTE_Z[1] - m.RECORTE_Z[0]) + 2 * math.radians(m.RECORTE_GRAUS) * R_EXT


# ---------------------------------------------------------------------------
# Cotas
# ---------------------------------------------------------------------------
def cota_h(ax, x0, x1, y, txt=None, off=0, cor="k", fs=8):
    ax.annotate("", (x0, y + off), (x1, y + off),
                arrowprops=dict(arrowstyle="<->", lw=0.7, color=cor, shrinkA=0, shrinkB=0))
    for x in (x0, x1):
        ax.plot([x, x], [y, y + off * 1.1 if off else y], lw=0.4, color=cor)
    ax.text((x0 + x1) / 2, y + off + (6 if off >= 0 else -6), txt or f"{abs(x1 - x0):.0f}",
            ha="center", va="bottom" if off >= 0 else "top", fontsize=fs, color=cor)


def cota_v(ax, y0, y1, x, txt=None, off=0, cor="k", fs=8):
    ax.annotate("", (x + off, y0), (x + off, y1),
                arrowprops=dict(arrowstyle="<->", lw=0.7, color=cor, shrinkA=0, shrinkB=0))
    for y in (y0, y1):
        ax.plot([x, x + off * 1.1 if off else x], [y, y], lw=0.4, color=cor)
    ax.text(x + off + (6 if off >= 0 else -6), (y0 + y1) / 2, txt or f"{abs(y1 - y0):.0f}",
            ha="left" if off >= 0 else "right", va="center", fontsize=fs, color=cor, rotation=90)


def prep(ax, titulo):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titulo, fontsize=10, color=MARROM, fontweight="bold", loc="left")


def cabecalho(fig, pagina, titulo):
    fig.text(0.03, 0.965, "TAMBOR HEROICA · v1", fontsize=15, color=MARROM, fontweight="bold")
    fig.text(0.03, 0.935, titulo, fontsize=11, color="#333")
    fig.text(0.97, 0.965, f"folha {pagina}/4 · medidas em mm · quantidade: {QTD} unidades",
             fontsize=8, ha="right", color="#555")
    fig.text(0.97, 0.945, "Heroica · Florianópolis · 01/10/2026", fontsize=8, ha="right", color="#555")
    fig.add_artist(plt.Line2D([0.03, 0.97], [0.925, 0.925], color=MARROM, lw=1))


def tabela(ax, linhas, cab, larguras, fs=7.5):
    ax.axis("off")
    t = ax.table(cellText=linhas, colLabels=cab, cellLoc="left", colWidths=larguras,
                 bbox=[0, 0, 1, 1])
    t.auto_set_font_size(False)
    t.set_fontsize(fs)
    for (r, c), cel in t.get_celld().items():
        cel.set_edgecolor("#bbb")
        if r == 0:
            cel.set_facecolor("#f1e6e8")
            cel.set_text_props(fontweight="bold")


# ---------------------------------------------------------------------------
# Folha 1 — capa
# ---------------------------------------------------------------------------
def folha_capa(pdf):
    fig = plt.figure(figsize=A4)
    cabecalho(fig, 1, "Visão geral · display de chão para PDV (tambor de aço 200 L recortado)")
    imgs = [("renders_cheio/render_frente.png", "com produto (granola 300 g)"),
            ("renders_cheio/render_iso.png", "isométrica"),
            ("renders_vazio/render_detalhe_vao.png", "vão, prateleiras e testeiras")]
    for i, (arq, leg) in enumerate(imgs):
        ax = fig.add_axes([0.03 + i * 0.215, 0.30, 0.21, 0.6])
        ax.imshow(plt.imread(os.path.join(SAIDA, arq)))
        ax.axis("off")
        ax.set_title(leg, fontsize=8, color="#555")
    txt = (
        "O QUE É\n"
        "Tambor de aço 200 L NOVO, recortado\n"
        "na frente (120°), com 2 prateleiras de MDF\n"
        "e tampo-bandeja rosa. Fica no chão da loja;\n"
        "topo e prateleiras expõem produto.\n\n"
        "QUEM FAZ O QUÊ\n"
        "• Serralheiro (folha 2): recorte, reforços,\n"
        "   cantoneiras, pintura eletrostática.\n"
        "• Marceneiro (folha 3): prateleiras,\n"
        "   testeiras, tampo laqueado.\n"
        "• Gráfica (folha 4): adesivos.\n"
        "• Heroica (folha 4): perfil de borracha,\n"
        "   LED, montagem final.\n\n"
        "CORES\n"
        "Externo: RAL 3005 (vinho ≈ #602221).\n"
        "Interno e tampo: rosa Heroica\n"
        "   (aprovar amostra; ref. RAL 3015).\n"
        "Prateleiras: MDF BP amadeirado claro."
    )
    fig.text(0.695, 0.88, txt, fontsize=8.2, va="top", family="DejaVu Sans", linespacing=1.45)
    ficha = (
        f"Ø tambor {m.T['d_ext']:.0f} × altura {m.ALTURA:.0f} (+{m.ESP_TAMPO + m.ESP_ANEL} tampo)\n"
        f"Vão: {CORDA_VAO:.0f} largura (corda) × {m.RECORTE_Z[1] - m.RECORTE_Z[0]} altura\n"
        f"Prateleiras: face de cima a {m.PRAT_TOPO_Z[0]} e {m.PRAT_TOPO_Z[1]} do chão\n"
        f"Topo de exposição a {m.ALTURA + m.ESP_TAMPO:.0f} do chão\n"
        f"Peso estimado vazio: ~{PESO:.0f} kg · capacidade: ~16 pacotes de granola"
    )
    fig.text(0.03, 0.25, "FICHA", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.03, 0.225, ficha, fontsize=8.2, va="top", linespacing=1.5)
    fig.text(0.40, 0.24, "ATENÇÃO", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.40, 0.225,
             "1. Medir o tambor comprado antes de cortar: Ø e altura variam ±10 mm por fabricante.\n"
             "   Se variar, avisar a Heroica: prateleiras e tampo são ajustados no modelo.\n"
             "2. Fazer 1 tambor piloto completo e aprovar antes dos outros 3.\n"
             "3. Nenhuma superfície tem contato direto com alimento (produto vai embalado).",
             fontsize=8.2, va="top", linespacing=1.5)
    pdf.savefig(fig)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Folha 2 — serralheria
# ---------------------------------------------------------------------------
def folha_serralheria(pdf):
    fig = plt.figure(figsize=A4)
    cabecalho(fig, 2, "Serralheria · recorte, reforço, apoios e pintura")

    # Vista frontal (elevação)
    ax = fig.add_axes([0.02, 0.08, 0.36, 0.82])
    prep(ax, "VISTA FRONTAL")
    r = m.T["d_ext"] / 2
    ax.add_patch(Rectangle((-r, 0), 2 * r, m.ALTURA, fill=False, lw=1.2))
    for z in m.T["frisos_z"]:
        ax.plot([-r, r], [z, z], lw=0.5, color=CINZA, ls="--")
    c = CORDA_VAO / 2
    ax.add_patch(Rectangle((-c, m.RECORTE_Z[0]), 2 * c, m.RECORTE_Z[1] - m.RECORTE_Z[0],
                           fill=True, fc="#f6e3e8", ec=ROSA, lw=1.4))
    # reforços (tracejado, por dentro)
    for z in (Z_ARCO_SUP, Z_ARCO_INF):
        ax.add_patch(Rectangle((-r + 8, z), 2 * r - 16, m.BARRA[0], fill=False, ls="--", lw=0.7, ec=CINZA))
    xm = c + m.AFASTAMENTO_REFORCO * math.cos(math.radians(30))
    for s in (-1, 1):
        ax.add_patch(Rectangle((s * xm - (m.BARRA[0] if s > 0 else 0) * 0, Z_ARCO_INF + m.BARRA[0]),
                               s * m.BARRA[0] * 0.87, COMP_MONT, fill=False, ls="--", lw=0.7, ec=CINZA))
    cota_h(ax, -r, r, m.ALTURA, f"Ø {m.T['d_ext']:.0f}", off=40)
    cota_h(ax, -c, c, m.RECORTE_Z[1], f"{CORDA_VAO:.0f} (corda)\n{ARCO_VAO:.0f} medido na fita, por fora",
           off=-60, cor=ROSA)
    cota_v(ax, 0, m.ALTURA, -r, off=-50)
    cota_v(ax, 0, m.RECORTE_Z[0], r, off=40)
    cota_v(ax, m.RECORTE_Z[0], m.RECORTE_Z[1], r, off=40, cor=ROSA)
    cota_v(ax, m.RECORTE_Z[1], m.ALTURA, r, off=40)
    ax.text(0, m.RECORTE_Z[0] + 260, "RECORTE\n(remover)", ha="center", fontsize=8, color=ROSA)
    ax.text(0, (m.RECORTE_Z[1] + m.ALTURA) / 2, "faixa do letreiro\n(não furar)", ha="center",
            va="center", fontsize=7, color="#555")
    ax.text(0, -60, "tracejado = reforço por dentro", ha="center", fontsize=7, color=CINZA)
    ax.set_xlim(-r - 120, r + 140)
    ax.set_ylim(-90, m.ALTURA + 130)

    # Planta (corte horizontal)
    ax = fig.add_axes([0.38, 0.42, 0.30, 0.48])
    prep(ax, "PLANTA (corte na altura das prateleiras)")
    ax.add_patch(Circle((0, 0), R_EXT, fill=False, lw=1.2))
    a0, a1 = -90 - m.RECORTE_GRAUS / 2, -90 + m.RECORTE_GRAUS / 2
    ax.add_patch(Arc((0, 0), 2 * R_EXT, 2 * R_EXT, theta1=a0, theta2=a1, lw=4, color="white"))
    ax.add_patch(Arc((0, 0), 2 * R_EXT, 2 * R_EXT, theta1=a0, theta2=a1, lw=1, color=ROSA, ls=":"))
    ax.add_patch(Arc((0, 0), 2 * (m.R_INT - 6), 2 * (m.R_INT - 6), theta1=a0 - m.SOBRA_ARCO_GRAUS,
                     theta2=a1 + m.SOBRA_ARCO_GRAUS, lw=2.2, color=CINZA))
    for a in (a0, a1):
        ax.plot([0, R_EXT * math.cos(math.radians(a))], [0, R_EXT * math.sin(math.radians(a))],
                lw=0.5, color=ROSA, ls="--")
    ax.add_patch(Arc((0, 0), 180, 180, theta1=a0, theta2=a1, color=ROSA, lw=0.8))
    ax.text(0, -120, f"{m.RECORTE_GRAUS}°", ha="center", color=ROSA, fontsize=9)
    ax.add_patch(Arc((0, 0), 2 * (m.R_INT - 6) + 60, 2 * (m.R_INT - 6) + 60, theta1=a0 - m.SOBRA_ARCO_GRAUS,
                     theta2=a0, color=CINZA, lw=0.6))
    ax.text(-R_EXT * 0.98, -R_EXT * 0.62, f"+{m.SOBRA_ARCO_GRAUS}°", fontsize=7, color=CINZA)
    # prateleira D
    ang = math.degrees(math.asin(m.Y_FRENTE_PRAT / R_PRAT))
    pts = [(R_PRAT * math.cos(math.radians(t)), R_PRAT * math.sin(math.radians(t)))
           for t in [ang + (180 - 2 * ang) * i / 60 for i in range(61)]]
    ax.add_patch(Polygon(pts, closed=True, fc="#efe0cc", ec="#9b7b55", lw=0.8))
    ax.add_patch(Rectangle((-COMP_TEST / 2, Y_TEST), COMP_TEST, m.ESP_TEST, fc="#d8b48a", ec="#9b7b55", lw=0.6))
    for a in m.ANGULOS_CANT:
        t = math.radians(a)
        ax.plot(m.R_INT * 0.93 * math.cos(t), m.R_INT * 0.93 * math.sin(t), marker="s", ms=6,
                color=MARROM)
    for s in (-1, 1):
        t = math.radians(-90 + s * (m.RECORTE_GRAUS / 2 + math.degrees((m.AFASTAMENTO_REFORCO + m.BARRA[0] / 2) / m.R_INT)))
        ax.plot(m.R_INT * 0.985 * math.cos(t), m.R_INT * 0.985 * math.sin(t), marker="|", ms=12,
                mew=3, color=CINZA)
    ax.text(0, 330, "FUNDO", ha="center", fontsize=7, color="#555")
    ax.text(0, -340, "FRENTE", ha="center", fontsize=8, fontweight="bold")
    ax.text(0, 60, "prateleira D\n(marceneiro)", ha="center", fontsize=7, color="#7a5c3a")
    ax.set_xlim(-360, 360)
    ax.set_ylim(-380, 360)
    fig.text(0.39, 0.415, "■ cantoneira de apoio (3 por prateleira: esquerda, fundo, direita)\n"
             "▬ arco de reforço (barra chata calandrada)   | montante de reforço",
             fontsize=7, color="#333", va="top")

    # Detalhe
    ax = fig.add_axes([0.69, 0.50, 0.29, 0.40])
    prep(ax, "DETALHE · borda do vão (vista de dentro)")
    ax.add_patch(Rectangle((0, 0), 140, 160, fc="#f3eded", ec=MARROM, lw=1))
    ax.add_patch(Rectangle((-80, 0), 80, 160, fc="white", ec=ROSA, lw=1, ls=":"))
    ax.add_patch(Rectangle((-6, 0), 10, 160, fc="#222"))
    ax.add_patch(Rectangle((m.AFASTAMENTO_REFORCO, 0), m.BARRA[0], 120, fc="#bbb", ec="k", lw=0.6))
    ax.add_patch(Rectangle((-80, 120), 220, m.BARRA[0], fc="#ccc", ec="k", lw=0.6, alpha=0.8))
    cota_h(ax, 0, m.AFASTAMENTO_REFORCO, 10, f"{m.AFASTAMENTO_REFORCO}", off=-25, fs=7)
    cota_h(ax, m.AFASTAMENTO_REFORCO, m.AFASTAMENTO_REFORCO + m.BARRA[0], 60, '1"', off=-25, fs=7)
    ax.text(-40, 60, "VÃO", ha="center", color=ROSA, fontsize=8)
    ax.text(-8, 175, "perfil U de borracha\n(canal 1,0–1,5 mm)", ha="center", fontsize=6.5)
    ax.text(90, 175, "barra chata 1\"×1/8\"\nsolda MIG ponteada\nou rebite 4,8 a cada 100",
            ha="center", fontsize=6.5)
    ax.set_xlim(-100, 170)
    ax.set_ylim(-30, 220)

    # Lista + instruções
    ax = fig.add_axes([0.69, 0.30, 0.29, 0.155])
    linhas = [
        ["Tambor 200 L novo, tampa fixa", "1", f"{QTD}", "—"],
        ['Barra chata 1"×1/8" calandr.', "2", f"{2 * QTD}", f"{COMP_ARCO:.0f} · R {m.R_INT:.0f}"],
        ['Barra chata 1"×1/8" reta', "2", f"{2 * QTD}", f"{COMP_MONT:.0f}"],
        ['Cantoneira 3/4"×1/8"', "6", f"{6 * QTD}", f"{m.COMP_CANT} · 2 furos Ø5"],
        ["Rebite de repuxo 4,8", "12", f"{12 * QTD}", "cantoneiras"],
    ]
    tabela(ax, linhas, ["Item", "/tb", "total", "medida"], [0.50, 0.08, 0.10, 0.32], fs=6.3)
    fig.text(0.69, 0.28,
             "SEQUÊNCIA\n"
             f"1. Marcar o vão: {ARCO_VAO:.0f} na fita, centrado na frente,\n"
             f"   de {m.RECORTE_Z[0]} a {m.RECORTE_Z[1]} do chão. Cortar e rebarbar.\n"
             f"2. Soldar os 2 arcos ({m.AFASTAMENTO_REFORCO} da borda) e os 2 montantes\n"
             "   entre eles (solda de topo). Tudo por dentro.\n"
             f"3. Cantoneiras: aba de cima a {m.PRAT_TOPO_Z[0] - m.ESP_PRAT} e {m.PRAT_TOPO_Z[1] - m.ESP_PRAT}\n"
             "   do chão, em 0°/90°/180° (esq., fundo, dir.). Rebitar\n"
             "   pelas pontas (o meio da peça fica ~3 mm da parede).\n"
             "4. Lixar cantos vivos. Pintura eletrostática:\n"
             "   fora RAL 3005; dentro rosa (amostra Heroica).\n"
             "5. Furar 4 × Ø5 na tampa do tambor p/ fixar o tampo.",
             fontsize=6.8, va="top", linespacing=1.4)
    pdf.savefig(fig)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Folha 3 — marcenaria
# ---------------------------------------------------------------------------
def folha_marcenaria(pdf):
    fig = plt.figure(figsize=A4)
    cabecalho(fig, 3, "Marcenaria · prateleiras em D, testeiras e tampo-bandeja")

    ax = fig.add_axes([0.02, 0.38, 0.40, 0.52])
    prep(ax, f"PRATELEIRA D · MDF {m.ESP_PRAT} BP amadeirado claro · {2 * QTD} peças")
    ang = math.degrees(math.asin(m.Y_FRENTE_PRAT / R_PRAT))
    pts = [(R_PRAT * math.cos(math.radians(t)), R_PRAT * math.sin(math.radians(t)))
           for t in [ang + (180 - 2 * ang) * i / 80 for i in range(81)]]
    ax.add_patch(Polygon(pts, closed=True, fc="#efe0cc", ec="#9b7b55", lw=1))
    ax.plot([0], [0], "+", color="k")
    cota_h(ax, -R_PRAT, R_PRAT, 0, f"Ø {2 * R_PRAT:.0f} (raio {R_PRAT:.1f})", off=R_PRAT + 40)
    cota_h(ax, -FRENTE_PRAT / 2, FRENTE_PRAT / 2, m.Y_FRENTE_PRAT, f"frente reta {FRENTE_PRAT:.0f}", off=-45)
    cota_v(ax, m.Y_FRENTE_PRAT, R_PRAT, R_PRAT, f"{PROF_PRAT:.0f}", off=40)
    cota_v(ax, m.Y_FRENTE_PRAT, 0, -R_PRAT, f"{-m.Y_FRENTE_PRAT:.0f} (centro → frente)", off=-30)
    ax.text(0, 120, "fita de borda na curva\n(fundo e laterais)", ha="center", fontsize=7.5)
    ax.text(0, m.Y_FRENTE_PRAT + 22, "frente: recebe a testeira (sem fita)", ha="center", fontsize=7)
    ax.set_xlim(-R_PRAT - 90, R_PRAT + 100)
    ax.set_ylim(m.Y_FRENTE_PRAT - 110, R_PRAT + 90)

    ax = fig.add_axes([0.02, 0.10, 0.40, 0.24])
    prep(ax, f"TESTEIRA · MDF {m.ESP_TEST} BP · {2 * QTD} peças (vista de frente e corte)")
    ax.add_patch(Rectangle((0, 0), COMP_TEST, m.ALT_TEST, fc="#d8b48a", ec="#9b7b55"))
    ax.add_patch(Rectangle((COMP_TEST / 2 - 60, 6), 120, m.ALT_TEST - 12, fc="white", ec="#999", lw=0.5))
    ax.text(COMP_TEST / 2, m.ALT_TEST / 2, "porta-etiqueta / QR", ha="center", va="center", fontsize=6)
    cota_h(ax, 0, COMP_TEST, 0, f"{COMP_TEST:.0f}", off=-25)
    cota_v(ax, 0, m.ALT_TEST, COMP_TEST, f"{m.ALT_TEST}", off=20)
    x0 = COMP_TEST + 90
    ax.add_patch(Rectangle((x0, 0), m.ESP_TEST, m.ALT_TEST, fc="#d8b48a", ec="#9b7b55"))
    ax.add_patch(Rectangle((x0 + m.ESP_TEST, 0), 70, m.ESP_PRAT, fc="#efe0cc", ec="#9b7b55"))
    cota_v(ax, m.ESP_PRAT, m.ALT_TEST, x0, f"{m.ALT_TEST - m.ESP_PRAT}", off=-12, fs=7)
    ax.text(x0 + 40, m.ESP_PRAT + 8, "prateleira", fontsize=6.5)
    ax.text(x0 + 40, -22, "2 parafusos 4×40\npela testeira", fontsize=6.5, va="top")
    ax.set_xlim(-30, x0 + 140)
    ax.set_ylim(-70, m.ALT_TEST + 50)

    ax = fig.add_axes([0.45, 0.45, 0.53, 0.45])
    prep(ax, "TAMPO-BANDEJA · corte (laca rosa Heroica) · 4 conjuntos")
    rt = m.D_TAMPO / 2
    ax.add_patch(Rectangle((-rt, 0), m.D_TAMPO, m.ESP_TAMPO, fc="#f1c7d4", ec=ROSA))
    for s in (-1, 1):
        ax.add_patch(Rectangle((s * rt - (m.LARG_ANEL if s > 0 else 0), m.ESP_TAMPO), m.LARG_ANEL,
                               m.ESP_ANEL, fc="#f1c7d4", ec=ROSA))
    ax.add_patch(Rectangle((-m.D_CENTRAGEM / 2, -m.ESP_CENTRAGEM), m.D_CENTRAGEM, m.ESP_CENTRAGEM,
                           fc="#eee", ec="#999"))
    # tambor por baixo
    ax.plot([-m.T["d_ext"] / 2, -m.T["d_ext"] / 2, m.T["d_ext"] / 2, m.T["d_ext"] / 2],
            [-80, 0, 0, -80], color=MARROM, lw=1.5)
    ax.plot([-m.R_INT, m.R_INT], [-10, -10], color=MARROM, lw=0.8, ls="--")
    cota_h(ax, -rt, rt, m.ESP_TAMPO + m.ESP_ANEL, f"Ø {m.D_TAMPO}", off=30)
    cota_h(ax, rt - m.LARG_ANEL, rt, m.ESP_TAMPO + m.ESP_ANEL, f"{m.LARG_ANEL}", off=10, fs=7)
    cota_h(ax, -m.D_CENTRAGEM / 2, m.D_CENTRAGEM / 2, -m.ESP_CENTRAGEM, f"Ø {m.D_CENTRAGEM} (centragem)",
           off=-40)
    cota_v(ax, 0, m.ESP_TAMPO + m.ESP_ANEL, -rt, f"{m.ESP_TAMPO}+{m.ESP_ANEL}", off=-15, fs=7)
    ax.text(0, m.ESP_TAMPO + 30, "anel colado e grampeado sobre o disco: borda que segura o produto",
            ha="center", fontsize=7)
    ax.text(rt + 20, -50, "bordão do\ntambor", fontsize=7, color=MARROM)
    ax.text(0, -95, "disco de centragem: encaixa dentro do bordão. Medir o tambor e ajustar (folga 5 mm).\n"
            "Fixação: 4 parafusos sextavados 3/16\" × 1\" de baixo para cima, pela tampa do tambor.",
            ha="center", fontsize=7, va="top")
    ax.set_xlim(-rt - 70, rt + 90)
    ax.set_ylim(-150, 110)

    ax = fig.add_axes([0.45, 0.24, 0.53, 0.17])
    linhas = [
        ["Prateleira D", f"MDF {m.ESP_PRAT} BP amadeirado claro", f"Ø{2 * R_PRAT:.0f} cortado a {PROF_PRAT:.0f}",
         "2", f"{2 * QTD}", "fita na curva"],
        ["Testeira", f"MDF {m.ESP_TEST} BP amadeirado claro", f"{COMP_TEST:.0f} × {m.ALT_TEST}", "2", f"{2 * QTD}",
         "fita nas 4 bordas"],
        ["Tampo (disco)", f"MDF {m.ESP_TAMPO} p/ laca", f"Ø{m.D_TAMPO}", "1", f"{QTD}", "laca rosa"],
        ["Anel do tampo", f"MDF {m.ESP_ANEL} p/ laca", f"Ø{m.D_TAMPO}/Ø{m.D_TAMPO - 2 * m.LARG_ANEL}", "1",
         f"{QTD}", "laca rosa"],
        ["Centragem", f"MDF {m.ESP_CENTRAGEM} cru", f"Ø{m.D_CENTRAGEM}", "1", f"{QTD}", "sem acabamento"],
    ]
    tabela(ax, linhas, ["Peça", "Material", "Medida", "/tambor", "total", "Acabamento"],
           [0.15, 0.29, 0.21, 0.09, 0.08, 0.18])
    fig.text(0.45, 0.20,
             "Arquivos DXF 1:1 de todas as peças (para CNC/tupia com gabarito) vão junto: dxf/*.dxf\n"
             "Laca: rosa Heroica, mesma amostra aprovada para o interior do tambor.\n"
             "Prateleiras entram no tambor de pé pelo vão e giram lá dentro (testado no modelo:\n"
             f"vão de {m.RECORTE_Z[1] - m.RECORTE_Z[0]} de altura > {2 * R_PRAT:.0f} da prateleira).",
             fontsize=7.2, va="top", linespacing=1.45)
    pdf.savefig(fig)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Folha 4 — gráfica, compras e montagem
# ---------------------------------------------------------------------------
def folha_montagem(pdf):
    fig = plt.figure(figsize=A4)
    cabecalho(fig, 4, "Gráfica · compras · montagem final")
    ax = fig.add_axes([0.03, 0.70, 0.94, 0.19])
    linhas = [
        ["Letreiro HEROICA (arco, faixa de cima)", "vinil branco recortado", "altura de letra 80; ~420 de largura",
         f"{QTD}", "Pilcrow Rounded Heavy; centro a 800"],
        ["Moldura do vão", "vinil rosa recortado", f"faixa de 30 em volta do vão (perímetro ≈ {PERIM_VAO:.0f})",
         f"{QTD}", "pode ser em 4 tiras"],
        ["Selo 'Celebre suas conquistas'", "vinil impresso + laminação", "Ø200", f"{2 * QTD}",
         "laterais esq./dir., centro a 470 do chão"],
        ["QR code + cupom", "vinil impresso", "100 × 100", f"{QTD}", "lateral, abaixo de um selo"],
        ["Etiqueta de preço/QR p/ testeira", "papel ou vinil", f"até {COMP_TEST - 20:.0f} × {m.ALT_TEST - 12}",
         f"{2 * QTD}", "trocável pelo lojista"],
    ]
    tabela(ax, linhas, ["Adesivo", "Material", "Medida", "qtd total", "Obs."], [0.25, 0.17, 0.28, 0.08, 0.22])
    ax2 = fig.add_axes([0.03, 0.52, 0.94, 0.12])
    linhas = [
        ["Perfil U de borracha EPDM preto, canal 1,0–1,5 mm", f"{PERIM_VAO / 1000:.1f} m + 10%",
         f"{math.ceil(PERIM_VAO * 1.1 * QTD / 1000)} m", "contorno do vão"],
        ["Barra LED magnética recarregável USB-C, sensor de presença, ~30 cm, 4000 K",
         "2", f"{2 * QTD}", "sob a tampa e sob a prateleira de cima"],
        ["Pé nivelador ou feltro adesivo Ø40", "4", f"{4 * QTD}", "protege o piso da loja"],
    ]
    tabela(ax2, linhas, ["Compra (Heroica)", "/tambor", "total", "uso"], [0.50, 0.12, 0.10, 0.28])
    fig.text(0.03, 0.45,
             "MONTAGEM FINAL (depois da pintura curada, 24 h)\n"
             "1. Aplicar o perfil U em todo o contorno do vão (começar no meio da base, emenda embaixo).\n"
             "2. Prateleira de baixo: entrar de pé pelo vão, girar e apoiar nas 3 cantoneiras. Depois, a de cima.\n"
             "   Parafusar a testeira na frente de cada prateleira (2 parafusos 4×40).\n"
             "3. Encaixar o tampo (disco de centragem dentro do bordão) e fixar com 4 parafusos por dentro.\n"
             "4. Aplicar os adesivos: letreiro, moldura, selos e QR. Superfície limpa com álcool isopropílico.\n"
             "5. LED: colar a chapinha metálica sob a prateleira de cima; a outra barra gruda direto na tampa\n"
             "   de aço. Deixar no modo sensor. Ensinar o lojista a recarregar (USB-C).\n"
             "6. Teste: carregar com produto, empurrar o topo de lado e conferir se não balança.",
             fontsize=7.8, va="top", linespacing=1.5)
    pdf.savefig(fig)
    plt.close(fig)


def dxf_pecas():
    """DXF 1:1 (mm) das peças de MDF, um arquivo por peça."""
    pasta = os.path.join(SAIDA, "dxf")
    os.makedirs(pasta, exist_ok=True)
    ang = math.asin(m.Y_FRENTE_PRAT / R_PRAT)
    p1 = (R_PRAT * math.cos(ang), m.Y_FRENTE_PRAT)
    p2 = (-R_PRAT * math.cos(ang), m.Y_FRENTE_PRAT)
    pecas = {
        "prateleira_D": cq.Workplane("XY").moveTo(*p1).threePointArc((0, R_PRAT), p2).close(),
        "testeira": cq.Workplane("XY").rect(COMP_TEST, m.ALT_TEST),
        "tampo_disco": cq.Workplane("XY").circle(m.D_TAMPO / 2),
        "tampo_anel": cq.Workplane("XY").circle(m.D_TAMPO / 2).circle(m.D_TAMPO / 2 - m.LARG_ANEL),
        "disco_centragem": cq.Workplane("XY").circle(m.D_CENTRAGEM / 2),
    }
    for nome, wp in pecas.items():
        cq.exporters.export(wp.extrude(1).faces("<Z"), os.path.join(pasta, f"{nome}.dxf"))
    return list(pecas)


if __name__ == "__main__":
    arq = os.path.join(SAIDA, "Tambor_Heroica_v1_fornecedores.pdf")
    with PdfPages(arq) as pdf:
        folha_capa(pdf)
        folha_serralheria(pdf)
        folha_marcenaria(pdf)
        folha_montagem(pdf)
    print("ok", arq, dxf_pecas())
