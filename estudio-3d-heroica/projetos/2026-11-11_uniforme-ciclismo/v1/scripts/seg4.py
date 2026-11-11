import cv2, numpy as np, sys
T = float(sys.argv[1])
a = cv2.imread('full-1.png'); H, W = a.shape[:2]
y0, y1, x0, x1 = 400, 2150, 700, 2850
a = a[y0:y1, x0:x1]
g0 = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY).astype(np.float32)
lab = cv2.cvtColor(a, cv2.COLOR_BGR2LAB).astype(np.float32)
mag = 0
for c in range(3):
    ch = cv2.GaussianBlur(lab[..., c], (5, 5), 1.2)
    gx = cv2.Sobel(ch, cv2.CV_32F, 1, 0); gy = cv2.Sobel(ch, cv2.CV_32F, 0, 1)
    mag = np.maximum(mag, np.hypot(gx, gy) / 8 * (1 if c == 0 else 2))
bar = cv2.dilate((mag > T).astype(np.uint8), np.ones((3, 3), np.uint8))
free = 1 - bar
n, l = cv2.connectedComponents(free, connectivity=4)
mean = cv2.blur(g0, (7, 7)); sq = cv2.blur(g0*g0, (7, 7)); sd = np.sqrt(np.maximum(sq - mean*mean, 0))
seed = (g0 >= 254) | ((np.abs(g0 - 228) <= 1.5) & (sd < 0.6))
cnt = np.bincount(l.ravel(), minlength=n); sc = np.bincount(l.ravel(), weights=seed.ravel(), minlength=n)
bgids = np.where((sc / np.maximum(cnt, 1) > 0.3) & (cnt > 2000))[0]
bgids = bgids[bgids != 0]
bg = np.isin(l, bgids)
suit = (~bg).astype(np.uint8)
suit = cv2.morphologyEx(suit, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
n2, l2, st, _ = cv2.connectedComponentsWithStats(suit)
keep = [i for i in range(1, n2) if st[i, 4] > 100000]
print(T, [list(map(int, st[i])) for i in keep])
full = np.zeros((H, W), np.uint8)
for i in keep:
    m = (l2 == i).astype(np.uint8)*255
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    f = np.zeros_like(m); cv2.drawContours(f, cs, -1, 255, -1)
    full[y0:y1, x0:x1] |= f
cv2.imwrite('w/suit.png', full)
A = cv2.imread('full-1.png'); v = A.copy(); v[full == 0] = (0, 200, 0)
cv2.imwrite('w/suit_vis.jpg', cv2.resize(v, (W//3, H//3)))
