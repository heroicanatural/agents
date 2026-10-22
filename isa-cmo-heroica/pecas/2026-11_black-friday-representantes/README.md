# Black Friday · condições para representantes (22/10/2026)

Arte em HTML (1080x1350) com as condições passadas pelo Roberto em 22/10:

| Pedido a partir de | Bonificação em granolas |
|---|---|
| R$ 1.000 | 5% |
| R$ 1.500 | 7% |
| R$ 2.000 | 10% |
| R$ 2.350 | 12% |

Prazos de pagamento: 15 / 21 / 28 / 35 / 45 / 60 dias.

Fonte: Nunito (stand-in da Pilcrow Rounded, que não está disponível neste ambiente). Para renderizar em PNG: abrir `arte.html` no Chrome a 1080x1350 e capturar, ou usar o script Playwright da sessão.

Pendências: vigência da campanha (datas), regra de prazo por faixa (se houver), pedido mínimo para prazo de 60 dias (se houver).

## Versão Canva (22/10/2026)

Montada via MCP do Canva na conta marketing@heroicanatural.com, a partir de uma cópia da página 1 do design DAHUpQEpi1s (Brand Kit Heroica kAFUpr0nkN4). Mesmo layout e hierarquia do `arte.html`: logo no topo esquerdo, tag REPRESENTANTES à direita, BLACK / FRIDAY em bloco marrom, subtítulo, quatro faixas de bonificação (bege, amarelo, rosa, marrom com texto bege), seis pílulas de prazo e rodapé.

- **design_id:** `DAHYxSBoy9g`
- **Título no Canva:** Black Friday 2026 · Condições para representantes
- **Link de edição:** https://www.canva.com/design/DAHYxSBoy9g/edit (link compartilhável gerado na sessão: https://www.canva.com/d/EYHDg4na2OB1P1v)
- **Formato:** 1080x1350, uma página
- **Logo:** asset oficial `MAGbhrRQIqA` (wordmark HEROICA bege sobre bloco marrom), 220x64 no topo esquerdo
- **Export PNG:** gerado com sucesso pelo `export-design` (job 313953f8). A URL de download expira em poucas horas e o proxy desta sessão não deixou baixar o arquivo para o repositório, então o PNG precisa ser baixado de novo pelo Canva (Compartilhar → Baixar → PNG) quando for distribuir.

### Pendente de ajuste manual no Canva

1. **Fonte.** A API não troca família de fonte: todos os textos ficaram na fonte padrão do editor (fontRef `YACgEZ1cb1Q`, bold). Trocar tudo para **Pilcrow Rounded** (fontRef `YAGXH66DCbs`, do Brand Kit) e conferir se BLACK / FRIDAY continuam cabendo nas larguras (600 e 400 px).
2. **Fundo da página.** O fundo real da página continua `#161911` (herdado da cópia); o bege `#eedab3` é um retângulo full-bleed na camada de baixo. Funciona no export, mas se alguém mover ou apagar o retângulo o fundo escuro aparece. Ideal: definir a cor de fundo da página como `#eedab3` e apagar o retângulo.
3. **Espaçamento de letras.** O HTML usa letter-spacing nas tags e títulos de seção (2–4 px) e tracking negativo no BLACK FRIDAY; a API não expõe isso. Ajustar à mão se quiser ficar idêntico.
4. **Opacidade dos títulos de seção e rodapé.** Aplicada como opacidade do elemento (0,75 e 0,85), não como cor; se a fonte mudar, conferir se a leitura continua boa.
5. **Datas de vigência** continuam fora da arte (não definidas). Quando o Roberto fechar, entra uma linha abaixo do subtítulo ou no rodapé.

### Por que essa peça existe

Porquê: dar ao time de representantes um material único, claro e no padrão da marca para empurrar pedidos maiores na Black Friday. Destino: pedido médio dos representantes subindo para a faixa de R$ 2.000+ durante a campanha. Como saber: distribuição de pedidos por faixa de bonificação no fechamento da BF, comparada ao mês anterior.
