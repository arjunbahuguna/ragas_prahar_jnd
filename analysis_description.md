# Statistical Analysis of Pitch JND Across Praharas (Time-of-Day Segments)

## 1. Experimental Design

### 1.1 Motivation

Indian raga theory prescribes specific ragas to particular **praharas** (time-of-day segments), implying that perceptual and affective states of listeners co-vary with time of day. This study translates that musicological claim into a psychoacoustic prediction: **does pitch discrimination acuity — measured as the just noticeable difference (JND) for pure-tone frequency — systematically change across the day?**

### 1.2 Experimental Structure

The experiment follows a **within-subject, repeated-measures design** in which each participant completes a **2-down 1-up adaptive staircase** procedure for frequency discrimination at up to three time-of-day windows:

| Level | Clock window |
|-------|-------------|
| Morning | 8:00–10:00 AM |
| Afternoon | 4:00–6:00 PM |
| Evening | 10:00 PM–12:00 AM |

These windows approximate distinct praharas in the traditional Indian day–night cycle.

The staircase converges on the listener's JND (in Hz), reported as both an **arithmetic mean** and a **geometric mean** of reversal values. The arithmetic mean is used as the primary dependent variable.

### 1.3 Factors and Covariates

| Variable | Role | Type | Levels / Range |
|----------|------|------|----------------|
| TimeOfDay | Within-subject factor | Categorical (3 levels) | Morning, Afternoon, Evening |
| Chronotype | Between-subject factor | Categorical (3 levels) | Morning, Night, Depends |
| Volume | Covariate | Continuous (0–100) | Playback slider percentage |
| AnyLoudExposure | Covariate | Binary | 0 = no recent loud exposure, 1 = yes |
| Participant | Grouping / random factor | Categorical | Unique per person |

---

## 2. Data Preprocessing

### 2.1 Consent Filtering

Only rows containing explicit consent (`"Yes I consent"`) are retained. Three early pilot rows (Ariana, Oriol) that predate the consent field are excluded from inferential analysis.

### 2.2 Name Standardisation

Participants entered their names in varying formats across sessions (e.g., `"Ariana Pereira"`, `"Ariana"`, `"Carlos Pereira"`, `"Carlos pereira"`). A deterministic mapping reduces every name to a canonical **first-name-only** form:

$$
\text{Name}_{\text{standardised}} = f(\text{Name}_{\text{raw}})
$$

where $f$ is a lookup table:

| Raw variants | Standardised |
|-------------|-------------|
| Ariana Pereira, Ariana | Ariana |
| Oriol Freixa Dachs | Oriol |
| Anna Dachs Casafont | Anna |
| Josep Freixa Guitart | Josep |
| Carlos Pereira, Carlos pereira | Carlos |
| Avina Pereira, Avina Pereira  | Avina |
| Inés, Inés Broto Clemente | Inés |
| Hemanth Ramia Jegdish | Hemanth |
| Federico De Lellis | Federico |
| Yuhang Wu | Yuhang |
| Victoria , Jenny , Marla , Jessica , Rafael , Fernando  | Victoria, Jenny, Marla, Jessica, Rafael, Fernando |

Leading and trailing whitespace is also stripped.

### 2.3 Numeric Conversion

Some JND and volume entries use European decimal notation (comma as decimal separator, e.g., `"1,937"` instead of `"1.937"`). A conversion function replaces commas with dots and casts to `float`:

$$
\text{to\_num}(x) = \texttt{float}\bigl(\texttt{str}(x).\texttt{replace}(\text{","}, \text{"."})\bigr)
$$

Percentage signs (`%`) are stripped from the volume column similarly.

### 2.4 Outlier Removal (IQR Method)

