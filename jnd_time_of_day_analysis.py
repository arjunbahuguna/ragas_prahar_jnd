import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.anova import AnovaRM
from statsmodels.formula.api import mixedlm
import os
import matplotlib.pyplot as plt
import seaborn as sns


# ---------------------------------------------------------------------
# 1. Load and clean the data
# ---------------------------------------------------------------------

os.makedirs("img", exist_ok=True)

raw = pd.read_csv("JND by Time of Day (respostes) - Respostes al formulari 1.csv")

# Rename columns to simpler names (adjust if column names differ slightly)
raw = raw.rename(
    columns={
        "By completing this form, you are consenting to sharing your data with the research team as described above. ": "Consent",
        "Are you a Morning or Night Person?": "Chronotype",
        "Volume Intensity (Approximate percentage set in the slider). Example: 50": "Volume",
        "When did you take the test?": "When",
        "User ID": "UserID",
        "Geometric Mean": "JND_geo",
        "Arithmetic Mean": "JND_arith",
        "Optional Notes - Did you spend time in a loud environment today such as at a concert or in a train station? If so, describe the setting and the duration you were there:": "Notes",
    }
)

# Keep only rows with explicit consent and non-missing JND
df = raw.loc[raw["Consent"].fillna("").str.contains("Yes", case=False)]
df = df.dropna(subset=["JND_arith", "JND_geo"])

# Drop obvious artefact rows (e.g. trailing summary / #ERROR! rows)
df = df[~df["Name"].fillna("").eq("Name")]
df = df[~df["JND_arith"].astype(str).str.contains("#ERROR!", na=False)]

# -----------------------------------------------------------------
# 1b. Standardise participant names to first-name-only
# -----------------------------------------------------------------
name_map = {
    "Oriol Freixa Dachs": "Oriol",
    "Ariana Pereira": "Ariana",
    "Anna Dachs Casafont": "Anna",
    "Josep Freixa Guitart": "Josep",
    "Carlos Pereira": "Carlos",
    "Carlos pereira": "Carlos",
    "Avina Pereira": "Avina",
    "Avina Pereira ": "Avina",
    "Inés Broto Clemente": "Inés",
    "Inés": "Inés",
    "Hemanth Ramia Jegdish": "Hemanth",
    "Federico De Lellis": "Federico",
    "Yuhang Wu": "Yuhang",
    "Victoria ": "Victoria",
    "Marla ": "Marla",
    "Jessica ": "Jessica",
    "Jenny ": "Jenny",
    "Rafael ": "Rafael",
    "Fernando ": "Fernando",
}
df["Name"] = df["Name"].str.strip().replace(name_map)


def to_num(x):
    if pd.isna(x):
        return np.nan
    s = str(x).replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return np.nan


df["JND_arith"] = df["JND_arith"].apply(to_num)
df["JND_geo"] = df["JND_geo"].apply(to_num)

