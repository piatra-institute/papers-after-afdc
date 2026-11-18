# Brief

Written before research begins and, for the analysis plan below, before any election-return data were downloaded or inspected. The plan was fixed on 2026-11-18; its SHA-256 at the time of the first outcome download is recorded by `simulation/fetch_data.py` in `simulation/data/fetch-log.json` and in audit.md. Any later deviation is listed under "Deviations" at the end of this file with its reason.

## Question

The 1996 welfare law replaced Aid to Families with Dependent Children (AFDC) with block-granted Temporary Assistance for Needy Families (TANF). Over the following two decades the share of poor families with children who received cash assistance fell in every state, by very different amounts. Did counties in states where cash protection eroded more move further toward the Republican presidential candidate when they were hit by the same local economic shock, the rise of Chinese import competition after 2000? And is the estimated amplification, with its uncertainty, large enough to have decided Michigan, Wisconsin or Pennsylvania in 2016?

## Claim to test

Hypothesis H: the effect of commuting-zone exposure to Chinese import competition (2000 to 2008) on the change in the county Republican share of the two-party presidential vote (2000 to 2016) is larger where the state's AFDC/TANF-to-poverty ratio fell more between 1995–96 and 2015–16. In the specification below, H predicts $\gamma > 0$.

The paper reports $\gamma$ with its interval whatever its sign, together with the placebo, robustness and bridge results. If the evidence does not support H, the paper says so.

## Kind

Empirical test on public data (ships a simulation folder holding the analysis): moderation design, pre-registered in this file, plus a short documentary history of the 1996 law and its cash-protection accounting. `has_simulation: true`.

## Strongest serious alternative

