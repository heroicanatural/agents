"""
Tambor Heroica v1 — conceito A + itens do B (aprovado em 01/10/2026). Quantidade: 4.

Tambor de aço 200 L novo, recorte frontal de 120°, 2 prateleiras em D com testeira
porta-preço, tampo-bandeja rosa com borda, interior rosa, LED magnético, adesivos.

Rodar:
    ESTUDIO_NODE_MODULES=<pasta>/node_modules python tambor_v1.py
Gera em ./saida: STEP da montagem, renders, lista de corte e relatório de validação.
Desenhos e PDF do fornecedor: python desenhos_v1.py
"""
import json
import math
import os
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", ".."))
import biblioteca_heroica as bib  # noqa: E402
from biblioteca_heroica import Peca, chapa, DENSIDADE  # noqa: E402

# ======================================================================
# PARÂMETROS (mm) — mude aqui
# ======================================================================
T = bib.TAMBOR_200L
R_INT = T["d_int"] / 2                 # 285,75
ALTURA = T["altura"]                   # 880

RECORTE_GRAUS = 120                    # largura angular do vão (corda ≈ 495 mm na parede interna)
RECORTE_Z = (140, 720)                 # do chão; acima de 720 fica a faixa da marca

# prateleiras (MDF 15 BP amadeirado claro)
ESP_PRAT = 15
FOLGA_PAREDE = 5                       # entre prateleira e parede (passa livre pelos montantes)
PRAT_TOPO_Z = (150, 440)               # face de cima de cada prateleira
Y_FRENTE_PRAT = -125                   # corte reto da frente da prateleira (formato D)

# testeira porta-preço (MDF 15, fica 20 mm acima da prateleira: segura o produto)
ESP_TEST = 15
ALT_TEST = 35

# tampo-bandeja (MDF, laca rosa)
D_TAMPO = 610
ESP_TAMPO = 18
ESP_ANEL = 15
LARG_ANEL = 20                         # borda que segura o produto
D_CENTRAGEM = 550                      # disco sob o tampo, encaixa dentro do bordão
ESP_CENTRAGEM = 9

# reforço (barra chata 1" × 1/8") e apoio (cantoneira 3/4" × 1/8")
BARRA = (25.4, 3.2)
AFASTAMENTO_REFORCO = 12               # da borda do corte (deixa lugar para o perfil U)
SOBRA_ARCO_GRAUS = 15                  # quanto o arco passa de cada lado do vão
CANT = (19.05, 3.2)
COMP_CANT = 80
ANGULOS_CANT = (0, 90, 180)            # direita, fundo, esquerda

# produto de referência
GRANOLA = bib.PRODUTOS["granola_300g"]  # 160 × 240 × 80

# cores (render)
MARROM, ROSA, MADEIRA, BRANCO, LED, ACO = "#5E2129", "#E3A1B5", "#D8B48A", "#F4EFE9", "#FFE9A8", "#7d7d7d"


# ======================================================================
# PEÇAS
# ======================================================================
def arco_barra(z0, raio_ext, graus, larg, esp):
    """Barra chata calandrada (de pé, encostada na parede interna)."""
    anel = cq.Workplane("XY").workplane(offset=z0).circle(raio_ext).circle(raio_ext - esp).extrude(larg)
    return anel.intersect(bib.setor(raio_ext + 50, graus, z0 - 1, z0 + larg + 1))


