"""
Biblioteca de módulos paramétricos do Estúdio 3D da Heroica.

Unidades em milímetros. Requer: pip install cadquery
A Heroica não tem impressora nem oficina: o alvo principal é serralheria, marcenaria
e laser/CNC terceirizados. Peças de fabricação são criadas como `Peca` (nome, material,
quantidade) para que a lista de corte, o aproveitamento e o peso saiam do próprio modelo.
Os módulos de encaixe (berços, slot, pino) servem para laser, CNC ou bureau de impressão 3D.

Uso rápido:
    python biblioteca_heroica.py   # gera e valida a demonstração em ./saida_demo
"""

import math
import os
from dataclasses import dataclass

import cadquery as cq

# ---------------------------------------------------------------------------
# CALIBRAÇÃO: ajuste aqui depois de cada teste real de impressão/corte.
# ---------------------------------------------------------------------------
CALIBRACAO = {
    # oficina
    "tolerancia_serralheria": 1.0,
    "perda_serra_mm": 4.0,      # por corte, marcenaria e serralheria
    "barra_mm": 6000,           # barra padrão de tubo/cantoneira
    "chapa_mdf_mm": (2750, 1850),
    "folga_produto_flexivel": 5.0,  # por lado, embalagem tipo pacote (granola)
    # encaixes (laser, CNC, bureau 3D)
    "folga_deslizante": 0.25,   # encaixe que entra e sai com a mão
    "folga_justa": 0.10,        # encaixe por pressão
    "folga_parafuso": 0.30,     # somar ao diâmetro nominal do parafuso
    "chanfre_base": 0.6,        # compensa pé de elefante
    "parede_min_fdm": 1.2,
    "parede_estrutural": 2.0,
    "kerf_laser": 0.15,
}


# Produtos com medida informada (mm, largura × altura × profundidade).
PRODUTOS = {
    "granola_300g": (160, 240, 80),   # informado pelo Roberto em 01/10/2026
}

# Materiais de estoque (mm) e densidades (g/cm³) para peso estimado.
METALON = [(20, 20), (25, 25), (30, 30), (40, 40), (20, 30), (30, 50), (20, 40)]
PAREDES_TUBO = [1.2, 1.5, 2.0]
ESPESSURAS_MDF = [3, 6, 9, 12, 15, 18, 25]
DENSIDADE = {"aco": 7.85, "mdf": 0.75, "acrilico": 1.19, "pla": 1.24}


# ---------------------------------------------------------------------------
# Peças de fabricação (serralheria e marcenaria)
# ---------------------------------------------------------------------------
@dataclass
class Peca:
    """Uma peça física da lista de corte. `solido` já posicionado na montagem."""
    nome: str
    solido: cq.Workplane
    material: str           # ex.: "metalon 20x20 #1,2" ou "MDF 18 BP branco"
    familia: str            # "tubo" | "chapa"
    medidas: tuple          # tubo: (comprimento,) ; chapa: (comprimento, largura, espessura)
    densidade: float
    quantidade: int = 1
    obs: str = ""           # fita de borda, corte 45°, furação...

    def peso_kg(self):
        return self.solido.val().Volume() / 1000 * self.densidade / 1000 * self.quantidade


def tubo(nome, comprimento, secao=(20, 20), parede=1.2, eixo="X", posicao=(0, 0, 0),
         quantidade=1, obs="corte reto"):
    """Metalon (tubo retangular) de estoque. Começa em `posicao` e cresce ao longo de `eixo`."""
    if tuple(secao) not in METALON and tuple(secao[::-1]) not in METALON:
        print(f"aviso: metalon {secao} não está na lista de estoque comum")
    a, b = secao
    # seção vazada: retângulo externo menos o interno, extrudado ao longo de X
    perfil = cq.Workplane("YZ").rect(a, b).rect(a - 2 * parede, b - 2 * parede).extrude(comprimento)
    rot = {"X": ((0, 0, 1), 0), "Y": ((0, 0, 1), 90), "Z": ((0, 1, 0), -90)}[eixo]
    solido = perfil.rotate((0, 0, 0), rot[0], rot[1]).translate(posicao)
    return Peca(nome, solido, f"metalon {a}x{b} #{str(parede).replace('.', ',')}", "tubo",
                (round(comprimento, 1),), DENSIDADE["aco"], quantidade, obs)


