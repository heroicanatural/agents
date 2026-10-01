# Diário de aprendizados

Um bloco por projeto, mais recente no topo. Regras que se confirmarem em dois projetos sobem para a seção 3 do prompt ou viram parâmetro da biblioteca.

## Modelo

```
## AAAA-MM-DD — nome do projeto (vN)
- Processo/material:
- Funcionou:
- Falhou:
- Medida real vs. projetada (folgas, encaixes):
- Regra nova:
- Módulo adicionado/alterado na biblioteca:
```

## 2026-10-01 — Tambor Heroica (v0 conceitos → v1 fabricação)
- Processo/material: tambor de aço 200 L recortado (serralheiro) + MDF (marceneiro) + vinil (gráfica). 4 unidades.
- Funcionou: modelo paramétrico com peças nomeadas → lista de corte, DXF, PDF e renders saem do mesmo script. Prateleira em D (frente reta) dá a borda para a testeira porta-preço.
- Falhou na 1ª rodada (pego pela checagem de interferência, antes de chegar à oficina):
  1. Cantoneira reta em parede curva: encosta nas **pontas**, não no meio (flecha de 2,8 mm para 80 mm em R 286). Rebite vai nas pontas.
  2. Montantes do reforço sobrepostos aos arcos: montante vai **entre** os arcos, com solda de topo.
  3. Canto da prateleira batendo no montante: folga da parede subiu de 3 para 5 mm.
- Render: matplotlib não resolve profundidade em cilindros (triângulos longos). Trocado por three.js no Chromium headless (`ferramentas/render_cena.mjs`).
- Regra nova: disco cheio não passa por vão menor que o diâmetro; checar sempre **como a peça entra** (de pé, girando, pelo topo).
- Regra nova: altura do produto + aba da testeira + 15 mm ≤ vão livre (senão não dá para repor).
- Módulos adicionados à biblioteca: `tambor_200l`, `setor`, `interferencias`, `cena_json`/`renderizar`.
- Pendente de calibração real: cor RAL 3005 vs. marca; diâmetro interno do bordão (disco de centragem); vinil em superfície curva.

## Calibração atual

| Parâmetro | Valor | Origem |
|---|---|---|
| Tolerância serralheria | ±1 mm | padrão do prompt, ainda não confirmado com fornecedor |
| Perda de serra (marcenaria) | 4 mm por corte | padrão do prompt, ainda não confirmado |
| Chapa MDF inteira | 2750 × 1850 mm | padrão de mercado, confirmar com o marceneiro |
| Kerf laser | 0,15 mm | padrão do prompt, ainda não medido |
| Folga de produto em berço/prateleira (embalagem flexível) | 5 mm por lado | suposição, testar com a granola |
