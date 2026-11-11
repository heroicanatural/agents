import base64, io, math
from svgelements import SVG, Path
from PIL import Image, ImageDraw
import cairosvg

def paths(fn):
    out = {}
    for i, e in enumerate(SVG.parse(fn).elements()):
        if isinstance(e, Path) and len(e) > 0 and e.bbox() is not None:
            e.reify(); out[i] = (e.d(), e.bbox())
    return out
P4 = paths('p4.svg'); P1 = paths('p1.svg')
PIECES = {'lat_dir': 1, 'barriga': 3, 'manga_a': 5, 'bolsofr_a': 6, 'corpo': 8, 'bolso_a': 9, 'bolso_b': 10,
          'manga_b': 12, 'bolsofr_b': 13, 'lat_esq': 33}
LABELS = list(range(14, 33))
# wordmark: letters 255..261 of page 1
x0 = min(P1[i][1][0] for i in range(255, 262)); y0 = min(P1[i][1][1] for i in range(255, 262))
x1 = max(P1[i][1][2] for i in range(255, 262)); y1 = max(P1[i][1][3] for i in range(255, 262))
WM_W, WM_H = x1 - x0, y1 - y0
WM = ' '.join(P1[i][0] for i in range(255, 262))
def wordmark(cx, cy, width, rot, fill):
    s = width / WM_W
    return (f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s}) translate({-x0 - WM_W/2},{-y0 - WM_H/2})">'
            f'<path d="{WM}" fill="{fill}"/></g>')
# badge raster -> circle png (upright)
b = Image.open('badge300-5.png').convert('RGB').rotate(-90, expand=True)
w, h = b.size; cxp, cyp, r = w/2 - 2, h/2, 362
cxp, cyp = 382, 386  # centre after rotation (approx)
bb = b.crop((int(cxp - r), int(cyp - r), int(cxp + r), int(cyp + r)))
m = Image.new('L', bb.size, 0); ImageDraw.Draw(m).ellipse((2, 2, bb.size[0]-3, bb.size[1]-3), fill=255)
bb.putalpha(m); buf = io.BytesIO(); bb.save(buf, 'PNG'); bb.save('badge_clean.png')
BADGE = base64.b64encode(buf.getvalue()).decode()