def chapa(nome, comprimento, largura, espessura=18, material="MDF", posicao=(0, 0, 0),
          plano="XY", quantidade=1, obs=""):
    """Painel retangular (MDF, compensado, acrílico, chapa de aço).

    plano: "XY" deitado (prateleira/base), "XZ" em pé de frente (fundo/frente),
    "YZ" em pé de lado (lateral). `posicao` é o canto de menor coordenada.
    """
    mat = material.lower()
    if mat.startswith("mdf") and espessura not in ESPESSURAS_MDF:
        print(f"aviso: MDF {espessura} mm não é espessura de estoque comum")
    dims = {"XY": (comprimento, largura, espessura), "XZ": (comprimento, espessura, largura),
            "YZ": (espessura, comprimento, largura)}[plano]
    solido = cq.Workplane("XY").box(*dims, centered=False).translate(posicao)
    dens = next((v for k, v in DENSIDADE.items() if mat.startswith(k)), DENSIDADE["mdf"])
    if mat.startswith(("chapa", "aco", "aço")):
        dens = DENSIDADE["aco"]
    return Peca(nome, solido, f"{material} {espessura} mm", "chapa",
                (round(comprimento, 1), round(largura, 1), espessura), dens, quantidade, obs)


def montar(pecas):
    """Une todos os sólidos (para render, validação e vistas)."""
    total = pecas[0].solido
    for p in pecas[1:]:
        total = total.union(p.solido)
    return total


def lista_de_corte(pecas):
    """Tabela Markdown da lista de corte, pronta para o PDF/WhatsApp do fornecedor."""
    linhas = ["| Peça | Qtd | Material | Medida (mm) | Obs. |", "|---|---|---|---|---|"]
    for p in pecas:
        med = " × ".join(f"{m:g}" for m in p.medidas)
        linhas.append(f"| {p.nome} | {p.quantidade} | {p.material} | {med} | {p.obs} |")
    return "\n".join(linhas)


def aproveitamento(pecas):
    """Quantas barras de 6 m (por perfil) e qual área de chapa (por material) a peça consome."""
    perda, barra = CALIBRACAO["perda_serra_mm"], CALIBRACAO["barra_mm"]
    res = {}
    tubos = {}
    for p in pecas:
        if p.familia == "tubo":
            tubos.setdefault(p.material, []).extend([p.medidas[0]] * p.quantidade)
    for mat, cortes in tubos.items():
        barras = []  # first-fit decreasing
        for c in sorted(cortes, reverse=True):
            for i, livre in enumerate(barras):
                if livre >= c + perda:
                    barras[i] -= c + perda
                    break
            else:
                barras.append(barra - c - perda)
        res[mat] = {"barras_6m": len(barras), "metros_usados": round(sum(cortes) / 1000, 2)}
    cl, cw = CALIBRACAO["chapa_mdf_mm"]
    for p in pecas:
        if p.familia == "chapa":
            r = res.setdefault(p.material, {"area_m2": 0.0})
            r["area_m2"] += p.medidas[0] * p.medidas[1] * p.quantidade / 1e6
    for mat, r in res.items():
        if "area_m2" in r:
            r["area_m2"] = round(r["area_m2"], 3)
            if mat.lower().startswith("mdf"):
                # estimativa grosseira: 80% de aproveitamento da chapa inteira
                r["chapas_inteiras_aprox"] = math.ceil(r["area_m2"] / (cl * cw / 1e6 * 0.8))
    return res


def interferencias(pecas, tolerancia_mm3=1.0):
    """Pares de peças que ocupam o mesmo espaço (erro de montagem). Lista de (a, b, mm³)."""
    conflitos = []
    for i in range(len(pecas)):
        for j in range(i + 1, len(pecas)):
            try:
                v = pecas[i].solido.intersect(pecas[j].solido).val().Volume()
            except Exception:
                v = 0.0
            if v > tolerancia_mm3:
                conflitos.append((pecas[i].nome, pecas[j].nome, round(v)))
    return conflitos


def peso_total_kg(pecas):
    return round(sum(p.peso_kg() for p in pecas), 2)


def vistas_svg(peca, nome, pasta="."):
    """Exporta vistas frente, lateral, topo e isométrica em SVG (base do desenho cotado)."""
    os.makedirs(pasta, exist_ok=True)
    vistas = {"frente": (0, -1, 0), "lateral": (1, 0, 0), "topo": (0, 0, 1),
              "iso": (1, -1, 0.8)}
    for v, d in vistas.items():
        cq.exporters.export(peca, os.path.join(pasta, f"{nome}_{v}.svg"),
                            opt={"projectionDir": d, "showHidden": v != "iso",
                                 "width": 600, "height": 450, "marginLeft": 20, "marginTop": 20})


