# Card de entrega no Gmail para os pedidos da Heroica · 11/11/2026

Pedido do Roberto: fazer os e-mails de envio aparecerem como o card "Em breve · Entrega prevista para amanhã" que a Amazon tem no Gmail.

Dono sugerido: Lucas Guedes (e-commerce). Não é tarefa de Instagram; a Leila só levantou o caminho.

## Como funciona

O card vem do recurso de rastreio de compras do Gmail. Ele lê o e-mail de pedido/envio e, quando entende os dados (número de rastreio, loja, produto, previsão de entrega), mostra o card no topo da caixa de entrada e na aba de compras.

O Gmail entende melhor quando o e-mail traz **dados estruturados (schema.org `ParcelDelivery` / `Order`, em JSON-LD)** escondidos no HTML. A Shopify aceita isso nos modelos de e-mail de envio.

## Passo a passo

1. **Enviar do domínio próprio** (ex.: pedidos@heroicanatural.com), não do remetente padrão da Shopify.
2. **Autenticar o domínio:** SPF, DKIM e DMARC configurados (Shopify → Configurações → Notificações → domínio do remetente). Sem isso o Gmail ignora os dados estruturados.
3. **Colar o bloco abaixo** no modelo "Confirmação de envio" (e "Atualização de envio") da Shopify.
4. **Testar:** fazer um pedido teste, enviar para um Gmail e conferir se o card aparece.
5. **Registro no Google:** historicamente o Gmail só exibia dados estruturados de remetentes registrados e com volume e reputação. Não consegui confirmar a regra atual (as páginas do Google não abriram deste ambiente). Se o card não aparecer depois do teste, o próximo passo é o formulário de registro de remetente do Gmail.

## Expectativa

Sem garantia. O Gmail decide sozinho quando mostrar o card, e o volume da Heroica (centenas de pedidos/mês) é pequeno perto de Amazon. Mesmo assim vale fazer: os passos 1 e 2 melhoram a entrega de todos os e-mails da loja (menos spam), e o bloco é custo zero.

## Bloco para o modelo de e-mail da Shopify (rascunho, testar antes)

```liquid
<script type="application/ld+json">
{
  "@context": "http://schema.org",
  "@type": "ParcelDelivery",
  "deliveryAddress": {
    "@type": "PostalAddress",
    "name": "{{ shipping_address.name }}",
    "streetAddress": "{{ shipping_address.address1 }}",
    "addressLocality": "{{ shipping_address.city }}",
    "addressRegion": "{{ shipping_address.province_code }}",
    "addressCountry": "{{ shipping_address.country_code }}",
    "postalCode": "{{ shipping_address.zip }}"
  },
  "carrier": {
    "@type": "Organization",
    "name": "{{ fulfillment.tracking_company }}"
  },
  "trackingNumber": "{{ fulfillment.tracking_number }}",
  "trackingUrl": "{{ fulfillment.tracking_url }}",
  "itemShipped": [
    {% for line in fulfillment.fulfillment_line_items %}
    {
      "@type": "Product",
      "name": "{{ line.line_item.title | escape }}"
    }{% unless forloop.last %},{% endunless %}
    {% endfor %}
  ],
  "partOfOrder": {
    "@type": "Order",
    "orderNumber": "{{ order_name }}",
    "orderStatus": "http://schema.org/OrderInTransit",
    "merchant": {
      "@type": "Organization",
      "name": "Heroica"
    },
    "orderUrl": "{{ order_status_url }}"
  }
}
</script>
```

Se a transportadora informar previsão de entrega, dá para incluir `"expectedArrivalUntil"` com a data. Os nomes das variáveis Liquid mudam conforme o modelo da Shopify; o Guedes confere no editor de notificações.
