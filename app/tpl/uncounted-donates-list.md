Донаты на рассмотрении:
{% for d in donates %}
`💰 #{{d.id}}` {{d.amount}} {{d.currency.name}} закинул `{{d.author_name or d.author_phone or "инкогнито"}}` через `{{d.source.name}}`{% endfor %}

Чтобы принять/отклонить донат, набери знак *+* или *-* и # доната следом, например `+42` или `-12`.