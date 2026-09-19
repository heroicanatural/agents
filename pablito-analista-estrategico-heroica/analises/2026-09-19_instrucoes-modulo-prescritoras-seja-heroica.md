# Instruções de construção: ambiente "Prescritoras" no app Seja Heroica

Escrito por Pablito em 19/09/2026 a pedido de Roberto, com base na call com a Bhava de 11/09/2026 (`2026-09-11_bhava_retencao-e-prescritoras.md`). Decisões já tomadas por Roberto: ambiente separado do de creators; visitas feitas por alguém do time, possivelmente uma nutricionista parceira; a comunidade é o canal de contato próximo com as prescritoras.

Marcação de origem: **[Bhava]** = prática descrita por Livia ou Gabi na call; **[Heroica]** = já existe no Seja Heroica segundo o Roberto na call; **[proposta]** = sugestão minha, para Roberto confirmar ou trocar.

---

## 0. Como usar este documento

É um brief para a IA que constrói o app. Está em fases; cada fase tem escopo fechado e critérios de aceite. Construa a fase 1 inteira antes de abrir a 2. Não invente dados de exemplo com nomes de nutricionistas reais. Onde houver "[decidir]", Roberto precisa responder antes de codar aquele ponto; o restante pode ser construído com o valor padrão indicado.

Premissa sobre a base de código: o Seja Heroica já tem autenticação, perfis de creator, cupons atribuídos a pessoas, seeding integrado ao Bling, push notification, Nuts e um painel admin com curadoria **[Heroica]**. O ambiente de prescritoras reutiliza esses serviços, mas tem telas, regras, moeda de pontos e permissões próprias. Nada de creator aparece para uma prescritora e vice-versa, salvo quando a mesma pessoa tem os dois perfis.

---

## 1. Objetivo e princípios

**Objetivo do ambiente:** transformar nutricionistas (e outros profissionais de saúde que prescrevem alimentação) em prescritoras recorrentes de Heroica, medindo tudo pelo uso de cupom de paciente, e mantê-las próximas da marca por uma comunidade que dá algo a elas além de produto.

**Princípios, todos vindos do que a Bhava fez dar certo:**

1. **Visita antes de amostra.** Ninguém recebe produto sem passar por uma sessão de apresentação **[Bhava]**. O sistema trava o seeding para quem não foi visitada.
2. **Cupom é a unidade de medida.** Prescrição não é rastreável; cupom de paciente é **[Bhava]**. Todo indicador do painel deriva de cupom.
3. **Amostra é cara, então é escalonada e única por padrão.** Reenvio só por gatilho, nunca por calendário **[Bhava]**.
4. **Sem fee, sem comissão em dinheiro.** A Bhava opera com cupom, amostra e pontos **[Bhava]**. Comissão a nutricionista pode conflitar com o código de ética da profissão **[proposta, validar antes de mudar]**.
5. **Comunidade dá valor para a nutri, não só para a Heroica.** Conteúdo de carreira, gestão e consultório, não só produto **[Bhava]**.
6. **Uma pessoa dona.** Na Bhava é a Nath, em tempo integral **[Bhava]**. Aqui o sistema precisa de um papel "gestora do programa" com dono nomeado desde o dia 1 **[decidir: quem]**.

---

## 2. Papéis e permissões

| Papel | Quem | Vê e faz |
|---|---|---|
| Prescritora | nutricionista ou profissional de saúde aprovada | seu perfil, seus cupons e resultados, agenda de visitas, comunidade, materiais, mercadinho de pontos |
| Visitadora | pessoa do time ou nutricionista parceira que conduz sessões **[decisão do Roberto]** | agenda de sessões, lista de inscritas, registro pós-visita, comunidade como autora. Não vê financeiro nem seeding |
| Gestora do programa | dona do programa | tudo da visitadora + fila de amostras, tiers, aprovação, curadoria, KPIs, campanhas |
| Admin | Roberto | tudo + configurações (percentuais, tiers, regras de pontos) |

Uma pessoa pode ter perfil de prescritora e de creator ao mesmo tempo; o app mostra um seletor de ambiente no topo, e cada ambiente mantém seus próprios cupons, pontos e regras **[Bhava puxa nutris influenciadoras para creators; proposta de implementação]**.

---

## 3. Modelo de dados

### 3.1 Prescritora

