# Editorial record

Status: author-side record, 2026-11-18. This is not an independent editorial review; editorial-review.json and visual-review.json are left to a reviewer from another model family.

## Contribution and reader

Question: did the post-1996 erosion of state cash assistance amplify the presidential-vote response to the China trade shock, and could any such amplification have decided Michigan, Wisconsin or Pennsylvania in 2016? Reader: political economists, welfare-policy researchers and political scientists who know the China-shock and policy-feedback literatures but not their intersection.

Contribution against the closest prior work. Autor, Dorn, Hanson and Majlesi (2020) estimate the main effect of the China shock on county presidential vote shares. Margalit (2011), Kim and Pelc (2021a, 2021b) and Balcazar and Lee (working paper) study the targeted Trade Adjustment Assistance program as a moderator. European work (Swank and Betz 2003; Halikiopoulou and Vlandas 2016; Vlandas and Halikiopoulou 2022; Gingrich 2019; Milner 2021) studies welfare generosity and far-right support across countries. This paper adds a pre-registered test, on public data, of whether state differences in the general cash safety net for poor families moderated the US presidential-vote response to the shock, with placebo, robustness and power analysis, and a vote-level translation for the three states. The result is a wrong-signed interaction whose interval includes zero and excludes amplification larger than about a quarter of the average effect per standard deviation; the 2016 translation is uninformative because the flip-sufficient interaction is smaller than the standard error.

## Material worth preserving

- The documentary history with primary-source quotations: the 1994 and 1995 alternatives (24-month WORK transition; sum-sufficient FMAP matching with an unemployment-based time-limit exemption), the H.R. 4 veto message's downturn language, the roll-call splits and the signing statement's contingency-funding objection.
- The finding that erosion correlates 0.81 with the 1995–96 ratio and about zero with the 2015–16 ratio.
- The validation chain: the code reproduces ADHM's 1.71 (0.90) on their file; open returns give 1.90 (0.92).
- The bridge's statement of resolution: the γ needed to flip each state is below the standard error.

## Reverse outline

1. Cash protection and the political response to job loss: the two trends, the compensation hypothesis, the closest prior work and the residual question; summary of the result.
2. What the 1996 law changed: statute, alternatives, vetoes, votes, signing objection; the measured erosion; who the program served (relevant to the third rival).
3. What earlier studies establish about politics: trade-shock voting, policy feedback, rivals (race and state policy choices; status-threat readings of 2016).
4. Data and design: sources, variables, moderator facts (erosion tracks starting levels), specification, identification and its limits, inference, pre-registration and deviations.
5. Results: validation; the primary interaction; Table 1 windows and placebos; robustness (Figure 2); precision.
6. Implications for the three states: formula, counterfactuals, Table 2, Figure 3, resolution statement.
7. What the test does and does not show: what is excluded; why the moderator limits inference; causal reading; inference caveats; what a sharper test would use; conclusion at the right scale.
8. Code and data availability.

## Strongest rival

Erosion proxies for persistent state traits (racial composition of the caseload, region, partisanship) that themselves condition the response to job loss (Soss et al. 2001; Baccini and Weymouth 2021). The design addresses this with competing interactions (county white share, South, 1996 state vote, state mean shock), a pre-reform placebo moderator and pre-period placebo outcomes; none changes the reading. A second rival, that TANF barely reached trade-displaced workers, predicts the null and is consistent with ADH's transfer accounting; the paper states it as a limit on what the null says about cash protection.

## Decisions and remaining checks

- The seed's stipulated Bayesian table was dropped: with priors and Bayes factors not informed by data it adds nothing; no data-informed version was built because the interaction estimate already summarizes the evidence.
- The seed's threshold arithmetic is replaced by the bridge computed from the estimated interaction and the FEC margins.
- The seed's three counterfactual histories were cut to the documentary record of the alternatives; the paper makes no claim about their enactment or survival.
- Rounding errors caught by the claims binding (Table 1 2000–2012 lower bound, low-1996-benefit moderator) were corrected in the prose.
- Neutral framing: parties are named only where the record names them (roll calls, veto of the Republican reconciliation bill, candidates' margins).
- Remaining: independent review of all 66 source claims (all `verified: false`), claim coverage, editorial and visual records. The shift-share inference of Adão, Kolesár and Morales is not implemented because industry shares are not in the public archive at county level; the paper states the omission.
