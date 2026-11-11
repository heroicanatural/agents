import cv2, numpy as np
from collections import deque
A = cv2.imread('full-1.png'); H, W = A.shape[:2]
m = cv2.imread('w/suit.png', 0) > 0
g = cv2.GaussianBlur(cv2.cvtColor(A, cv2.COLOR_BGR2GRAY), (3, 3), 0).astype(int)
hsv = cv2.cvtColor(A, cv2.COLOR_BGR2HSV); sat = hsv[..., 1].astype(int)
out = ~m
q = deque()
ys, xs = np.where(m & cv2.dilate(out.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool))
for y, x in zip(ys, xs): q.append((y, x))
removed = 0
while q:
    y, x = q.popleft()
    if out[y, x]: continue
    gp = g[y, x]
    if sat[y, x] > 12 or gp < 150: continue
    ok = False
    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
        yy, xx = y+dy, x+dx
        if out[yy, xx] and gp <= g[yy, xx] + 1: ok = True; break
    if ok:
        out[y, x] = True; removed += 1
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            yy, xx = y+dy, x+dx
            if not out[yy, xx]: q.append((yy, xx))
print('removed', removed)
mm = (~out).astype(np.uint8)
mm = cv2.morphologyEx(mm, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
cv2.imwrite('w/suit2.png', mm*255)
v = A.copy(); v[mm == 0] = (0, 200, 0)
cv2.imwrite('w/suit_vis2.jpg', cv2.resize(v, (W//3, H//3)))
cv2.imwrite('w/suit_vis2_zoom.png', v[420:1100, 1750:2700])
