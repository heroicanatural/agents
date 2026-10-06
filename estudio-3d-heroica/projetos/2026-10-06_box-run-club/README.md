# Box Run Club Heroica

Pedido (Roberto, 06/10/2026): estrutura móvel em compensado naval, inspirada no carrinho de DJ do run club do Lumin ("Run & a rave"), com espaço para a marca Heroica e para patrocinador. A caixa vai sobre um **carrinho-plataforma comprado pronto** (4 rodas pneumáticas, cabo em T). O Estúdio projeta só a caixa.

## Versão atual: v2 (06/10) — pronta para orçamento de corte
- Fábrica: `v2/saida/Box_RunClub_v2_FABRICA.pdf` + `v2/saida/dxf/chapa_1.dxf`, `chapa_2.dxf`
- Montagem: `v2/saida/Box_RunClub_v2_GUIA_DE_MONTAGEM.pdf`
- Texto para a fábrica: `v2/pedido_fabrica.md`

| | v1 | v2 |
|---|---|---|
| Carrinho | suposto 1200 × 600 | **ficha real: 1000 × 600, 45 cm dobrado, 300 kg** |
| Caixa (C × L × A) | 1190 × 580 × 800 | **990 × 1000 × 800** (passa 200 de cada lado, pedido do Roberto) |
| Acesso ao baú | 1 porta 410 × 405 | **2 portas 385 × 435** + divisória central |
| Baú | 1160 × 550 × 520 | 2 compartimentos de 960 × 478 × 520 |
| Chapas | 2 (51%) | 2 (69%, laterais encaixadas invertidas) |
| Peso da caixa | ~39 kg | ~54 kg |

## O desenho (v2)
- **Tampo de trabalho a 1000 do chão**, 975 × 970 úteis. A caixa de som deitada vai atravessada, encostada na fachada, e a controladora fica na frente dela.
- **Lado do DJ** (lado do cabo do carrinho): painel baixo com 2 portas que abrem para os lados. Fita LED logo abaixo do tampo.
- **Divisória central:** separa equipamento/cabos de produto e apoia o meio do tampo, que vence ~1 m.
- **Fachada** do lado oposto, subindo até 1250: Heroica + patrocinador (840 × 200).
- **Laterais** inclinadas (590 → 800): Heroica + patrocinador (600 × 160).
- **Balanço:** a caixa passa 200 de cada lado da plataforma. O fundo fica a 450, ~100 acima do topo das rodas (Ø~350, a confirmar).
- **Fixação no carrinho:** 4 parafusos M8 com borboleta, dentro da área da plataforma.
- **Montagem:** cola PU + parafusos 4,0 × 40 em 132 furos-guia feitos pela CNC.

## Validação (v2/saida/validacao.json)
- 8 tipos de peça (15 peças + 2 portas que saem do recorte), todas válidas. **Zero interferências.**
- Plano de corte verificado: distância real ≥ 12 mm entre peças e margem de 10 mm.

## A confirmar
- Altura real do topo da plataforma (a ficha diz "45 cm dobrado") e o Ø das rodas.
- A fábrica fura Ø3 ou só marca?

## Histórico
- v1: caixa do tamanho da plataforma suposta, 1 porta. Substituída pela v2 (não usar).
