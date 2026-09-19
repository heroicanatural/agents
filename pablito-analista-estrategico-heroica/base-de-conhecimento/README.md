# Base de conhecimento do Pablito

Tudo que estiver nesta pasta deve ser subido na base de conhecimento do projeto onde o Pablito roda. Ele compara cada transcrição nova com as anteriores; sem histórico, ele só tira fotografia, não enxerga tendência.

## Checklist do que subir

- [ ] Transcrições anteriores, uma por arquivo, em `transcricoes/`, nomeadas `AAAA-MM-DD_tipo_assunto.md` (ex.: `2026-09-17_call-cliente_angeloni.md`). No topo de cada uma: data, participantes, tipo (reunião interna, call com cliente, fornecedor, representante, áudio) e origem (Fathom, áudio transcrito, ata).
- [ ] Análises já entregues pelo Pablito, em `../analises/`.
- [ ] Contexto do negócio atualizado: canais (e-commerce, B2B canal verde, grande varejo), calendário de eventos (HTX, maratonas, Ironman, corridas de rua), metas do período e caixa disponível.
- [ ] Organograma do time com quem é dono de quê, para que ele atribua pendências a pessoas reais.
- [ ] Lista de clientes B2B, representantes e fornecedores recorrentes, para reconhecer nomes que aparecem nas transcrições.
- [ ] Raio-x mais recente da Heroica (hoje em `../../isa-cmo-heroica/raio-x/`), para que o diagnóstico converse com o que a Isa já mapeou.

## Sugestão de organização

```
base-de-conhecimento/
  transcricoes/     uma transcrição por arquivo, com data no nome
  contexto/         metas, calendário, organograma, listas de clientes e fornecedores
```

Se a transcrição vier truncada ou com erro de reconhecimento de fala, não corrija antes de subir: o Pablito sinaliza os trechos ambíguos e é melhor que ele veja o original.
