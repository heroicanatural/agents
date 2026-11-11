# Uniforme Heroica 2026 · ciclismo (macaquinho)

Pedido do Roberto (11/11/2026): novo uniforme inspirado na referência de gravel (degradê rosa→pêssego→amarelo, branco no meio, bermuda rosa-choque com letras escuras), usando como base o mockup do macaquinho do fornecedor (sem as informações do layout antigo).

## v1 · conceito 1
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