States that cut cash assistance most differ from other states in ways that themselves condition the political response to job loss: racial composition and racial politics of welfare (Soss and colleagues; the CBPP's observation that low-TPR states have larger Black populations), Southern location, prior partisanship and union density. A positive interaction could reflect those traits, not cash protection. A second alternative is that the moderator is partly an outcome of the shock (trade-exposed states gained poor families, lowering the ratio). The robustness and falsification tests below are designed against both. A third alternative is that cash assistance after 1996 reached so few working-age adults in trade-exposed manufacturing areas that state differences in it cannot plausibly move county votes; this predicts $\gamma \approx 0$.

## Cornerstone literature

- Trade shocks and politics: Autor, Dorn and Hanson 2013 (AER, local labor-market effects, transfers); Autor, Dorn, Hanson and Majlesi 2020 (AER, presidential vote shares, the template design); Margalit 2011 (APSR, Trade Adjustment Assistance and anti-incumbent voting); Colantone and Stanig 2018 (APSR, Brexit; AJPS, Western Europe); Che et al. on PNTR; Choi, Kuziemko, Washington and Wright on NAFTA; Jensen, Quinn and Weymouth 2017; Baccini and Weymouth 2021.
- Compensation and embedded liberalism: Ruggie 1982; Rodrik 1998; work testing whether welfare generosity moderates the political effect of economic risk (Swank and Betz 2003; Halikiopoulou and Vlandas 2016; Gingrich 2019; Bisbee et al. 2020); Fetzer 2019 on austerity and Brexit.
- Policy feedback and welfare: Soss 1999; Mettler and Soss 2004; Campbell 2012; Soss, Fording and Schram; Corman, Dave and Reichman 2017 on welfare reform and women's turnout.
- Welfare reform and cash protection: CRS R45966 (poverty-gap accounting); Parolin 2021; Bitler and Hoynes 2016; Ziliak; the CBPP TANF-to-poverty series; the Welfare Rules Databook.
- Inference: Cameron, Gelbach and Miller (multiway clustering; wild cluster bootstrap); Adão, Kolesár and Morales and Borusyak, Hull and Jaravel on shift-share inference; Nizalova and Murtazashvili and Bun and Harrison on interactions with an exogenous treatment and an endogenous moderator.

## Analysis plan (fixed before outcome data)

### Sample and units

Counties of the 48 contiguous states in the 1990-definition county sample of Autor, Dorn, Hanson and Majlesi (ADHM 2020, 3,107 counties). The District of Columbia is dropped because the CBPP series has no value for it (it is one county and would be absorbed by its state fixed effect in any case). County codes in later returns are mapped to 1990 definitions: 46102 to 46113, 12086 to 12025, 51515 merged into 51019, 51560 into 51005, 51780 into 51083; Broomfield (08014) is excluded, as in ADHM.

### Variables

- Outcome $\Delta R_c$: change in the Republican percentage of the two-party presidential vote in county $c$, from the MIT Election Data and Science Lab county returns (CC0), candidate votes summed over all reported modes. Primary window 2000 to 2016; secondary window 2012 to 2016; the 2000 to 2008 and 2000 to 2012 windows are reported as the time profile.
- Shock $X_z$: ADHM's change in Chinese import penetration in commuting zone $z$, 2000 to 2008 (`d_imp_usch_pd_0008`), instrumented with the corresponding exposure built from Chinese exports to eight other high-income countries (`d_imp_otch_lag_pd_0008`).
- Moderator $M_s$: erosion of the state AFDC/TANF-to-poverty ratio (families receiving cash assistance per 100 families with children in poverty, two-year averages, CBPP), $M_s = \mathrm{TPR}_{1995\text{–}96} - \mathrm{TPR}_{2015\text{–}16}$. Larger means more protection lost. In regressions $M_s$ is centred at its unweighted mean over the 48 states.
- Controls $W_c$: ADHM's full presidential controls except the Census division dummies, which state fixed effects absorb: CZ manufacturing employment share, routine-task share and offshorability index (2000); county population shares by sex, college education, foreign birth, nine age groups and four racial or ethnic groups (2000); county Republican two-party shares in 1992 and 1996 (Algara and Amlani county returns, CC0).
- Weights: county total presidential votes in 2000 (MEDSL), as in ADHM.

### Primary specification

Two-stage least squares, weighted:

$$\Delta R_c = \alpha_{s(c)} + \beta X_{z(c)} + \gamma\, X_{z(c)} \tilde M_{s(c)} + W_c'\delta + \varepsilon_c,$$

with state fixed effects $\alpha_s$ absorbing the moderator's main effect, endogenous regressors $X$ and $X\tilde M$, and instruments $Z$ and $Z\tilde M$. The interaction is identified from within-state variation in commuting-zone exposure crossed with the state-level moderator. Primary inference: standard errors two-way clustered by state and commuting zone. The hypothesis test is the two-sided 95% interval for $\gamma$; this is the single primary test. Effects are also reported as the difference in the shock effect between states at the 25th and 75th percentiles of $M$.

### Validation steps (not hypothesis tests)

- V1: replicate ADHM Table 5, panel B, column 6 (2000 to 2016, division dummies, full controls, CZ clustering) with the open returns; their published estimate is 1.71 (0.90).
- V2: compare MEDSL 2016 state totals for Michigan, Wisconsin and Pennsylvania with the FEC's official returns.

### Robustness (pre-specified)

- R1: OLS in place of 2SLS.
- R2: unweighted.
- R3: inference variants for the primary $\gamma$: clustering by CZ only and by state only; a wild cluster bootstrap by state (Rademacher weights, null imposed, 9,999 draws, fixed seed) for the reduced-form interaction $Z\tilde M$.
- R4: alternative moderators, each standardized by its standard deviation across the 48 states and oriented so that larger values mean less cash protection: (a) minus the 2015–16 TPR level; (b) minus the July 2016 real maximum TANF benefit for a family of three (Welfare Rules Databook Table L5, deflated to 1996 dollars by the July CPI-U); (c) the percentage decline in the real maximum benefit, July 1996 to July 2016; (d) minus the July 1996 AFDC maximum benefit, a pre-reform generosity diagnostic; (e) TPR erosion from 1995–96 to 2007–08, the end of the shock window. Benefit rules: California and Massachusetts use the non-exempt standard; Wisconsin 2016 uses the Community Service Jobs payment; footnoted state figures are taken as printed.
- R5: competing moderators added one at a time and then jointly, each interacted with the shock and instrumented analogously: county white population share (2000); a South indicator (Census South divisions); the state Republican two-party share in 1996; the state vote-weighted mean of the shock.
- R6: alternative shock from County Business Patterns: the CZ decline in manufacturing employment from 2000 to 2008 as a percentage of 2000 total CBP employment, with suppressed cells imputed at the midpoint of their size class; estimated by OLS and by 2SLS with the ADHM instrument.
- R7: leave-one-state-out range of $\gamma$.

### Falsification tests

- F1: pre-period placebo outcomes, 1992 to 1996 (primary placebo) and 1996 to 2000, both from the Algara and Amlani returns, regressed on the same shock and interaction with the controls excluding the lagged vote shares. H's identifying assumption predicts $\gamma \approx 0$.
- F2: placebo moderator, the AFDC-era change in the ratio from 1978–79 to 1995–96, oriented as a decline. If it moderates as strongly as post-reform erosion, the interaction reflects persistent state traits.

### Bridge to 2016

For Michigan, Wisconsin and Pennsylvania, the net change in the Democratic-minus-Republican margin implied by setting each state's erosion to a counterfactual value $M^\ast$ is $\sum_{c \in s} 2\,\hat\gamma\, X_{z(c)} (M_s - M^\ast) V_c / 100$, with $V_c$ the county's 2016 two-party vote. Two counterfactuals: (a) $M^\ast = 0$, retaining the 1995–96 ratio, which lies outside the observed range of erosion; (b) $M^\ast$ equal to the smallest erosion among the 48 states, which stays within it. The interval is the image of the primary 95% interval for $\gamma$. Each is compared with the Trump margin in the FEC's official returns, and the paper states only whether the interval includes effects at least as large as the margin.

### Decision rule

H is supported if the primary 95% interval for $\gamma$ excludes zero on the positive side, the primary placebo interaction is not distinguishable from zero, and the sign survives R1 to R6. Anything else is reported as not supported or inconclusive, with intervals. Non-significance is not read as evidence of no effect; where useful the paper states which effect sizes the interval excludes.

## Deviations

Recorded after the outcome data were downloaded. None changes a specification, a variable definition, a window, a weight or the decision rule.

1. Source of the MEDSL file. The current Harvard Dataverse release (doi:10.7910/DVN/VOQCHQ) requires a guestbook form that collects personal details before download. The analysis uses MEDSL's own public copy of the 2000–2016 release (GitHub repository MEDSL/county-returns, commit f44e3fc, file countypres_2000-2016.csv, git blob eea9214), the same dataset that Dataverse distributes under CC0 1.0.
2. Two data corrections, found by comparing MEDSL with the Algara and Amlani returns and with the FEC totals. (a) County total votes, used only for the 2000 weights, are summed over candidate rows, because the file's `totalvotes` field repeats the county value for same-name Virginia cities (Fairfax, Franklin, Richmond, Roanoke, Bedford). (b) Kansas City, Missouri, which MEDSL reports as a separate unit (code 36000) from 2004 to 2016, is added to Jackson County (29095), where it lies. Without (b) the Jackson County 2016 share would omit the city.
3. In the County Business Patterns aggregation, Broomfield (08014, created 2001) is assigned to Boulder's commuting zone and statewide records (county code 999) are dropped.
4. Inference detail not stated in the plan: intervals for state-clustered and two-way-clustered statistics use the t distribution with $G - 1 = 47$ degrees of freedom; CZ-clustered statistics use $G - 1$ with $G$ the number of commuting zones.
5. Additions labelled in the results as descriptive and not pre-registered: (a) V1b, the estimation code applied to ADHM's own analysis file (the only place where its vote-share columns are read); (b) the correlations of the erosion measure with the 1995–96 and 2015–16 ratios; (c) the minimum detectable interaction at 80% power implied by the estimated standard error; (d) the shock effect estimated separately for terciles of states ordered by erosion, shown in Figure 1.
