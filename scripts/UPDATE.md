# Daily update

1. Open https://s11l84-26-fall.matchtrak.com/11/main.nsf/schedule-regiongames-t-by-div?OpenView&Start=1&Count=200&ExpandView&RestrictToCategory=R84 in the built-in browser and read the page text.
2. Match each MatchTrak game to `data/games.json` by `id` (the 5-digit game number, never shown on the site).
3. Update `date`, `time`, and `field` when MatchTrak changes them.
4. Replace `home` or `away` only when MatchTrak shows a real team name: `L84-Call_R` becomes `Call`.  Fix casing (`Poladian-Melzer`, `Benavides Zacarias`, `Gonzalez`).  Keep the neutral label while MatchTrak shows a placeholder such as `#Semis-01`.
5. For final games, set `home_score` and `away_score` as numbers, home first.  Put penalty kicks, forfeits, or postponements in `note` (for example, `PK 4-3` or `Postponed`).
6. Skip MatchTrak games marked Canceled that show only placeholder seeds.  If a real game becomes Canceled, set `note` to `Canceled`.
7. Set `updated` to the current Pacific time in ISO format, then run `python3 scripts/build.py`.
8. Confirm the build prints 53 games unless MatchTrak added or removed some, then commit and push to `main`.
