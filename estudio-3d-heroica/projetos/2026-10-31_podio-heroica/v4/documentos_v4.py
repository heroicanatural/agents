"""
Pódio Heroica v4 (desmontável/flat) — documentos: SERRA, CNC e GUIA (desmontado + montagem).
Rode antes: podio_v4.py.     python documentos_v4.py
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
import podio_v4 as m  # noqa: E402

SAIDA = os.path.join(AQUI, "saida")
VAL = json.load(open(os.path.join(SAIDA, "validacao.json")))
LISTA = json.load(open(os.path.join(SAIDA, "lista_de_cortes.json")))
PECAS = {p["ref"]: p for p in json.load(open(os.path.join(SAIDA, "pecas.json")))}
DATA = "09/11/2026"
MARROM, ROSA = "#5E2129", "#C9607F"
TIT = "PÓDIO HEROICA · v4 (desmontável)"
PK = VAL["pesos_kg"]


def cab(fig, sub, folha, tot, doc):
    dz.cabecalho(fig, TIT, sub, f"{doc} · folha {folha}/{tot} · medidas em mm", f"Heroica · {DATA}")


def img(fig, arq, caixa, titulo=None):
    ax = fig.add_axes(caixa)
    ax.imshow(plt.imread(os.path.join(SAIDA, arq)))
    ax.axis("off")
    if titulo:
        ax.set_title(titulo, fontsize=8, color="#555")


def acab(ref):
    if ref[0] in "KPAS":
        return "madeira + verniz" if ref[0] in "KP" else "madeira (oculta)"
    return "marrom Heroica (RAL 3005)"


def plano_desenho(pdf, ch, titulo, folha, tot, doc, com_furos=False):
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, titulo, folha, tot, doc)
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.80])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 2200, 1600, fc="#faf7f2", ec="#999"))
    for e in ch:
        ref, x, y, ang = e[:4]
        if com_furos:
            p = PECAS[ref]
            xs = [q[0] for q in p["contorno"]]
            ys = [q[1] for q in p["contorno"]]
            c = [(u - min(xs), v - min(ys)) for u, v in p["contorno"]]
            f = [(u - min(xs), v - min(ys), d) for u, v, d in p["furos"]]
            ca, sa = round(math.cos(math.radians(ang))), round(math.sin(math.radians(ang)))
            rot = [(u * ca - v * sa, u * sa + v * ca) for u, v in c]
            mx, my = min(q[0] for q in rot), min(q[1] for q in rot)
            bw, bh = max(q[0] for q in rot) - mx, max(q[1] for q in rot) - my
            dz.desenhar_peca(ax, c, [], f, mapa=(lambda u, v, x=x, y=y, ca=ca, sa=sa, mx=mx, my=my:
                                                (x + u * ca - v * sa - mx, y + u * sa + v * ca - my)))
        else:
            w, h = e[4], e[5]
            bw, bh = (h, w) if ang in (90, 270) else (w, h)
            ax.add_patch(Rectangle((x, y), bw, bh, fc="#efe0cc", ec="#9b7b55", lw=0.8))
        if min(bw, bh) > 45:
            ax.text(x + bw / 2, y + bh / 2, f"{ref}\n{max(bw, bh):.0f}×{min(bw, bh):.0f}" if min(bw, bh) > 120 else ref,
                    ha="center", va="center", fontsize=6.5, color="#5a4630", rotation=90 if bh > bw * 3 else 0)
    dz.cota_h(ax, 0, 2200, 1600, "2200", off=30)
    dz.cota_v(ax, 0, 1600, 0, "1600", off=-30)
    ax.set_xlim(-80, 2260)
    ax.set_ylim(-60, 1700)
    pdf.savefig(fig)
    plt.close(fig)


def capa(fig):
    img(fig, "renders/render_frente.png", [0.01, 0.33, 0.36, 0.58], "montado")
    img(fig, "renders/desmontado.png", [0.36, 0.33, 0.36, 0.58], "desmontado (pilha chata)")
    pm, pi = VAL["montado_mm"], VAL["pilha_mm"]
    fig.text(0.03, 0.28, "O PÓDIO", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.03, 0.265,
             f"Montado: {pm[0]} × {pm[1]}, selo a {pm[2]}. Desmontado: pilha de {pi[0]} × {pi[1]} × {pi[2]}.\n"
             "Cada caixa = CORPO dobrável (frente 15 + 2 laterais 9 em dobradiças) + TAMPO 15 com tacos por baixo.\n"
             f"Sem ferramenta no PDV. Total ~{VAL['peso_total_kg']:.0f} kg; peça mais pesada {VAL['maior_peca_kg']:.1f} kg.",
             fontsize=8.2, va="top", linespacing=1.6)


def serra(pdf):
    planos = [(e, c) for e in ("15", "9") for c in VAL["serra_plano"][e]]
    tot = 2 + len(planos)
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Pacote SERRA / SECCIONADORA · só cortes retos", 1, tot, "SERRA")
    capa(fig)
    fig.text(0.74, 0.89,
             "PARA O FORNECEDOR\n"
             "Compensado de PINUS 2200 × 1600:\n"
             f"{VAL['serra_chapas']['15']} chapa de 15 mm + {VAL['serra_chapas']['9']} chapa de 9 mm.\n\n"
             "Todas as peças são retangulares.\n"
             "Sem furos na serra (feitos na montagem).\n\n"
             "• Medidas finais (já descontada a serra).\n"
             "• Plano de corte em faixas nas folhas\n"
             "   seguintes; planilha CSV junto.\n"
             "• Tolerância ±0,5; esquadro conferido.\n"
             "• Identificar cada peça com a letra\n"
             "   (lápis ou etiqueta) no verso.",
             fontsize=7.8, va="top", linespacing=1.45)
    pdf.savefig(fig)
    plt.close(fig)
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Lista de cortes", 2, tot, "SERRA")
    ax = fig.add_axes([0.04, 0.10, 0.92, 0.80])
    linhas = [[g["ref"], g["nome"], str(g["qtd"]), f"{g['comp']} × {g['larg']} × {g['esp']}", acab(g["ref"])]
              for g in LISTA]
    dz.tabela(ax, linhas, ["Ref", "Peça", "Qtd", "Comp. × larg. × esp.", "Acabamento"],
              [0.07, 0.36, 0.07, 0.22, 0.28], fs=6.6)
    fig.text(0.04, 0.06, f"{sum(g['qtd'] for g in LISTA)} peças. Tacos (A): 4 por tampo = 2 tacos de 2 camadas coladas.",
             fontsize=8)
    pdf.savefig(fig)
    plt.close(fig)
    for n, (esp, ch) in enumerate(planos, 1):
        plano_desenho(pdf, ch, f"Plano de corte · chapa {n}: {esp} mm (2200 × 1600) · serra ~4", 2 + n, tot, "SERRA")


def cnc(pdf):
    planos = [(e, c) for e in ("15", "9") for c in VAL["cnc_plano"][e]]
    tot = 1 + len(planos)
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Pacote CNC · chapa_15mm_1.dxf e chapa_9mm_1.dxf", 1, tot, "CNC")
    capa(fig)
    fig.text(0.74, 0.89,
             "PARA O FORNECEDOR\n"
             f"Pinus 2200 × 1600: {VAL['cnc_chapas']['15']} × 15 mm + {VAL['cnc_chapas']['9']} × 9 mm.\n"
             "DXF em mm, escala 1:1.\n\n"
             "CAMADAS\n"
             "■ CORTE_INTERNO (azul): Ø28 da haste\n"
             "   (tampo e prateleira da 1) e Ø5 dos\n"
             "   pinos (laterais da 1). Cortar primeiro.\n"
             "■ CORTE_EXTERNO (vermelho): contornos.\n"
             "■ TEXTO_NAO_CORTAR: letra da peça.\n\n"
             "• Fresa Ø6, microjunta nas peças pequenas\n"
             "   (tacos 60 × 60, tiras e bordas de 30).",
             fontsize=7.8, va="top", linespacing=1.45)
    pdf.savefig(fig)
    plt.close(fig)
    for n, (esp, ch) in enumerate(planos, 1):
        plano_desenho(pdf, ch, f"Plano de corte CNC · chapa {n}: {esp} mm", 1 + n, tot, "CNC", com_furos=True)


MAT = [
    ["Peças cortadas (serra ou CNC) — ver lista de cortes", "fornecedor", "1 kit"],
    ["Dobradiça reta 3\" (76 mm) + parafusos 3,5 × 12 (curtos: não atravessam 9 mm)", "ferragens", "16"],
    ["Cola PU + parafusos 3,0 × 25 (tacos/travessa/bordas sob os tampos)", "ferragens", "~60"],
    ["Pino suporte de prateleira Ø5", "ferragens", "4"],
    [f"Tubo 1\" preto, 2 partes de ~{(m.Z_SELO - m.SELO_D / 2 + 40) / 2:.0f} + luva + ponteira", "alumínio", "1"],
    [f"Selo Ø{m.SELO_D} PVC expandido 10 mm impresso + 2 abraçadeiras U 1\"", "gráfica", "1"],
    ["Números 1, 2, 3 + \"Celebre suas conquistas\" + QR (vinil)", "gráfica", "1 kit"],
    [f"Fita LED 5 V USB {m.W1 - 40} + perfil c/ difusor + power bank 20 000 mAh", "elétrica", "1"],
    ["Feltro adesivo (pés dos corpos) · 2 cintas de velcro (prender os corpos dobrados)", "ferragens", "12 + 2"],
    ["Fundo + esmalte marrom (RAL 3005) · verniz nos tampos e prateleira", "tintas", "—"],
]
PREP = [
    ("Tira de batente", "Em cada frente, cole a tira R por DENTRO, na borda DIREITA (vista de trás é a esquerda),\n"
     "rente à borda e ao pé. É nela que a lateral direita (M) encosta e dobra por cima da esquerda."),
    ("Dobradiças", "Lateral esquerda L: encostada direto na frente. Lateral direita M (9 mais curta): encostada\n"
     "na tira. 3 dobradiças por lateral nas caixas 1 e 2 (a 100 do pé, no meio, a 130 do topo);\n"
     "2 na caixa 3 (a 90 do pé e do topo). Abas nas faces de DENTRO, eixo na quina.\n"
     "Teste: L dobra primeiro e deita na frente; M dobra por cima. Abertas, as duas param em 90°."),
    ("Tampos (sem medir)", "Monte o corpo aberto em 90° e apoie o tampo por cima, alinhado. Por baixo, cole e parafuse\n"
     "(3,0 × 25 de baixo para cima) os 2 tacos nas quinas da frente e a travessa S atrás, entre as\n"
     "laterais, com ~2 mm de folga. Assim eles ficam exatamente no lugar. Bordas B/C nos tampos 2 e 3."),
    ("Furos (só SERRA)", f"Tampo 1 e prateleira: Ø28 (serra-copo 1 1/8\") no centro, a 90 do fundo da caixa 1.\n"
     f"Laterais da 1: 2 furos Ø5 cada, a {m.Z_PRAT1 - m.T - 8} do pé (pinos da prateleira)."),
    ("Acabamento e marca", "Marrom nos corpos; verniz nos tampos e na prateleira. Números em vinil nas frentes;\n"
     "\"Celebre suas conquistas\" + QR na 1. LED sob o beiral do tampo 1."),
]
PASSOS = [
    ("1", "Abrir os corpos", "etapas/etapa_1.png",
     "Corpo em pé, frente para o cliente. Abra a lateral de cima (M) e depois a de baixo (L)\n"
     "até as duas pararem sozinhas em 90° (batente). Faça o mesmo nos corpos 2 e 3."),
    ("2", "Tampo", "etapas/etapa_2.png",
     "Desça o tampo sobre o corpo: os 2 tacos entram nas quinas da frente e a travessa entre\n"
     "as laterais, atrás. Pronto: a caixa travou no esquadro. Beiral do tampo 1 para a frente."),
    ("3", "Prateleira, haste e selo (caixa 1)", "etapas/etapa_3.png",
     "4 pinos nos furos das laterais da 1, prateleira por cima (furo para trás). Haste montada\n"
     "(2 partes) pelo furo do tampo e da prateleira até o chão. Selo na haste com as abraçadeiras.\n"
     "Power bank na prateleira, ligar o LED."),
    ("4", "Caixas 2 e 3", "etapas/etapa_4.png",
     "2 à esquerda, 1 no centro, 3 à direita, frentes alinhadas. Produto em cima da 2 e da 3;\n"
     "estoque e copinhos dentro delas (abertas atrás).\n\n"
     "DESMONTAR: tire produto, selo, haste e prateleira; levante os tampos; dobre L e depois M\n"
     "(por cima); feche cada corpo com a cinta de velcro."),
]


def guia(pdf):
    tot = 6
    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Guia · o que vem no kit e o que comprar", 1, tot, "MONTAGEM")
    img(fig, "renders/kit.png", [0.01, 0.30, 0.34, 0.60], "kit: 3 corpos dobrados + 3 tampos")
    ax = fig.add_axes([0.37, 0.42, 0.61, 0.48])
    dz.tabela(ax, MAT, ["Item", "Onde", "Qtd"], [0.70, 0.15, 0.15], fs=6.8)
    fig.text(0.37, 0.37, "MAPA", fontsize=9, fontweight="bold", color=MARROM)
    fig.text(0.37, 0.35, "F frente (15)  K tampo (15)  L lateral esquerda  M lateral direita  R tira de batente\n"
             "A taco  S travessa do tampo  B/C bordas  P1 prateleira   (número = caixa 1, 2 ou 3)",
             fontsize=8, va="top", family="DejaVu Sans Mono", linespacing=1.6)
    pdf.savefig(fig)
    plt.close(fig)

    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Desmontado · como o pódio viaja", 2, tot, "MONTAGEM")
    img(fig, "renders/desmontado.png", [0.01, 0.30, 0.46, 0.62], "pilha chata")
    img(fig, "etapas/corpo_dobrado.png", [0.48, 0.42, 0.24, 0.50], "corpo dobrado: M por cima de L")
    ax = fig.add_axes([0.74, 0.42, 0.24, 0.48])
    cd = VAL["corpo_dobrado_mm"]
    linhas = [[f"Corpo {n} (dobrado)", f"{cd[str(n)][0]} × {cd[str(n)][1]} × {cd[str(n)][2]}", f"{PK[f'corpo {n}']}"]
              for n in (1, 2, 3)]
    tb = {1: (m.W1 + 2 * m.BEIRAL_L, m.D1 + m.BEIRAL_F), 2: (m.W2, m.D2), 3: (m.W3, m.D3)}
    linhas += [[f"Tampo {n}", f"{tb[n][0]} × {tb[n][1]} × {VAL['pilha_alturas_mm'][f'tampo {n}']}", f"{PK[f'tampo {n}']}"]
               for n in (1, 2, 3)]
    linhas += [["Prateleira", f"{m.W1 - 2 * m.T - 4} × {m.D1 - m.TF - m.T - 30} × 9", f"{PK['prateleira']}"],
               ["Haste + selo + LED", "2 tubos ~84 · Ø52", "~1,5"]]
    dz.tabela(ax, linhas, ["Peça", "Medida", "kg"], [0.40, 0.42, 0.18], fs=6.6)
    pi = VAL["pilha_mm"]
    fig.text(0.04, 0.25,
             f"Tudo empilhado: {pi[0]} × {pi[1]} × {pi[2]} mm, ~{VAL['peso_total_kg']:.0f} kg — cabe deitado em qualquer porta-malas ou\n"
             f"banco traseiro. A peça mais pesada é o corpo 1 dobrado ({VAL['maior_peca_kg']:.1f} kg): a promotora carrega\n"
             "tudo sozinha, em 3–4 viagens curtas (ou de uma vez num carrinho dobrável, opcional).\n"
             "Ordem da pilha (de baixo para cima): corpos 1, 2, 3 · tampos 1, 2, 3 (tacos para cima) · prateleira.",
             fontsize=8.4, va="top", linespacing=1.6)
    pdf.savefig(fig)
    plt.close(fig)

    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Preparação na oficina · uma vez só", 3, tot, "MONTAGEM")
    y = 0.88
    for t, tx in PREP:
        fig.text(0.04, y, t.upper(), fontsize=9, fontweight="bold", color=MARROM, va="top")
        fig.text(0.24, y, tx, fontsize=8, va="top", linespacing=1.45)
        y -= 0.035 + 0.028 * (tx.count("\n") + 1)
    pdf.savefig(fig)
    plt.close(fig)

    for k in range(2):
        fig = plt.figure(figsize=dz.A4_PAISAGEM)
        cab(fig, "No PDV · montar em 4 passos (~5 min, sem ferramenta)", 4 + k, tot, "MONTAGEM")
        for j, (n, t, im, tx) in enumerate(PASSOS[2 * k:2 * k + 2]):
            yy = 0.50 - j * 0.45
            img(fig, im, [0.03, yy, 0.30, 0.40])
            fig.text(0.37, yy + 0.37, f"PASSO {n} · {t.upper()}", fontsize=11, fontweight="bold", color=MARROM)
            fig.text(0.37, yy + 0.33, tx, fontsize=8.6, va="top", linespacing=1.55)
            fig.text(0.03, yy - 0.005, "rosa = peças deste passo", fontsize=7, color=ROSA)
        pdf.savefig(fig)
        plt.close(fig)

    fig = plt.figure(figsize=dz.A4_PAISAGEM)
    cab(fig, "Áreas de arte (gráfica)", 6, tot, "MONTAGEM")
    ax = fig.add_axes([0.05, 0.15, 0.90, 0.70])
    ax.set_aspect("equal")
    ax.axis("off")
    x = 0
    for nome, w, h, txt in (("FRENTE CAIXA 2", m.W2, m.H2 - m.TF, "2"),
                            ("FRENTE CAIXA 1", m.W1, m.H1 - m.TF, "1\n\nCelebre suas conquistas\n+ QR"),
                            ("FRENTE CAIXA 3", m.W3, m.H3 - m.TF, "3"), ("SELO (PVC)", m.SELO_D, m.SELO_D, "smile")):
        ax.add_patch(Rectangle((x, 0), w, h, fc="#f1e1e5", ec=MARROM))
        ax.text(x + w / 2, h / 2, txt, ha="center", va="center", fontsize=10 if len(txt) < 3 else 8, color=MARROM)
        dz.cota_h(ax, x, x + w, 0, off=-50)
        dz.cota_v(ax, 0, h, x + w, off=30)
        ax.text(x + w / 2, -130, nome, ha="center", fontsize=8, fontweight="bold")
        x += w + 160
    ax.set_xlim(-80, x)
    ax.set_ylim(-200, m.H1 + 60)
    pdf.savefig(fig)
    plt.close(fig)


if __name__ == "__main__":
    with PdfPages(os.path.join(SAIDA, "Podio_v4_SERRA_lista_de_cortes.pdf")) as pdf:
        serra(pdf)
    with PdfPages(os.path.join(SAIDA, "Podio_v4_CNC.pdf")) as pdf:
        cnc(pdf)
    with PdfPages(os.path.join(SAIDA, "Podio_v4_GUIA_desmontado_e_montagem.pdf")) as pdf:
        guia(pdf)
    print("ok")
