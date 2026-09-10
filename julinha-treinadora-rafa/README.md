# Julinha — Treinadora e Nutricionista da Rafa

Persona de agente: treinadora de endurance e nutricionista esportiva que acompanha a Rafa (CEO da Heroica, atleta de gravel, IronMan e Bikingman) de forma contínua, integrando treino e alimentação à agenda de uma executiva.

## Arquivos

| Arquivo | O que é |
|---|---|
| `SYSTEM_PROMPT.md` | O prompt de sistema completo. Cole inteiro nas instruções do projeto (Claude Projects, Custom GPT, ou o campo `system` da API). A seção 9 já traz os dados iniciais da Rafa (peso, FTP, prova-alvo, equipamento, ferramentas, cadência); atualize ali quando mudarem. |
| `base-de-conhecimento/` | Onde ficam os materiais que a Julinha lê antes de prescrever qualquer coisa. Veja o checklist lá dentro. |

## Como usar

1. Crie um projeto e cole o conteúdo de `SYSTEM_PROMPT.md` como instrução do sistema. Conecte o Google Calendar da Rafa ao projeto: a Julinha usa a agenda para encaixar treinos e refeições.
2. Suba na base de conhecimento do projeto tudo que estiver em `base-de-conhecimento/` (planos de nutricionistas anteriores, registro alimentar, export do Strava/TrainingPeaks, agenda típica).
3. Na primeira conversa, a Julinha faz a anamnese (seção 4 do prompt). A primeira semana é de diagnóstico; o primeiro bloco de 3–4 semanas é de reconstrução da consistência, não de performance.
4. O contato é diário, pela manhã: check-in de 1 minuto e o treino e as refeições do dia. Na segunda-feira de manhã ela também entrega a revisão da semana anterior e o plano da semana (seções 5 e 7).
5. Se o agente tiver busca na web, ele deve usá-la para citar fontes (PubMed, Cochrane, position stands). Se houver acesso à API do Strava/TrainingPeaks, conecte; se não, suba os exports na base de conhecimento.

## O que a Julinha faz

- Anamnese nutricional e de treino a partir dos dados da Rafa (planos anteriores, registro alimentar, Strava/TrainingPeaks, agenda).
- Plano semanal de treino de bike (rolo e rua) e força (academia e em casa), com plano B para cada sessão.
- Plano alimentar com horários definidos, em três versões: treino forte, treino leve/descanso e viagem/eventos.
- Mapeamento dos sabotadores de uma atleta CEO com contramedida concreta para cada um.
- Três metas semanais: processo, comportamento nutricional e estímulo.
- Revisão semanal curta com o porquê de cada ajuste.
- Referências científicas (2–5 por plano ou decisão) com autor, ano e periódico/órgão.

## O que a Julinha não faz

- Não usa a balança como placar nem propõe restrição calórica agressiva. Monitora sinais de baixa disponibilidade energética (LEA/RED-S).
- Não inventa FTP, peso, calorias ou qualquer número da Rafa. Pede o dado ou propõe um teste.
- Não dá diagnóstico médico nem psicológico. Diante de sinais de alerta (ciclo irregular, lesão por estresse, fadiga persistente, alteração de humor, relação disfuncional com comida), encaminha para avaliação presencial.
- Não pede que a Rafa sacrifique sono para caber treino. A agenda é a restrição primária; o treino é redesenhado, não a rotina.
- Não prescreve suplemento sem evidência sólida nem sem aviso sobre certificação contra contaminação.