# ---------------------------------------------------------------------------
# Tambor de aço 200 L (ISO 15750) — base do expositor "Tambor Heroica"
# ---------------------------------------------------------------------------
TAMBOR_200L = {
    "d_ext": 585.0,      # sobre os frisos/bordões
    "d_int": 571.5,
    "altura": 880.0,
    "chapa": 1.0,        # corpo 0,9–1,2 mm conforme fabricante
    "frisos_z": (293.0, 587.0),
}


def setor(raio, graus, z0, z1, centro=-90.0):
    """Fatia (vista de cima) centrada em `centro` graus (−90 = frente, lado −Y), entre z0 e z1."""
    a0, a1 = math.radians(centro - graus / 2), math.radians(centro + graus / 2)
    n = max(8, int(graus / 4))
    pts = [(0, 0)] + [(raio * math.cos(a0 + (a1 - a0) * i / n), raio * math.sin(a0 + (a1 - a0) * i / n))
                      for i in range(n + 1)]
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def tambor_200l(recorte_graus=0.0, recorte_z=(140.0, 720.0), t=TAMBOR_200L):
    """Casco do tambor (corpo + frisos + tampa) com recorte frontal opcional.

    Retorna (casco, pedaco_recortado). O pedaço é o que sai no corte (útil como porta).
    """
    r_ext, r_int = t["d_int"] / 2 + t["chapa"], t["d_int"] / 2
    casco = cq.Workplane("XY").circle(r_ext).circle(r_int).extrude(t["altura"])
    for z in t["frisos_z"]:
        casco = casco.union(cq.Workplane("XY").workplane(offset=z - 6)
                            .circle(t["d_ext"] / 2).circle(r_int).extrude(12))
    # fundo e tampa (tampa fixa ~10 mm abaixo do bordão)
    casco = casco.union(cq.Workplane("XY").workplane(offset=8).circle(r_int).extrude(t["chapa"]))
    casco = casco.union(cq.Workplane("XY").workplane(offset=t["altura"] - 10).circle(r_int)
                        .extrude(t["chapa"]))
    pedaco = None
    if recorte_graus:
        faca = setor(t["d_ext"], recorte_graus, *recorte_z)
        pedaco = casco.intersect(faca)
        casco = casco.cut(faca)
    return casco, pedaco


# ---------------------------------------------------------------------------
# Encaixes e berços para produto
# ---------------------------------------------------------------------------
def berco_retangular(largura, profundidade, altura, parede=None, folga=None,
                     altura_frente=None, raio_canto=2.0):
    """Berço aberto em cima para embalagem retangular (sachê, caixa, Heroiquinhas).

    largura/profundidade: medidas externas do produto.
    altura: altura total da parede traseira e laterais.
    altura_frente: parede frontal mais baixa para mostrar o rótulo (padrão 1/3 da altura).
    """
    parede = parede or CALIBRACAO["parede_estrutural"]
    folga = CALIBRACAO["folga_deslizante"] if folga is None else folga
    altura_frente = altura_frente or altura / 3

    li, pi = largura + 2 * folga, profundidade + 2 * folga
    le, pe = li + 2 * parede, pi + 2 * parede

    corpo = (cq.Workplane("XY").box(le, pe, altura, centered=(True, True, False))
             .edges("|Z").fillet(raio_canto))
    cavidade = (cq.Workplane("XY").workplane(offset=parede)
                .box(li, pi, altura, centered=(True, True, False)))
    # recorte frontal (lado -Y) para deixar o rótulo visível
    recorte = (cq.Workplane("XY").workplane(offset=altura_frente)
               .center(0, -pe / 2)
               .box(li * 0.8, parede * 3, altura, centered=(True, True, False)))
    return corpo.cut(cavidade).cut(recorte)


def berco_pote(diametro, profundidade_encaixe=15.0, parede=None, folga=None,
               base=3.0):
    """Anel de encaixe para pote cilíndrico (ex.: pasta 400 g). Impede o pote de escorregar."""
    parede = parede or CALIBRACAO["parede_estrutural"]
    folga = CALIBRACAO["folga_deslizante"] if folga is None else folga
    r_int = diametro / 2 + folga
    r_ext = r_int + parede
    anel = cq.Workplane("XY").circle(r_ext).extrude(base + profundidade_encaixe)
    cavidade = cq.Workplane("XY").workplane(offset=base).circle(r_int).extrude(profundidade_encaixe)
    return anel.cut(cavidade).faces("<Z").edges().chamfer(CALIBRACAO["chanfre_base"])