Campos coletados na inscrição (LP pública + formulário no app):

- nome, e-mail, WhatsApp, cidade, estado
- profissão (nutricionista, médica, educadora física, outra) e número de registro profissional (CRN, CRM, CREF) **[Bhava aceita qualquer profissional de saúde]**
- especialidade principal: esportiva, clínica, funcional, comportamental, materno-infantil, outra **[Bhava segmenta assim]**
- atende em: consultório presencial, online, os dois
- pacientes atendidos por mês, faixa (até 20, 20 a 50, 50 a 100, mais de 100) **[proposta; a Bhava usa só seguidores e Livia disse que nutri tem 20 a 50 pacientes]**
- Instagram e número de seguidores
- como conheceu a Heroica: evento (qual), indicação de colega (quem), Instagram, loja, outro
- aceite de termos do programa e de uso de dados (LGPD)

Campos preenchidos pelo time depois:

- status do funil (seção 4)
- tier de amostra (1, 2, 3)
- visitadora responsável, data da visita, notas da visita
- flags: ativa nas redes, candidata a creator, relevante
- histórico de amostras (data, kit, custo, nota Bling)
- cupom próprio e cupom de paciente (código, data de ativação)

### 3.2 Sessão de visita

- data, hora, duração, link da reunião, capacidade (padrão 12; Bhava faz 10 a 15) **[Bhava]**
- visitadora
- lista de inscritas, presença por inscrita
- pauta padrão (seção 5.2) e material apresentado

### 3.3 Amostra (seeding)

Reutiliza a entidade de seeding dos creators **[Heroica]**, com campo `tipo_destinatario = prescritora`, `tier`, `motivo` (primeira amostra, reenvio por cupom, reenvio por post, reenvio por pedido, kit consultório) e `custo_estimado`.

### 3.4 Cupom

Reutiliza a atribuição de cupom por pessoa já existente **[Heroica]**. Dois cupons por prescritora:

- **uso próprio:** código genérico do programa, desconto padrão 20% **[Bhava; decidir valor]**, limitado a N usos por mês **[proposta: 2]**
- **paciente:** código personalizado escolhido pela prescritora, desconto padrão 10% **[Bhava; decidir valor]**, sem limite de usos, sem comissão

Cada pedido com cupom de paciente registra: prescritora, valor, produtos, se é primeira compra do cliente, data.

### 3.5 Pontos ("Nuts Prescritoras")

Moeda separada da dos creators, com regras e mercadinho próprios **[proposta; a Bhava usa a mesma moeda "flows" para tudo, mas aqui os ambientes são separados por decisão do Roberto]**. Ledger com origem de cada crédito e débito.

### 3.6 Comunidade

- post (autor, tipo: conteúdo Heroica, pergunta de prescritora, caso de consultório, evento), comentários, curtidas
- grupos: por especialidade e por cidade/região **[proposta]**
- materiais (arquivos versionados com categoria)
- eventos (data, cidade, vagas, inscritas)

---

## 4. Funil de status e regras de transição

```
inscrita → aprovada → visita agendada → visitada → amostra enviada → ativa → recorrente → relevante
                                                                        ↘ inativa (90 dias sem uso de cupom)
```

| Status | Como entra | O que libera |
|---|---|---|
| inscrita | preencheu o formulário | nada; recebe mensagem de boas-vindas com link de agendamento |
| aprovada | gestora aprova (checa registro profissional e perfil) | pode se inscrever em sessão de visita |
| visita agendada | escolheu um slot | lembrete automático |
| visitada | visitadora marca presença e preenche o registro | cupom próprio ativado; formulário de personalização do cupom de paciente; entra na fila de amostra com o tier atribuído |
| amostra enviada | seeding despachado (nota no Bling) | acesso pleno à comunidade e ao mercadinho |
| ativa | cupom de paciente usado ao menos 1x | contagem para KPIs |
| recorrente | cupom usado em 2 meses consecutivos **[proposta]** | elegível a reenvio |
| relevante | recorrente + postou marcando a Heroica, ou gestora marca à mão | elegível a kit completo, convite a creator, convite a evento |
| inativa | 90 dias sem uso de cupom de paciente | fluxo de reativação; sai das listas de reenvio |

Regras que o sistema impõe:

