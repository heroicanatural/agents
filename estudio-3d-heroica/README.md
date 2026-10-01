# Estúdio 3D da Heroica

Persona de agente: designer industrial, engenheiro de produto e artista 3D da Heroica. Transforma ideias, rascunhos e fotos em peças prontas para imprimir, fabricar ou renderizar.

## Arquivos

| Arquivo | O que é |
|---|---|
| `SYSTEM_PROMPT.md` | O prompt de sistema completo. Cole inteiro nas instruções do projeto (Claude Projects, Claude Code, ou o campo `system` da API). |
| `biblioteca_heroica.py` | Módulos paramétricos reutilizáveis (CadQuery). O agente reusa e amplia a cada projeto. |
| `aprendizados.md` | Diário de projeto: o que funcionou, o que falhou, regras novas. |
| `base-de-conhecimento/` | Brandbook, logo vetorial, medidas reais dos produtos, impressora e fornecedores. Veja o checklist lá dentro. |
| `projetos/` | Um diretório por projeto, com versões `v1/`, `v2/`… |

## Como usar

1. Rode o agente onde ele possa **executar Python** (Claude Code ou um projeto com ferramenta de código). Sem isso ele só entrega conceito e script, sem validar a malha nem gerar STL.
2. Dependências: `pip install cadquery trimesh` (modelagem e validação). Opcionais: Blender (renders realistas), PrusaSlicer CLI (tempo e filamento).
3. Preencha o checklist de `base-de-conhecimento/`. O que estiver marcado **[a confirmar]** na seção 5 do prompt o agente vai perguntar.
4. Peça em linguagem natural: "preciso de um display de balcão para 12 potes de pasta, MDF, premium".

## Fluxo

Briefing → referências (5 a 8, com link) → 3 conceitos → ficha técnica → modelo paramétrico → validação (manifold, DFM, estabilidade, renders) → entrega → iteração v1, v2…

## O que o agente não faz

- Não inventa medida de produto: sem medida real, declara suposição e pede confirmação antes de mandar para fabricação.
- Não declara validado o que não conseguiu verificar.
- Não trata peça impressa em FDM como embalagem de contato com alimento.
- Não fecha orçamento nem pedido com fornecedor; prepara o arquivo e a ficha.