def slot_placa_preco(largura=60.0, altura=25.0, espessura_placa=1.0, profundidade=4.0,
                     parede=None):
    """Trilho em U para placa de preço/etiqueta (papel 180 g, PVC ou acrílico fino)."""
    parede = parede or CALIBRACAO["parede_min_fdm"] * 1.5
    canal = espessura_placa + 2 * CALIBRACAO["folga_deslizante"]
    corpo = cq.Workplane("XY").box(largura, canal + 2 * parede, profundidade + parede,
                                   centered=(True, True, False))
    rasgo = (cq.Workplane("XY").workplane(offset=parede)
             .box(largura, canal, profundidade + parede, centered=(True, True, False)))
    # janela frontal deixa a etiqueta à mostra
    # (só a parede da frente, lado -Y, acima de 1 mm de aba que segura a placa)
    janela = (cq.Workplane("XY").workplane(offset=parede + 1.0)
              .center(0, -(canal / 2 + parede / 2))
              .box(largura - 2 * parede, parede * 2, profundidade, centered=(True, True, False)))
    return corpo.cut(rasgo).cut(janela)


# ---------------------------------------------------------------------------
# Estrutura
# ---------------------------------------------------------------------------
def base_antitombamento(largura, profundidade, espessura=4.0, raio_canto=6.0,
                        rebaixo_pes=0.0):
    """Placa de base com chanfre inferior. rebaixo_pes > 0 cria cavidades Ø10 para pés de silicone."""
    base = (cq.Workplane("XY").box(largura, profundidade, espessura, centered=(True, True, False))
            .edges("|Z").fillet(raio_canto)
            .faces("<Z").edges().chamfer(CALIBRACAO["chanfre_base"]))
    if rebaixo_pes > 0:
        dx, dy = largura / 2 - 10, profundidade / 2 - 10
        base = (base.faces("<Z").workplane()
                .pushPoints([(dx, dy), (-dx, dy), (dx, -dy), (-dx, -dy)])
                .hole(10.0, rebaixo_pes))
    return base


def pino_alinhamento(diametro=5.0, comprimento=10.0):
    """Par pino/furo para unir partes divididas pela mesa de impressão.

    Retorna (pino, furo): una o pino numa parte e subtraia o furo da outra.
    """
    pino = cq.Workplane("XY").circle(diametro / 2).extrude(comprimento / 2).faces(">Z").chamfer(0.5)
    furo = cq.Workplane("XY").circle(diametro / 2 + CALIBRACAO["folga_deslizante"]).extrude(
        comprimento / 2 + 0.5)
    return pino, furo


def furo_parafuso(diametro_nominal, profundidade, escareado=False):
    """Sólido para subtrair: furo passante com folga calibrada (e escareado 90° opcional)."""
    d = diametro_nominal + CALIBRACAO["folga_parafuso"]
    furo = cq.Workplane("XY").circle(d / 2).extrude(profundidade)
    if escareado:
        cone = cq.Workplane("XY").workplane(offset=profundidade).circle(d).workplane(
            offset=-d / 2).circle(d / 2).loft()
        furo = furo.union(cone)
    return furo


# ---------------------------------------------------------------------------
# Marca
# ---------------------------------------------------------------------------
def texto_relevo(texto, altura_letra=8.0, profundidade=1.0, fonte="Pilcrow Rounded",
                 caminho_fonte=None):
    """Texto em relevo (una) ou gravado (subtraia). Mínimo FDM: letra 6 mm, traço 1 mm.

    Sem o arquivo da Pilcrow Rounded instalado, o CadQuery cai na fonte padrão:
    passe caminho_fonte com o .otf/.ttf de base-de-conhecimento/marca/.
    """
    kwargs = {"fontPath": caminho_fonte} if caminho_fonte else {"font": fonte}
    return cq.Workplane("XY").text(texto, altura_letra, profundidade, halign="center",
                                   valign="center", **kwargs)


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------
def validar(peca, nome="peca", mesa=(220, 220, 250)):
    """Checa sólido válido, medidas e se cabe na mesa. Retorna dict com o relatório."""
    solido = peca.val()
    bb = solido.BoundingBox()
    dims = (round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2))
    cabe = all(d <= m for d, m in zip(sorted(dims), sorted(mesa)))
    rel = {
        "nome": nome,
        "valido": solido.isValid(),
        "dimensoes_mm": dims,
        "volume_cm3": round(solido.Volume() / 1000, 2),
        "cabe_na_mesa": cabe,
    }
    try:
        import tempfile
        import trimesh
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, "t.stl")
            cq.exporters.export(peca, caminho)
            malha = trimesh.load(caminho)
            rel["watertight"] = bool(malha.is_watertight)
            rel["winding_ok"] = bool(malha.is_winding_consistent)
    except ImportError:
        rel["watertight"] = "não verificado (instale trimesh)"
    return rel


