# Data Dictionary

Column-level descriptions for every dataset used by the project.

---

## 1. Historical results (`results.csv`)

| column      | type     | description                                                |
|-------------|----------|------------------------------------------------------------|
| date        | date     | Match date (YYYY-MM-DD).                                   |
| home_team   | string   | Home team name.                                            |
| away_team   | string   | Away team name.                                            |
| home_score  | int      | Goals scored by the home team in regulation + ET.          |
| away_score  | int      | Goals scored by the away team in regulation + ET.          |
| tournament  | string   | Tournament name (e.g. "FIFA World Cup", "Friendly").       |
| city        | string   | City where the match was played.                           |
| country     | string   | Country where the match was played.                        |
| neutral     | 0/1      | 1 if the match was played at a neutral venue, else 0.      |

### Canonical model format (after conversion)

| column        | type   | description                                              |
|---------------|--------|----------------------------------------------------------|
| date          | date   | Match date.                                              |
| team_a        | string | Home team (standardized).                                |
| team_b        | string | Away team (standardized).                                |
| team_a_score  | int    | Goals for team_a.                                        |
| team_b_score  | int    | Goals for team_b.                                        |
| result        | int    | 2 = team_a win, 1 = draw, 0 = team_a loss.               |
| tournament    | string | Tournament name.                                         |
| city          | string | City.                                                    |
| country       | string | Country.                                                 |
| neutral       | 0/1    | Neutral-venue flag.                                      |

---

## 2. FIFA rankings (`fifa_rankings.csv`)

| column        | type   | description                                                |
|---------------|--------|------------------------------------------------------------|
| rank          | int    | World ranking position (1 = best).                         |
| team          | string | National team name.                                        |
| team_code     | string | 3-letter FIFA team code (e.g. FRA, ARG).                   |
| points        | float  | Official FIFA ranking points.                              |
| ranking_date  | date   | Date the ranking snapshot was published.                   |

---

## 3. Elo ratings (`elo_ratings.csv`)

| column        | type   | description                                                |
|---------------|--------|------------------------------------------------------------|
| rank          | int    | Elo rank position (1 = best).                              |
| team          | string | National team name.                                        |
| elo           | int    | World Football Elo rating.                                 |
| rating_date   | date   | Date the rating snapshot was taken.                        |

---

## 4. World Cup 2026 teams (`world_cup_2026_teams.csv`)

| column                | type   | description                                          |
|-----------------------|--------|------------------------------------------------------|
| team                  | string | Qualified national team.                             |
| confederation         | string | AFC, CAF, CONCACAF, CONMEBOL, OFC, or UEFA.          |
| is_host               | 0/1    | 1 if the team is a host nation.                      |
| qualified             | 0/1    | 1 if the team has qualified.                         |
| qualification_method  | string | "Host", "Qualification", "Playoff", etc.             |

---

## 5. World Cup 2026 groups (`world_cup_2026_groups.csv`)

| column  | type   | description                                          |
|---------|--------|------------------------------------------------------|
| group   | string | Group letter (A–L; 12 groups).                       |
| team    | string | Team in the group.                                   |
| pot     | int    | Seeding pot (1 = top seed, 4 = lowest).              |

---

## 6. World Cup 2026 schedule (`world_cup_2026_schedule.csv`)

| column     | type   | description                                              |
|------------|--------|----------------------------------------------------------|
| match_id   | int    | Unique match identifier.                                 |
| stage      | string | `group_stage`, `round_of_32`, `round_of_16`, etc.        |
| group      | string | Group letter for group-stage matches, else blank.        |
| date       | date   | Match date.                                              |
| venue      | string | Stadium name.                                            |
| city       | string | City.                                                    |
| country    | string | Host country.                                            |
| team_a     | string | First listed team.                                       |
| team_b     | string | Second listed team.                                      |
