# FIFA World Cup Awards Predictor Report

## Methodology
- These awards are explainable analytics estimates based on manually editable player priors, team profiles, and Monte Carlo team progression probabilities. They are not official FIFA predictions.
- Player awards combine editable priors, position logic, expected minutes, and Monte Carlo team progression probabilities.
- Team awards combine editable team-award profiles with tournament progression signals and player star-power context.
- Player of the Match and Goal of the Tournament are proxy estimates because this project does not simulate full player-event logs or actual goal quality.

## Golden Ball podium
| golden_ball_rank | player | team | position | golden_ball_probability | award_podium |
| --- | --- | --- | --- | --- | --- |
| 1 | Kylian Mbappe | France | forward | 0.0221616 | Golden Ball |
| 2 | Vinicius Junior | Brazil | forward | 0.0204515 | Silver Ball |
| 3 | Jude Bellingham | England | midfielder | 0.0201383 | Bronze Ball |
| 4 | Harry Kane | England | forward | 0.0194654 |  |
| 5 | Emiliano Martinez | Argentina | goalkeeper | 0.0193349 |  |
| 6 | Alisson Becker | Brazil | goalkeeper | 0.0190308 |  |
| 7 | Bruno Fernandes | Portugal | midfielder | 0.0185179 |  |
| 8 | Florian Wirtz | Germany | midfielder | 0.0183677 |  |
| 9 | Thibaut Courtois | Belgium | goalkeeper | 0.0183642 |  |
| 10 | Mike Maignan | France | goalkeeper | 0.0183098 |  |

## Golden Boot podium
| golden_boot_rank | player | team | position | expected_goals_score | boot_podium |
| --- | --- | --- | --- | --- | --- |
| 1 | Kylian Mbappe | France | forward | 116.964 | Golden Boot |
| 2 | Harry Kane | England | forward | 116.953 | Silver Boot |
| 3 | Vinicius Junior | Brazil | forward | 98.9184 | Bronze Boot |
| 4 | Lautaro Martinez | Argentina | forward | 84.15 |  |
| 5 | Bukayo Saka | England | forward | 76.2048 |  |
| 6 | Lionel Messi | Argentina | forward | 72.072 |  |
| 7 | Romelu Lukaku | Belgium | forward | 71.232 |  |
| 8 | Julian Alvarez | Argentina | forward | 70.356 |  |
| 9 | Cristiano Ronaldo | Portugal | forward | 69.768 |  |
| 10 | Heung-Min Son | South Korea | forward | 68.04 |  |

## Golden Glove
| golden_glove_rank | player | team | golden_glove_probability | award |
| --- | --- | --- | --- | --- |
| 1 | Emiliano Martinez | Argentina | 0.0984551 | Golden Glove |
| 2 | Alisson Becker | Brazil | 0.0969384 |  |
| 3 | Thibaut Courtois | Belgium | 0.0964446 |  |
| 4 | Mike Maignan | France | 0.0946222 |  |
| 5 | Jordan Pickford | England | 0.0901192 |  |
| 6 | Yassine Bounou | Morocco | 0.0893903 |  |
| 7 | Manuel Neuer | Germany | 0.0888377 |  |
| 8 | Diogo Costa | Portugal | 0.0887436 |  |
| 9 | Unai Simon | Spain | 0.0874151 |  |
| 10 | Dominik Livakovic | Croatia | 0.0868154 |  |

## Young Player
| young_player_rank | player | team | position | young_player_probability | award |
| --- | --- | --- | --- | --- | --- |
| 1 | Lamine Yamal | Spain | forward | 1 | Young Player Award |

## Fair Play Trophy
| fair_play_rank | team | fair_play_probability | award |
| --- | --- | --- | --- |
| 1 | Morocco | 0.0768578 | Fair Play Trophy |
| 2 | Spain | 0.0759828 |  |
| 3 | Netherlands | 0.0707964 |  |
| 4 | Argentina | 0.0702672 |  |
| 5 | Japan | 0.0676986 |  |
| 6 | England | 0.0663156 |  |
| 7 | Brazil | 0.0646291 |  |
| 8 | France | 0.0645953 |  |
| 9 | Belgium | 0.0629285 |  |
| 10 | Portugal | 0.056797 |  |

