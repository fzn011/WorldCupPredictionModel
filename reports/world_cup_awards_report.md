# FIFA World Cup 2026 Awards Predictor Report

## Official data status
- official_final_enabled: True
- final_ready: True

## Methodology
- These are explainable analytics estimates based on official squads, editable player priors, team profiles, and Monte Carlo team progression probabilities. They are not official FIFA predictions.
- Player awards combine official squad priors, position logic, expected minutes, and Monte Carlo team progression.
- Team awards combine official team profiles with tournament progression and squad star-power context.
- Player of the Match and Goal of the Tournament are proxy estimates (no match-level player-event simulation).

## Golden Ball podium
| player_name | team | position_code | golden_ball_probability | award |
| --- | --- | --- | --- | --- |
| ADU Prince | Ghana | FW | 0.000977376 | Golden Ball |
| AYEW Jordan | Ghana | FW | 0.000977376 | Silver Ball |
| BAAH Christopher Bonsu | Ghana | FW | 0.000977376 | Bronze Ball |
| BEIER Maximilian | Germany | FW | 0.000977376 |  |
| FATAWU Abdul | Ghana | FW | 0.000977376 |  |
| HAVERTZ Kai | Germany | FW | 0.000977376 |  |
| NUAMAH Ernest | Ghana | FW | 0.000977376 |  |
| SULEMANA Kamaldeen | Ghana | FW | 0.000977376 |  |
| THOMAS-ASANTE Brandon | Ghana | FW | 0.000977376 |  |
| UNDAV Deniz | Germany | FW | 0.000977376 |  |

## Golden Boot podium
| player_name | team | expected_goals | award |
| --- | --- | --- | --- |
| AARONSON Brenden | United States | 0 | Golden Boot |
| AASGAARD Thelo | Norway | 0 | Silver Boot |
| ABADA Achref | Algeria | 0 | Bronze Boot |
| ABDALLAH ALFAKHORI | Jordan | 0 |  |
| ABDALLAH NASIB | Jordan | 0 |  |
| ABDI Ali | Tunisia | 0 |  |
| ABDULAZIZ HATEM | Qatar | 0 |  |
| ABDULELAH ALAMRI | Saudi Arabia | 0 |  |
| ABDULLAEV Abdulla | Uzbekistan | 0 |  |
| ABDULLAH ALHAMDDAN | Saudi Arabia | 0 |  |

## Golden Glove
| player_name | team | golden_glove_probability | award |
| --- | --- | --- | --- |
| ANANG Joseph | Ghana | 0.00832557 | Golden Glove |
| ASARE Benjamin | Ghana | 0.00832557 |  |
| BAUMANN Oliver | Germany | 0.00832557 |  |
| NEUER Manuel | Germany | 0.00832557 |  |
| NUEBEL Alexander | Germany | 0.00832557 |  |
| ZIGI Lawrence Ati | Ghana | 0.00832557 |  |
| CREPEAU Maxime | Canada | 0.00807704 |  |
| GOODMAN Owen | Canada | 0.00807704 |  |
| ST. CLAIR Dayne | Canada | 0.00807704 |  |
| BRADY Chris | United States | 0.00776639 |  |

## Young Player
| player_name | team | young_player_probability | award |
| --- | --- | --- | --- |
| BAAH Christopher Bonsu | Ghana | 0.0217869 | Young Player Award |
| YIRENKYI Caleb | Ghana | 0.0209424 |  |
| ELLOUMI Rayan | Tunisia | 0.020858 |  |
| HAMZA ABDELKARIM | Egypt | 0.0206046 |  |
| FERNANDEZ-PARDO Matias | Belgium | 0.0201824 |  |
| AYARI Khalil | Tunisia | 0.0200135 |  |
| YAMAL Lamine | Spain | 0.0200135 |  |
| DOUE Desire | France | 0.0199291 |  |
| AMAIMOUNI Ayoube | Morocco | 0.0195913 |  |
| ENDRICK | Brazil | 0.0195913 |  |

