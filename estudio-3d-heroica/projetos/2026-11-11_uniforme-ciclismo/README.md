# Uniforme Heroica 2026 · ciclismo (macaquinho)

Pedido do Roberto (11/11/2026): novo uniforme inspirado na referência de gravel (degradê rosa→pêssego→amarelo, branco no meio, bermuda rosa-choque com letras escuras), usando como base o mockup do macaquinho do fornecedor (sem as informações do layout antigo).

## v1 · conceito 1 (bermuda rosa-choque aprovada em 11/11)
- `v1/saida/Heroica_uniforme_2026_conceito1.png` (frente e costas)
- Cores: rosa #F7A3BC · pêssego #FFC39C · amarelo #FFE07A · rosa-choque #EF4F98 · marrom #3B2116 · branco
- Frente: degradê no peito e ombros, mangas em amarelo com HEROICA vertical marrom, faixa branca com HEROICA grande marrom, bermuda rosa-choque com HEROICA marrom na coxa.
- Costas: degradê com HEROICA branco, selo sorriso + SONHE.LUTE na lombar.

## Como foi feito (`v1/scripts/`, rodar na ordem a partir da pasta com `full-1.png` = mockup rasterizado a 300 dpi)
1. `seg4.py 2` e `peel.py`: recorte da silhueta (sem o painel cinza e a sombra).
2. `regions.py`: camisa, bermuda, gola, zíper.
3. `shading2.py`: sombreado do tecido sem as artes antigas.
4. `compose.py`: aplica cores e artes multiplicando pelo sombreado.

O PDF original do fornecedor não fica no repositório.

## v1 · arte de sublimação na faca da AR (tamanho G)
- `v1/sublimacao/Heroica_uniforme_2026_sublimacao_G_com_faca.pdf` — arte + linha de corte (azul, não imprime), lado certo do tecido.
- `v1/sublimacao/Heroica_uniforme_2026_sublimacao_G_espelhado_para_impressao.pdf` — só a arte, espelhada para o papel de sublimação.
- `v1/sublimacao/Heroica_uniforme_2026_sublimacao_G.svg` — vetorial editável (Corel/Illustrator), escala real 1380 × 912 mm.
- Sangria de ~5 mm em todas as peças. Logo HEROICA vetorial (tirado do arquivo da AR); selo do sorriso em imagem 300 dpi.
- Conferir com a AR: qual ponta da LATERAL é a axila (assumido: ponta estreita em cima) e a altura da cintura nela (assumido 400 pt ≈ 141 mm); a bermuda não está na faca — tecido rosa-choque liso.
- Script: `v1/scripts/sublimacao_build.py` (lê as páginas 1, 4 e 5 do PDF da AR convertidas em SVG).

## v2 · conceito 2 (paleta Heroica) — atual
Roberto (11/11): usar só cores da paleta; o rosa-choque não é da marca.
Brandbook ainda não está na base, então usei só cores de artes já aprovadas: marrom #602221 (peças aprovadas) e, do arquivo da AR, rosa claro #F5C7C8, bege #EAD7B9 e magenta #C2236B.
- Degradê rosa claro → bege (frente, costas, mangas); HEROICA em marrom em todas as aplicações; bermuda e laterais da perna em magenta.
- Mockup: `v2/saida/Heroica_uniforme_2026_conceito2.png` · Sublimação G: `v2/sublimacao/` (com faca, espelhado, SVG).