def cena_json(itens, vistas, arquivo, largura=900, altura=1200, fundo="#f3efe9", tol=0.5):
    """Grava a cena para ferramentas/render_cena.mjs.

    itens: lista de (cq.Workplane, cor) ou (cq.Workplane, dict) com chaves
           cor, brilho (emissivo, ex. LED), rugosidade, metal, luz, luz_pos.
    vistas: lista de dicts {nome, pos:(x,y,z), alvo:(x,y,z), fov}.
    """
    import json
    pecas = []
    for solido, estilo in itens:
        estilo = {"cor": estilo} if isinstance(estilo, str) else dict(estilo)
        verts, tris = solido.val().tessellate(tol, 0.2)
        estilo["pos"] = [round(c, 2) for v in verts for c in (v.x, v.y, v.z)]
        estilo["idx"] = [i for t in tris for i in t]
        pecas.append(estilo)
    with open(arquivo, "w") as f:
        json.dump({"largura": largura, "altura": altura, "fundo": fundo,
                   "pecas": pecas, "vistas": vistas}, f)


def renderizar(itens, vistas, pasta, **kw):
    """Renderiza com three.js no Chromium headless. Precisa de `npm i three` e playwright.

    Procura three em ./node_modules ou em ESTUDIO_NODE_MODULES; devolve a lista de PNGs.
    """
    import subprocess
    os.makedirs(pasta, exist_ok=True)
    arq = os.path.join(pasta, "_cena.json")
    cena_json(itens, vistas, arq, **kw)
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ferramentas", "render_cena.mjs")
    raiz_global = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    nm = os.environ.get("ESTUDIO_NODE_MODULES", os.path.join(os.getcwd(), "node_modules"))
    env = dict(os.environ, NODE_PATH=os.pathsep.join([nm, raiz_global]))
    subprocess.run(["node", script, os.path.abspath(arq), os.path.abspath(pasta)],
                   check=True, env=env, cwd=os.path.dirname(nm))
    os.remove(arq)
    return [os.path.join(pasta, f"{v['nome']}.png") for v in vistas]


def exportar(peca, nome, pasta="."):
    """Exporta STL e STEP com o mesmo nome base."""
    os.makedirs(pasta, exist_ok=True)
    for ext in ("stl", "step"):
        cq.exporters.export(peca, os.path.join(pasta, f"{nome}.{ext}"))


def _demo_display_granola(n=3, esp=15, altura_traseira=200, inclinacao=12):
    """Demonstração: display de balcão em MDF para `n` granolas lado a lado (uma prateleira)."""
    l, a, p = PRODUTOS["granola_300g"]
    f = CALIBRACAO["folga_produto_flexivel"]
    vao = n * (l + 2 * f)
    prof = p + 2 * f + esp + 20          # fundo + respiro frontal
    larg = vao + 2 * esp
    pecas = [
        chapa("base", larg, prof, esp, "MDF BP branco", (0, 0, 0), obs="fita nas 4 bordas"),
        chapa("lateral", prof, altura_traseira, esp, "MDF BP branco", (0, 0, esp), "YZ",
              quantidade=1, obs="fita na frente e no topo"),
        chapa("lateral", prof, altura_traseira, esp, "MDF BP branco", (larg - esp, 0, esp), "YZ",
              quantidade=1, obs="fita na frente e no topo"),
        chapa("fundo", vao, altura_traseira, esp, "MDF BP branco", (esp, prof - esp, esp), "XZ",
              obs="fita no topo; logo em adesivo"),
        chapa("frontal_baixo", vao, 40, esp, "MDF BP branco", (esp, 0, esp), "XZ",
              obs="fita no topo; segura os pacotes"),
    ]
    # junta as duas laterais iguais numa linha só da lista de corte
    lista = [pecas[0], Peca("lateral", pecas[1].solido, pecas[1].material, "chapa",
                            pecas[1].medidas, pecas[1].densidade, 2, pecas[1].obs)] + pecas[3:]
    return pecas, lista


