💵 Топ самых щедрых ребят 💵{% for sum, author in chart %}
`🌟 {{"%-7s" % sum | int}}` - **{{author.introduce | unmd}}**{% else %}
Пока никого 😞{% endfor %}{% if other_sum %}
+ ещё **{{other_sum | int}}** от **{{other_author_count}}** ребят!{% endif %}