def serralheria():
    pecas = []
    casco, pedaco = bib.tambor_200l(RECORTE_GRAUS, RECORTE_Z)
    pecas.append(Peca("tambor 200 L recortado", casco, "tambor aço 200 L novo", "outro",
                      (T["d_ext"], ALTURA), DENSIDADE["aco"], 1, "recorte 120°, ver vista"))
    graus_arco = RECORTE_GRAUS + 2 * SOBRA_ARCO_GRAUS
    raio_arco = R_INT
    comp_arco = round(math.radians(graus_arco) * (raio_arco - BARRA[1] / 2))
    z_sup = RECORTE_Z[1] + AFASTAMENTO_REFORCO
    z_inf = RECORTE_Z[0] - AFASTAMENTO_REFORCO - BARRA[0]
    for nome, z in (("reforço arco superior", z_sup), ("reforço arco inferior", z_inf)):
        pecas.append(Peca(nome, arco_barra(z, raio_arco, graus_arco, *BARRA),
                          'barra chata 1" × 1/8"', "tubo", (comp_arco,), DENSIDADE["aco"], 1,
                          f"calandrar R {raio_arco:.0f} int. de parede"))
    # montantes: barra de pé entre os arcos (solda de topo), afastada da borda do corte
    alt_mont = z_sup - (z_inf + BARRA[0])
    for lado, sinal in (("esq", -1), ("dir", 1)):
        ang_borda = math.radians(-90 + sinal * RECORTE_GRAUS / 2)
        desloc = (AFASTAMENTO_REFORCO + BARRA[0] / 2) / R_INT * sinal
        ang = ang_borda + desloc
        # barra reta na parede curva: encosta nas bordas, folga no meio
        flecha = R_INT - math.sqrt(R_INT ** 2 - (BARRA[0] / 2) ** 2)
        r = R_INT - flecha - BARRA[1] / 2 - 0.05
        m = (cq.Workplane("XY").box(BARRA[0], BARRA[1], alt_mont, centered=(True, True, False))
             .rotate((0, 0, 0), (0, 0, 1), math.degrees(ang) + 90)
             .translate((r * math.cos(ang), r * math.sin(ang), z_inf + BARRA[0])))
        pecas.append(Peca(f"reforço montante {lado}", m, 'barra chata 1" × 1/8"', "tubo",
                          (round(alt_mont),), DENSIDADE["aco"], 1, "reta, corte reto"))
    # cantoneiras de apoio das prateleiras
    for i, zt in enumerate(PRAT_TOPO_Z):
        z = zt - ESP_PRAT - CANT[0]
        for a in ANGULOS_CANT:
            ang = math.radians(a)
            # cantoneira reta na parede curva: as pontas encostam, o meio fica com folga (flecha)
            flecha = R_INT - math.sqrt(R_INT ** 2 - (COMP_CANT / 2) ** 2)
            r = R_INT - flecha - CANT[0] / 2 - 0.05
            perfil = (cq.Workplane("XZ").polyline([(0, 0), (CANT[0], 0), (CANT[0], CANT[1]),
                                                   (CANT[1], CANT[1]), (CANT[1], CANT[0]), (0, CANT[0])])
                      .close().extrude(COMP_CANT / 2, both=True))
            # aba vertical encostada na parede (lado +X local), aba horizontal para dentro
            c = (perfil.mirror("YZ").translate((CANT[0] / 2, 0, 0))
                 .rotate((0, 0, 0), (0, 0, 1), a)
                 .translate((r * math.cos(ang), r * math.sin(ang), z)))
            pecas.append(Peca(f"cantoneira prat.{i + 1}", c, 'cantoneira 3/4" × 1/8"', "tubo",
                              (COMP_CANT,), DENSIDADE["aco"], 1,
                              f"2 furos Ø5 a 12 mm das pontas (meio fica {flecha:.1f} mm afastado da parede)"))
    return pecas, pedaco


def prateleira_d(z_topo):
    r = R_INT - FOLGA_PAREDE
    disco = cq.Workplane("XY").workplane(offset=z_topo - ESP_PRAT).circle(r).extrude(ESP_PRAT)
    corte = cq.Workplane("XY").box(2 * r + 10, 2 * r, ESP_PRAT + 10).translate(
        (0, Y_FRENTE_PRAT - r, z_topo - ESP_PRAT / 2))
    return disco.cut(corte)


