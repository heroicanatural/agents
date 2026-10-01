// Renderizador WebGL do Estúdio 3D (three.js + Chromium headless via Playwright).
// Uso: NODE_PATH="$(npm root -g):./node_modules" node render_cena.mjs cena.json pasta_saida
// cena.json: {largura, altura, fundo, pecas:[{cor, pos:[...], idx:[...], brilho?}], vistas:[{nome, pos, alvo, fov?}]}
// Gerado por biblioteca_heroica.cena_json(). Unidades em mm, Z para cima.
import { createRequire } from "module";
import fs from "fs";
import path from "path";

const require = createRequire(path.join(process.cwd(), "x.js"));
const { chromium } = require("playwright");
const threePath = require.resolve("three").replace(/three\.cjs$/, "three.module.min.js");

const [cenaArq, saida = "."] = process.argv.slice(2);
const cena = JSON.parse(fs.readFileSync(cenaArq, "utf8"));
fs.mkdirSync(saida, { recursive: true });

const html = `<!doctype html><html><body style="margin:0;background:${cena.fundo || "#f3efe9"}">
<script type="module">
import * as THREE from "http://local/three.js";
const cena = await (await fetch("http://local/cena.json")).json();
const W = cena.largura || 900, H = cena.altura || 1200;
const r = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
r.setSize(W, H); r.setPixelRatio(1);
r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
r.outputColorSpace = THREE.SRGBColorSpace;
r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.05;
document.body.appendChild(r.domElement);
const s = new THREE.Scene();
s.background = new THREE.Color(cena.fundo || "#f3efe9");
s.add(new THREE.HemisphereLight(0xffffff, 0xd8cfc4, 1.1));
const key = new THREE.DirectionalLight(0xffffff, 2.2);
key.position.set(-900, -1400, 2200); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -1200, right: 1200, top: 1200, bottom: -1200, near: 10, far: 6000 });
s.add(key);
const fill = new THREE.DirectionalLight(0xfff2e6, 0.6); fill.position.set(1400, -600, 900); s.add(fill);
const rim = new THREE.DirectionalLight(0xffffff, 0.8); rim.position.set(300, 1500, 1500); s.add(rim);
// chão que só recebe sombra
const chao = new THREE.Mesh(new THREE.PlaneGeometry(8000, 8000), new THREE.ShadowMaterial({ opacity: 0.18 }));
chao.receiveShadow = true; s.add(chao);
for (const p of cena.pecas) {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(p.pos, 3));
  g.setIndex(p.idx); g.computeVertexNormals();
  const m = p.brilho
    ? new THREE.MeshStandardMaterial({ color: p.cor, emissive: p.cor, emissiveIntensity: p.brilho, side: THREE.DoubleSide })
    : new THREE.MeshStandardMaterial({ color: p.cor, roughness: p.rugosidade ?? 0.6, metalness: p.metal ?? 0.1, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(g, m); mesh.castShadow = true; mesh.receiveShadow = true; s.add(mesh);
  if (p.luz) { // luz pontual (LED)
    const l = new THREE.PointLight(p.cor, p.luz, 700, 1.5); l.position.set(...p.luz_pos); s.add(l);
  }
}
window.renderVista = (v) => {
  const c = new THREE.PerspectiveCamera(v.fov || 30, W / H, 10, 20000);
  c.up.set(0, 0, 1); c.position.set(...v.pos); c.lookAt(...v.alvo);
  r.render(s, c); return r.domElement.toDataURL("image/png");
};
window.pronto = true;
</script></body></html>`;

const browser = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await browser.newPage();
page.on("console", (m) => { if (m.type() === "error") console.error(m.text()); });
await page.route("http://local/**", (route) => {
  const u = route.request().url();
  if (u.endsWith("three.js")) return route.fulfill({ path: threePath, contentType: "text/javascript" });
  if (u.endsWith("cena.json")) return route.fulfill({ path: cenaArq, contentType: "application/json" });
  return route.fulfill({ body: html, contentType: "text/html" });
});
await page.goto("http://local/index.html");
await page.waitForFunction(() => window.pronto === true, null, { timeout: 120000 });
for (const v of cena.vistas) {
  const url = await page.evaluate((v) => window.renderVista(v), v);
  const arq = path.join(saida, `${v.nome}.png`);
  fs.writeFileSync(arq, Buffer.from(url.split(",")[1], "base64"));
  console.log("ok", arq);
}
await browser.close();