# -----------------------------------------------------------------
# 1c. Remove outliers using 1.5×IQR rule on both JND columns
# -----------------------------------------------------------------
def iqr_mask(series: pd.Series) -> pd.Series:
    """Return a boolean mask that is True for non-outlier rows."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    return (series >= Q1 - 1.5 * IQR) & (series <= Q3 + 1.5 * IQR)

n_before = len(df)
mask_arith = iqr_mask(df["JND_arith"].dropna()).reindex(df.index, fill_value=True)
mask_geo = iqr_mask(df["JND_geo"].dropna()).reindex(df.index, fill_value=True)
df = df[mask_arith & mask_geo].copy()
print(f"Outlier removal (1.5×IQR): {n_before} → {len(df)} rows "
      f"({n_before - len(df)} removed)")


def to_volume(x):
    if pd.isna(x):
        return np.nan
    s = str(x).replace("%", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


df["Volume_num"] = df["Volume"].apply(to_volume)

# ---------------------------------------------------------------------
# 2. Factor coding and participant ID
# ---------------------------------------------------------------------

mapping_time = {
    "Morning (8-10AM)": "Morning",
    "Morning (8-10 AM)": "Morning",
    "Afternoon (4-6PM)": "Afternoon",
    "Afternoon (4-6 PM)": "Afternoon",
    "Evening (10PM-12AM)": "Evening",
    "Evening (10PM-12 AM)": "Evening",
}
df["TimeOfDay"] = df["When"].map(mapping_time)

df["Chronotype"] = df["Chronotype"].astype("category")

df["UserID"] = df["UserID"].astype(str).str.strip()
df["Participant"] = np.where(df["UserID"].isin(["", "nan"]), df["Name"], df["UserID"])
df["Participant"] = df["Participant"].astype("category")


def any_loud(notes: object) -> int:
    if pd.isna(notes):
        return 0
    s = str(notes).lower()
    keywords = ["train", "metro", "concert", "loud", "public transport", "station"]
    return int(any(k in s for k in keywords))


df["AnyLoudExposure"] = df["Notes"].apply(any_loud)

# ---------------------------------------------------------------------
# 3. Define analysis variables (arithmetic-mean JND and log-transform)
# ---------------------------------------------------------------------

df = df.dropna(subset=["JND_arith"])
df["logJND"] = np.log10(df["JND_arith"])

# ---------------------------------------------------------------------
# 4. Summary statistics
# ---------------------------------------------------------------------

sns.set_theme(style="whitegrid")

summary_time = (
    df.groupby("TimeOfDay", observed=True)[["JND_arith", "logJND"]]
    .agg(["count", "mean", "median", "std", "min", "max"])
)

summary_time_chrono = df.groupby(
    ["TimeOfDay", "Chronotype"], observed=True
)["logJND"].agg(["count", "mean", "std"])

print("Summary by TimeOfDay")
print(summary_time)
print("\nSummary by TimeOfDay × Chronotype")
print(summary_time_chrono)

# Save summary tables for reuse
summary_time.to_csv("img/summary_by_timeofday.csv")
summary_time_chrono.to_csv("img/summary_by_timeofday_chronotype.csv")

# ---------------------------------------------------------------------
# 4a. Figures: distribution checks and main effects
# ---------------------------------------------------------------------

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
sns.histplot(df["JND_arith"], bins=30, kde=True, ax=ax[0])
ax[0].set_title("Arithmetic-mean JND (raw)")
ax[0].set_xlabel("JND (Hz)")
ax[0].set_ylabel("Count")
sns.histplot(df["logJND"], bins=30, kde=True, ax=ax[1])
ax[1].set_title("Arithmetic-mean JND (log10)")
ax[1].set_xlabel("log10(JND)")
ax[1].set_ylabel("Count")
fig.tight_layout()
fig.savefig("img/distributions_raw_vs_log.png", dpi=200)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
order = ["Morning", "Afternoon", "Evening"]
sns.violinplot(data=df, x="TimeOfDay", y="logJND", order=order, inner=None, ax=ax)
sns.boxplot(
    data=df,
    x="TimeOfDay",
    y="logJND",
    order=order,
    width=0.25,
    showcaps=True,
    boxprops={"facecolor": "white", "zorder": 3},
    showfliers=False,
    ax=ax,
)
ax.set_title("log10(JND) by Time of Day")
ax.set_xlabel("Time of day (prahar approximation)")
ax.set_ylabel("log10(Arithmetic-mean JND)")
fig.tight_layout()
fig.savefig("img/logjnd_by_timeofday_violin_box.png", dpi=200)
plt.close(fig)

# ---------------------------------------------------------------------
# 5. Core repeated-measures ANOVA (participants with all three times)
# ---------------------------------------------------------------------

df_rm = df.dropna(subset=["TimeOfDay"]).copy()

counts = df_rm.groupby("Participant", observed=True)["TimeOfDay"].nunique()
complete_ids = counts[counts == 3].index
df_complete = df_rm[df_rm["Participant"].isin(complete_ids)].copy()

df_complete["TimeOfDay"] = pd.Categorical(
    df_complete["TimeOfDay"],
    categories=["Morning", "Afternoon", "Evening"],
    ordered=True,
)

try:
    # AnovaRM expects exactly one value per subject×condition.
    df_complete_agg = (
        df_complete.groupby(["Participant", "TimeOfDay"], observed=True)["logJND"]
        .mean()
        .reset_index()
    )

    anova_rm = AnovaRM(
        data=df_complete_agg,
        depvar="logJND",
        subject="Participant",
        within=["TimeOfDay"],
    ).fit()

    print("\nRepeated-measures ANOVA (TimeOfDay on logJND)")
    print(anova_rm)
except ValueError as e:
    print("\nRepeated-measures ANOVA could not be fit:", e)

# Spaghetti plot (within-subject trajectories) for complete participants
if len(complete_ids) > 0:
    fig, ax = plt.subplots(figsize=(7, 4))
    for pid, g in df_complete_agg.groupby("Participant", observed=True):
        g = g.sort_values("TimeOfDay")
        ax.plot(g["TimeOfDay"], g["logJND"], alpha=0.35, linewidth=1)
    ax.set_title("Within-subject trajectories (complete cases)")
    ax.set_xlabel("Time of day")
    ax.set_ylabel("log10(Arithmetic-mean JND)")
    fig.tight_layout()
    fig.savefig("img/spaghetti_complete_participants.png", dpi=200)
    plt.close(fig)

# ---------------------------------------------------------------------
# 6. Mixed-effects model with Chronotype and covariates
# ---------------------------------------------------------------------

df_mixed = df_rm.dropna(subset=["logJND"]).copy()

df_mixed["TimeOfDay"] = pd.Categorical(
    df_mixed["TimeOfDay"],
    categories=["Morning", "Afternoon", "Evening"],
    ordered=True,
)
df_mixed["Chronotype"] = df_mixed["Chronotype"].cat.remove_unused_categories()

formula = "logJND ~ TimeOfDay * Chronotype + Volume_num + AnyLoudExposure"

md = mixedlm(
    formula=formula,
    data=df_mixed,
    groups=df_mixed["Participant"],
)
mixed_res = md.fit(reml=False, method="lbfgs")

print("\nMixed-effects model with TimeOfDay × Chronotype, Volume, AnyLoudExposure")
print(mixed_res.summary())

# Interaction plot (estimated mean ± CI visually via pointplot)
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.pointplot(
    data=df_mixed,
    x="TimeOfDay",
    y="logJND",
    hue="Chronotype",
    order=order,
    dodge=0.25,
    errorbar=("ci", 95),
    ax=ax,
)
ax.set_title("Mean log10(JND) by TimeOfDay × Chronotype (95% CI)")
ax.set_xlabel("Time of day")
ax.set_ylabel("log10(Arithmetic-mean JND)")
ax.legend(title="Chronotype", bbox_to_anchor=(1.02, 1), loc="upper left")
fig.tight_layout()
fig.savefig("img/interaction_timeofday_chronotype_pointplot.png", dpi=200)
plt.close(fig)

# Volume relationship plot
fig, ax = plt.subplots(figsize=(7, 4))
sns.regplot(
    data=df_mixed,
    x="Volume_num",
    y="logJND",
    scatter_kws={"alpha": 0.6},
    line_kws={"color": "black"},
    ax=ax,
)
ax.set_title("Volume vs log10(JND)")
ax.set_xlabel("Volume slider (%)")
ax.set_ylabel("log10(Arithmetic-mean JND)")
fig.tight_layout()
fig.savefig("img/volume_vs_logjnd_regplot.png", dpi=200)
plt.close(fig)

# ---------------------------------------------------------------------
# 7. Simple outlier diagnostics and sensitivity analysis
# ---------------------------------------------------------------------

df_mixed["resid"] = mixed_res.resid
resid_std = (df_mixed["resid"] - df_mixed["resid"].mean()) / df_mixed["resid"].std(
    ddof=1
)
df_mixed["is_outlier"] = (np.abs(resid_std) > 3).astype(int)

print("\nNumber of extreme residuals (|z| > 3):", df_mixed["is_outlier"].sum())

# Residual distribution plot
fig, ax = plt.subplots(figsize=(7, 4))
sns.histplot(df_mixed["resid"], bins=25, kde=True, ax=ax)
ax.set_title("Mixed model residuals")
ax.set_xlabel("Residual")
ax.set_ylabel("Count")
fig.tight_layout()
fig.savefig("img/mixed_model_residuals_hist.png", dpi=200)
plt.close(fig)

df_no_out = df_mixed[df_mixed["is_outlier"] == 0].copy()
md_no_out = mixedlm(
    formula=formula,
    data=df_no_out,
    groups=df_no_out["Participant"],
)
mixed_res_no_out = md_no_out.fit(reml=False, method="lbfgs")

print("\nMixed-effects model excluding extreme residuals")
print(mixed_res_no_out.summary())

