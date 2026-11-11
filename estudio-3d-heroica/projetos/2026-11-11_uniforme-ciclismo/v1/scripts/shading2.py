import cv2, numpy as np
A = cv2.imread('full-1.png'); H, W = A.shape[:2]
J = cv2.imread('w/jersey.png', 0) > 0
S = cv2.imread('w/shorts.png', 0) > 0
Z = cv2.imread('w/zipper.png', 0) > 0
B, G, R = [A[..., i].astype(np.float32) for i in range(3)]
hsv = cv2.cvtColor(A, cv2.COLOR_BGR2HSV); sat = hsv[..., 1].astype(np.float32)
Zd = np.zeros_like(Z)
rg = cv2.medianBlur(np.clip(R - G, 0, 255).astype(np.uint8), 41).astype(np.float32)
letters = ((rg > 10) & (R - G < rg - 6)) | ((R - G > 10) & (R - G < 40) & (R > 238))
graf = J & ((R < 228) | (sat > 60) | letters) & ~Zd
graf = cv2.dilate(graf.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0
graf &= J
w = (J & ~graf & ~Zd).astype(np.float32)
out = R.copy(); hole = graf.copy()
for sig in (6, 15, 40, 100):
    num = cv2.GaussianBlur(R * w, (0, 0), sig); den = cv2.GaussianBlur(w, (0, 0), sig)
    fill = num / np.maximum(den, 1e-4)
    ok = hole & (den > 0.15)
    out[ok] = fill[ok]; hole &= ~ok
out[hole] = 245
# blend seam: smooth transition
sm = cv2.GaussianBlur(out, (0, 0), 2)
out = np.where(graf, sm, out)
shJ = np.clip(out / 250.0, 0, 1.03)
# shorts
L = cv2.cvtColor(A, cv2.COLOR_BGR2GRAY).astype(np.float32)
gS = S & (L > 70); gS = (cv2.dilate(gS.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0) & S
w = (S & ~gS).astype(np.float32); o = L.copy(); hole = gS.copy()
for sig in (6, 15, 40, 100):
    num = cv2.GaussianBlur(L * w, (0, 0), sig); den = cv2.GaussianBlur(w, (0, 0), sig)
    f = num / np.maximum(den, 1e-4); ok = hole & (den > (0.15 if sig < 100 else 0.005)); o[ok] = f[ok]; hole &= ~ok
# rim light at silhouette edge is real: keep L where near boundary and not text
shS = o / np.percentile(o[S], 60)
np.save('w/shJ.npy', shJ.astype(np.float32)); np.save('w/shS.npy', shS.astype(np.float32))
cv2.imwrite('w/shJc.jpg', cv2.resize((np.clip(shJ, 0, 1)*J*255 + np.clip(shS*0.45, 0, 1)*S*255).astype(np.uint8)[400:2120, 850:2750], None, fx=0.35, fy=0.35))