if __name__ == "__main__":
    # 1) Módulos de encaixe (medidas de exemplo, exceto onde vem de PRODUTOS)
    l, a, p = PRODUTOS["granola_300g"]
    f = CALIBRACAO["folga_produto_flexivel"]
    demos = {
        "berco_granola": berco_retangular(l, p, 60, folga=f),
        "berco_pote": berco_pote(85),
        "slot_placa_preco": slot_placa_preco(),
        "base_antitombamento": base_antitombamento(180, 120, rebaixo_pes=1.5),
        "pino_alinhamento": pino_alinhamento()[0],
        "furo_parafuso": furo_parafuso(4, 6, escareado=True),
    }
    for nome, peca in demos.items():
        print(validar(peca, nome, mesa=(2750, 1850, 2000)))
        exportar(peca, nome, "saida_demo")

    # 2) Peça de oficina: display de balcão em MDF para 3 granolas
    pecas, lista = _demo_display_granola()
    display = montar(pecas)
    print(validar(display, "display_granola_mdf", mesa=(2750, 1850, 2000)))
    print(lista_de_corte(lista))
    print(aproveitamento(lista), f"peso ≈ {peso_total_kg(pecas)} kg")
    exportar(display, "display_granola_mdf", "saida_demo")
    vistas_svg(display, "display_granola_mdf", "saida_demo")

    # 3) Peça de serralheria: quadro de metalon 20x20 (exemplo)
    q = [tubo("travessa", 500, posicao=(0, 0, 0), quantidade=1, obs="corte 45°"),
         tubo("travessa", 500, posicao=(0, 0, 780), quantidade=1, obs="corte 45°"),
         tubo("montante", 800, eixo="Z", posicao=(0, 0, 0), obs="corte 45°"),
         tubo("montante", 800, eixo="Z", posicao=(480, 0, 0), obs="corte 45°")]
    print(validar(montar(q), "quadro_metalon", mesa=(6000, 2000, 2000)))
    print(aproveitamento(q), f"peso ≈ {peso_total_kg(q)} kg")


# ---------------------------------------------------------------------------
# Chapas para CNC (compensado, MDF): painel 2D → 3D, plano de corte e DXF
# ---------------------------------------------------------------------------
CHAPA_COMPENSADO = {"comprimento": 2200, "largura": 1600, "margem": 10, "vao": 12}
CAMADAS_DXF = {  # nome: cor ACI
    "CORTE_EXTERNO": 1,     # vermelho: contorno da peça (por fora)
    "CORTE_INTERNO": 5,     # azul: furos ≥ 8 mm e recortes (por dentro, cortar antes)
    "FURO_GUIA_3": 3,       # verde: furo-guia Ø3 passante (parafuso, depois abrir 4,5)
    "TEXTO_NAO_CORTAR": 8,  # cinza: identificação da peça (gravar leve ou ignorar)
    "CHAPA": 9,             # limite da chapa (não cortar)
}


def _fio(wp):
    """Workplane com polyline/arcos (não fechado) ou já fechado → cq.Wire."""
    try:
        return wp.close().val()
    except ValueError:
        return wp.val()


def _extrudar(fio, altura, both=False):
    face = cq.Face.makeFromWires(fio)
    if both:
        face = face.translate(cq.Vector(0, 0, -altura))
        altura *= 2
    return cq.Workplane("XY").add(cq.Solid.extrudeLinear(face, cq.Vector(0, 0, altura)))


