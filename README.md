# Tuesday 24 November 2026 — the world in one image

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/keikuroba/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/keikuroba/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A drawn broadsheet that sums up Tuesday 24 November 2026 in five stories
plus a ticker:

- **Lead / Poland.** NATO rushes AWACS surveillance planes to Poland
  after three Russian Kh-101 cruise missiles came down in the south-east
  of the country on 20 November. The North Atlantic Council met in
  emergency session in Brussels; Secretary General Rutte vows the
  alliance will defend "every inch" of allied territory.
- **Baltics / Estonia.** Moscow accuses Estonia of hostile acts "on the
  verge of triggering open war" after Tallinn says it will close its
  land border with Russia from 1 December, blaming a Russian arson plot
  against a defence firm.
- **Markets / Nvidia.** Jensen Huang is reinstated as Nvidia's chief
  executive eleven days after he resigned. The shares jump 31%, the
  Nasdaq 6.5% and the S&P 500 4.7% — the best day on Wall Street since
  April 2025. President Trump takes credit for the comeback.
- **Climate / Antalya.** COP31 collapses: the summit in Antalya ends
  with no deal and the draft drops any fossil-fuel phase-out, leaving a
  split world empty-handed.
- **The Gulf / Hormuz.** The United Nations counts 25 seafarers killed
  and 134 attacks on shipping in and around the Strait of Hormuz since
  February, and warns the strangled waterway must not become "the new
  normal".
- **Ticker.** Indonesia factory fire: 24 dead; Trump halts the Iowa
  explosives blast; Alcaraz wins his first ATP Finals title; India
  pledges $1.6bn to Nepal; Gaza strikes kill a UN worker; Verstappen
  wins the Las Vegas Grand Prix; the World Chess Championship opens in
  Geneva.

## How it works

`tools/make_image.py` draws the broadsheet with Pillow (five illustrated
stories, masthead, ticker) and writes `entry.png` — a 1024×1024 PNG.
`main.py` is the entry point: it checks the picture is a well-formed PNG
(signature, IHDR first, every CRC, IEND with nothing after it, size and
dimension caps) and then copies it byte-for-byte to `/output/entry.png`.
The copy is deterministic: two runs write identical bytes.

Run it locally with `python3 main.py` (the script reads `entry.png` from
the repository root and writes `/output/entry.png`).
