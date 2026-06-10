# Golden Ball / Best Player Analytics Report

## Methodology
- Uses manually editable candidate priors (no live scraping).
- Applies position-specific impact weighting (forward/midfielder/defender/goalkeeper).
- Adds team progression influence from Monte Carlo stage probabilities.
- Applies expected-minutes factor for likely tournament involvement.
- Converts final scores to probability shares across candidates.

## Summary
- Candidate count: 50
- Teams represented: 11
- Top player: Emiliano Martinez
- Top team: Argentina
- Top probability: 3.82%
- Validation passed: True

## Top 20 candidates
| rank | player | team | position | golden_ball_probability | golden_ball_probability_percent | final_golden_ball_score | team_progression_score | position_impact_score | star_role_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Emiliano Martinez | Argentina | goalkeeper | 0.0382347 | 3.82 | 866.016 | 0 | 836 | 8.2 |
| 2 | Alisson Becker | Brazil | goalkeeper | 0.0368304 | 3.68 | 834.21 | 0.5 | 800.5 | 8 |
| 3 | Mike Maignan | France | goalkeeper | 0.0352971 | 3.53 | 799.48 | 1.5 | 774 | 7.5 |
| 4 | Yassine Bounou | Morocco | goalkeeper | 0.0346887 | 3.47 | 785.7 | 0.5 | 781.5 | 7 |
| 5 | Diogo Costa | Portugal | goalkeeper | 0.0330457 | 3.3 | 748.485 | 0.75 | 740 | 6.9 |
| 6 | Jordan Pickford | England | goalkeeper | 0.0326185 | 3.26 | 738.81 | 0.5 | 729.5 | 6.9 |
| 7 | Unai Simon | Spain | goalkeeper | 0.0322686 | 3.23 | 730.884 | 1.75 | 738 | 6.8 |
| 8 | Manuel Neuer | Germany | goalkeeper | 0.0314604 | 3.15 | 712.58 | 7 | 771 | 7 |
| 9 | Koen Casteels | Belgium | goalkeeper | 0.0303012 | 3.03 | 686.323 | 2.25 | 707.5 | 6.3 |
| 10 | Sergio Rochet | Uruguay | goalkeeper | 0.029745 | 2.97 | 673.724 | 0 | 695 | 6.4 |
| 11 | Jude Bellingham | England | midfielder | 0.0224842 | 2.25 | 509.268 | 0.5 | 447 | 9.1 |
| 12 | Kylian Mbappe | France | forward | 0.021743 | 2.17 | 492.48 | 1.5 | 415.4 | 9.5 |
| 13 | Bruno Fernandes | Portugal | midfielder | 0.0215463 | 2.15 | 488.025 | 0.75 | 445 | 8.5 |
| 14 | Rodri | Spain | midfielder | 0.0212602 | 2.13 | 481.545 | 1.75 | 434.5 | 8.8 |
| 15 | Florian Wirtz | Germany | midfielder | 0.0207647 | 2.08 | 470.322 | 7 | 436 | 8.6 |
| 16 | Jamal Musiala | Germany | midfielder | 0.0205191 | 2.05 | 464.758 | 7 | 417.5 | 8.7 |
| 17 | Antonio Rudiger | Germany | defender | 0.0201775 | 2.02 | 457.02 | 7 | 408.5 | 7.3 |
| 18 | Kevin De Bruyne | Belgium | midfielder | 0.0194271 | 1.94 | 440.024 | 2.25 | 429 | 8.9 |
| 19 | Ruben Dias | Portugal | defender | 0.0194046 | 1.94 | 439.515 | 0.75 | 394.2 | 7.4 |
| 20 | Achraf Hakimi | Morocco | defender | 0.0193152 | 1.93 | 437.49 | 0.5 | 391.8 | 7.8 |

## Position breakdown
| position | candidate_count | total_probability | avg_final_score |
| --- | --- | --- | --- |
| goalkeeper | 10 | 0.33449 | 757.621 |
| midfielder | 16 | 0.287478 | 406.961 |
| forward | 16 | 0.22783 | 322.522 |
| defender | 8 | 0.150202 | 425.261 |

## Team progression note
Team progression is a strong factor in this estimate because end-of-tournament awards often favor players whose teams go deep into semi-finals/final.

## Limitations
- This is an explainable analytics estimate, not an official award prediction.
- Candidate priors are manually editable inputs and should be updated before production use.
- No live player-stat scraping is used in this step.
- Output quality depends on both player priors and Monte Carlo team progression quality.

## Responsible-use note
This educational model output is not betting advice.