# routing

Наборы правил (`.srs`) для [LimCoreWRT](https://github.com/l-limon-l/LimCoreWRT).

Здесь лежат списки, которых нет в [itdoginfo/allow-domains](https://github.com/itdoginfo/allow-domains).
Исходники — обычный JSON в формате source rule-set для sing-box; CI компилирует их
в `.srs` и кладёт в rolling-релиз `latest`, откуда роутер сам их забирает и обновляет
раз в сутки.

## Наборы

| Файл | Что внутри | Ссылка для sing-box |
| --- | --- | --- |
| `spotify/domain.json` | домены Spotify (приложение, веб-плеер, CDN) | `releases/latest/download/spotify.srs` |
| `spotify/ip.json` | accesspoint/dealer Spotify | `releases/latest/download/spotify_ip.srs` |

### Зачем Spotify отдельный IP-набор

Десктопный клиент Spotify ходит на свой accesspoint по голому IP, без DNS-запроса,
поэтому доменные правила этот трафик не видят вообще. Плюс он использует там QUIC
(UDP/443), который плохо переживает туннель: соединения пересоздаются, событие о смене
трека не доезжает, и активность в Discord залипает на одном треке до конца его
длительности. LimCore использует этот IP-набор дважды — чтобы завернуть трафик в прокси
и чтобы отбить по нему UDP, заставив клиент откатиться на TLS/TCP.

## Как добавить набор

1. Положить `<имя>/domain.json` (и при необходимости `<имя>/ip.json`).
2. Добавить строчки компиляции в `.github/workflows/build.yml`.
3. Запушить в `main` — CI сам пересоберёт релиз.
