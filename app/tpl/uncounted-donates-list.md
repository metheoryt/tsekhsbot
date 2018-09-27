Донаты на рассмотрении:

{% for d in dds %}
`- #{{d.id}} {{d.amount}}{{d.currency.name}}` от `{{d.author_name or d.author_phone or "инкогнито"}}` через `{{d.source.name}}`
{% endfor %}

Чтобы принять/отклонить донат, набери знак *+* или *-* и # доната следом, например `+42` или `-12`.