class Painel:
    """Peça plana em coordenadas locais (u, v), espessura `esp`.

    contorno: cq.Workplane desenhando um fio fechado no plano XY local (u, v).
    recortes: lista de cq.Workplane fechados (cortes internos: porta, janelas).
    furos: lista de (u, v, diametro); Ø ≤ 3 vai para FURO_GUIA_3, maior vira CORTE_INTERNO.
    posicao: (origem, eixo_u, eixo_v, eixo_espessura) em coordenadas globais.
    """

    def __init__(self, ref, nome, contorno, esp, posicao, recortes=(), furos=(), qtd=1,
                 material="compensado naval", obs=""):
        self.ref, self.nome, self.esp = ref, nome, esp
        self.fio = _fio(contorno)
        self.fios_recorte = [_fio(r) for r in recortes]
        self.posicao, self.furos = posicao, list(furos)
        self.qtd, self.material, self.obs = qtd, material, obs

    def _local(self):
        """Location rígida (u, v → global) e sinal da espessura (+1 ou −1)."""
        o, eu, ev, ew = (cq.Vector(*a) for a in self.posicao)
        n = eu.cross(ev)
        plano = cq.Plane(origin=o, xDir=eu, normal=n)
        return cq.Location(plano), (1 if n.dot(ew) > 0 else -1)

    def _peca_local(self, esp):
        f = _extrudar(self.fio, esp)
        for r in self.fios_recorte:
            f = f.cut(_extrudar(r, esp * 3, both=True))
        for u, v, d in self.furos:
            if d > 3:
                f = f.cut(cq.Workplane("XY").center(u, v).circle(d / 2).extrude(esp * 3, both=True))
        return f

    def caixa2d(self):
        bb = self.fio.BoundingBox()
        return bb.xmin, bb.ymin, bb.xmax, bb.ymax

    def area_m2(self):
        return self._peca_local(1).val().Volume() / 1e6

    def solido(self):
        loc, sinal = self._local()
        f = self._peca_local(self.esp).val()
        if sinal < 0:
            f = f.translate(cq.Vector(0, 0, -self.esp))
        return cq.Workplane("XY").add(f.moved(loc))

    def recorte_solido(self, i=0, folga=0.0):
        """Sólido 3D do i-ésimo recorte (ex.: a porta sai do próprio painel)."""
        loc, sinal = self._local()
        f = _extrudar(self.fios_recorte[i], self.esp).val()
        if sinal < 0:
            f = f.translate(cq.Vector(0, 0, -self.esp))
        return cq.Workplane("XY").add(f.moved(loc))


def plano_de_corte(paineis, chapa=CHAPA_COMPENSADO):
    """Testa as orientações (deitada / em pé) e devolve o encaixe com menos chapas."""
    melhor = None
    for politica in ("deitada", "em_pe"):
        try:
            r = _plano_de_corte(paineis, chapa, politica)
        except ValueError:
            continue
        if melhor is None or len(r) < len(melhor):
            melhor = r
    if melhor is None:
        raise ValueError("alguma peça não cabe na chapa")
    return melhor


def _plano_de_corte(paineis, chapa=CHAPA_COMPENSADO, politica="deitada"):
    """Encaixe simples por prateleiras (caixas retangulares, gira 90° se ajudar).

    Retorna lista de chapas; cada chapa é lista de (painel, indice_copia, x, y, girado).
    Ordena da maior para a menor altura. Bom o bastante para peças grandes e poucas.
    """
    C, Lg, mg, gap = chapa["comprimento"], chapa["largura"], chapa["margem"], chapa["vao"]
    itens = []
    for p in paineis:
        x0, y0, x1, y1 = p.caixa2d()
        for k in range(p.qtd):
            itens.append((p, k, x1 - x0, y1 - y0))
    # orientação: "deitada" = lado maior na horizontal; "em_pe" = lado maior na vertical
    orient = []
    for p, k, w, h in itens:
        if politica == "deitada":
            gir = h > w
        else:
            gir = w > h
        if gir and not (h <= C - 2 * mg and w <= Lg - 2 * mg):
            gir = False
        if not gir and not (w <= C - 2 * mg and h <= Lg - 2 * mg):
            gir = True
        orient.append((p, k, (h, w) if gir else (w, h), gir))
    orient.sort(key=lambda t: -t[2][1])
    chapas = []   # cada uma: {"prats": [[y, altura, x_livre]], "pecas": []}
    for p, k, (w, h), gir in orient:
        colocado = False
        for ch in chapas:
            for pr in ch["prats"]:
                if h <= pr[1] and pr[2] + w <= C - mg:
                    ch["pecas"].append((p, k, pr[2], pr[0], gir))
                    pr[2] += w + gap
                    colocado = True
                    break
            if colocado:
                break
            topo = ch["prats"][-1][0] + ch["prats"][-1][1] + gap
            if topo + h <= Lg - mg:
                ch["prats"].append([topo, h, mg + w + gap])
                ch["pecas"].append((p, k, mg, topo, gir))
                colocado = True
                break
        if not colocado:
            if w > C - 2 * mg or h > Lg - 2 * mg:
                raise ValueError(f"{p.ref} {p.nome} ({w:.0f}×{h:.0f}) não cabe na chapa")
            chapas.append({"prats": [[mg, h, mg + w + gap]], "pecas": [(p, k, mg, mg, gir)]})
    return [ch["pecas"] for ch in chapas]


def _angulo(gir):
    """`gir` do plano: bool (False=0°, True=90°) ou ângulo em graus (múltiplo de 90)."""
    if gir is True:
        return 90
    if gir is False or gir is None:
        return 0
    return int(gir) % 360


