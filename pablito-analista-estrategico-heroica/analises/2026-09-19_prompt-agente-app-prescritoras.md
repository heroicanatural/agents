# Prompt para o agente que constrói o app Seja Heroica: ambiente Prescritoras

Escrito por Pablito em 19/09/2026. Cole o bloco abaixo inteiro como primeira mensagem para o agente do app. Ele é autocontido; o brief completo está em `2026-09-19_instrucoes-modulo-prescritoras-seja-heroica.md`.

---

```
Você vai construir um novo ambiente dentro do app Seja Heroica chamado "Prescritoras", separado do ambiente de creators. Trabalhe em fases. Antes de escrever código, faça o mapeamento do item 1 e me apresente o plano do item 2. Só depois implemente a fase 1. Não abra a fase 2 sem eu aprovar a fase 1.

## 1. Mapeie o que já existe antes de tocar em qualquer coisa

Leia o código e me devolva um resumo curto de como funcionam hoje, com os arquivos principais:
- autenticação e perfis (como um creator é criado, aprovado, autenticado)
- cupons: como um cupom é atribuído a uma pessoa e como uma venda da loja é ligada a esse cupom
- seeding: como um envio é planejado e como ele gera nota no Bling
- push notifications e mural de recados
- Nuts: ledger, regras de crédito, mercadinho
- painel admin e a tela de curadoria (a que sugere aprovar/descontinuar creators)
- integrações externas (Shopify, Bling, REVI ou WhatsApp, e-mail)

Aponte o que dá para reutilizar como serviço compartilhado e o que precisa ser duplicado ou parametrizado. Se algo abaixo conflitar com a arquitetura atual, diga antes de implementar, não adapte em silêncio.

## 2. Regras fixas do ambiente Prescritoras

Estas regras não são negociáveis; o sistema precisa impor todas.

R1. Ambiente separado. Uma prescritora não vê nada de creators e um creator não vê nada de prescritoras. A mesma pessoa pode ter os dois perfis; nesse caso aparece um seletor de ambiente e cada ambiente mantém seus próprios cupons, pontos e regras.
R2. Amostra só depois da visita. É impossível gerar seeding para uma prescritora com status anterior a "visitada".
R3. Cupom de paciente é a unidade de medida. Todo indicador do painel deriva de uso de cupom.
R4. Sem comissão em dinheiro, sem saque, sem saldo financeiro. Prescritoras recebem cupom, amostra e pontos.
R5. Reenvio de amostra exige gatilho registrado e intervalo mínimo de 90 dias desde o último envio.
R6. Ninguém é excluída. Status "inativa" tira a pessoa das filas, mas o cupom continua ativo.

## 3. Papéis

- prescritora: vê seu perfil, seus cupons e resultados, agenda de sessões, comunidade (fase 2), materiais (fase 2), mercadinho (fase 2).
- visitadora: pessoa do time ou nutricionista parceira, com login próprio e ambiente próprio (item 6A). Vê quem vai visitar, registra presença e notas, acompanha como estão performando as que já visitou, publica na comunidade. Não vê financeiro, custo de amostra, seeding nem dados de outras visitadoras, salvo se a gestora liberar.
- gestora do programa: tudo da visitadora + aprovação, fila de amostras, tiers, curadoria, KPIs.
- admin: tudo + configurações (percentuais de cupom, tiers, regras de pontos, capacidade de sessão).

## 4. Modelo de dados

Prescritora, campos de inscrição: nome, e-mail, WhatsApp, cidade, estado, profissão (nutricionista, médica, educadora física, outra), número de registro profissional, especialidade (esportiva, clínica, funcional, comportamental, materno-infantil, outra), atende em (presencial, online, ambos), faixa de pacientes por mês (até 20, 20 a 50, 50 a 100, mais de 100), Instagram, seguidores, como conheceu (evento e qual, indicação de colega e quem, Instagram, loja, outro), aceite de termos e LGPD.
Campos internos: status, tier de amostra (1, 2, 3), visitadora responsável, data e notas da visita, flags (ativa nas redes, candidata a creator, relevante), histórico de amostras, cupom próprio, cupom de paciente, data do último envio, data do último uso de cupom.

Sessão de visita: data, hora, duração, link da reunião, capacidade (padrão 12, configurável), visitadora, inscritas, presença por inscrita, notas por inscrita.

Amostra: reutilize a entidade de seeding existente com tipo_destinatario = prescritora, tier, motivo (primeira amostra, reenvio por cupom, reenvio por post, reenvio por pedido, kit consultório) e custo estimado.

Cupom: reutilize a atribuição existente. Dois por prescritora:
- próprio: código genérico do programa, desconto padrão 20%, limite padrão de 2 usos por mês, configurável.
- paciente: código personalizado escolhido por ela, desconto padrão 10%, sem limite de usos, sem comissão. Validar unicidade e lista de palavras proibidas.
Cada venda com cupom de paciente registra prescritora, valor, produtos, se é primeira compra do cliente, data.

## 5. Funil de status e transições

inscrita > aprovada > visita agendada > visitada > amostra enviada > ativa > recorrente > relevante; qualquer status pode ir para inativa.

- inscrita: preencheu o formulário. Dispara boas-vindas com link da agenda.
- aprovada: gestora aprovou (confere registro e perfil). Libera inscrição em sessão.
- visita agendada: escolheu um slot. Dispara lembretes 24 h e 1 h antes.
- visitada: visitadora marcou presença e salvou o registro. Ativa o cupom próprio, abre o formulário de personalização do cupom de paciente, coloca na fila de amostra com o tier atribuído.
- amostra enviada: seeding despachado com nota no Bling.
- ativa: cupom de paciente usado ao menos 1 vez.
- recorrente: cupom usado em 2 meses consecutivos.
- relevante: recorrente e (postou marcando a Heroica ou marcada à mão pela gestora).
- inativa: 90 dias sem uso de cupom de paciente. Automático.
- no-show em sessão: volta para aprovada e recebe novo link. No segundo no-show, gestora decide.

## 6. Fluxos da fase 1

Inscrição: página pública /prescritoras com formulário (o texto de marketing eu forneço depois; use placeholders). Grava como inscrita e dispara a automação de boas-vindas. Fila de inscritas no admin com link do Instagram e registro, botões aprovar e recusar com motivo.

Sessões: gestora cria slots. Prescritora aprovada escolhe slot no app. Tela de registro pós-visita para a visitadora: presença por inscrita, nota livre, tier sugerido, flags. Salvar muda status para visitada e dispara as ações do status.

Cupons: ativação do próprio na visita; formulário do cupom de paciente; aviso por push e WhatsApp quando ativo. Push "uma paciente sua comprou" com produto e valor a cada venda, como já existe para creators.

Amostras: fila no admin ordenada por data de visita, com tier, custo estimado e idade na fila. Gestora seleciona lote e gera seeding pelo fluxo existente do Bling. Tiers padrão, configuráveis pelo admin:
- tier 1: pacote de Heroiquinhas sortidas
- tier 2: 1 granola + 1 pasta + Heroiquinhas
- tier 3: kit completo
- kit consultório: 1 granola com display de mesa, disponível para qualquer tier mediante pedido e endereço do consultório.
Push e WhatsApp "sua amostra saiu" com rastreio.

## 6A. Ambiente logado da visitadora

A visitadora entra com login próprio e cai em um ambiente só dela, com três abas. Tudo é filtrado pelas prescritoras vinculadas a ela (as que estão nas sessões dela ou que a gestora atribuiu a ela). A gestora vê o mesmo ambiente com filtro por visitadora.

Aba "A visitar":
- próximas sessões dela com data, hora, link da reunião e lista de inscritas
- para cada inscrita: nome, cidade, especialidade, faixa de pacientes, Instagram com link, como conheceu a Heroica, se é reagendamento por no-show
- botão "iniciar registro" que abre a tela de presença e notas da sessão
- fila de aprovadas ainda sem sessão marcada, para ela chamar por WhatsApp (botão que abre conversa com mensagem pré-preenchida)
- contador: sessões na semana, inscritas na semana, vagas livres

Aba "Já visitadas":
- lista de todas as prescritoras que ela visitou, com data da visita, status atual do funil, tier atribuído, se a amostra já saiu, cupom de paciente ativo ou não
- filtros por status, especialidade, cidade e período
- em cada linha, as notas que ela escreveu na visita e um campo para adicionar acompanhamento depois (data + texto)
- alertas: visitada há mais de 14 dias sem amostra enviada; visitada há mais de 30 dias sem ativar o cupom de paciente; amostra entregue há 21 dias sem uso de cupom
- ação por linha: "mandar mensagem" (abre WhatsApp com template) e "sinalizar para gestora" (marca relevante, candidata a creator, ou pede reenvio, com motivo)

Aba "Performance":
- das prescritoras que ela visitou: quantas ativaram cupom, quantas viraram ativas, recorrentes e relevantes; taxa visitada para ativa em 60 dias
- usos de cupom de paciente e receita atribuída, no mês e acumulado, das prescritoras dela
- ranking das prescritoras dela por receita atribuída e por uso de cupom
- comparação dela com a média do programa nas mesmas métricas (sem mostrar nomes de outras visitadoras)
- sem valores de custo de amostra, sem ROI financeiro, sem dados de outras visitadoras

Regras:
- cada prescritora tem uma visitadora responsável, definida na primeira sessão em que foi marcada como presente; a gestora pode reatribuir
- a visitadora edita só notas e acompanhamentos; não muda status, tier nem cupom (exceto o registro pós-visita, que muda para visitada e atribui tier sugerido, sujeito a revisão da gestora)
- todas as ações dela ficam em log com data e usuário

Painel da gestora, tela inicial com mês atual e anterior:
- funil: inscritas, aprovadas, visitadas, amostras enviadas, ativas; taxa visitada para ativa em 60 dias em destaque
- base: total, ativas, recorrentes, relevantes, inativas; % de ativas
- cupons: usos e receita atribuída por cupom de paciente, top 10, primeiras compras geradas
- ROI: receita atribuída no período dividida por custo de amostras + frete no período
- fila: tamanho, idade média, custo do lote pendente
- exportação CSV de prescritoras e de vendas por cupom

Automações (use a integração de WhatsApp e e-mail que já existe; se não existir, crie um serviço de mensagens com adaptador e me avise):
- inscrição: WhatsApp + e-mail, boas-vindas + link da agenda
- aprovação: push + WhatsApp
- 24 h e 1 h antes da sessão: WhatsApp + push
- registro de visita: push + WhatsApp com cupom próprio e link do formulário do cupom de paciente
- cupom de paciente criado: push + WhatsApp
- seeding despachado: push + WhatsApp
- venda no cupom: push
Mensagens transacionais não entram no limite de recência de campanhas.

## 7. Critérios de aceite da fase 1

Só me chame para revisar quando todos passarem, com testes automatizados cobrindo R1, R2, R4, R5, as transições de status e a autorização do ambiente da visitadora:
1. Uma prescritora se inscreve, é aprovada, escolhe sessão, é marcada como visitada, recebe os dois cupons e aparece na fila com tier, sem nenhuma intervenção manual fora do app.
2. Tentar gerar seeding para status anterior a visitada falha com erro claro, na interface e na API.
3. Uma venda com cupom de paciente aparece no perfil dela, no painel e no ROI em até 1 hora.
4. A gestora vê funil do mês e idade da fila na tela inicial.
5. Nenhum dado, rota ou tela de prescritora é acessível pelo ambiente de creators, e vice-versa. Inclua teste de autorização por papel.
6. Uma pessoa com os dois perfis vê o seletor de ambiente e os dados não se misturam.
7. Prescritora inativa há 90 dias muda de status automaticamente e some da fila de reenvio.
8. A visitadora, logada com o papel dela, vê nas três abas apenas as prescritoras vinculadas a ela; uma tentativa de acessar prescritora de outra visitadora, a fila de seeding ou qualquer valor de custo retorna erro de autorização, na interface e na API.
9. Ao marcar presença numa sessão, a prescritora aparece em "Já visitadas" com a visitadora como responsável; ao registrar uma venda no cupom de paciente dela, a aba "Performance" da visitadora atualiza em até 1 hora.
10. Os alertas de "Já visitadas" (14 dias sem amostra, 30 dias sem cupom ativo, 21 dias sem uso após entrega) aparecem e somem conforme os dados mudam.

## 8. Fases seguintes, só para você planejar a arquitetura agora, sem implementar

Fase 2: comunidade (feed, comentários, curtidas, grupos por especialidade e região, enquetes), biblioteca de materiais com cartão de indicação gerado com o cupom da prescritora, moeda "Nuts Prescritoras" com ledger separado dos Nuts de creators, mercadinho próprio, push de novo conteúdo, alerta para gestora de pergunta sem resposta há 48 h.
Fase 3: curadoria automática com motivo legível (aprovar, reenviar, não reenviar, convidar para creators, convidar para evento), reativação aos 60 dias, métrica de retenção de paciente vindo de prescritora contra cliente médio, mapa por cidade e especialidade, convite a creator com ativação do seletor de ambiente.

Deixe o modelo de dados pronto para isso (ledger de pontos por ambiente, entidade de post, entidade de evento), mas não construa telas dessas fases agora.

## 9. Como trabalhar

- Padrões de código, testes e nomes iguais aos do ambiente de creators.
- Valores configuráveis (percentuais, limites, capacidade, tiers, dias de inatividade) ficam em configuração do admin, nunca hardcoded.
- Não crie dados de exemplo com nomes de pessoas reais.
- A cada fase, entregue: resumo do que foi feito, lista de arquivos, como testar à mão, o que ficou pendente e por quê.
- Se encontrar uma decisão que não está aqui, use o valor padrão indicado, registre em uma lista "decisões assumidas" e siga. Só pare se a decisão for irreversível ou mudar a estrutura de dados.
```
