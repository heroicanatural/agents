# Agentes da Heroica

Personas de agentes de IA da Heroica. Cada pasta tem o prompt de sistema, um README de uso e a estrutura de base de conhecimento.

| Agente | Papel | Pasta |
|---|---|---|
| Isa | CMO da Heroica. Estratégia de marca, campanhas 360, briefings de creators, peças de Instagram, análise de dados e placar semanal. | [`isa-cmo-heroica/`](isa-cmo-heroica/) |
| Julinha | Treinadora de endurance e nutricionista esportiva da Rafa. Anamnese, plano semanal de bike e força, plano alimentar com horários, sabotadores de atleta CEO e revisão semanal com base em evidência. | [`julinha-treinadora-rafa/`](julinha-treinadora-rafa/) |

## Convenção

```
<nome-do-agente>/
  SYSTEM_PROMPT.md        prompt de sistema completo, pronto para colar
  README.md               como usar, o que o agente faz e não faz
  base-de-conhecimento/   materiais que o agente lê antes de conversar
  <entregas>/             saídas do agente com data no nome (ex.: raio-x/, planos/)
```
