+++
title = "Help"
path = "en/help"
template = "page.html"
+++

## Materials — how to play Mahjong {#materials--how-to-play-mahjong}
{{ <help_items items={load_data(path="data/help/materials.yml")} lang={lang} default_lang={config.default_language} /> }}

## Interactive — single player Mahjong and trainers {#interactive--single-player-mahjong-and-trainers}
{{ <help_items items={load_data(path="data/help/interactive.yml")} lang={lang} default_lang={config.default_language} /> }}

## Mahjong online {#mahjong-online}
{{ <help_items items={load_data(path="data/help/online.yml")} lang={lang} default_lang={config.default_language} /> }}

## Other Mahjong clubs {#other-mahjong-clubs}
{{ <help_items items={load_data(path="data/help/clubs.yml")} lang={lang} default_lang={config.default_language} /> }}
