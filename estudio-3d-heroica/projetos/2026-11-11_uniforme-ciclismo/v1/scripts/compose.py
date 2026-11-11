import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
A = cv2.imread('full-1.png'); H, W = A.shape[:2]
J = cv2.imread('w/jersey.png', 0) > 0
S = cv2.imread('w/shorts.png', 0) > 0
C = cv2.imread('w/collar.png', 0) > 0
M = cv2.imread('w/suit2.png', 0) > 0
shJ = np.load('w/shJ.npy'); shS = np.load('w/shS.npy')
ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
def hx(h): h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], np.float32) / 255
PINK, PEACH, YEL = hx('#F7A3BC'), hx('#FFC39C'), hx('#FFE07A')
HOT, MARROM, WHITE = hx('#EF4F98'), hx('#3B2116'), np.ones(3, np.float32)
def lerp(a, b, t): return a[None, None] * (1 - t[..., None]) + b[None, None] * t[..., None]
def ss(e0, e1, x): t = np.clip((x - e0) / (e1 - e0), 0, 1); return t*t*(3-2*t)
# --- jersey design (RGB float)
front = xs < 1760
cx = np.where(front, 1420, 2215).astype(np.float32)
half = np.where(front, 250, 300).astype(np.float32)
d = np.abs(xs - cx) / half                        # 0 centre .. 1 torso edge .. >1 sleeves
t = np.clip(d / 1.45, 0, 1)
grad = np.where((t < 0.5)[..., None], lerp(PINK, PEACH, t / 0.5), lerp(PEACH, YEL, (t - 0.5) / 0.5))
# vertical shift: lower = warmer
grad = grad * 0.85 + lerp(PINK, YEL, ss(500, 1150, ys)) * 0.15
yfade = np.where(front, 1010, 980)
fade = ss(yfade, yfade + 170, ys) * (1 - ss(1.05, 1.25, d))   # torso fades to white, sleeves keep colour
design = grad * (1 - fade[..., None]) + WHITE[None, None] * fade[..., None]
# sleeve cuffs (yellow band) — bottom of sleeves
cuff = np.zeros((H, W), np.float32)
for (x0, x1, y0, y1, ang) in []: pass
design = design.astype(np.float32)
# --- wordmark alpha from back
wm = A[630:775, 1890:2370].astype(np.float32)
Gc = wm[..., 1]; bgG = np.percentile(Gc, 30)
a = np.clip((Gc - bgG - 8) / (245 - bgG - 8), 0, 1)
ys_, xs_ = np.where(a > 0.5); a = np.pad(a[ys_.min():ys_.max()+1, xs_.min():xs_.max()+1], 6)
cv2.imwrite('w/wm_alpha.png', (a*255).astype(np.uint8))
def place(layer_rgb, alpha_canvas, color, img_a, cx_, cy_, width, ang):
    h0, w0 = img_a.shape; s = width / w0
    big = cv2.resize(img_a, (int(w0*s), int(h0*s)), interpolation=cv2.INTER_CUBIC)
    Mx = cv2.getRotationMatrix2D((big.shape[1]/2, big.shape[0]/2), ang, 1.0)
    Mx[0, 2] += cx_ - big.shape[1]/2; Mx[1, 2] += cy_ - big.shape[0]/2
    al = cv2.warpAffine(big, Mx, (W, H))
    al = np.clip(al, 0, 1)
    layer_rgb[:] = layer_rgb * (1 - al[..., None]) + color[None, None] * al[..., None]
    alpha_canvas[:] = np.maximum(alpha_canvas, al)