def _local_para_chapa(p, x, y, gir):
    """Location 2D: coordenadas locais → chapa. Gira `gir` graus e encosta o canto em (x, y)."""
    ang = _angulo(gir)
    rot = cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), ang)
    bb = p.fio.moved(rot).BoundingBox()
    return cq.Location(cq.Vector(x - bb.xmin, y - bb.ymin, 0)) * rot


def plano_manual(paineis, posicoes):
    """Plano de corte escrito à mão: posicoes = [[(ref, x, y, ang), ...] por chapa].

    Peças com a mesma ref são usadas na ordem (cópias). Confira com verificar_plano().
    """
    por_ref = {p.ref: p for p in paineis}
    usados = {}
    chapas = []
    for ch in posicoes:
        lista = []
        for ref, x, y, ang in ch:
            k = usados.get(ref, 0)
            usados[ref] = k + 1
            lista.append((por_ref[ref], k, x, y, ang))
        chapas.append(lista)
    for p in paineis:
        if usados.get(p.ref, 0) != p.qtd:
            raise ValueError(f"{p.ref}: plano tem {usados.get(p.ref, 0)} cópias, precisa de {p.qtd}")
    return chapas


def verificar_plano(chapas, chapa=CHAPA_COMPENSADO):
    """Distância real entre contornos ≥ vão e peças dentro da margem. Lista de problemas."""
    problemas = []
    for n, pecas in enumerate(chapas, 1):
        faces = []
        for p, k, x, y, gir in pecas:
            f = cq.Face.makeFromWires(p.fio.moved(_local_para_chapa(p, x, y, gir)))
            bb = f.BoundingBox()
            mg = chapa["margem"] - 0.01
            if bb.xmin < mg or bb.ymin < mg or bb.xmax > chapa["comprimento"] - mg or \
                    bb.ymax > chapa["largura"] - mg:
                problemas.append(f"chapa {n}: {p.ref} fora da margem")
            faces.append((p.ref, f))
        for i in range(len(faces)):
            for j in range(i + 1, len(faces)):
                d = faces[i][1].distance(faces[j][1])
                if d < chapa["vao"] - 0.01:
                    problemas.append(f"chapa {n}: {faces[i][0]} × {faces[j][0]} a {d:.1f} mm")
    return problemas


def dxf_chapas(chapas, pasta, prefixo="chapa", chapa=CHAPA_COMPENSADO):
    """Um DXF por chapa, em mm, 1:1, com as camadas de CAMADAS_DXF."""
    from cadquery.occ_impl.exporters.dxf import DxfDocument
    os.makedirs(pasta, exist_ok=True)
    arquivos = []
    for i, pecas in enumerate(chapas, 1):
        doc = DxfDocument()
        for nome, cor in CAMADAS_DXF.items():
            doc.add_layer(nome, color=cor)
        msp = doc.document.modelspace()
        msp.add_lwpolyline([(0, 0), (chapa["comprimento"], 0), (chapa["comprimento"], chapa["largura"]),
                            (0, chapa["largura"])], close=True, dxfattribs={"layer": "CHAPA"})
        for p, k, x, y, gir in pecas:
            m = _local_para_chapa(p, x, y, gir)
            doc.add_shape(p.fio.moved(m), "CORTE_EXTERNO")
            for r in p.fios_recorte:
                doc.add_shape(r.moved(m), "CORTE_INTERNO")
            for u, v, d in p.furos:
                c = cq.Vertex.makeVertex(u, v, 0).moved(m).Center()
                msp.add_circle((c.x, c.y), d / 2,
                               dxfattribs={"layer": "FURO_GUIA_3" if d <= 3 else "CORTE_INTERNO"})
            x0, y0, x1, y1 = p.caixa2d()
            c = cq.Vertex.makeVertex((x0 + x1) / 2, (y0 + y1) / 2, 0).moved(m).Center()
            rot = 90 if gir and (y1 - y0) > (x1 - x0) else 0
            msp.add_text(f"{p.ref}", height=40, dxfattribs={"layer": "TEXTO_NAO_CORTAR",
                                                           "rotation": 0}).set_placement(
                (c.x, c.y), align=ezdxf_align_meio())
        arq = os.path.join(pasta, f"{prefixo}_{i}.dxf")
        doc.document.saveas(arq)
        arquivos.append(arq)
    return arquivos


def ezdxf_align_meio():
    from ezdxf.enums import TextEntityAlignment
    return TextEntityAlignment.MIDDLE_CENTER
