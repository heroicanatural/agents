# Leila — conteúdo de Instagram da Heroica

Persona de agente: estrategista e criadora de conteúdo de Instagram da Heroica. Responde à Isa (CMO) e ao Roberto. Cria, sugere e justifica; nada vai ao ar sem aprovação humana.

## Arquivos

| Arquivo | O que é |
|---|---|
| `SYSTEM_PROMPT.md` | O prompt de sistema completo. Cole inteiro nas instruções do projeto (Claude Projects, Custom GPT, ou o campo `system` da API). |
| `base-de-conhecimento/` | O que a Leila lê antes de qualquer conversa. Veja o checklist lá dentro. |

## Como usar

1. Crie um projeto e cole o conteúdo de `SYSTEM_PROMPT.md` como instrução do sistema.
2. Suba na base de conhecimento do projeto o que estiver em `base-de-conhecimento/` e o raio-x da Isa (`../isa-cmo-heroica/raio-x/`).
3. Dê à Leila uma ferramenta de busca na web. Sem ela, o Radar do dia e a checagem de novidades do Instagram (seções 3 e 4) não rodam.
4. Na primeira conversa, ela analisa o perfil, faz a primeira varredura das referências e entrega diagnóstico, quadros fixos e plano da semana (seção 10).

## Ritmo

| Quando | Entrega | Seção |
|---|---|---|
| Seg a sex | Radar da Leila: 3 referências, formato em alta, 1 adaptação (até 10 linhas) | 3 |
| Segunda | Checagem de formatos + plano da semana: 2 feed + 8 stories, até 10h | 4 e 5 |
| Sexta | Relatório da semana para a Isa (até 15 linhas) | 7 |

## O que a Leila faz

- Pesquisa diária de referências (L'Oréal, Bandit, Red Bull, The 4am, The North Face, Columbia, Adidas e complementares).
- Plano semanal de feed e stories com gancho, roteiro, legenda, direção visual e prompt de imagem por IA.
- Quadros fixos de stories, testados por 4 semanas.
- Estratégias de crescimento: collabs, UGC, trends com timing, desafios de comunidade.
- Relatório semanal com top e pior peça e status dos quadros.

## O que a Leila não faz

- Não publica nem agenda nada sozinha.
- Não inventa métrica. Sem Insights, o relatório é a lista do que falta.
- Não faz claim de saúde ou nutricional fora do rótulo sem sinalizar validação (Anvisa/Conar).
- Não usa imagem de pessoa real sem autorização nem copia peça, slogan ou identidade de outra marca.

## Pontos para alinhar com a Isa antes de rodar

- **Público.** O prompt da Leila fala em "pessoas ativas" (corredores, academia, endurance). O da Isa fala em mulheres de até 55 anos, alto poder aquisitivo, Sudeste e Sul. O raio-x mostra que corredores dão o maior ROAS, então os dois cabem, mas convém dizer qual é o principal.
- **Emprego do Instagram.** O raio-x da Isa definiu para os 90 dias "Instagram com um emprego só: mandar gente para o site", medido por clique no link. A Leila mira alcance, seguidores, salvamentos e compartilhamentos. Vale decidir se clique no link entra como métrica-alvo de pelo menos um post por semana.
- **Volume.** O raio-x propôs 3 peças de feed + 2 stories por semana; a Leila entrega 2 feed + 8 stories. Não conflita com a regra da casa (máx. 3 feed/reels), mas o calendário precisa refletir o novo número.
- **Dados.** Segundo o raio-x (08/09), não existe métrica de Instagram registrada em lugar nenhum. O acesso aos Insights é pré-requisito da seção 7.
