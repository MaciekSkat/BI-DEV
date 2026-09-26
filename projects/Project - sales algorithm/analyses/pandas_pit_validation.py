# %% [markdown]
# ## Prototyp walidacyjny: ważona, przycinana (trimmed) średnia PIT
#
# **Cel:** niezależne źródło prawdy w pandas, do porównania z logiką,
# którą napiszemy później w SQL/dbt (model `int_pit_avg`).
#
# **Zakres:** ten skrypt sprawdza WYŁĄCZNIE rdzeń algorytmu — point-in-time
# matching po dniu tygodnia, zanikającą wagę i trimmed mean. Cold start
# i kanibalizacja to osobne, kolejne kroki — nie są tu jeszcze uwzględnione.
#
# **Jak używać:**
# 1. Uruchom w VS Code jako Interactive Python (komórki `# %%` działają
#    tak samo jak w notebooku, bez potrzeby pliku .ipynb).
# 2. Ścieżki do plików M5 poniżej zakładają, że ten skrypt leży
#    w folderze `analyses/` projektu — dostosuj jeśli trzeba.
# 3. Parametry w sekcji niżej to ROZSĄDNE WARTOŚCI DOMYŚLNE, nie kopia
#    oryginalnego algorytmu — podmień, jeśli pamiętasz konkretne liczby
#    (np. ile tygodni wstecz, jak mocno zanika waga, próg do trimowania).

# %%
import pandas as pd
import numpy as np

# %% [markdown]
# ### Parametry — dostosuj świadomie, nie zgaduj

# %%
LOOKBACK_WEEKS = 8        # ile ostatnich (tego samego dnia tygodnia) obserwacji bierzemy pod uwagę
DECAY_RATE = 0.85         # waga = DECAY_RATE ** (ile tygodni temu); 1.0 = brak zanikania wagi
MIN_SAMPLES_FOR_TRIM = 4  # od ilu obserwacji zaczynamy w ogóle odrzucać skrajności
TRIM_COUNT = 1            # ile najniższych i najwyższych wartości odrzucamy, gdy próbka wystarczająca

# %% [markdown]
# ### Wczytanie surowych danych M5

# %%
SALES_PATH = "../data/raw/sales_train_evaluation.csv"
CALENDAR_PATH = "../data/raw/calendar.csv"

sales_wide = pd.read_csv(SALES_PATH)
calendar = pd.read_csv(CALENDAR_PATH)

print("sales_wide:", sales_wide.shape)
print("calendar:  ", calendar.shape)

# %% [markdown]
# ### Wybór próbki: FOODS_3, jeden sklep, 3 produkty o największej sprzedaży
# (unikamy produktów prawie-same-zera, na nich trudno cokolwiek sensownie zwalidować)

# %%
STORE_ID = "CA_1"
DEPT_ID = "FOODS_3"

subset = sales_wide[
    (sales_wide["dept_id"] == DEPT_ID) & (sales_wide["store_id"] == STORE_ID)
].copy()

day_cols = [c for c in subset.columns if c.startswith("d_")]
subset["total_sales"] = subset[day_cols].sum(axis=1)

top_items = subset.sort_values("total_sales", ascending=False).head(3)["item_id"].tolist()
print("Wybrane produkty do testu:", top_items)

# %% [markdown]
# ### Przekształcenie do formatu długiego (jeden wiersz = jeden dzień jednego produktu)

# %%
long_df = subset[subset["item_id"].isin(top_items)].melt(
    id_vars=["item_id", "store_id", "dept_id"],
    value_vars=day_cols,
    var_name="d",
    value_name="units_sold",
)

long_df = long_df.merge(calendar[["d", "date", "wday"]], on="d", how="left")
long_df["date"] = pd.to_datetime(long_df["date"])
long_df = long_df.sort_values(["item_id", "date"]).reset_index(drop=True)

print(long_df.head())

# %% [markdown]
# ### Główna funkcja: ważona, przycinana średnia PIT dla jednej daty