PINK, PEACH, YEL, HOT, MARROM, WHITE = '#F5C7C8', '#F0CFC0', '#EAD7B9', '#C2236B', '#602221', '#FFFFFF'
BLEED = 28  # pt total stroke -> 14 pt (~5 mm) de sangria
defs, body = [], []
def lin(id_, x1, y1, x2, y2, stops):
    st = ''.join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    defs.append(f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>')
def fillp(d, paint, clip=None):
    c = f' clip-path="url(#{clip})"' if clip else ''
    return f'<path d="{d}" fill="{paint}" stroke="{paint}" stroke-width="{BLEED}" stroke-linejoin="round"{c}/>'
def clip(id_, d): defs.append(f'<clipPath id="{id_}"><path d="{d}"/></clipPath>')
def bleedclip(id_, d):  # clip = piece + bleed (via a mask of stroked path)
    defs.append(f'<mask id="{id_}" maskUnits="userSpaceOnUse" x="-100" y="-100" width="4200" height="2800"><path d="{d}" fill="#fff" stroke="#fff" stroke-width="{BLEED}" stroke-linejoin="round"/></mask>')
def grp(maskid, inner): return f'<g mask="url(#{maskid})">{inner}</g>'

G = 'stop'
GR = [(0, PINK, 1), (0.45, PEACH, 1), (1, YEL, 1)]
# ---------- CORPO (frentes + costas) ----------
d = P4[8][0]; bleedclip('m_corpo', d)
NX, NY = 1430, 730          # centro da gola
# costas: degradê horizontal a partir do centro
lin('g_back_l', NX, 0, NX - 520, 0, GR); lin('g_back_r', NX, 0, NX + 520, 0, GR)
# frentes: perpendicular ao meio da frente (aresta do zíper)
lin('g_fr_l', 1140, 290, 1140 - 0.888*430, 290 + 0.46*430, GR)
lin('g_fr_r', 1720, 290, 1720 + 0.888*430, 290 + 0.46*430, GR)
# fade para branco: costas (baixo) e frentes (perto da costura com a barriga)
lin('f_back', 0, 1060, 0, 1330, [(0, WHITE, 0), (1, WHITE, 1)])
lin('f_fr_l', 810 + 0.47*0, 120, 810 + 0.47*150, 120 + 0.88*150, [(0, WHITE, 1), (1, WHITE, 0)])
lin('f_fr_r', 2050, 120, 2050 - 0.47*150, 120 + 0.88*150, [(0, WHITE, 1), (1, WHITE, 0)])
inner = []
inner.append(f'<rect x="300" y="-60" width="{NX-300}" height="2000" fill="url(#g_back_l)"/>')
inner.append(f'<rect x="{NX}" y="-60" width="{2400-NX}" height="2000" fill="url(#g_back_r)"/>')
# frentes (acima da linha do ombro ~ y 620, separadas pela gola)
lin('mk_fr', 0, 540, 0, 760, [(0, WHITE, 1), (1, WHITE, 0)])
defs.append('<mask id="m_fr" maskUnits="userSpaceOnUse" x="0" y="-100" width="3000" height="1000"><rect x="0" y="-100" width="3000" height="1000" fill="url(#mk_fr)"/></mask>')
inner.append('<g mask="url(#m_fr)"><polygon points="300,-60 1430,-60 1430,800 300,800" fill="url(#g_fr_l)"/>'
             '<polygon points="1430,-60 2560,-60 2560,800 1430,800" fill="url(#g_fr_r)"/></g>')
# costura do ombro suavizada: faixa de transição
lin('g_sh', 0, 520, 0, 700, [(0, WHITE, 0), (1, WHITE, 0)])
inner.append('<rect x="300" y="-60" width="2200" height="2000" fill="url(#f_back)"/>')
inner.append('<polygon points="400,-60 1290,-60 1290,700 400,700" fill="url(#f_fr_l)"/>')
inner.append('<polygon points="1570,-60 2460,-60 2460,700 1570,700" fill="url(#f_fr_r)"/>')
inner.append(wordmark(NX, 1010, 430, 0, MARROM))
body.append(grp('m_corpo', ''.join(inner)))
# ---------- BARRIGA ----------
d = P4[3][0]; bleedclip('m_barriga', d)
body.append(grp('m_barriga', f'<rect x="1000" y="1880" width="960" height="720" fill="{WHITE}"/>' + wordmark(1478, 2120, 640, 0, MARROM)))
# ---------- MANGAS ----------
for k, idx, rot in (('a', 5, -90), ('b', 12, 90)):
    d, bb = P4[idx]; bleedclip(f'm_manga_{k}', d)
    cx = (bb[0] + bb[2]) / 2
    defs.append(f'<radialGradient id="g_manga_{k}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{bb[1]}" r="900">'
                f'<stop offset="0" stop-color="{PEACH}"/><stop offset="0.45" stop-color="{YEL}"/><stop offset="1" stop-color="{YEL}"/></radialGradient>')
    body.append(grp(f'm_manga_{k}', f'<rect x="{bb[0]-40}" y="{bb[1]-40}" width="{bb[2]-bb[0]+80}" height="{bb[3]-bb[1]+80}" fill="url(#g_manga_{k})"/>'
                    + wordmark(cx, 640, 470, rot, MARROM)))
# ---------- LATERAIS (tronco em cima, perna rosa-choque embaixo) ----------
CINTURA = 400   # pt a partir do topo da peça (conferir com a AR)
for k, idx, rot in (('dir', 1, -90), ('esq', 33, 90)):
    d, bb = P4[idx]; bleedclip(f'm_lat_{k}', d)
    cx = (bb[0] + bb[2]) / 2; ytop = bb[1]; yw = ytop + CINTURA
    lin(f'g_lat_{k}', 0, ytop, 0, yw, [(0, YEL, 1), (0.55, WHITE, 1), (1, WHITE, 1)])
    body.append(grp(f'm_lat_{k}',
        f'<rect x="{bb[0]-40}" y="{ytop-40}" width="{bb[2]-bb[0]+80}" height="{CINTURA+40}" fill="url(#g_lat_{k})"/>'
        f'<rect x="{bb[0]-40}" y="{yw}" width="{bb[2]-bb[0]+80}" height="{bb[3]-yw+40}" fill="{HOT}"/>'
        + wordmark(cx + (8 if k == 'dir' else -8), yw + (bb[3] - yw) / 2, 380, rot, MARROM)))
# ---------- BOLSOS ----------
for idx in (6, 9, 10, 13):
    d, bb = P4[idx]; bleedclip(f'm_b{idx}', d)
    inner = f'<rect x="{bb[0]-40}" y="{bb[1]-40}" width="{bb[2]-bb[0]+80}" height="{bb[3]-bb[1]+80}" fill="{WHITE}"/>'
    if idx == 9:
        cx = (bb[0] + bb[2]) / 2
        inner += f'<image x="{cx-85}" y="{bb[1]+45}" width="170" height="170" href="data:image/png;base64,{BADGE}"/>'
        inner += (f'<text x="{cx}" y="{bb[1]+300}" text-anchor="middle" font-family="Inter" font-weight="900" '
                  f'font-size="54" letter-spacing="4" fill="{MARROM}">SONHE.LUTE</text>')
    body.append(grp(f'm_b{idx}', inner))
# ---------- FACA (linha de corte, não imprime) ----------
faca = ''.join(f'<path d="{P4[i][0]}" fill="none" stroke="#00A0E0" stroke-width="2.5"/>' for i in PIECES.values())
labels = ''.join(f'<path d="{P4[i][0]}" fill="#00A0E0" fill-opacity="0.25"/>' for i in LABELS)
W, H = 3912.4701, 2585.7218
def doc(with_faca=True, mirror=False):
    content = ''.join(body)
    if with_faca: content += f'<g id="FACA_nao_imprimir">{faca}{labels}</g>'
    if mirror: content = f'<g transform="translate({W},0) scale(-1,1)">{content}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W*25.4/72:.1f}mm" height="{H*25.4/72:.1f}mm" viewBox="0 0 {W} {H}">'
            f'<defs>{"".join(defs)}</defs><rect width="{W}" height="{H}" fill="#fff"/>{content}</svg>')
import os; os.makedirs('out', exist_ok=True)
open('out/Heroica_uniforme_2026_v2_sublimacao_G.svg', 'w').write(doc(True))
cairosvg.svg2pdf(bytestring=doc(True).encode(), write_to='out/Heroica_uniforme_2026_v2_sublimacao_G_com_faca.pdf')
cairosvg.svg2pdf(bytestring=doc(False, mirror=True).encode(), write_to='out/Heroica_uniforme_2026_v2_sublimacao_G_espelhado_para_impressao.pdf')
cairosvg.svg2png(bytestring=doc(True).encode(), write_to='out/preview.png', output_width=2400)
print('ok', WM_W, WM_H)
