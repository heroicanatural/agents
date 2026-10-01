# Base de conhecimento do Estúdio 3D

Quanto mais medida real tiver aqui, menos o agente supõe.

## Checklist do que subir

- [ ] Brandbook (manual Bradda, set/2025) com a paleta hex **definitiva** (o manual e o guia interno divergem).
- [ ] Logo vetorial (SVG ou PDF) nas versões marrom, bege e sobre bloco.
- [ ] Fonte Pilcrow Rounded (arquivos .otf/.ttf) para relevos e gravações.
- [ ] Ficha de cada embalagem com medidas reais em mm (trena/paquímetro) e peso cheio:
  - [x] Granola 300 g: 160 × 240 × 80 mm (L × A × P). Falta: peso cheio, tipo de embalagem (stand-up com zip?).
  - [ ] Pote de pasta 400 g (Ø tampa, Ø corpo, altura, material).
  - [ ] Heroiquinhas 40 g.
- [ ] Fotos de cada embalagem: frente, lateral, topo, contra fundo neutro.
- [ ] Ficha de cada fornecedor (um arquivo por fornecedor em `fornecedores/`):
  - Serralheiro: tubos e chapas que tem em estoque, faz pintura eletrostática? dobra chapa? prazo típico.
  - Marceneiro: chapas e padrões de BP que trabalha, tem coladeira de borda? corta em seccionadora? prazo típico.
  - Laser/CNC: área útil da máquina, materiais e espessuras, formato de arquivo aceito.
  - Gráfica/comunicação visual: adesivo, lona, impressão UV em chapa, facas.
  - Como prefere receber o pedido (WhatsApp com PDF? e-mail?).
- [ ] Fotos dos PDVs (balcão, gôndola, estande de evento) com medidas do espaço disponível.

## Sugestão de organização

```
base-de-conhecimento/
  marca/          brandbook, logo vetorial, fontes
  produtos/       fichas de medidas e fotos por SKU
  fornecedores/   uma ficha por fornecedor: contato, capacidades, materiais, prazos, preços já pagos
  pdv/            fotos e medidas dos pontos de venda e do estande
```
