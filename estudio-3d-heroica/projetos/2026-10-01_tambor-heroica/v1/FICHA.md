# Tambor Heroica v1: ficha técnica

Conceito A + itens do B, aprovado pelo Roberto em 01/10/2026. **4 unidades**, tambores novos de 200 L.

## Medidas
| | mm |
|---|---|
| Tambor | Ø585 × 880 (padrão ISO 15750; medir o comprado antes de cortar) |
| Vão frontal | 120°: 497 na corda (601 medidos na fita, por fora) × 580 de altura, de 140 a 720 do chão |
| Faixa do letreiro | 720 a 880 (160) |
| Prateleiras (face de cima) | 150 e 440 do chão; vão livre de 275 e 280 (granola: 240) |
| Topo de exposição | 898 do chão; tampo Ø610 com borda de 15 mm |
| Peso vazio | ~28 kg (tambor ~15 kg + MDF ~10 kg + aço ~3 kg); centro de massa a 508 do chão |
| Capacidade | ~16 granolas 300 g (5 por prateleira em 2 fileiras + 5 no topo) |

## Materiais e acabamento
- **Serralheiro:** recorte; reforço com 2 arcos e 2 montantes de barra chata 1" × 1/8", soldados por dentro; 6 cantoneiras 3/4" × 1/8" rebitadas; pintura eletrostática RAL 3005 por fora e rosa Heroica por dentro.
- **Marceneiro:** 2 prateleiras em D (MDF 15 BP amadeirado claro, com fita na curva); 2 testeiras porta-preço de 484 × 35; tampo Ø610 + anel Ø610/570 + disco de centragem Ø550, com laca rosa.
- **Gráfica:** letreiro HEROICA em vinil branco (letra de 80 mm, Pilcrow Rounded Heavy); moldura rosa de 30 mm em volta do vão; 2 selos Ø200 "Celebre suas conquistas"; QR code com cupom.
- **Compra Heroica:** perfil U de borracha EPDM (canal 1,0–1,5 mm, 2,6 m por tambor); 2 barras LED magnéticas recarregáveis com sensor; feltro ou pé nivelador.

## Validação (rodada em 01/10, `saida/validacao.json`)
- 16 peças com sólido válido e malha fechada. **Zero interferências** entre peças (a 1ª rodada achou 3 erros, todos corrigidos; ver aprendizados).
- A granola passa sobre a testeira com folga de 15 mm (compartimento de baixo) e 20 mm (de cima).
- A prateleira (Ø562) entra de pé pelo vão (580 de altura) e gira dentro do tambor.
- Estabilidade: base Ø585 e centro de massa a 508 mm vazio. Cheio, as 16 granolas somam ~5 kg, metade delas no topo. Teste de empurrão lateral fica na lista de montagem do piloto.
- Ainda não verificado: a cor real (amostra) e o diâmetro interno do bordão do tambor comprado.

## Como ajustar (`tambor_v1.py`, topo do arquivo)
- Tambor com outra medida: `bib.TAMBOR_200L` (d_int, altura).
- Vão mais largo ou mais estreito: `RECORTE_GRAUS` (120 = 497 mm de largura). Acima de ~140° o tambor perde muita rigidez.
- Produto mais alto (pote, kit): `PRAT_TOPO_Z` e `RECORTE_Z`.
- Borda do tampo mais alta: `ESP_ANEL`.
- Depois de mudar, rode `tambor_v1.py` e `desenhos_v1.py`: modelo, validação, lista de corte, renders, PDF e DXF saem de novo.

## Arquivos
- `saida/Tambor_Heroica_v1_fornecedores.pdf`: 4 folhas (visão geral, serralheria, marcenaria, gráfica/compras/montagem).
- `saida/dxf/`: peças de MDF em escala 1:1.
- `saida/tambor_heroica_v1.step`: montagem 3D.
- `saida/lista_de_corte.md` e `saida/renders_*`.
- `pedidos_de_orcamento.md`: textos prontos para WhatsApp.