- Seeding bloqueado para status anterior a "visitada" **[Bhava]**.
- No-show em sessão: volta para "aprovada", recebe novo link. Dois no-shows: gestora decide **[proposta]**.
- Reenvio de amostra: intervalo mínimo de 90 dias desde o último envio e exige um gatilho registrado (cupom rodou, postou, pediu) **[Bhava: 3 a 4 meses, só por gatilho]**.
- Status nunca é "excluída". Como na lógica dos creators, ninguém sai do programa; o cupom continua ativo e a pessoa some das filas **[Heroica]**.

---

## 5. Fluxos

### 5.1 Inscrição

1. LP pública `/prescritoras` com: o que é o programa, o que a prescritora recebe (visita, amostra, cupons, comunidade, materiais), o que a Heroica espera (usar, conhecer, indicar quando fizer sentido clínico), FAQ curto, formulário. Isa escreve o texto.
2. Formulário grava a prescritora com status "inscrita" e dispara mensagem de boas-vindas por WhatsApp (REVI) e e-mail com o link da agenda.
3. Gestora vê fila de "inscritas" no admin, com link para o Instagram e o número de registro, e aprova ou recusa com motivo.

### 5.2 Visita em grupo

1. Gestora cria slots de sessão (semanal no início; Bhava faz diário). Capacidade padrão 12.
2. Prescritora aprovada escolhe o slot no app. Confirmação por WhatsApp e push; lembrete 24 h e 1 h antes.
3. Pauta padrão da sessão, 45 a 60 min, a ser construída como material do app **[Bhava: essência, produtos, valores]**:
   - história da Heroica e por que existe (5 min)
   - produtos: composição, porção sugerida, para quem serve e para quem não serve, como encaixar num plano alimentar (20 min). Isso responde à objeção "granola é calórica" que Gabi citou.
   - como funciona o programa: cupons, amostra, comunidade, pontos, o que não fazemos (fee, comissão) (10 min)
   - perguntas (15 min)
4. Ao final, a visitadora abre a tela de registro: presença por inscrita, nota livre por pessoa, tier de amostra sugerido, flags. Salvar muda status para "visitada".
5. Visitada recebe na hora: cupom próprio ativo, formulário para escolher o nome do cupom de paciente (a Bhava faz isso por automação), e aviso de que a amostra entra na fila.

### 5.3 Amostra

1. Fila de amostras no admin, ordenada por data de visita, com tier, custo estimado e idade na fila. Meta: idade média abaixo de 21 dias **[proposta; a Bhava está com 3 meses e considera problema]**.
2. Tiers **[Bhava por influência; conteúdo é proposta, Roberto define]**:
   - Tier 1 (até 2 mil seguidores, até 20 pacientes/mês): pacote de Heroiquinhas sortidas
   - Tier 2 (2 a 10 mil seguidores ou 20 a 50 pacientes): 1 granola + 1 pasta + Heroiquinhas
   - Tier 3 (acima disso ou marcada relevante): kit completo
   - **Kit consultório** (qualquer tier, mediante pedido e registro de endereço do consultório): 1 pacote de granola para o cafezinho da recepção com display de mesa **[ideia da Livia, 27:00]**
3. Gestora seleciona lote da semana e gera o seeding; integração Bling já existente emite a nota e a Karina despacha **[Heroica]**.
4. Prescritora recebe push e WhatsApp "sua amostra saiu", com pedido para postar se quiser (sem obrigação) e lembrete do cupom de paciente.

### 5.4 Cupons e atribuição

- Uso próprio: ativado na visita. Limite mensal configurável.
- Paciente: criado no nome escolhido; validação de unicidade e de palavras proibidas. Ativação avisada por push e WhatsApp.
- Cada venda com cupom de paciente gera push para a prescritora "uma paciente sua comprou" com produto e valor, como já acontece com creators **[Heroica]**.
- Sem saldo em dinheiro. A venda gera Nuts Prescritoras (seção 7).

### 5.5 Comunidade

Este é o canal de proximidade. Regras de conteúdo:

