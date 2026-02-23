## Formalized hypothesis

Indian raga theory assigns specific ragas to particular praharas (time‑of‑day segments), implying that the perceptual and affective state of listeners co‑varies with time of day. Translating this into a psychoacoustic prediction about pitch discrimination:

- **Operationalization of prahara**: In this dataset, praharas are approximated by three clock‑time windows used in the experiment: `Morning (8–10 AM)`, `Afternoon (4–6 PM)`, and `Evening (10 PM–12 AM)`. These windows are taken as representative segments within distinct praharas of the traditional day–night cycle.
- **Dependent variable (DV)**: Individual pitch‐difference just noticeable difference (JND) in Hz, estimated via a 2‑down 1‑up pure‑tone frequency discrimination staircase and summarized per participant × time‑of‑day as a central tendency measure (primary analysis: arithmetic mean; sensitivity analysis: geometric mean).
- **Within‑subject factor**: `Prahar / Time of day` with three levels (`Morning`, `Afternoon`, `Evening`), for participants who contributed repeated measurements.
- **Between‑subject / individual‑difference factors and covariates**:
  - `Chronotype`: Morning / Night / Depends (self‑reported “Are you a Morning or Night Person?”).
  - `Playback level`: Approximate volume slider percentage.
  - `Recent loud sound exposure`: Self‑reported notes about being in loud environments (train, concert, etc.), encoded as categorical covariates (e.g., none / moderate / high exposure).

**Primary musicologically‑motivated hypotheses (time‑of‑day main effect and chronotype interaction)**

- **H1a (time‑of‑day effect)**: Mean pitch JND differs across praharas/time‑of‑day windows; that is, there is a systematic modulation of pitch discrimination acuity by time of day consistent with raga‑time theory (listeners are not equally sensitive to pitch in all praharas).
- **H0a (time‑of‑day null)**: Mean pitch JND is the same across praharas/time‑of‑day windows; i.e., there is no reliable effect of time of day on pitch discrimination, once inter‑individual variability is accounted for.

Formally, for participant $i$ at time‑of‑day level $t \in \{\text{Morning, Afternoon, Evening}\}$, let $Y_{it}$ be the (log‑transformed) arithmetic‑mean JND:

- **H0a**: $\mu_{\text{Morning}} = \mu_{\text{Afternoon}} = \mu_{\text{Evening}}$
- **H1a**: $\exists\, t, t' : \mu_t \neq \mu_{t'}$

where $\mu_t$ denotes the population mean of $\log(Y_{it})$ at time‑of‑day level $t$.

In addition, let $c \in \{\text{Morning type, Night type, Depends}\}$ index chronotype groups, and $\mu_{t,c}$ be the mean log‑JND for chronotype $c$ at time‑of‑day level $t$:

- **H1b (chronotype × time‑of‑day interaction)**: The time‑of‑day effect on JND depends on chronotype. For example, Morning‑type participants may show lower JNDs (better pitch discrimination) in the morning relative to evening, whereas Night‑type participants may be relatively sharper in the evening.
- **H0b (no interaction)**: For all $c$, the pattern of $\mu_{t,c}$ across time‑of‑day levels is identical up to a constant offset; i.e., the difference in mean JND between praharas is the same for all chronotype groups.

The interaction hypothesis H1b will be tested in an extended ANOVA / mixed‑effects framework, conditional on having enough participants per chronotype group.

---

## Data preparation and summary statistics plan

Before any inferential tests, the dataset will be cleaned and described in a way that directly reflects the experimental design.

- **Step 1 – Filter valid observations**
  - Retain only rows with explicit consent (e.g., `"Yes I consent"` in the consent column).
  - Drop rows without a valid `Geometric Mean` and `Arithmetic Mean` JND estimate.
  - Remove obvious spreadsheet artefacts and summary rows (e.g., trailing rows with `#ERROR!` or empty entries).

- **Step 2 – Define participant identifier and repeated‑measures subset**
  - Use `User ID` as the primary participant ID where available.
  - Where `User ID` is not unique or is missing, disambiguate by combining `Name` and `User ID` (or, if needed, `Name` plus date/time stamp) to construct a stable participant identifier.
  - Confirm that each participant contributes at most one JND value per time‑of‑day level; if duplicates occur (e.g., multiple afternoon runs), choose a pre‑registered rule (e.g., average their JNDs within that time window or retain the first/most complete run).
  - Define the **core repeated‑measures analysis set** as all participants who have valid JND measurements for **all three** time‑of‑day levels (Morning, Afternoon, Evening). This subset will be used for the primary repeated‑measures ANOVA / mixed‑model tests.
  - Participants with only one or two time‑of‑day measurements will be retained for descriptive statistics and for mixed‑effects models that can handle missing cells, but not for the strict repeated‑measures ANOVA.

