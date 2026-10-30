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

## 2026-10-29 — Balcão de degustação dobrável (compensado 12, peças planas)
- Processo: CNC com espiga e rasgo; dobradiças só entre a frente e as laterais (fixas); o resto encaixa sem ferramenta.
- Funcionou: base e tampo com rasgos travam o esquadro do "U" dobrável. As hastes da bandeira guiadas em 2 pontos (tampo + prateleira de cima) e apoiadas na prateleira de baixo dispensam suporte colado.
- Erro pego no render: os rasgos das espigas da frente das prateleiras atravessavam a área de marca. Regra: **face de marca sem rasgo/furo passante**; prender a prateleira pelas laterais.
- Ordem de montagem importa: com o corpo já na base, as laterais não abrem para receber as prateleiras. Prateleira entra ANTES da base (está no guia).
- Encaixe CNC: rasgo = espessura REAL + 0,5; rasgo mais comprido que a espiga em Ø fresa; alívio de fresa (Ø × Ø/2) na base de cada espiga. Novos na biblioteca: `contorno_espigas`, `rasgo`, `poli_ret`, `FRESA`.
- Pendente de calibração: espessura real do compensado 12 do fornecedor e folga 0,5 (testar 1 encaixe antes de cortar tudo).
- **Perguntar o PROCESSO do fornecedor antes de desenhar.** Luciano Lâminas corta em serra (esquadrejadeira), não CNC: espiga, rasgo e furo não saem. Regra: o mesmo desenho ganha 2 pacotes — SERRA (lista de cortes, só retângulos, plano em faixas, furos na montagem) e CNC (DXF com furos e furos-guia).
- Substitutos de encaixe para serra: tacos colados com a peça montada (ficam no lugar sem medir) e travessas de apoio. Ficam invisíveis por fora, melhor que espiga aparente.
- v3 com estética de referência (expositor Red Bull): preto fosco + madeira natural + ripado + placa com halo de LED. Ripado parafusado por DENTRO (furos-guia na frente), sem parafuso aparente.
- Renderizador ganhou `ambiente` (luz geral) para mostrar LED em "loja à meia-luz". LED de 5 W sobre fundo escuro dá halo discreto; avisar o cliente.

## 2026-10-06 — Box Run Club (caixa de compensado naval sobre carrinho-plataforma)
- Processo/material: compensado naval 15 mm, corte CNC (DXF), montagem pelo próprio usuário. Carrinho comprado pronto.
- Mudança de escopo no meio: o usuário mandou a foto do carrinho depois que eu já tinha projetado rodas, eixo e alça. Regra nova: **perguntar "o que vai embaixo / o que já existe" antes de projetar estrutura móvel.**
- Funcionou: furos-guia Ø3 feitos pela CNC nas linhas de união (7,5 da borda, a cada ~150). O usuário monta sem medir nada, só cola, grampo, pré-furo e parafuso.
- Funcionou: porta = recorte do próprio painel (a fresa Ø6 deixa ~3 mm de folga por lado) + batentes por dentro.
- Encaixe nas chapas: largura da caixa escolhida para caber em 2 chapas (a 1ª tentativa ia para 3). O encaixe agora testa peças deitadas e em pé.
- Bugs de ferramenta corrigidos: Workplane do CadQuery consome o fio pendente na 1ª extrusão (guardar `Wire`); `transformGeometry` vira spline e quebra o DXF (usar `Location`/`moved`).
- Módulos adicionados à biblioteca: `Painel`, `plano_de_corte`, `dxf_chapas` (camadas CORTE_EXTERNO/INTERNO/FURO_GUIA_3/TEXTO). `ferramentas/desenho.py` (cotas, tabela, peça 2D).
- Pendente: medida real da plataforma; retorno da fábrica sobre os furos Ø3; peso real.
- v2 (mesmo dia): caixa pode passar 200 de cada lado do carrinho; acesso ao baú virou requisito ("vai servir pra guardar coisas"). Duas portas + divisória central (organiza e apoia o tampo de ~1 m).
- Encaixe: o automático pedia 3 chapas; à mão, as 2 laterais trapezoidais encaixam invertidas pela diagonal → 2 chapas, 69%. Criados `plano_manual` + `verificar_plano` (distância real entre contornos). Regra: **peças trapezoidais iguais → testar par invertido antes de aceitar chapa extra.**
- Regra nova: pedir a ficha técnica do item comprado (carrinho) logo no briefing. A ficha mudou o comprimento de 1190 para 990.

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
