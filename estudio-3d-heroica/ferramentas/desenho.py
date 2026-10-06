"""Utilitários de prancha técnica (matplotlib): cotas, cabeçalho, tabela, polígonos de peças."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

A4_PAISAGEM = (11.69, 8.27)
A4_RETRATO = (8.27, 11.69)
MARROM = "#5E2129"


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


def cabecalho(fig, titulo, subtitulo, direita1="", direita2=""):
    fig.text(0.03, 0.965, titulo, fontsize=15, color=MARROM, fontweight="bold")
    fig.text(0.03, 0.937, subtitulo, fontsize=10.5, color="#333")
    fig.text(0.97, 0.965, direita1, fontsize=8, ha="right", color="#555")
    fig.text(0.97, 0.947, direita2, fontsize=8, ha="right", color="#555")
    fig.add_artist(plt.Line2D([0.03, 0.97], [0.927, 0.927], color=MARROM, lw=1))


def tabela(ax, linhas, cab, larguras, fs=7.5):
    ax.axis("off")
    t = ax.table(cellText=linhas, colLabels=cab, cellLoc="left", colWidths=larguras, bbox=[0, 0, 1, 1])
    t.auto_set_font_size(False)
    t.set_fontsize(fs)
    for (r, c), cel in t.get_celld().items():
        cel.set_edgecolor("#bbb")
        if r == 0:
            cel.set_facecolor("#f1e6e8")
            cel.set_text_props(fontweight="bold")
    return t


def desenhar_peca(ax, contorno, recortes=(), furos=(), fc="#efe0cc", ec="#9b7b55", mapa=None,
                  cor_furo_guia="#1a8a3a", cor_interno="#2346b0"):
    """Desenha a peça (contorno + recortes + furos). `mapa(u, v) -> (x, y)` posiciona na prancha."""
    mapa = mapa or (lambda u, v: (u, v))
    ax.add_patch(Polygon([mapa(*p) for p in contorno], closed=True, fc=fc, ec=ec, lw=0.8))
    for r in recortes:
        ax.add_patch(Polygon([mapa(*p) for p in r], closed=True, fc="white", ec=cor_interno, lw=0.8))
    for u, v, d in furos:
        x, y = mapa(u, v)
        if d <= 3:
            ax.add_patch(Circle((x, y), 6, fc=cor_furo_guia, ec="none"))
        else:
            ax.add_patch(Circle((x, y), d / 2, fc="white", ec=cor_interno, lw=0.7))