def marcenaria():
    r = R_INT - FOLGA_PAREDE
    larg_d = 2 * math.sqrt(r ** 2 - Y_FRENTE_PRAT ** 2)
    prof_d = r - Y_FRENTE_PRAT
    y_test = Y_FRENTE_PRAT - ESP_TEST
    comp_test = 2 * math.sqrt((R_INT - FOLGA_PAREDE - 1) ** 2 - y_test ** 2)
    pecas = []
    for i, zt in enumerate(PRAT_TOPO_Z):
        pecas.append(Peca(f"prateleira D {i + 1}", prateleira_d(zt), "MDF BP amadeirado claro",
                          "chapa", (round(2 * r), round(prof_d), ESP_PRAT), DENSIDADE["mdf"], 1,
                          f"círculo Ø{2 * r:.0f} cortado reto a {prof_d:.0f} do fundo; "
                          f"frente reta {larg_d:.0f}; fita na borda curva"))
        t = (cq.Workplane("XY").box(comp_test, ESP_TEST, ALT_TEST, centered=(True, False, False))
             .translate((0, y_test, zt - ESP_PRAT)))
        pecas.append(Peca(f"testeira {i + 1}", t, "MDF BP amadeirado claro", "chapa",
                          (round(comp_test), ALT_TEST, ESP_TEST), DENSIDADE["mdf"], 1,
                          "fita nas 4 bordas; parafusar na frente da prateleira"))
    z0 = ALTURA
    tampo = cq.Workplane("XY").workplane(offset=z0).circle(D_TAMPO / 2).extrude(ESP_TAMPO)
    anel = (cq.Workplane("XY").workplane(offset=z0 + ESP_TAMPO).circle(D_TAMPO / 2)
            .circle(D_TAMPO / 2 - LARG_ANEL).extrude(ESP_ANEL))
    cent = (cq.Workplane("XY").workplane(offset=z0 - ESP_CENTRAGEM).circle(D_CENTRAGEM / 2)
            .extrude(ESP_CENTRAGEM))
    pecas += [
        Peca("tampo", tampo, "MDF cru p/ laca", "chapa", (D_TAMPO, D_TAMPO, ESP_TAMPO),
             DENSIDADE["mdf"], 1, f"disco Ø{D_TAMPO}; laca rosa"),
        Peca("anel do tampo", anel, "MDF cru p/ laca", "chapa", (D_TAMPO, D_TAMPO, ESP_ANEL),
             DENSIDADE["mdf"], 1, f"anel Ø{D_TAMPO}/Ø{D_TAMPO - 2 * LARG_ANEL}; colar sobre o tampo; laca rosa"),
        Peca("disco de centragem", cent, "MDF cru", "chapa", (D_CENTRAGEM, D_CENTRAGEM, ESP_CENTRAGEM),
             DENSIDADE["mdf"], 1, "colar sob o tampo, centrado; ajustar ao bordão do tambor"),
    ]
    return pecas


def acessorios():
    """LED (2 barras magnéticas) — só para render e conferência de posição."""
    led1 = cq.Workplane("XY").box(300, 15, 10).translate((0, -40, ALTURA - 10 - 6))      # sob a tampa do tambor
    led2 = cq.Workplane("XY").box(300, 15, 10).translate((0, -40, PRAT_TOPO_Z[1] - ESP_PRAT - 6))
    return [led1, led2]


