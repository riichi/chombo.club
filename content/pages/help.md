+++
title = "Pomoc"
path = "help"
template = "page.html"
+++

## Materiały — jak grać w mahjonga {#materiały--jak-grać-w-mahjonga}
{{ <help_items items={load_data(path="data/help/materials.yml")} lang={lang} default_lang={config.default_language} /> }}

## Interaktywne — mahjong single player i trainery {#interaktywne--mahjong-single-player-i-trainery}
{{ <help_items items={load_data(path="data/help/interactive.yml")} lang={lang} default_lang={config.default_language} /> }}

## Mahjong online {#mahjong-online}
{{ <help_items items={load_data(path="data/help/online.yml")} lang={lang} default_lang={config.default_language} /> }}

## Inne kluby mahjongowe {#inne-kluby-mahjongowe}
{{ <help_items items={load_data(path="data/help/clubs.yml")} lang={lang} default_lang={config.default_language} /> }}