dummy = np.zeros((H, W), np.float32)
# front: big marrom HEROICA across lower torso
place(design, dummy, MARROM, a, 1370, 1215, 500, 8)
# back: white HEROICA on gradient (upper back)
place(design, dummy, WHITE, a, 2195, 720, 520, 0)
# sleeves: yellow cuffs drawn as marrom small HEROICA on outer sleeves
place(design, dummy, MARROM, a, 1000, 870, 260, -88)
place(design, dummy, MARROM, a, 2575, 900, 260, 88)
# --- shorts design: hot pink + original text alpha recoloured marrom
L = cv2.cvtColor(A, cv2.COLOR_BGR2GRAY).astype(np.float32)
txt = np.clip((L - 70) / (200 - 70), 0, 1) * S
shorts_col = lerp(HOT, MARROM, txt)
# --- render
out = A.astype(np.float32)[..., ::-1] / 255
sj = shJ[..., None]
jr = design * sj
ssv = shS[..., None]
sv = np.power(np.clip(ssv, 0.05, 3), 0.75)
sr = shorts_col * np.minimum(sv, 1) * 0.97 + np.clip(sv - 1, 0, 1) * 0.10
out = np.where(J[..., None], jr, out)
out = np.where(S[..., None], sr, out)
# keep original smiley badges (back lower + front sleeve) and collar
keep = np.zeros((H, W), bool)
bd = (xs - 2187)**2 + (ys - 1222)**2 < 75**2
keep |= bd | ((ys > 1290) & (ys < 1352) & (xs > 2050) & (xs < 2300) & ~S)
orig = A.astype(np.float32)[..., ::-1] / 255
# badge on pink-ish? recolour ok - paste original
out = np.where(keep[..., None], orig, out)
# zipper redrawn (smooth line)
zl = np.zeros((H*4//4, W), np.uint8)
pz = [1.03677177e-04, -1.68335361e-01, 1.50962369e+03]
yy = np.arange(652, 1338, 2); xx = np.polyval(pz, yy)
pts = np.stack([xx*8, yy*8], 1).astype(np.int32)
cv2.polylines(zl, [pts], False, 255, 9, cv2.LINE_AA, shift=3)
za = (cv2.GaussianBlur(zl.astype(np.float32)/255, (0, 0), 0.7) * J)[..., None]
out = out * (1 - za) + np.array([0.1, 0.09, 0.09])[None, None] * za
# --- clean background
bgc = np.ones(3, np.float32)
# soft shadow under suit
sh = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 18)
base = np.ones((H, W, 3), np.float32) * (1 - 0.18 * sh[..., None])
Mf = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 0.8)[..., None]
final = base * (1 - Mf) + out * Mf
final = np.clip(final, 0, 1)
img = Image.fromarray((final * 255).astype(np.uint8))
# crop to suits with margin and add header
img = img.crop((450, 220, 3100, 2250))
Wc, Hc = img.size
canvas = Image.new('RGB', (Wc, Hc + 260), 'white'); canvas.paste(img, (0, 220))
dr = ImageDraw.Draw(canvas)
fb = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Black.otf', 92)
fs = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', 44)
fr = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Medium.otf', 38)
m = tuple(int(c*255) for c in MARROM)
dr.text((90, 80), 'HEROICA', font=fb, fill=m)
dr.text((560, 108), 'UNIFORME 2026 · CICLISMO', font=fs, fill=m)
dr.text((Wc - 90, 108), 'conceito 1 · frente e costas', font=fr, fill=(150, 120, 110), anchor='ra')
dr.line((90, 215, Wc - 90, 215), fill=m, width=4)
# palette chips
x0 = 90; y0 = Hc + 140
for nome, c in (('rosa', PINK), ('pêssego', PEACH), ('amarelo', YEL), ('rosa-choque', HOT), ('marrom', MARROM), ('branco', WHITE)):
    col = tuple(int(v*255) for v in c)
    dr.rounded_rectangle((x0, y0, x0 + 70, y0 + 70), 14, fill=col, outline=(210, 210, 210), width=2)
    dr.text((x0 + 88, y0 + 14), nome, font=fr, fill=(90, 70, 60)); x0 += 88 + int(dr.textlength(nome, font=fr)) + 70
canvas.save('w/uniforme_v1.png')
canvas.resize((Wc // 3, (Hc + 260) // 3)).save('w/uniforme_v1_small.png')