def graficos():
    """Adesivos (gráfica): letreiro em arco, moldura rosa do vão, 2 selos laterais."""
    itens = []
    # letreiro HEROICA (Pilcrow Rounded no real; aqui a fonte padrão só marca posição)
    h, z = 80, (RECORTE_Z[1] + ALTURA - 10) / 2
    letras = [cq.Workplane("XZ").text(ch, h, 1.5, halign="center", valign="center", kind="bold")
              for ch in "HEROICA"]
    larg = [l.val().BoundingBox().xlen for l in letras]
    esp = h * 0.18
    s = -(sum(larg) + esp * 6) / 2
    r = R_INT + T["chapa"] + 0.3
    for l, w in zip(letras, larg):
        ang = math.degrees((s + w / 2) / r)
        itens.append((l.translate((0, -r, z)).rotate((0, 0, 0), (0, 0, 1), ang), BRANCO))
        s += w + esp
    # moldura rosa 30 mm em volta do vão
    moldura = (bib.setor(R_INT + 3, RECORTE_GRAUS + 12, RECORTE_Z[0] - 30, RECORTE_Z[1] + 30)
               .cut(bib.setor(R_INT + 10, RECORTE_GRAUS, *RECORTE_Z))
               .cut(cq.Workplane("XY").circle(R_INT + T["chapa"] + 0.2).extrude(ALTURA)))
    itens.append((moldura, ROSA))
    # selos laterais Ø200
    for a in (0, 180):
        selo = (cq.Workplane("XZ").circle(100).extrude(1.5).translate((0, -(R_INT + 6), 470))
                .rotate((0, 0, 0), (0, 0, 1), a + 90))
        itens.append((selo, BRANCO))
    return itens


def interior_rosa():
    """Pintura interna (só para render): película na parede interna, atrás do vão."""
    return (cq.Workplane("XY").workplane(offset=10).circle(R_INT - 0.2).circle(R_INT - 0.8)
            .extrude(ALTURA - 21).cut(bib.setor(R_INT + 20, RECORTE_GRAUS, *RECORTE_Z)))


def granolas():
    l, a, p = GRANOLA
    itens = []
    def fileira(z, y, n):
        for i in range(n):
            x = (i - (n - 1) / 2) * (l + 10)
            b = (cq.Workplane("XY").box(l, p, a, centered=(True, True, False)).edges("|Z").fillet(10)
                 .translate((x, y, z)))
            rot = cq.Workplane("XY").box(l * 0.8, 1.5, a * 0.45).translate((x, y - p / 2 - 0.8, z + a * 0.45))
            itens.extend([(b, {"cor": "#E9DDCF", "rugosidade": 0.8}), (rot, ROSA)])
    for zt in PRAT_TOPO_Z:
        fileira(zt, Y_FRENTE_PRAT + p / 2 + 10, 3)       # fileira da frente
        fileira(zt, Y_FRENTE_PRAT + p * 1.5 + 25, 2)     # fileira de trás
    fileira(ALTURA + ESP_TAMPO, -60, 3)
    fileira(ALTURA + ESP_TAMPO, 60, 2)
    return itens


# ======================================================================
# VALIDAÇÃO
# ======================================================================
def validar_tudo(serr, marc):
    rel = {"pecas": []}
    for p in serr + marc:
        v = bib.validar(p.solido, p.nome, mesa=(3000, 3000, 3000))
        rel["pecas"].append({k: v[k] for k in ("nome", "valido", "watertight", "dimensoes_mm")})
    # interferências entre peças (volume da interseção)
    conflitos = bib.interferencias(serr + marc)
    todas = serr + marc
    rel["interferencias_mm3"] = conflitos
    # vãos livres e produto
    vao1 = PRAT_TOPO_Z[1] - ESP_PRAT - PRAT_TOPO_Z[0]
    vao2 = RECORTE_Z[1] - PRAT_TOPO_Z[1]
    sobre_test = ALT_TEST - ESP_PRAT
    rel["vao_livre_mm"] = {"compartimento 1": vao1, "compartimento 2 (até o topo do vão)": vao2}
    rel["granola_passa_sobre_testeira"] = {
        "comp1": vao1 - GRANOLA[1] - sobre_test, "comp2": vao2 - GRANOLA[1] - sobre_test}
    # prateleira entra pelo vão? (de pé, girando dentro do tambor)
    r = R_INT - FOLGA_PAREDE
    prof = r - Y_FRENTE_PRAT
    rel["montagem_prateleira"] = {
        "largura_D": round(2 * r), "profundidade_D": round(prof),
        "vao_altura": RECORTE_Z[1] - RECORTE_Z[0],
        "entra_de_pe": 2 * r < (RECORTE_Z[1] - RECORTE_Z[0]),
    }
    # peso e centro de massa (aço + MDF), sem produto e com 16 granolas (~0,3 kg cada)
    massa, mom = 0.0, 0.0
    for p in todas:
        m = p.peso_kg()
        massa += m
        mom += m * p.solido.val().Center().z
    rel["peso_kg"] = round(massa, 1)
    rel["cg_z_mm"] = round(mom / massa)
    return rel


