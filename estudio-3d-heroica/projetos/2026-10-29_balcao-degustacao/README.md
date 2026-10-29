# Balcão de degustação dobrável Heroica

Pedido (Roberto, 29/10/2026): balcão promocional para degustação em PDV, no formato do balcão com testeira de referência (84 × 42 cm de base, 2 m com a bandeira), mas **só com peças planas**:
- laterais fixas na frente por dobradiça;
- tampo que encaixa nas faces frontal e laterais;
- prateleiras internas encaixáveis;
- 2 furos no tampo para as hastes da bandeira.

## v1 (29/10) — pronta para orçamento de corte
- Fábrica: `v1/saida/Balcao_Degustacao_v1_FABRICA.pdf` + `v1/saida/dxf/chapa_1.dxf`, `chapa_2.dxf`
- Montagem e desmontagem: `v1/saida/Balcao_Degustacao_v1_GUIA_DE_MONTAGEM.pdf`

## O desenho
- **Material:** compensado 12 mm, corte CNC. 7 tipos de peça (8 peças), ~22 kg.
- **Medidas:** montado com 880 × 440 × 2000 (com bandeira), mesa a **920 do chão**.
- **Corpo:** frente 840 × 920 + 2 laterais 408 × 920 com 3 dobradiças cada. As laterais dobram para dentro e o corpo fecha com **~25 mm** de espessura para transporte.
- **Encaixes:** base e tampo encaixam por espiga e rasgo nas 3 faces (2 espigas na frente, 1 em cada lateral) e travam o esquadro. Montagem do dia a dia sem ferramenta.
- **Prateleiras:** 814 × 395, presas por espigas de 150 que atravessam as laterais. Vãos de 286 / 288 / 298.
- **Frente:** sem nenhum furo ou rasgo; a área inteira fica livre para a marca.
- **Bandeira:** 2 hastes de alumínio 1" (838 + 838, com luva) passam pelo tampo e pela prateleira de cima e apoiam na de baixo. Testeira 840 × 300 presa com 4 abraçadeiras U.
- **Rasgos:** 12,5 (chapa 12,0 + 0,5 de folga), com sobra para a fresa Ø6 nas pontas e alívio na base das espigas.

## Validação (v1/saida/validacao.json)
- Peças válidas, **zero interferências** (inclusive hastes × furos e laterais dobradas × frente).
- 1 balcão = 2 chapas (44%). 2 balcões = 3 chapas, 4 balcões = 6 chapas.

## A confirmar
- **Espessura real da chapa** (paquímetro): o arquivo é refeito se não for 12,0.
- Medida da abraçadeira U 1" comprada (furos a 34 mm).
- Quantidade: se forem 2 ou mais, cortar junto sai mais barato por unidade.
