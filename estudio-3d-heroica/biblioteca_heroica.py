"""
Biblioteca de módulos paramétricos do Estúdio 3D da Heroica.

Unidades em milímetros. Requer: pip install cadquery
Cada função devolve um cq.Workplane pronto para unir (union) ou subtrair (cut).
Ao terminar um projeto, mova para cá o que for reutilizável e registre em aprendizados.md.

Uso rápido:
    python biblioteca_heroica.py   # gera e valida as peças de demonstração em ./saida_demo
"""

import cadquery as cq

# ---------------------------------------------------------------------------
# CALIBRAÇÃO: ajuste aqui depois de cada teste real de impressão/corte.
# ---------------------------------------------------------------------------
CALIBRACAO = {
    "folga_deslizante": 0.25,   # encaixe que entra e sai com a mão
    "folga_justa": 0.10,        # encaixe por pressão
    "folga_parafuso": 0.30,     # somar ao diâmetro nominal do parafuso
    "chanfre_base": 0.6,        # compensa pé de elefante
    "parede_min_fdm": 1.2,
    "parede_estrutural": 2.0,
    "kerf_laser": 0.15,
}


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
        import trimesh
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, "t.stl")
            cq.exporters.export(peca, caminho)
            malha = trimesh.load(caminho)
            rel["watertight"] = bool(malha.is_watertight)
            rel["winding_ok"] = bool(malha.is_winding_consistent)
    except ImportError:
        rel["watertight"] = "não verificado (instale trimesh)"
    return rel


def exportar(peca, nome, pasta="."):
    """Exporta STL e STEP com o mesmo nome base."""
    import os
    os.makedirs(pasta, exist_ok=True)
    for ext in ("stl", "step"):
        cq.exporters.export(peca, os.path.join(pasta, f"{nome}.{ext}"))


if __name__ == "__main__":
    # Demonstração com medidas SUPOSTAS (não são as embalagens reais da Heroica).
    demos = {
        "berco_retangular": berco_retangular(95, 30, 60),
        "berco_pote": berco_pote(85),
        "slot_placa_preco": slot_placa_preco(),
        "base_antitombamento": base_antitombamento(180, 120, rebaixo_pes=1.5),
        "pino_alinhamento": pino_alinhamento()[0],
        "furo_parafuso": furo_parafuso(4, 6, escareado=True),
    }
    for nome, peca in demos.items():
        print(validar(peca, nome))
        exportar(peca, nome, "saida_demo")