- **Step 3 – Encode experimental factors and covariates**
  - Map `When did you take the test?` into a factor `TimeOfDay` with levels:
    - `Morning`: Morning (8–10 AM)
    - `Afternoon`: Afternoon (4–6 PM)
    - `Evening`: Evening (10 PM–12 AM)
  - Encode `Chronotype` as a factor with levels `Morning`, `Night`, `Depends`.
  - Convert `Volume Intensity` into a numeric variable (strip `%` and cast to 0–100).
  - Parse the free‑text `Optional Notes` into a coarse `NoiseExposure` factor (e.g., `None`, `PublicTransport`, `LoudMusic`, `Other`), and optionally a binary `AnyLoudExposure` indicator.

- **Step 4 – Choose and transform the dependent variable**
  - Primary DV: **`Arithmetic Mean` JND (Hz)**, as the main psychoacoustic outcome of interest.
  - Secondary DV for robustness checks: `Geometric Mean` JND.
  - Due to the very large range and right‑skew of JND values (including clear outliers), apply a log transform:
    - $Y = \log_{10}(\text{JND})$ or $Y = \ln(\text{JND})$.
  - Inspect histograms and Q–Q plots of raw vs. log‑transformed JND to verify improved normality.

- **Step 5 – Descriptive statistics**
  - Compute, per `TimeOfDay`:
    - Number of unique participants and total observations.
    - Mean, median, standard deviation, interquartile range of raw JND and log‑JND.
  - Compute, per `TimeOfDay × Chronotype` (if sample size allows):
    - Mean and 95% confidence intervals of log‑JND.
  - Visualizations:
    - Boxplots or violin plots of log‑JND by `TimeOfDay`.
    - Spaghetti plots of within‑subject trajectories (each participant’s log‑JND across time‑of‑day levels), to visualize consistent improvements/declines.
    - Optional: colour‑code trajectories by chronotype or noise exposure level.

These summary statistics will indicate whether there is an apparent time‑of‑day trend and will guide decisions about outlier handling and model specification.

---

## ANOVA‑based inferential analysis plan

Given that most participants were measured repeatedly across the three time‑of‑day windows, an ANOVA framework that respects the within‑subject structure is appropriate.

### 1. Core model: within‑subject time‑of‑day effect

- **Design**: One‑factor repeated‑measures ANOVA (or, equivalently, a linear mixed‑effects model with random intercepts for participants) on log‑JND.
  - **Within‑subject factor**: `TimeOfDay` (Morning, Afternoon, Evening).
  - **Subject factor**: Participant ID (random effect).

- **Statistical model (mixed‑effects formulation)**:

  $$
  Y_{it} = \beta_0 + b_i + \beta_{\text{TimeOfDay}(t)} + \epsilon_{it},
  $$

  where:
  - $Y_{it}$ is log‑JND for participant $i$ at time‑of‑day level $t$,
  - $b_i \sim \mathcal{N}(0, \sigma_b^2)$ is a random intercept for participant $i$,
  - $\epsilon_{it} \sim \mathcal{N}(0, \sigma^2)$ is residual error,
  - $\beta_{\text{TimeOfDay}(t)}$ captures the fixed effect of time of day (with one level as reference).

- **Hypothesis test**:
  - Test the omnibus effect of `TimeOfDay`:
    - Repeated‑measures ANOVA: F‑test of the within‑subject factor.
    - Mixed model: Likelihood‑ratio test (full model vs. model without `TimeOfDay`) or F‑test on the fixed factor.
  - If significant, perform post‑hoc pairwise comparisons between time‑of‑day levels (Morning vs Afternoon, Morning vs Evening, Afternoon vs Evening), with multiple‑comparison correction (e.g., Holm–Bonferroni or Tukey for estimated marginal means).

- **Assumption checks**:
  - **Normality of residuals**: Inspect residual Q–Q plots and Shapiro–Wilk tests on within‑subject residuals; if strong deviations remain even after log transform, consider robust or non‑parametric alternatives (e.g., rank‑based repeated‑measures tests).
  - **Sphericity (for classical repeated‑measures ANOVA)**: Use Mauchly’s test; if violated, apply Greenhouse–Geisser or Huynh–Feldt corrections to degrees of freedom and p‑values.
  - **Influence diagnostics**: Identify participants whose JNDs are extreme outliers even on the log scale (e.g., > 3 SD from the mean). Run sensitivity analyses with and without those participants to check robustness of the time‑of‑day effect.

### 2. Extended model: chronotype interaction and covariates

To connect more closely to individual differences that might align with raga‑time intuitions, extend the model to include chronotype and key confounding variables.

- **Design**: Mixed‑effects ANOVA / linear mixed‑effects model with:
  - Within‑subject factor: `TimeOfDay` (3 levels).
  - Between‑subject factor: `Chronotype` (Morning / Night / Depends).
  - Covariates: `Volume` (continuous), `AnyLoudExposure` (binary) or `NoiseExposure` (categorical).

- **Model**:

  $$
  Y_{it} = \beta_0 + b_i + \beta_{\text{TimeOfDay}(t)} + \beta_{\text{Chronotype}(i)} + \beta_{\text{TimeOfDay} \times \text{Chronotype}} + \gamma_1 \text{Volume}_{it} + \gamma_2 \text{NoiseExposure}_{it} + \epsilon_{it},
  $$

  where $b_i$ is a random intercept for participant $i$.

