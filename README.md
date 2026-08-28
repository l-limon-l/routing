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
| `ai/domain.json` | домены ChatGPT/Sora и Claude (включая Claude Code) | `releases/latest/download/ai.srs` |
| `ai/ip.json` | собственные подсети Anthropic | `releases/latest/download/ai_ip.srs` |

### Зачем Spotify отдельный IP-набор

Десктопный клиент Spotify ходит на свой accesspoint по голому IP, без DNS-запроса,
поэтому доменные правила этот трафик не видят вообще. Плюс он использует там QUIC
(UDP/443), который плохо переживает туннель: соединения пересоздаются, событие о смене
трека не доезжает, и активность в Discord залипает на одном треке до конца его
длительности. LimCore использует этот IP-набор дважды — чтобы завернуть трафик в прокси
и чтобы отбить по нему UDP, заставив клиент откатиться на TLS/TCP.

### Почему AI не берётся из Re-filter

В Re-filter есть домены OpenAI, но нет ни `anthropic.com`, ни `claude.com` — Claude Code через
него не заработает вообще. А его `ipsum.lst` для IP не годится: там только IPv4, адреса
ChatGPT лежат внутри `104.16.0.0/12` (весь Cloudflare целиком), а от Anthropic есть ровно
один `/32` вместо всей сети.

Поэтому IP-набор здесь содержит только собственное пространство Anthropic — `160.79.104.0/21` и
`2607:6bc0::/32` (по RDAP зарегистрированы на Anthropic, PBC). Оно выделенное, поэтому его
можно заворачивать целиком, и `api.anthropic.com` попадёт в прокси даже без DNS-запроса.
Адреса ChatGPT сюда не попадают осознанно: он живёт на общем аникасте Cloudflare
(`8.6.112.0/24`, `8.47.69.0/24` — по RDAP это Cloudflare, Inc.), и заворачивать их значило бы
тащить в туннель чужой трафик.

## Как добавить набор

1. Положить `<имя>/domain.json` (и при необходимости `<имя>/ip.json`).
2. Добавить строчки компиляции в `.github/workflows/build.yml`.
3. Запушить в `main` — CI сам пересоберёт релиз.
