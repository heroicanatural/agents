import cv2, numpy as np
A = cv2.imread('full-1.png'); H, W = A.shape[:2]
M = cv2.imread('w/suit2.png', 0) > 0
g = cv2.cvtColor(A, cv2.COLOR_BGR2GRAY).astype(int)
hsv = cv2.cvtColor(A, cv2.COLOR_BGR2HSV); sat = hsv[..., 1].astype(int)
dark = (M & (g < 110)).astype(np.uint8)
op = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))
n, l, st, _ = cv2.connectedComponentsWithStats(op)
print([list(map(int, s)) for s in st[1:] if s[4] > 5000])
shorts = np.zeros((H, W), np.uint8); collar = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if st[i, 4] < 5000: continue
    comp = (l == i).astype(np.uint8)
    if st[i, 1] > 1100: shorts |= comp
    elif st[i, 1] < 600: collar |= comp
# include text on shorts: close + fill holes, limited to M
for name, m, k in (('shorts', shorts, 61), ('collar', collar, 9)):
    c = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    cs, _ = cv2.findContours(c, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    f = np.zeros_like(c); cv2.drawContours(f, cs, -1, 1, -1)
    f &= M.astype(np.uint8)
    cv2.imwrite(f'w/{name}.png', f*255)
    if name == 'shorts': shorts = f
    else: collar = f
ys = np.arange(H)[:, None]
dk = (shorts > 0)
top = np.where(dk.any(0), dk.argmax(0), H)
from scipy.ndimage import median_filter
top = median_filter(top, size=31)
shorts = (M & ((ys >= top[None, :]) | (ys > 1500))).astype(np.uint8)
cv2.imwrite('w/shorts.png', shorts*255)
xs = np.arange(W)[None, :]
zipper = (M & (g < 120) & (sat < 60) & (xs > 1430) & (xs < 1510) & (ys < 1345) & ~(shorts > 0) & ~(collar > 0)).astype(np.uint8)
cv2.imwrite('w/zipper.png', zipper*255)
jersey = M & ~(shorts > 0) & ~(collar > 0)
cv2.imwrite('w/jersey.png', jersey.astype(np.uint8)*255)
v = np.zeros_like(A); v[jersey] = (200, 200, 255); v[shorts > 0] = (60, 60, 200); v[collar > 0] = (0, 0, 0); v[zipper > 0] = (0, 255, 0)
cv2.imwrite('w/regions.jpg', cv2.resize(v, (W//3, H//3)))