- **Hypothesis tests**:
  - Main effect of `TimeOfDay` (as above).
  - Main effect of `Chronotype`.
  - Interaction `TimeOfDay × Chronotype`:
    - Tests whether the time‑of‑day pattern differs systematically across Morning, Night, and Depends groups, consistent with chronobiological expectations (e.g., Morning types having their best performance earlier in the day).
  - Effects of covariates:
    - `Volume`: whether higher playback level systematically improves or worsens discrimination.
    - `NoiseExposure`: whether recent loud‑sound exposure is associated with elevated JNDs.

- **Post‑hoc analyses**:
  - Plot estimated marginal means of log‑JND for each `TimeOfDay × Chronotype` cell with confidence intervals.
  - If the interaction is significant, perform simple‑effects tests (e.g., time‑of‑day contrasts within each chronotype group, or chronotype contrasts within each time‑of‑day).

---

## Potential confounding factors and how they are addressed

- **Chronotype vs. testing time alignment**
  - Musicological theory suggests that “right” or “wrong” times may be person‑ and culture‑dependent. Chronotype may shift a participant’s optimal performance window.
  - Addressed by explicitly including `Chronotype` and the `TimeOfDay × Chronotype` interaction in the extended model, and by inspecting within‑participant trajectories stratified by chronotype.

- **Playback volume differences**
  - Different volume intensities may alter audibility and perceived loudness, which in turn could affect discrimination thresholds.
  - Addressed by:
    - Including `Volume` as a covariate.
    - Descriptively checking whether volume distributions differ across time‑of‑day levels (e.g., are night tests typically softer or louder?).

- **Recent loud‑sound exposure and temporary threshold shifts**
  - Participants sometimes report train rides, loud music, or other noisy contexts, which can induce short‑term hearing fatigue and elevated thresholds.
  - Addressed by:
    - Coding noise exposure from the notes and including it as a covariate.
    - Running sensitivity analyses excluding sessions with clear “high exposure” labels (e.g., trains, concerts, loud music for long durations).

- **Order/practice effects**
  - If most participants followed the same time‑of‑day sequence (e.g., Morning → Afternoon → Evening), improvements or deteriorations could reflect learning or fatigue rather than circadian factors.
  - Addressed by:
    - Extracting ordering information from timestamps and summarizing the order in which time‑of‑day conditions were completed.
    - If feasible, including “session index” (1st, 2nd, 3rd session for each participant) as an additional within‑subject covariate, or at least verifying descriptively that the time‑of‑day effect is not fully explained by monotonic learning.

- **Device and environment heterogeneity**
  - The study likely involved varied listening setups (earbuds, headphones, speakers) and environments; these are only partially captured in free‑text notes.
  - Address by:
    - Acknowledging this as a limitation in interpretation.
    - Where information is present in notes (e.g., “headphones”), optionally coding a coarse device/environment variable and exploring it descriptively.

- **Unequal sample sizes and missing time‑of‑day cells**
  - Not all participants may have completed all three time‑of‑day measurements.
  - Address by:
    - Using mixed‑effects models that can handle missing cells more flexibly than strict repeated‑measures ANOVA.
    - For the classical repeated‑measures ANOVA, restricting to participants with complete Morning, Afternoon, and Evening data and reporting the effective N.

- **Extreme outliers**
  - Some JND values are orders of magnitude larger than others, which can dominate variance and violate model assumptions.
  - Address by:
    - Applying log transformation as the primary step.
    - Identifying highly influential data points using standardized residuals and influence measures.
    - Reporting results both with and without these extreme cases and treating them cautiously in interpretation (e.g., possible misunderstanding of the task, distractions, or technical issues).

---

## Planned analysis sequence

1. **Clean and structure the dataset** according to the rules in the data‑preparation section, define participant IDs, and construct the `TimeOfDay`, `Chronotype`, `Volume`, and noise‑exposure variables.
2. **Compute and visualize summary statistics**:
   - Per time‑of‑day and chronotype, for both raw and log‑JND.
   - Within‑subject trajectories across the three time‑of‑day windows.
3. **Fit the core within‑subject model**:
   - Repeated‑measures ANOVA or mixed‑effects model on log‑JND with `TimeOfDay` as the within‑subject factor.
   - Check assumptions and report the omnibus effect plus corrected post‑hoc comparisons.
4. **Fit the extended model**:
   - Add `Chronotype` and its interaction with `TimeOfDay`, plus `Volume` and noise‑exposure covariates.
   - Test for the interaction and interpret in relation to the musicological hypothesis about time‑of‑day‑specific acuity.
5. **Sensitivity and robustness checks**:
   - Repeat key analyses on:
     - Subsets excluding high‑exposure sessions.
     - Subsets excluding extreme outliers.
     - Arithmetic‑mean JND as DV instead of geometric‑mean JND.
6. **Interpretation in a raga‑theoretical context**:
   - Relate any observed time‑of‑day modulation in JND (and chronotype interactions) back to time‑specific raga practice, discussing whether pitch discrimination is measurably sharper in particular praharas for this sample and what that implies (or does not yet prove) about the perceptual underpinnings of raga‑time assignments.
---