## Fair Play Trophy
| team | fair_play_probability | award |
| --- | --- | --- |
| Cabo Verde | 0.0869921 | Fair Play Trophy |
| Congo DR | 0.0869921 |  |
| Curaçao | 0.0869921 |  |
| Haiti | 0.0869921 |  |
| Iraq | 0.0869921 |  |
| Jordan | 0.0869921 |  |
| Panama | 0.0869921 |  |
| Saudi Arabia | 0.0869921 |  |
| Uzbekistan | 0.0869921 |  |
| Belgium | 0.00681756 |  |

## Most Entertaining Team
| team | most_entertaining_probability | award |
| --- | --- | --- |
| Cabo Verde | 0.087146 | Most Entertaining Team |
| Congo DR | 0.087146 |  |
| Curaçao | 0.087146 |  |
| Haiti | 0.087146 |  |
| Iraq | 0.087146 |  |
| Jordan | 0.087146 |  |
| Panama | 0.087146 |  |
| Saudi Arabia | 0.087146 |  |
| Uzbekistan | 0.087146 |  |
| Germany | 0.00626362 |  |

## Predicted Team of the Tournament
| formation_slot | player_name | team | position_code |
| --- | --- | --- | --- |
| GK1 | ANANG Joseph | Ghana | GK |
| DEF1 | ADJETEY Jonas | Ghana | DF |
| DEF2 | ANTON Waldemar | Germany | DF |
| DEF3 | BROWN Nathaniel | Germany | DF |
| DEF4 | KIMMICH Joshua | Germany | DF |
| MID1 | AMIRI Nadiem | Germany | MF |
| MID2 | BOAKYE Augustine | Ghana | MF |
| MID3 | GORETZKA Leon | Germany | MF |
| FWD1 | ADU Prince | Ghana | FW |
| FWD2 | AYEW Jordan | Ghana | FW |
| FWD3 | BAAH Christopher Bonsu | Ghana | FW |

## Player of the Match proxy
| player_name | team | estimated_potm_count |
| --- | --- | --- |
| AHMED Ali | Canada | 0.297126 |
| BUCHANAN Tajon | Canada | 0.297126 |
| DAVID Jonathan | Canada | 0.297126 |
| DAVID Promise | Canada | 0.297126 |
| LARIN Cyle | Canada | 0.297126 |
| OLUWASEYI Tani | Canada | 0.297126 |
| CHOINIERE Mathieu | Canada | 0.285428 |
| EUSTAQUIO Stephen | Canada | 0.285428 |
| FLORES Marcelo | Canada | 0.285428 |
| KONE Ismael | Canada | 0.285428 |

## Goal of the Tournament proxy
| player_name | team | goal_of_tournament_proxy_probability |
| --- | --- | --- |
| AARONSON Brenden | United States | 0.00721154 |
| ADAMS Tyler | United States | 0.00721154 |
| ADJETEY Jonas | Ghana | 0.00721154 |
| ADU Prince | Ghana | 0.00721154 |
| AHMED Ali | Canada | 0.00721154 |
| AMIRI Nadiem | Germany | 0.00721154 |
| ANANG Joseph | Ghana | 0.00721154 |
| ANTON Waldemar | Germany | 0.00721154 |
| ARFSTEN Max | United States | 0.00721154 |
| ASARE Benjamin | Ghana | 0.00721154 |

## Limitations
- Analytics estimate only; not an official FIFA prediction.
- Depends on Monte Carlo sample size and upstream match model quality.
- Depends on editable player priors and conservative team profile defaults.
- Fan-voted style awards are proxy analytics, not fan-vote forecasts.
- No match-level player event simulation or actual goal-quality modeling.
- No betting advice.

## Summary snapshot
- Top Golden Ball player: ADU Prince
- Top Golden Boot player: AARONSON Brenden
- Top Golden Glove player: ANANG Joseph
- Top Young Player: BAAH Christopher Bonsu
- Fair Play team: Cabo Verde
- Most Entertaining Team: Cabo Verde
- Team of the Tournament count: 11