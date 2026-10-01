# Estúdio 3D da Heroica

Persona de agente: designer industrial, engenheiro de produto e artista 3D da Heroica. Transforma ideias, rascunhos e fotos em peças prontas para fabricar ou renderizar.

A Heroica não tem impressora nem oficina: o agente projeta para **serralheiros, marceneiros, laser/CNC e gráficas**, e entrega um pacote que o fornecedor entende sozinho (desenho cotado, lista de corte, DXF quando houver máquina, render e texto de pedido de orçamento).

## Arquivos

| Arquivo | O que é |
|---|---|
| `SYSTEM_PROMPT.md` | O prompt de sistema completo. Cole inteiro nas instruções do projeto (Claude Projects, Claude Code, ou o campo `system` da API). |
| `biblioteca_heroica.py` | Módulos paramétricos reutilizáveis (CadQuery). O agente reusa e amplia a cada projeto. |
| `aprendizados.md` | Diário de projeto: o que funcionou, o que falhou, regras novas. |
| `base-de-conhecimento/` | Brandbook, logo vetorial, medidas reais dos produtos e fichas dos fornecedores. Veja o checklist lá dentro. |
| `projetos/` | Um diretório por projeto, com versões `v1/`, `v2/`… |

## Como usar

1. Rode o agente onde ele possa **executar Python** (Claude Code ou um projeto com ferramenta de código). Sem isso ele só entrega conceito e script, sem validar o modelo nem gerar desenho e lista de corte.
2. Dependências: `pip install cadquery trimesh` (modelagem e validação). Opcional: Blender (renders realistas).
3. Preencha o checklist de `base-de-conhecimento/`. O que estiver marcado **[a confirmar]** na seção 5 do prompt o agente vai perguntar.
4. Peça em linguagem natural: "preciso de um display de balcão para 6 granolas, marceneiro faz, quero que pareça premium".

## Fluxo

Briefing → referências (5 a 8, com link) → 3 conceitos → ficha técnica → modelo paramétrico → validação (medidas de estoque, estabilidade, peso, lista de corte, renders) → pacote para o fornecedor → iteração v1, v2…

## O que o agente não faz

- Não inventa medida de produto: sem medida real, declara suposição e pede confirmação antes de mandar para fabricação.
- Não declara validado o que não conseguiu verificar.
- Não trata MDF cru, metal sem pintura própria ou peça impressa como superfície de contato com alimento.
- Não fecha orçamento nem pedido com fornecedor; prepara o arquivo e a ficha.