if __name__ == "__main__":
    saida = os.path.join(AQUI, "saida")
    os.makedirs(saida, exist_ok=True)
    serr, pedaco = serralheria()
    marc = marcenaria()
    rel = validar_tudo(serr, marc)
    print(json.dumps(rel, indent=1, ensure_ascii=False))
    with open(os.path.join(saida, "validacao.json"), "w") as f:
        json.dump(rel, f, indent=1, ensure_ascii=False)

    # lista de corte agrupada (iguais viram uma linha com quantidade)
    def agrupar(pecas):
        grupos = {}
        for p in pecas:
            chave = (p.nome.rstrip("0123456789 ").replace(" esq", "").replace(" dir", "")
                     .replace("prat.", "prateleira").replace("arco superior", "arco").replace("arco inferior", "arco"),
                     p.material, p.medidas)
            if chave in grupos:
                grupos[chave].quantidade += 1
            else:
                grupos[chave] = Peca(chave[0], p.solido, p.material, p.familia, p.medidas,
                                     p.densidade, 1, p.obs)
        return list(grupos.values())
    lista_s, lista_m = agrupar(serr[1:]), agrupar(marc)
    with open(os.path.join(saida, "lista_de_corte.md"), "w") as f:
        f.write("## Serralheria (por tambor)\n\n" + bib.lista_de_corte(lista_s) + "\n\n")
        f.write(f"Aproveitamento: {bib.aproveitamento(lista_s)}\n\n")
        f.write("## Marcenaria (por tambor)\n\n" + bib.lista_de_corte(lista_m) + "\n\n")
        f.write(f"Aproveitamento: {bib.aproveitamento(lista_m)}\n")
    print(open(os.path.join(saida, "lista_de_corte.md")).read())

    montagem = bib.montar(serr + marc)
    cq.exporters.export(montagem, os.path.join(saida, "tambor_heroica_v1.step"))
    # renders
    estilo = {"tambor 200 L recortado": {"cor": MARROM, "rugosidade": 0.45, "metal": 0.0}}
    itens = []
    for p in serr:
        itens.append((p.solido, estilo.get(p.nome, {"cor": ACO, "metal": 0.5, "rugosidade": 0.4})))
    for p in marc:
        cor = ROSA if ("tampo" in p.nome or "centragem" in p.nome) else MADEIRA
        itens.append((p.solido, {"cor": cor, "rugosidade": 0.7}))
    itens.append((interior_rosa(), ROSA))
    for led in acessorios():
        c = led.val().Center()
        itens.append((led, {"cor": LED, "brilho": 1.6, "luz": 1.2, "luz_pos": (c.x, c.y - 40, c.z - 60)}))
    itens += graficos()
    vistas = [
        {"nome": "render_frente", "pos": (0, -3700, 900), "alvo": (0, 0, 560), "fov": 25},
        {"nome": "render_iso", "pos": (-2200, -2900, 1700), "alvo": (0, 0, 520), "fov": 25},
        {"nome": "render_detalhe_vao", "pos": (1200, -2100, 1300), "alvo": (-40, -60, 470), "fov": 28},
    ]
    vazio = bib.renderizar(itens, vistas, os.path.join(saida, "renders_vazio"), largura=900, altura=1100)
    cheio = bib.renderizar(itens + granolas(), vistas[:2], os.path.join(saida, "renders_cheio"),
                           largura=900, altura=1100)
    print("renders:", vazio + cheio)
