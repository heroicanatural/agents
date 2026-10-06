# Box Run Club Heroica

Pedido (Roberto, 06/10/2026): estrutura móvel em compensado naval, inspirada no carrinho de DJ do run club do Lumin ("Run & a rave"), com espaço para a marca Heroica e para patrocinador. A caixa vai sobre um **carrinho-plataforma comprado pronto** (4 rodas pneumáticas, cabo em T). O Estúdio projeta só a caixa.

**Status v1 (06/10):** pronta para orçamento de corte.
- Fábrica: `v1/saida/Box_RunClub_v1_FABRICA.pdf` + `v1/saida/dxf/chapa_1.dxf`, `chapa_2.dxf`
- Montagem: `v1/saida/Box_RunClub_v1_GUIA_DE_MONTAGEM.pdf`
- Texto para a fábrica: `v1/pedido_fabrica.md`

## Suposições (a confirmar antes de cortar)
- Plataforma de **1200 × 600 mm, a 450 mm do chão** (modelo mais comum; ex.: [Obramax 1,20 × 0,60 × 0,42](https://www.obramax.com.br/carro-plataforma-1200x600mm-madeira-500kg-sem-abas-89547836/p), [Gadotti 120 × 60 × 45](https://www.gadotticar.com.br/produto/carro-plataforma-400-roda-macica)). **Medir o carrinho comprado.**
- Equipamento de referência: controladora Pioneer DDJ-FLX4 (482 × 273 mm) e caixa JBL PartyBox 310 deitada (688 × 368 × 326 mm). Os dois cabem juntos no tampo.
- Compensado naval 15 mm em chapa de 2200 × 1600 ([padrão de mercado](https://www.ceddistribuidora.com.br/produtos/compensado-naval-15mm-220x160/), ~37 kg por chapa).

## O desenho
- Caixa de 1190 × 580 × 800, com fundo a 450 e tampo de trabalho a **1000 do chão** (altura de DJ em pé).
- **Lado do DJ**, no lado do cabo do carrinho: painel baixo com porta de 410 × 405 para o baú (1160 × 550 × 520 internos). Fita LED logo abaixo do tampo.
- **Fachada** do lado oposto, subindo até 1250: é a cara da marca para quem vem atrás correndo.
- **Laterais** inclinadas (590 → 800): Heroica + patrocinador.
- **Fixação no carrinho:** 4 parafusos M8 com borboleta; a caixa sai sem ferramenta.
- **Montagem:** cola PU + parafusos 4,0 × 40 em 92 furos-guia que a própria CNC fura. Não precisa de oficina.

## Validação (v1/saida/validacao.json)
- 10 peças válidas, **zero interferências**, cabe na plataforma.
- 2 chapas, aproveitamento de 51% (sobra ~meia chapa 2).
- Peso da caixa: ~39 kg.
