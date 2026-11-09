# Pódio Heroica — balcão de degustação

Conceito A da v4 do balcão (escolhido pelo Roberto em 31/10/2026): um pódio de 3 caixas no lugar do balcão com bandeira.

## Versão atual: v4 (09/11) — DESMONTÁVEL / FLAT
- Cada caixa = corpo dobrável (frente 15 + 2 laterais 9 em dobradiças; a direita dobra por cima da esquerda graças a uma tira de 9 mm) + tampo 15 com 2 tacos e travessa por baixo, que travam o esquadro. Todas abertas atrás.
- Desmontado: pilha de 730 × 905 × 348 mm, ~31 kg; peça mais pesada = corpo 1 dobrado (9,6 kg). Montagem no PDV em 4 passos, sem ferramenta.
- Serra: `v4/saida/Podio_v4_SERRA_lista_de_cortes.pdf` + CSV · CNC: `v4/saida/Podio_v4_CNC.pdf` + `v4/saida/cnc_dxf/` (1 chapa 15 mm + 1 chapa 9 mm)
- Desmontado e montagem: `v4/saida/Podio_v4_GUIA_desmontado_e_montagem.pdf`
- Modelo e validação: `v4/podio_v4.py` (interferências montado e dobrado = 0) · documentos: `v4/documentos_v4.py`

## v3 (03/11) — PILOTO: 15 mm onde apanha + carrinho dobrável (substituída pela v4)
- Serra: `v3/saida/Podio_v3_SERRA_lista_de_cortes.pdf` · CNC: `v3/saida/Podio_v3_CNC.pdf` + `v3/saida/cnc_dxf/` (1 chapa 15 mm + 2 chapas 9 mm)
- Montagem e transporte: `v3/saida/Podio_v3_GUIA_DE_MONTAGEM.pdf`
- **Material:** frentes e tampos em 15 mm (aguentam pancada de carrinho de compras); laterais, fundos, travessas, bordas e prateleira em 9 mm. Quinas com cantoneiras de alumínio por dentro.
- **Peso:** total ~33,5 kg; caixa 1 com 14 kg, caixa 2 com 10 kg e caixa 3 com 7 kg. É o maior peso que a promotora levanta de uma vez.
- **Transporte:** carrinho de plataforma dobrável comprado (≥ 910 × 610, 300 kg). As caixas vão encaixadas de **cabeça para baixo**: a 1 com o tampo no piso do carrinho, a 2 desce dentro da 1, a 3 dentro da 2. Ninguém levanta acima da cintura. O conjunto fica com 730 × 540 × 1090 de altura.
- **Validação:** zero interferências montado, encaixado e no carrinho.

## v2 (02/11) — 9 mm em tudo, ~27 kg (substituída pela v3)
- Serra: `v2/saida/Podio_v2_SERRA_lista_de_cortes.pdf` · CNC: `v2/saida/Podio_v2_CNC.pdf` + `v2/saida/cnc_dxf/`
- Montagem: `v2/saida/Podio_v2_GUIA_DE_MONTAGEM.pdf`
- **Material:** compensado de pinus 9 mm (era 15). As quinas são unidas por 14 cantoneiras de alumínio 20 × 20 × 1,5 por dentro (6,2 m no total). O tampo é colado e parafusado nas bordas, e a caixa 1 ganhou uma travessa no alto do fundo.
- **Peso:** **~27 kg total** com haste, selo e LED (v1: ~46,5 kg). A caixa 1 tem 11 kg e dá para 1 pessoa levantar.
- **Medidas:** caixas 2 e 3 um pouco maiores (662 × 462 × 620 e 624 × 424 × 420), porque a parede fina libera espaço para o encaixe. Montado: 2026 × 540.
- **Validação:** zero interferências montado e encaixado (com as cantoneiras); 2 chapas, 74% de aproveitamento.

## v1 (31/10) — substituída pela v2 (pesada: 45 kg)
- **Serra (Luciano):** `v1/saida/Podio_v1_SERRA_lista_de_cortes.pdf`. 22 peças retangulares, 2 chapas de 15 mm, 71% de aproveitamento.
- **CNC:** `v1/saida/Podio_v1_CNC.pdf` + `v1/saida/cnc_dxf/chapa_1.dxf`, `chapa_2.dxf`. Furos Ø28 da haste, Ø5 dos pinos e furos-guia.
- **Montagem:** `v1/saida/Podio_v1_GUIA_DE_MONTAGEM.pdf`. Preparação na oficina, 4 passos no PDV e áreas de arte.

## O desenho
- **Caixa 1 (1º lugar, balcão):** 700 × 500 × 920.
  - Aberta atrás para o promotor.
  - Tampo de madeira com beiral e LED.
  - Prateleira em 4 pinos removíveis.
  - Frente com "1", "Celebre suas conquistas" e QR.
- **Caixas 2 e 3 (expositoras):** 650 × 450 × 620 e 600 × 400 × 420. Fechadas, com borda de 30 no tampo (frente e lados). Até 12 granolas em pé em cima de cada uma.
- **Selo:** smile Ø520 em PVC impresso, numa haste preta de 1" que passa pelo tampo e pela prateleira até o chão. Topo a 2160.
- **Transporte:** a 3 entra na 2 e a 2 entra na 1 → um volume de 730 × 540 × 920.
- **Medidas:** montado com 1990 × 540. Compensado 15 mm. Caixa 1 ~20 kg, caixa 2 ~15 kg, caixa 3 ~10 kg.
- **Cores:** marrom Heroica (RAL 3005), tampos em madeira natural, números em creme, selo rosa.

## Validação (v1/saida/validacao.json)
- Zero interferências montado e zero interferências encaixado (transporte).
- Plano de corte CNC verificado (≥ 12 entre peças).

## A confirmar
- Espaço que as lojas liberam. Montado ocupa ~2,0 × 0,55 m. Arranjo compacto: 2 e 3 na frente, 1 atrás (está no guia).
- Fornecedor: serra ou CNC.