Before any modelling, univariate outliers in both **JND_arith** and **JND_geo** are identified and removed using the **1.5 × IQR rule** (Tukey's fences). For a variable $X$:

$$
Q_1 = X_{(0.25)}, \quad Q_3 = X_{(0.75)}, \quad \text{IQR} = Q_3 - Q_1
$$

$$
\text{Lower fence} = Q_1 - 1.5 \times \text{IQR}
$$

$$
\text{Upper fence} = Q_3 + 1.5 \times \text{IQR}
$$

A row is **retained** if and only if:

$$
Q_1 - 1.5 \cdot \text{IQR} \;\leq\; X_{\text{arith}} \;\leq\; Q_3 + 1.5 \cdot \text{IQR}
$$

$$
\quad\text{AND}\quad Q_1 - 1.5 \cdot \text{IQR} \;\leq\; X_{\text{geo}} \;\leq\; Q_3 + 1.5 \cdot \text{IQR}
$$

In the present data this removed **7 of 55** consented observations (12.7%), leaving **48 rows** for analysis. The removed rows correspond to extremely large JNDs (e.g., 128 Hz, 91 Hz, 740 Hz) that likely reflect misunderstandings of the task, attentional lapses, or equipment miscalibrations.

### 2.5 Log Transformation

JND values are right-skewed and span orders of magnitude (from ~1 Hz to ~50 Hz after outlier removal). Following standard psychoacoustic practice, a base-10 logarithmic transform is applied:

$$
Y_{it} = \log_{10}\!\bigl(\text{JND}_{\text{arith},\,it}\bigr)
$$

where $i$ indexes the participant and $t$ indexes the time-of-day condition.

**Rationale:** Psychophysical thresholds are better described by multiplicative (Weber-like) noise than additive noise. On the log scale:

- The distribution is more symmetric and closer to normal.
- Variance is more homogeneous across conditions (homoscedasticity).
- Coefficients have a natural ratio interpretation: a coefficient of $+\beta$ means the JND is multiplied by a factor of $10^{\beta}$.

---

## 3. Summary Statistics

After preprocessing, data are grouped by **TimeOfDay** and by **TimeOfDay × Chronotype**. For each cell, the following statistics are reported:

- $n$: number of observations
- $\bar{Y}$: sample mean of $\log_{10}(\text{JND})$
- $\tilde{Y}$: sample median
- $s$: sample standard deviation
- $\min(Y)$, $\max(Y)$

Observed cell means after outlier removal (48 rows, 16 per TimeOfDay):

| TimeOfDay | $n$ | Mean $\bar{Y}$ | Median $\tilde{Y}$ | SD $s$ |
|-----------|-----|----------------|---------------------|--------|
| Morning | 16 | ≈ 0.80 | ≈ 0.67 | ≈ 0.46 |
| Afternoon | 16 | ≈ 0.71 | ≈ 0.53 | ≈ 0.46 |
| Evening | 16 | ≈ 0.72 | ≈ 0.55 | ≈ 0.55 |

These raw means suggest only small differences across time-of-day levels, with wide within-condition variability.

---

## 4. Model 1: Repeated-Measures ANOVA

### 4.1 Design

The classical repeated-measures ANOVA tests whether the population means of $Y$ differ across TimeOfDay levels, treating each participant as their own control. This requires the **complete-case subset**: participants who provided valid JND measurements at all three time points.

For each complete participant $i$, if they contributed multiple runs at the same TimeOfDay level, we first average within condition:

$$
\bar{Y}_{it} = \frac{1}{n_{it}} \sum_{j=1}^{n_{it}} Y_{itj}
$$

### 4.2 Statistical Model

$$
\bar{Y}_{it} = \mu + \alpha_t + s_i + \varepsilon_{it}
$$

where:

- $\mu$ is the grand mean,
- $\alpha_t$ is the fixed effect of TimeOfDay level $t$, subject to the constraint $\sum_{t} \alpha_t = 0$,
- $s_i$ is the participant-specific deviation (blocking factor),
- $\varepsilon_{it} \sim \mathcal{N}(0, \sigma^2)$ is the residual error.

### 4.3 Hypothesis

$$
H_0\!: \alpha_{\text{Morning}} = \alpha_{\text{Afternoon}} = \alpha_{\text{Evening}} = 0
$$

$$
H_1\!: \exists\, t : \alpha_t \neq 0
$$

The omnibus $F$-statistic is:

$$
F = \frac{MS_{\text{TimeOfDay}}}{MS_{\text{error}}}
$$

where $MS_{\text{TimeOfDay}}$ is the mean square for the time-of-day factor and $MS_{\text{error}}$ is the within-subject residual mean square.

### 4.4 Result

In the current dataset, the repeated-measures ANOVA **could not be fitted** due to collinearity. After outlier removal, only a handful of participants have complete data at all three time points, and some had identical participant–condition assignments that produced a singular design matrix. This motivates the use of a mixed-effects model, which does not require complete cases.

---

## 5. Model 2: Linear Mixed-Effects Model (LMM)

### 5.1 Why a Mixed Model?

The LMM overcomes two limitations of the repeated-measures ANOVA:

1. **Incomplete data**: Not every participant completed all three time windows. The LMM uses all available observations (even from participants with 1 or 2 time points) by partially pooling information through the random-effects structure.
2. **Covariates and interactions**: The LMM can simultaneously include between-subject factors (Chronotype), continuous covariates (Volume), and their interactions with TimeOfDay.

### 5.2 Model Specification

The full model, in Wilkinson–Rogers formula notation, is:

```
logJND ~ TimeOfDay * Chronotype + Volume_num + AnyLoudExposure
```

Expanding the interaction and dummy-coding (with Morning as the reference level for both TimeOfDay and Chronotype), the model is:

$$
Y_{it} = \beta_0 + b_i + \beta_1 \, \mathbb{1}[t = \text{Aft}] + \beta_2 \, \mathbb{1}[t = \text{Eve}]
$$

$$
\quad + \beta_3 \, \mathbb{1}[c_i = \text{Morn}] + \beta_4 \, \mathbb{1}[c_i = \text{Night}]
$$

$$
\quad + \beta_5 \, \mathbb{1}[t = \text{Aft}] \cdot \mathbb{1}[c_i = \text{Morn}]
$$

$$
\quad + \beta_6 \, \mathbb{1}[t = \text{Eve}] \cdot \mathbb{1}[c_i = \text{Morn}]
$$

$$
\quad + \beta_7 \, \mathbb{1}[t = \text{Aft}] \cdot \mathbb{1}[c_i = \text{Night}]
$$

$$
\quad + \beta_8 \, \mathbb{1}[t = \text{Eve}] \cdot \mathbb{1}[c_i = \text{Night}]
$$

$$
\quad + \gamma_1 \, \text{Volume}_{it} + \gamma_2 \, \text{AnyLoudExposure}_{it} + \varepsilon_{it}
$$

where:

- $\mathbb{1}[\cdot]$ are indicator (dummy) functions,
- $c_i$ is the chronotype of participant $i$ (time-invariant),
- $b_i \sim \mathcal{N}(0, \sigma_b^2)$ is a **random intercept** for participant $i$,
- $\varepsilon_{it} \sim \mathcal{N}(0, \sigma^2)$ is the observation-level residual.

### 5.3 Interpretation of Coefficients

| Coefficient | Interpretation |
|-------------|---------------|
| $\beta_0$ | Mean logJND for the reference cell: Depends-type participants, Morning TimeOfDay, Volume = 0, no loud exposure |
| $\beta_1$ | Shift in logJND from Morning → Afternoon, for Depends-type participants |
| $\beta_2$ | Shift in logJND from Morning → Evening, for Depends-type participants |
| $\beta_3$ | Offset of Morning-type vs Depends-type participants, at Morning TimeOfDay |
| $\beta_4$ | Offset of Night-type vs Depends-type participants, at Morning TimeOfDay |
| $\beta_5$ | **Interaction**: how much the Morning→Afternoon shift differs for Morning-type relative to Depends-type |
| $\beta_6$ | **Interaction**: how much the Morning→Evening shift differs for Morning-type relative to Depends-type |
| $\beta_7$ | **Interaction**: how much the Morning→Afternoon shift differs for Night-type relative to Depends-type |
| $\beta_8$ | **Interaction**: how much the Morning→Evening shift differs for Night-type relative to Depends-type |
| $\gamma_1$ | Change in logJND per 1-unit increase in volume slider (%) |
| $\gamma_2$ | Shift in logJND for sessions with recent loud-environment exposure |

**Back-transforming coefficients:** since $Y = \log_{10}(\text{JND})$, a coefficient $\hat{\beta}$ corresponds to a multiplicative factor:

$$
\text{JND ratio} = 10^{\hat{\beta}}
$$

For example, $\hat{\beta} = +0.22$ means the JND is $10^{0.22} \approx 1.66$ times larger (66% worse pitch discrimination).

### 5.4 Random-Effects Structure

The random intercept captures the fact that each participant has a **person-specific baseline acuity**:

$$
b_i \sim \mathcal{N}(0, \sigma_b^2)
$$

$$
\text{Effective intercept for person } i = \beta_0 + b_i
$$

This accounts for the correlation among repeated observations from the same participant without requiring balanced data.

### 5.5 Estimation

The model is fitted by **maximum likelihood (ML)** using the L-BFGS-B optimiser (limited-memory Broyden–Fletcher–Goldfarb–Shanno with bound constraints). ML estimation maximises the marginal log-likelihood:

$$
\ell(\boldsymbol{\beta}, \sigma_b^2, \sigma^2) = \log \int \prod_{i=1}^{N} \prod_{t} f(Y_{it} \mid b_i, \boldsymbol{\beta}, \sigma^2) \; \phi(b_i; 0, \sigma_b^2) \; db_i
$$

where $f$ is the normal density for the observation-level model and $\phi$ is the normal density for the random intercept. The integral is available in closed form for the linear case.

### 5.6 Results

**Full model (N = 48, 45 groups):**

| Term | $\hat{\beta}$ | SE | $z$ | $p$ |
|------|--------------|-----|------|------|
| Intercept | −0.000 | 0.187 | −0.001 | 0.999 |
| TimeOfDay[Afternoon] | 0.066 | 0.185 | 0.355 | 0.722 |
| TimeOfDay[Evening] | 0.221 | 0.000 | 3430.6 | <0.001 |
| Chronotype[Morning] | 0.262 | 0.213 | 1.229 | 0.219 |
| Chronotype[Night] | 0.465 | 0.172 | 2.706 | 0.007 |
| Afternoon × Morning-type | −0.082 | 0.313 | −0.263 | 0.792 |
| Evening × Morning-type | −0.100 | 0.268 | −0.374 | 0.708 |
| Afternoon × Night-type | −0.311 | 0.185 | −1.683 | 0.092 |
| Evening × Night-type | −0.650 | 0.036 | −18.26 | <0.001 |
| Volume | 0.013 | 0.004 | 3.779 | <0.001 |
| AnyLoudExposure | −0.131 | 0.223 | −0.589 | 0.556 |
| $\hat{\sigma}_b^2$ (Group Var) | 0.159 | — | — | — |

**Key observations:**

- **Volume** is a significant predictor ($p < 0.001$): higher playback volume is associated with slightly larger (worse) logJND. Each 1% increase in volume corresponds to a factor of $10^{0.013} \approx 1.03$ (≈3% increase in JND).
- **Night-type chronotype** shows significantly higher JND overall ($\hat{\beta} = 0.465$, $p = 0.007$), corresponding to JNDs that are $10^{0.465} \approx 2.9$ times larger than Depends-type participants at the Morning reference time.
- The **Evening × Night-type interaction** is highly significant ($p < 0.001$, $\hat{\beta} = -0.650$), indicating that Night-type participants show a large *improvement* (lower JND) in the evening relative to what the main effects would predict. This is consistent with the chronobiological expectation that Night-type listeners have sharpened perception in the evening.
- The **TimeOfDay[Evening] main effect** appears significant in the full model, but with an anomalously small standard error (SE ≈ 0.000), which indicates a near-singular covariance structure for that term — a convergence artefact attributable to the small sample size.
- **AnyLoudExposure** is not significant ($p = 0.556$).

### 5.7 Sensitivity Analysis: Residual-Based Outlier Exclusion

After fitting, standardised residuals are computed:

$$
r_{it} = Y_{it} - \hat{Y}_{it}
$$

$$
z_{it} = \frac{r_{it} - \bar{r}}{s_r}
$$

Observations with $|z_{it}| > 3$ are flagged as **extreme residuals** and the model is refitted without them. In this dataset, **2 observations** were flagged.

**Sensitivity model (N = 46, 45 groups):**

| Term | $\hat{\beta}$ | SE | $z$ | $p$ |
|------|--------------|-----|------|------|
| Intercept | 0.089 | 0.217 | 0.411 | 0.681 |
| TimeOfDay[Afternoon] | −0.072 | 0.220 | −0.327 | 0.744 |
| TimeOfDay[Evening] | −0.020 | 0.214 | −0.096 | 0.924 |
| Chronotype[Morning] | 0.130 | 0.242 | 0.536 | 0.592 |
| Chronotype[Night] | 0.219 | 0.224 | 0.974 | 0.330 |
| Afternoon × Morning-type | 0.053 | 0.332 | 0.159 | 0.874 |
| Evening × Morning-type | 0.145 | 0.341 | 0.426 | 0.670 |
| Afternoon × Night-type | −0.174 | 0.220 | −0.791 | 0.429 |
| Evening × Night-type | −0.051 | 0.347 | −0.147 | 0.883 |
| Volume | 0.015 | 0.004 | 4.051 | <0.001 |
| AnyLoudExposure | −0.116 | 0.221 | −0.523 | 0.601 |
| $\hat{\sigma}_b^2$ (Group Var) | 0.155 | — | — | — |

After removing 2 extreme residuals, **no TimeOfDay or Chronotype effects remain significant**. Only **Volume** ($p < 0.001$) persists as a reliable predictor. The previously significant Night-type and Evening × Night-type effects disappear entirely, demonstrating that the full-model results were **highly sensitive to a small number of influential observations**.

---

## 6. Diagnostics and Limitations

### 6.1 Small Sample Size

With only 48 observations across 45 unique participants (mean group size ≈ 1.1), the random-intercept variance $\sigma_b^2$ is **poorly estimable**. Most participants contribute only 1 observation, which means:

- The random intercept for those participants is essentially just the residual.
- The model cannot distinguish within-person from between-person variance reliably.
- Standard errors for some coefficients may be unreliable (as evidenced by the anomalously small SE for TimeOfDay[Evening] in the full model).

### 6.2 Convergence Artefacts

The full model reports a residual scale of $\approx 0.0000$ and a Group Variance SE of $\approx 2846$, indicating near-boundary convergence. In such cases, the Wald $z$-tests and $p$-values should be interpreted with caution.

### 6.3 Repeated-Measures ANOVA Failure

The classical RM-ANOVA requires all participants to have exactly one observation per condition. After outlier removal, the subset of "complete" participants (those with all three time-of-day levels) was too small or had collinear predictors, causing a singular design matrix. The LMM provides a more robust alternative in such settings.

### 6.4 Recommendations for Future Work

- **Increase sample size**: A power analysis suggests that detecting a medium effect size ($f = 0.25$) in a 3-level within-subject design at $\alpha = 0.05$ and power $= 0.80$ requires approximately 28 complete participants (i.e., 84 total observations with 3 per participant).
- **Ensure complete repeated measures**: Each participant should ideally be tested at all three time windows to fully leverage the within-subject design.
- **Standardise listening conditions**: Control or record device type, ambient noise, and calibrate playback levels to reduce uncontrolled variance.

---

## 7. Conclusion

The analysis pipeline proceeds as:

$$
\text{Raw CSV} \;\xrightarrow{\text{consent filter}}\; \xrightarrow{\text{name standardisation}}\; \xrightarrow{\text{numeric conversion}}\; \xrightarrow{\text{IQR outlier removal}}\; \xrightarrow{\log_{10}}\; Y_{it}
$$

$$
Y_{it} \;\longrightarrow\; \text{LMM: } Y_{it} = \mathbf{X}_{it}\boldsymbol{\beta} + b_i + \varepsilon_{it}
$$

The full mixed-effects model suggests a possible **Evening × Night-type interaction** consistent with the hypothesis that chronotype modulates the time-of-day effect on pitch acuity. However, this result is **not robust**: it disappears after removing just 2 influential observations. The only consistently significant predictor across all models is **playback volume**.

Given the current sample size ($N = 48$, most participants measured only once), **the data are insufficient to reliably confirm or reject** the musicologically motivated hypothesis that pitch JND varies across praharas. A larger, balanced, repeated-measures study is needed.
