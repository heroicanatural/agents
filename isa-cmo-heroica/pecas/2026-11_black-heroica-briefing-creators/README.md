# Briefing creators · Black Heroica (novembro 2026)

Documento de direcionais para os creators do Seja Heroica, no mesmo papel do
"Antecipa Black" que a PINC manda para o Pinc Squad. Feito a pedido do Roberto
em 04/11/2026.

## Canva

- Design `DAHZ9kKmM9U`, "Briefing Black Heroica", 11 páginas 16:9.
- Editar: https://www.canva.com/d/uQJbxUbw_cMIX6_
- Ver: https://www.canva.com/d/anGtqcHIRiwqYWk
- Criado com create-design (brief + outline) e depois editado página a página.
  Paleta da Heroica: marrom #602221, bege #eedab3, creme #fff8e3, rosa
  #e64891, amarelo #ffc541.

## Estrutura (espelho do briefing da PINC)

| Pág. | Seção | O que tem |
|---|---|---|
| 1 | Capa | "Direcionais · BLACK HEROICA", missão do material, foto gerada com a embalagem real da Heroica (`MAHZ90tvrz4`) |
| 2 | Conceito | "A Heroica é legal. A sua vida é muito mais." Missão de novembro: comida de verdade e comprar perto como escolha inteligente. Três pontos: produto na rotina; Floripa/SC = compre perto; fora de SC = marca brasileira fundada por uma mulher atleta |
| 3 | Conheça a campanha | 1 a 30/11, até 30% OFF no site já aplicado, +5% com o cupom do creator, uma vez por ano. Vale em combos e produtos da Black, só no site. Agenda: 03/11 primeira onda, 06/11 sorteio R$300 no grupo VIP, 18/11 segunda onda, 27/11 pico |
| 4 | Direcionais · Floripa e SC | 4 ganchos: Compre perto, Desconto de verdade, Pós-treino de quem mora aqui, Estoque da vida real |
| 5 | Direcionais · fora de SC | 4 ganchos: Marca brasileira, Começou na cozinha de uma atleta, Sem pegadinha, Quem está por trás |
| 6 | Roteiro exemplo · Floripa · 30s | Linha do tempo 0-5 / 5-10 / 10-15 / 15-25 / 25-30s com as falas do Klike |
| 7 | Roteiro exemplo · fora de SC · 30s | Mesma lógica, versão marca brasileira + fundadora atleta |
| 8 | Chegou a sua vez | Vida real, Produto na rotina, História, Criatividade, Oportunidade comercial. Três fotos de fundo: cozinha com embalagem (gerada), creator com o pacote ao ar livre (foto real `MAHIzVByfuM`), cupom no celular com a Heroica na prateleira (gerada `MAHZ9wiHDVw`) |
| 9 | Figurinhas | Prévia do pack gerado (`MAHZ9shkVtQ`): BLACK HEROICA, ATÉ 30% OFF, +5% COM MEU CUPOM, FEITA EM FLORIPA, COMPRE PERTO, 1 A 30/11. Link do Drive por inserir |
| 10 | O que não pode faltar | Checklist de 6 itens + "Importante" sobre limites da oferta |
| 11 | Sonhe. Lute. | Fechamento, dúvidas no grupo VIP |

## Roteiros (Klike)

Gerados com `generate_video_script` em modo influencer, 30s, Meta, a partir
do contexto e da voz de marca cadastrados no Klike. O briefing do Klike foi
preenchido por mim sem confirmação prévia do Roberto (tom, duração,
plataforma). Os textos foram adaptados para caber nos slides e para
corrigir acentuação, que o Klike devolve sem diacríticos.

- Floripa/SC: "Rotina Local em Floripa", "Desconto Real sem Pegadinha",
  "Pós-Treino de Quem Mora Aqui".
- Fora de SC: "Apoie marcas nacionais neste treino", "Valorize o que é nosso
  de verdade", "A história por trás da sua granola".
- O Klike citou "até trinta e cinco por cento" em um post. Está correto: o
  deck do Papo dos Heroicos diz que o cupom a 5% acumula sobre os até 30% do
  site, "na prática 35% para quem compra com o cupom".

## Dados usados

- Mecânica, datas e agenda vêm do deck "Papo dos Heroicos 02/11"
  (`DAHZy_6bNF4`) e do relatório de outubro.
- Angeloni citado no gancho 02 da página 5, como no deck de novembro.
- "Fundada por uma mulher atleta" e "começou empacotando granola em casa"
  seguem o que está no contexto de marca do Klike e no pitch.

## Artes geradas (generate-image)

- `MAHZ90tvrz4` capa e página 8: creator na cozinha segurando a embalagem
  real (referência `MAHIzVByfuM`, foto da biblioteca).
- `MAHZ9wiHDVw` página 8: cupom no celular, prateleira com a Heroica.
- `MAHZ9shkVtQ` página 9: pack de figurinhas.
- Pedido do Roberto em 04/11: sempre que a imagem gerada tiver alguém
  segurando pote de granola, usar a embalagem da Heroica como referência.
  As duas primeiras versões (pote genérico, `MAHZ9t3JYSA` e `MAHZ9nojoOA`)
  foram descartadas.

## Pendências para o Roberto

- Conferir mecânica e datas com o que vai valer de fato (30% + 5%, agenda).
- Inserir o link do Drive do pack de figurinhas (página 9) e produzir o pack
  final a partir da prévia.
- Fontes: os textos adicionados via API ficam na fonte padrão do Canva;
  ajustar no editor para a fonte do deck.
- Decidir se os roteiros vão como estão ou se o Klike roda uma segunda rodada
  com briefing revisado por você.

## Versão enxuta de 4 slides (04/11, pedido do Roberto)

- Design `DAHZ-PcbNVE`, "Briefing Black Heroica", 4 páginas 16:9.
- Editar: https://www.canva.com/d/qhhkH62owz_A1fc
- Ver: https://www.canva.com/d/JnqxJ8bF664I1uY
- Estrutura pedida: 1 capa; 2 a campanha (como o cupom funciona, chance de
  liberar o seeding, por que novembro funciona); 3 roteiros (Floripa/SC e
  fora de SC, 30s, lado a lado); 4 figurinhas.
- Mecânica confirmada no Papo dos Heroicos: até 30% no site sem cupom, cupom
  a 5% acumulando (35% na prática), faixa de comissão acompanha, uma vez por
  ano. Seeding libera com R$189 em vendas ou 380 nuts. Cupom de melhor
  desempenho em novembro ganha prêmio surpresa.
- Fotos: capa com `MAHZ90tvrz4` (embalagem real), figurinhas `MAHZ9shkVtQ`.
- **Fonte:** Roberto pediu Pilcrow Rounded em tudo. O brief do create-design
  pediu a fonte, mas o gerador não aplicou e a API não permite trocar família
  de fonte. Pendência manual: no editor, selecionar tudo e aplicar Pilcrow
  Rounded (títulos bold, corpo regular).
- A versão longa de 11 páginas (`DAHZ9kKmM9U`) fica como material de apoio.
