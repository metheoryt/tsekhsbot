{# 
cfg = cfg

donate = Donate
thanks_a_day = str
#}
💰💰💰 новое пожертвование на *{{donate.amount}}* {{donate.currency.name}} подкинул нам *{{
        donate.author_name or donate.masked_phone or "Неизвестный аноним"
}}*, за что ему {{thanks_a_day}}!
Если есть желание подкинуть нам дровишек нам зиму, можете сделать это [быстро и удобно здесь]({{cfg.QIWI_ACCEPT_URL}})!
_или_ /stop _если надоел_