- A Heroica publica no mínimo 2 vezes por semana **[proposta]**, com mistura de: receita com porção e macros, ficha técnica de produto, bastidores da fábrica, calendário de eventos com convite, conteúdo de carreira (gestão de consultório, marketing para nutri, atendimento) **[Bhava: gestão, marketing, inovação, atendimento, desenvolvimento pessoal]**.
- Prescritoras podem postar: pergunta à Heroica, caso de consultório (sem dados de paciente), foto de uso, indicação de colega.
- Grupos por especialidade e por região para facilitar encontro presencial e convite a eventos (HTX, corridas).
- Enquetes rápidas da Heroica para ouvir a base (novo sabor, porção, embalagem).
- A visitadora e a gestora são as autoras oficiais; respondem perguntas em até 48 h **[proposta]**.
- Moderação: gestora pode ocultar post e comentário. Termos vedam claim de saúde não comprovado e dado de paciente.

### 5.6 Materiais para consultório

Biblioteca com download:

- tabela nutricional e porção sugerida de cada produto (PDF e imagem para WhatsApp)
- guia "como encaixar Heroica no plano alimentar" por objetivo
- cartão de indicação com o cupom da prescritora (gerado com o código dela, para imprimir ou mandar por WhatsApp ao paciente)
- imagens de produto com fundo transparente (as mesmas que a transição da Marcela pede)

### 5.7 Reativação e reenvio

- 60 dias sem uso de cupom: WhatsApp e push com conteúdo (não promoção) e pergunta "quer receber a novidade X?" **[proposta]**.
- 90 dias: status "inativa".
- Gatilho de reenvio registrado automaticamente quando: cupom de paciente somou acima de R$ X no trimestre **[decidir X]**, prescritora postou marcando a Heroica (registro manual pela gestora ou via link), prescritora pediu pelo app.

---

## 6. Painel da gestora (admin)

Tela inicial com os números do mês e comparação com o mês anterior:

1. **Funil:** inscritas, aprovadas, visitadas, amostras enviadas, ativas. Taxa visitada → ativa em 60 dias em destaque.
2. **Base:** total, ativas, recorrentes, relevantes, inativas. Percentual de ativas sobre a base.
3. **Cupons:** usos e receita atribuída por cupom de paciente, top 10 prescritoras, primeiras compras geradas.
4. **ROI do programa:** receita atribuída no período dividida por custo de amostras + frete no período. A Bhava usa este cálculo e considera 3 o piso **[Bhava]**. Mostrar também a versão incluindo custo de gente e ferramentas **[proposta]**.
5. **Retenção de paciente:** dos clientes que entraram por cupom de prescritora, quantos fizeram 2ª compra em 90 dias, comparado com o cliente médio da loja. É o argumento central da Livia (17:30) e precisa ser provado na Heroica.
6. **Fila de amostras:** tamanho, idade média, custo do lote pendente.
7. **Comunidade:** prescritoras ativas na comunidade nos últimos 30 dias, posts, perguntas sem resposta há mais de 48 h.
8. **Mapa:** distribuição por cidade e especialidade, para decidir onde fazer visita presencial ou evento.

Curadoria automática, no mesmo padrão da tela de creators **[Heroica]**:

- "aprovar": registro válido, perfil coerente
- "reenviar": recorrente, cupom rodou, sem envio há 90 dias
- "não reenviar": recebeu amostra, nunca ativou cupom, nunca entrou na comunidade
- "convidar para creators": relevante e acima de N seguidores
- "convidar para evento": ativa na cidade do próximo evento

Exportação CSV de tudo.

---

## 7. Nuts Prescritoras e mercadinho

Regras de crédito **[proposta, inspirada nos flows da Bhava e nos Nuts dos creators]**:

| Ação | Nuts |
|---|---|
| participou da visita | 50 |
| ativou cupom de paciente | 30 |
| cada venda no cupom de paciente | 10 por venda + 1 por R$ 10 |
| primeira compra de paciente novo | +20 |
| postou na comunidade | 5 (máximo 20 por semana) |
| respondeu enquete | 5 |
| indicou colega que foi visitada | 40 |
| presença em evento Heroica | 60 |
| postou nas redes marcando a Heroica (validado pela gestora) | 30 |

Mercadinho **[proposta]**: produtos Heroica, kit consultório extra, ingresso ou cortesia para HTX e eventos, materiais impressos personalizados, e itens de carreira (livro indicado, vaga em workshop) **[Bhava troca por produto e livros]**. Resgate gera seeding pelo fluxo normal. Sem conversão em dinheiro.

---

## 8. Automações (REVI para WhatsApp e e-mail, push do app)