# %%
def weighted_trimmed_mean_pit(item_df: pd.DataFrame, target_date: pd.Timestamp) -> dict:
    """
    Liczy prognozę dla target_date, używając WYŁĄCZNIE danych sprzed tej
    daty (point-in-time, zero data leakage), dopasowanych po tym samym
    dniu tygodnia (wday), z zanikającą wagą i trimmed mean.
    """
    target_row = calendar.loc[calendar["date"] == target_date.strftime("%Y-%m-%d"), "wday"]
    if target_row.empty:
        return {"error": "brak takiej daty w kalendarzu M5"}
    target_wday = target_row.iloc[0]

    history = (
        item_df[(item_df["date"] < target_date) & (item_df["wday"] == target_wday)]
        .sort_values("date", ascending=False)
        .head(LOOKBACK_WEEKS)
        .reset_index(drop=True)
    )

    n = len(history)
    if n == 0:
        return {"n_samples": 0, "forecast": None, "note": "brak historii — to przypadek dla cold start"}

    history["weeks_ago"] = history.index
    history["weight"] = DECAY_RATE ** history["weeks_ago"]

    values = history.sort_values("units_sold")

    if n >= MIN_SAMPLES_FOR_TRIM and TRIM_COUNT > 0 and (n - 2 * TRIM_COUNT) > 0:
        trimmed = values.iloc[TRIM_COUNT:-TRIM_COUNT]
        dropped_low = values.iloc[:TRIM_COUNT]["units_sold"].tolist()
        dropped_high = values.iloc[-TRIM_COUNT:]["units_sold"].tolist()
    else:
        trimmed = values
        dropped_low, dropped_high = [], []

    weighted_avg = np.average(trimmed["units_sold"], weights=trimmed["weight"])

    return {
        "n_samples": n,
        "forecast": round(float(weighted_avg), 2),
        "dropped_low": dropped_low,
        "dropped_high": dropped_high,
        "raw_values_used": trimmed["units_sold"].tolist(),
    }
#%%
def iqr_aware_trimmed_mean_pit(item_df: pd.DataFrame, target_date: pd.Timestamp, iqr_multiplier: float = 1.5) -> dict:
    """
    Wariant: zamiast ślepo odrzucać rangę najniższą/najwyższą, odrzuca
    wartość TYLKO jeśli jest realnym statystycznym outlierem
    (poza Q1 - iqr_multiplier*IQR albo Q3 + iqr_multiplier*IQR).
    Płynny, rosnący trend nie zostanie ucięty na krawędziach.
    """
    target_row = calendar.loc[calendar["date"] == target_date.strftime("%Y-%m-%d"), "wday"]
    if target_row.empty:
        return {"error": "brak takiej daty w kalendarzu M5"}
    target_wday = target_row.iloc[0]

    history = (
        item_df[(item_df["date"] < target_date) & (item_df["wday"] == target_wday)]
        .sort_values("date", ascending=False)
        .head(LOOKBACK_WEEKS)
        .reset_index(drop=True)
    )

    n = len(history)
    if n == 0:
        return {"n_samples": 0, "forecast": None, "note": "brak historii — cold start"}

    history["weeks_ago"] = history.index
    history["weight"] = DECAY_RATE ** history["weeks_ago"]

    q1 = history["units_sold"].quantile(0.25)
    q3 = history["units_sold"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - iqr_multiplier * iqr
    upper_bound = q3 + iqr_multiplier * iqr

    is_outlier = (history["units_sold"] < lower_bound) | (history["units_sold"] > upper_bound)
    dropped = history.loc[is_outlier, "units_sold"].tolist()
    kept = history.loc[~is_outlier]

    if kept.empty:
        kept = history  # zabezpieczenie — nie zostawiaj pustej próbki

    weighted_avg = np.average(kept["units_sold"], weights=kept["weight"])

    return {
        "n_samples": n,
        "forecast": round(float(weighted_avg), 2),
        "dropped_as_outliers": dropped,
        "bounds": (round(lower_bound, 1), round(upper_bound, 1)),
        "raw_values_used": kept["units_sold"].tolist(),
    }
# %% [markdown]
# ### Test na przykładowych datach — te liczby porównamy z wynikiem z dbt
# (daty celowo głęboko w danych, żeby było minimum LOOKBACK_WEEKS tygodni historii)

# %%
test_dates = pd.to_datetime(["2013-06-03", "2013-09-02", "2013-12-02"])

for item in top_items:
    item_df = long_df[long_df["item_id"] == item]
    print(f"\n=== {item} ===")
    for d in test_dates:
        blind = weighted_trimmed_mean_pit(item_df, d)
        smart = iqr_aware_trimmed_mean_pit(item_df, d)
        print(f"  {d.date()}")
        print(f"    ślepy trim (rank): forecast={blind.get('forecast')}, odrzucone={blind.get('dropped_low', []) + blind.get('dropped_high', [])}")
        print(f"    IQR-aware:         forecast={smart.get('forecast')}, odrzucone={smart.get('dropped_as_outliers')}, granice={smart.get('bounds')}")