## Most Entertaining Team
| most_entertaining_rank | team | most_entertaining_probability | award |
| --- | --- | --- | --- |
| 1 | Argentina | 0.0822798 | Most Entertaining Team |
| 2 | England | 0.0819584 |  |
| 3 | Portugal | 0.0792801 |  |
| 4 | Brazil | 0.0732805 |  |
| 5 | Spain | 0.0725305 |  |
| 6 | France | 0.070495 |  |
| 7 | Germany | 0.0695307 |  |
| 8 | Belgium | 0.0680309 |  |
| 9 | Uruguay | 0.0567817 |  |
| 10 | South Korea | 0.0497107 |  |

## Predicted Team of the Tournament
| formation_slot | player | team | position |
| --- | --- | --- | --- |
| GK1 | Emiliano Martinez | Argentina | goalkeeper |
| DEF1 | Achraf Hakimi | Morocco | defender |
| DEF2 | Virgil van Dijk | Netherlands | defender |
| DEF3 | Alphonso Davies | Canada | defender |
| DEF4 | Ruben Dias | Portugal | defender |
| MID1 | Jude Bellingham | England | midfielder |
| MID2 | Bruno Fernandes | Portugal | midfielder |
| MID3 | Florian Wirtz | Germany | midfielder |
| FWD1 | Kylian Mbappe | France | forward |
| FWD2 | Vinicius Junior | Brazil | forward |
| FWD3 | Harry Kane | England | forward |

## Player of the Match proxy
| player_of_match_proxy_rank | player | team | estimated_potm_count |
| --- | --- | --- | --- |
| 1 | Virgil van Dijk | Netherlands | 3.25996 |
| 2 | Memphis Depay | Netherlands | 3.04004 |
| 3 | Takefusa Kubo | Japan | 2.77537 |
| 4 | Santiago Gimenez | Mexico | 2.77313 |
| 5 | Hirving Lozano | Mexico | 2.52687 |
| 6 | Christian Pulisic | United States | 2.50771 |
| 7 | Dominik Livakovic | Croatia | 2.12347 |
| 8 | Wataru Endo | Japan | 2.02463 |
| 9 | Jonathan David | Canada | 1.95654 |
| 10 | Weston McKennie | United States | 1.89229 |

## Goal of the Tournament proxy
| goal_of_tournament_proxy_rank | player | team | goal_of_tournament_proxy_probability |
| --- | --- | --- | --- |
| 1 | Kylian Mbappe | France | 0.0425639 |
| 2 | Harry Kane | England | 0.0415295 |
| 3 | Vinicius Junior | Brazil | 0.0369819 |
| 4 | Lautaro Martinez | Argentina | 0.0316878 |
| 5 | Bukayo Saka | England | 0.0297594 |
| 6 | Lionel Messi | Argentina | 0.0296319 |
| 7 | Cristiano Ronaldo | Portugal | 0.0276861 |
| 8 | Julian Alvarez | Argentina | 0.0274469 |
| 9 | Romelu Lukaku | Belgium | 0.0273514 |
| 10 | Heung-Min Son | South Korea | 0.0273243 |

## Limitations
- Manually editable priors may not reflect final squads or current form.
- Monte Carlo probabilities depend on simulation sample size and upstream match model quality.
- No live player-event data or official FIFA judging inputs are used.
- Fan-vote awards are represented as proxy analytics, not actual fan-vote forecasts.
- This is not an official FIFA prediction.
- This is not betting advice.

## Summary snapshot
- Top Golden Ball player: Kylian Mbappe
- Top Golden Boot player: Kylian Mbappe
- Top Golden Glove player: Emiliano Martinez
- Top Young Player: Lamine Yamal
- Fair Play team: Morocco
- Most Entertaining Team: Argentina
- Team of the Tournament count: 11