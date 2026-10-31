"""
Pódio Heroica v1 — documentos: pacote SERRA (lista de cortes), pacote CNC (DXF + desenho) e GUIA.
Rode antes: podio_v1.py.     python documentos_v1.py
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
import podio_v1 as m  # noqa: E402

SAIDA = os.path.join(AQUI, "saida")
VAL = json.load(open(os.path.join(SAIDA, "validacao.json")))
LISTA = json.load(open(os.path.join(SAIDA, "lista_de_cortes.json")))
PECAS = {p["ref"]: p for p in json.load(open(os.path.join(SAIDA, "pecas.json")))}
DATA = "31/10/2026"
MARROM, ROSA, AZUL, VERDE = "#5E2129", "#C9607F", "#2346b0", "#1a8a3a"
TIT = "PÓDIO HEROICA · v1"
def ACAB_DE(ref):
    if ref[0] in "KP":
        return "madeira + verniz"
    return "marrom Heroica (RAL 3005)"


def cab(fig, sub, folha, tot, doc):
    dz.cabecalho(fig, TIT, sub, f"{doc} · folha {folha}/{tot} · medidas em mm", f"Heroica · {DATA}")


def img(fig, arq, caixa, titulo=None):
    ax = fig.add_axes(caixa)
    ax.imshow(plt.imread(os.path.join(SAIDA, arq)))
    ax.axis("off")
    if titulo:
        ax.set_title(titulo, fontsize=8, color="#555")


def capa_comum(fig):
    img(fig, "renders/render_frente.png", [0.01, 0.34, 0.36, 0.58], "montado")
    img(fig, "renders/render_led.png", [0.36, 0.34, 0.36, 0.58], "com LED")
    d, n = VAL["montado_mm"], VAL["aninhado_mm"]
    pk = VAL["peso_kg"]
    fig.text(0.03, 0.29, "O PÓDIO", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.03, 0.275,
             f"Montado: {d[0]} × {d[1]} (selo a {d[2]} de altura). Caixa 1 = balcão de degustação (mesa a {m.H1});\n"
             f"caixas 2 ({m.H2}) e 3 ({m.H3}) expõem produto. Para transporte, a 3 entra na 2 e a 2 entra na 1:\n"
             f"um volume só de {n[0]} × {n[1]} × {n[2]}.\n"
             f"Compensado 15 mm · caixa 1 ~{pk['caixa 1']:.0f} kg, caixa 2 ~{pk['caixa 2']:.0f} kg, caixa 3 ~{pk['caixa 3']:.0f} kg.",
             fontsize=8.2, va="top", linespacing=1.6)


# ---------------------------------------------------------------------------
# SERRA
# ---------------------------------------------------------------------------
def serra(pdf):
    tot = 2 + VAL["serra_chapas"]
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Pacote SERRA (esquadrejadeira) · só cortes retos", 1, tot, "SERRA")
    capa_comum(fig)
    fig.text(0.73, 0.89,
             "PARA O FORNECEDOR\n"
             "Compensado 15 mm (pinus/virola A/B),\n"
             f"chapa 2200 × 1600: {VAL['serra_chapas']} chapas.\n\n"
             "Todas as peças são RETANGULARES.\n"
             "Nenhum furo, rasgo ou encaixe na serra:\n"
             "os furos são feitos na montagem.\n\n"
             "• Medidas finais (já descontada a serra).\n"
             "• Plano de corte nas folhas seguintes,\n"
             "   em faixas (corte de ponta a ponta).\n"
             "• Tolerância ±0,5. Esquadro conferido.\n"
             "• Identificar cada peça com a letra\n"
             "   (lápis ou etiqueta) no verso.\n"
             "• O nº da referência é a caixa\n"
             "   (F1 = frente da caixa 1).",
             fontsize=7.8, va="top", linespacing=1.45)
    pdf.savefig(fig)
    plt.close(fig)

    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Lista de cortes", 2, tot, "SERRA")
    ax = fig.add_axes([0.04, 0.12, 0.92, 0.76])
    linhas = []
    total = 0
    for g in sorted(LISTA, key=lambda g: -g["comp"] * g["larg"]):
        linhas.append([g["ref"], g["nome"], str(g["qtd"]), f"{g['comp']} × {g['larg']}", ACAB_DE(g["ref"])])
        total += g["qtd"]
    dz.tabela(ax, linhas, ["Ref", "Peça", "Qtd", "Comprimento × largura (mm)", "Acabamento (Heroica)"],
              [0.07, 0.34, 0.08, 0.26, 0.25], fs=8)
    fig.text(0.04, 0.07, f"Total: {total} peças em {VAL['serra_chapas']} chapas de 15 mm. "
             "F2 e F3 incluem frente e fundo da caixa (por isso 2).", fontsize=8)
    pdf.savefig(fig)
    plt.close(fig)

    for n, ch in enumerate(VAL["serra_plano"], 1):
        fig = plt.figure(figsize=dz.A4_PAISAGEM)
        cab(fig, f"Plano de corte · chapa {n} (2200 × 1600 × 15) · corte de serra ~4", 2 + n, tot, "SERRA")
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
             f"Compensado 15 mm, 2200 × 1600: {VAL['cnc_chapas']} chapas.\n"
             "DXF em mm, escala 1:1.\n\n"
             "CAMADAS\n"
             "■ CORTE_INTERNO (azul): Ø28 da haste\n"
             "   (tampo e prateleira da 1) e Ø5 dos pinos.\n"
             "■ CORTE_EXTERNO (vermelho): contornos.\n"
             "■ FURO_GUIA_3 (verde): furos Ø3 passantes\n"
             "   nas linhas dos parafusos.\n"
             "■ TEXTO_NAO_CORTAR: letra da peça.\n\n"
             "• Fresa Ø6, microjuntas ok, ±0,3.\n"
             "• Bordas de 30 de largura: microjunta.",
             fontsize=7.8, va="top", linespacing=1.45)
    pdf.savefig(fig)
    plt.close(fig)
    for n, ch in enumerate(VAL["cnc_plano"], 1):
        fig = plt.figure(figsize=dz.A4_PAISAGEM)
        cab(fig, f"Plano de corte CNC · chapa {n} (2200 × 1600 × 15)", 1 + n, tot, "CNC")
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
MAT = [
    ["Peças cortadas (serra ou CNC) — ver lista de cortes", "fornecedor", "1 kit"],
    ["Cola PU + parafusos 4,0 × 40 (caixas) e 3,5 × 25 (bordas, por baixo do tampo)", "ferragens", "~150"],
    ["Pino suporte de prateleira Ø5 (prateleira da caixa 1)", "ferragens", "4"],
    [f"Tubo 1\" preto, 2 partes de ~{(m.Z_SELO - m.SELO_D / 2 + 40) / 2:.0f} + luva interna + ponteira", "alumínio", "1"],
    [f"Selo redondo Ø{m.SELO_D} em PVC expandido 10 mm, impresso (smile) + 2 abraçadeiras U 1\"", "gráfica", "1"],
    ["Números 1, 2, 3 + \"Celebre suas conquistas\" + QR em vinil recortado/impresso", "gráfica", "1 kit"],
    [f"Fita LED 5 V USB {m.W1 - 40} mm + perfil c/ difusor + power bank 20 000 mAh", "elétrica", "1"],
    ["Feltro adesivo para os pés das caixas (protege o piso da loja)", "ferragens", "12"],
    ["Fundo + esmalte marrom (RAL 3005) · verniz nos tampos e prateleira", "tintas", "—"],
]
PREP = [
    ("Caixa 1 (balcão)", "Frente F1 por fora das laterais L1 (cola + parafusos pela frente). Travessa S1 embaixo,\n"
     "no fundo, entre as laterais. Tampo K1 por cima, beiral de 40 para a frente. Furos dos pinos nas\n"
     f"laterais a {m.Z_PRAT1 - m.T - 8} do pé (Ø5)."),
    ("Caixas 2 e 3", "Frente e fundo (F) por fora das laterais (L). Tampo K por cima. Bordas: B na frente e C nos\n"
     "lados, coladas EM PÉ sobre o tampo e parafusadas por baixo (3,5 × 25). O fundo fica sem borda."),
    ("Conferir o encaixe", "Antes de pintar: a 3 tem que entrar na 2 e a 2 na 1 por baixo, com folga de ~10 de\n"
     "cada lado. Se pegar, lixe agora."),
    ("Pintura", "Caixas em marrom; tampos e prateleira com verniz. Lixar e selar as bordas do compensado."),
    ("Furos (só SERRA)", f"Tampo K1: Ø28 no centro, a 90 do fundo. Prateleira P1: Ø28 no centro, a "
     f"{m.D1 - 90 - m.T - 2:.0f} da frente.\nLaterais L1: 2 furos Ø5 a 60 da frente e a 60 do fundo, "
     f"{m.Z_PRAT1 - m.T - 8} do pé."),
    ("Marca", "Números em vinil nas frentes (1, 2, 3, altura ~45% da caixa), \"Celebre suas conquistas\" e QR\n"
     "na caixa 1. Selo: smile impresso no PVC, preso na haste com 2 abraçadeiras."),
    ("LED", "Perfil sob o beiral do tampo da 1, a 4 da borda; cabo pelo lado de dentro até o power bank\n"
     "na prateleira."),
]
PASSOS = [
    ("1", "Tirar as caixas", "etapas/etapa_1.png",
     "Levante a caixa 1 (2 pessoas, ~20 kg) e tire a 2 de dentro; tire a 3 de dentro da 2."),
    ("2", "Posicionar 2 – 1 – 3", "etapas/etapa_2.png",
     f"Caixa 2 à esquerda, 1 no meio, 3 à direita, frentes alinhadas, ~{m.VAO_PODIO} entre elas.\n"
     "Se o espaço for estreito: 2 e 3 lado a lado na frente e a 1 atrás (a degustação\n"
     "continua no 1º lugar)."),
    ("3", "Prateleira, haste e selo", "etapas/etapa_3.png",
     "4 pinos nos furos da caixa 1, prateleira por cima. Haste montada (2 partes) pelo furo\n"
     "do tampo e da prateleira até o chão. Selo na haste com as abraçadeiras."),
    ("4", "Produto e LED", "etapas/etapa_4.png",
     "Até 12 pacotes em pé em cima da 2 e da 3. Power bank na prateleira, ligar o LED.\n\n"
     "DESMONTAR: ao contrário. Não sentar nem subir nas caixas."),
]


def guia(pdf):
    tot = 2 + math.ceil(len(PASSOS) / 2) + 1
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Guia de montagem · materiais", 1, tot, "MONTAGEM")
    img(fig, "renders/transporte.png", [0.01, 0.20, 0.30, 0.60], "transporte: 3 dentro da 2, 2 dentro da 1")
    ax = fig.add_axes([0.33, 0.40, 0.65, 0.48])
    dz.tabela(ax, MAT, ["Item", "Onde", "Qtd"], [0.70, 0.15, 0.15], fs=7)
    fig.text(0.33, 0.35, "FERRAMENTAS", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.33, 0.33, "Oficina: parafusadeira, brocas 3 / 4,5 / 5, serra-copo 1 1/8\" (só no pacote serra), grampos.\n"
             "No PDV: sem ferramenta, ~5 min, 2 pessoas para tirar a caixa 1.",
             fontsize=8, va="top", linespacing=1.5)
    fig.text(0.33, 0.25, "MAPA", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.33, 0.23,
             "F frente/fundo   L lateral   K tampo   P1 prateleira   S1 travessa de fundo\n"
             "B borda da frente   C borda do lado   (o número = a caixa: 1, 2 ou 3)",
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
        cab(fig, "No PDV · montar em 4 passos", folha, tot, "MONTAGEM")
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
    for nome, w, h, txt in (("FRENTE CAIXA 2", m.W2, m.H2 - m.T, "2"), ("FRENTE CAIXA 1", m.W1, m.H1 - m.T,
                            "1\n\nCelebre suas conquistas\n+ QR"), ("FRENTE CAIXA 3", m.W3, m.H3 - m.T, "3"),
                            ("SELO (PVC)", m.SELO_D, m.SELO_D, "smile\nØ520")):
        ax.add_patch(Rectangle((x, 0), w, h, fc="#f1e1e5", ec=MARROM))
        ax.text(x + w / 2, h / 2, txt, ha="center", va="center", fontsize=10 if len(txt) < 3 else 8, color=MARROM)
        dz.cota_h(ax, x, x + w, 0, off=-50)
        dz.cota_v(ax, 0, h, x + w, off=30)
        ax.text(x + w / 2, -130, nome, ha="center", fontsize=8, fontweight="bold")
        x += w + 160
    ax.set_xlim(-80, x)
    ax.set_ylim(-200, m.H1 + 60)
    fig.text(0.05, 0.08, "Números em creme, altura ~45% da frente. Laterais lisas (ou patrocinador).", fontsize=8)
    pdf.savefig(fig)
    plt.close(fig)


if __name__ == "__main__":
    with PdfPages(os.path.join(SAIDA, "Podio_v1_SERRA_lista_de_cortes.pdf")) as pdf:
        serra(pdf)
    with PdfPages(os.path.join(SAIDA, "Podio_v1_CNC.pdf")) as pdf:
        cnc(pdf)
    with PdfPages(os.path.join(SAIDA, "Podio_v1_GUIA_DE_MONTAGEM.pdf")) as pdf:
        guia(pdf)
    print("ok")