| Gatilho | Canal | Mensagem |
|---|---|---|
| inscrição | WhatsApp + e-mail | boas-vindas + link da agenda |
| aprovação | push + WhatsApp | "você foi aprovada, escolha sua sessão" |
| 24 h e 1 h antes da sessão | WhatsApp + push | lembrete com link |
| registro de visita | push + WhatsApp | cupom próprio + formulário do cupom de paciente |
| cupom de paciente criado | push + WhatsApp | código ativo + cartão de indicação |
| seeding despachado | push + WhatsApp | "sua amostra saiu" + rastreio |
| venda no cupom | push | "uma paciente sua comprou X" |
| 60 dias sem uso | WhatsApp | conteúdo + pergunta |
| pergunta sem resposta há 48 h | push para gestora | alerta interno |
| novo post da Heroica | push | opcional, respeitando preferência da prescritora |

Respeitar recência mínima de 7 dias para mensagens de campanha em massa, como Bhava e Heroica já fazem **[Bhava 44:00, Heroica 43:10]**. Mensagens transacionais (lembrete, cupom, envio) não contam nesse limite.

---

## 9. Fases de construção e critérios de aceite

### Fase 1: operar o funil (construir primeiro)

Escopo: LP e formulário; papéis e permissões; perfil de prescritora; funil de status; sessões de visita com agenda, inscrição, lembretes e registro pós-visita; cupom próprio e cupom de paciente com atribuição de venda; fila de amostras com tiers e seeding via Bling; automações da tabela acima até "venda no cupom"; painel com funil, cupons, fila e ROI.

Aceite:

- uma prescritora consegue se inscrever, ser aprovada, escolher sessão, ser marcada como visitada, receber os dois cupons e aparecer na fila com tier, sem intervenção manual fora do app
- é impossível gerar seeding para status anterior a "visitada"
- uma venda com cupom de paciente aparece no perfil dela, no painel e no ROI em até 1 hora
- a gestora vê o funil do mês e a idade da fila na tela inicial
- nenhum dado ou tela de prescritora aparece no ambiente de creators, e vice-versa

### Fase 2: comunidade e proximidade

Escopo: feed com posts, comentários, curtidas; grupos por especialidade e região; materiais para consultório com cartão de indicação gerado; enquetes; Nuts Prescritoras e mercadinho; push de novo conteúdo; alerta de pergunta sem resposta.

Aceite:

- prescritora visitada posta, comenta, baixa material com seu cupom impresso e resgata item no mercadinho
- gestora publica conteúdo e responde; posts sem resposta há 48 h aparecem em alerta
- ledger de Nuts mostra origem de cada crédito

### Fase 3: inteligência e ponte

Escopo: curadoria automática; regras de reenvio por gatilho; reativação aos 60 e 90 dias; métrica de retenção de paciente; mapa por cidade; convite automático a evento e a creators; exportações.

Aceite:

- a curadoria sugere ações com motivo legível
- o painel mostra retenção de paciente vinda de prescritora contra cliente médio
- prescritora marcada "relevante" recebe convite a creator e, se aceitar, o seletor de ambiente aparece para ela

---

## 10. Decisões que faltam do Roberto antes de codar

1. Nome do ambiente e do programa (sugestões: "Heroica Prescritoras" ou "Consultório Heroica").
2. Quem é a gestora do programa e quem conduz as visitas nos primeiros 60 dias.
3. Percentuais dos cupons (padrão proposto: 20% próprio, 10% paciente, iguais aos da Bhava).
4. Conteúdo e custo dos três tiers de amostra e do kit consultório.
5. Valor X de cupom no trimestre que dispara reenvio.
6. Se aceita profissionais além de nutricionistas desde o início ou começa só com nutris.
7. Confirmação de que não haverá comissão em dinheiro, após checar o código de ética do CFN.

---

## 11. Riscos que o sistema não resolve

- Sem visitadora com agenda semanal fixa, o funil para em "aprovada". A Bhava só escalou quando contratou a Nath.
- Sem conteúdo novo na comunidade, ela morre em 30 dias. Precisa de dono e calendário, e a Marcela sai em 25/09.
- Amostra sem trava de custo vira o mesmo problema que os creators tinham antes da plataforma: kit caro para quem não posta nem vende.
- Claim de saúde em conteúdo para nutricionistas é mais sensível que para consumidora; passar tudo por validação antes de publicar.
