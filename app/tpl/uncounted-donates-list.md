Донаты на рассмотрении:
{% for d in donates %}
`💰 #{{d.id}}` {{d.amount | int}} {{d.currency.name.lower()}} закинул `{{d.author.name or d.author.phone or "инкогнито" | unmd}}` через `{{d.source.value}}`{% endfor %}

Чтобы принять/отклонить донат, набери # доната и "да" или "нет" следом, например `42 да` или `12 нет`.