# %% [markdown]
# ## Przygotowanie seeda sprzedaży dla dbt
#
# **Problem:** sales_train_evaluation.csv jest w formacie SZEROKIM (~1941
# kolumn d_1..d_1941) — SQL Server ma limit ok. 1024 kolumn na zwykłą
# tabelę, więc tego pliku nie da się wgrać jako seed wprost.
#
# **Rozwiązanie:** rozpłaszczamy do formatu DŁUGIEGO (jak w pandas_pit_
# validation.py), zawężamy do kilkunastu SKU + 1-2 lat danych (zgodnie
# z pierwotnym planem projektu), i zapisujemy jako nowy, mały CSV, który
# dopiero wtedy staje się seedem w dbt.

# %%
import pandas as pd

# %% [markdown]
# ### Parametry zawężenia — dostosuj świadomie

# %%
STORE_ID = "CA_1"
DEPT_ID = "FOODS_3"
N_ITEMS = 15                # ile SKU bierzemy do projektu
YEARS_OF_HISTORY = 2.5      # trochę więcej niż "1-2 lata" z planu — nadmiar
                             # to celowy bufor na PIT lookback (żeby najwcześniejsze
                             # daty w oknie i tak miały 8 tygodni historii wstecz)

# %%
SALES_PATH = "../data/raw/sales_train_evaluation.csv"
CALENDAR_PATH = "../data/raw/calendar.csv"
OUTPUT_PATH = "../seeds/sales_long.csv"

sales_wide = pd.read_csv(SALES_PATH)
calendar = pd.read_csv(CALENDAR_PATH)
calendar["date"] = pd.to_datetime(calendar["date"])

# %% [markdown]
# ### Wybór SKU — te same, którymi już walidowaliśmy logikę w pandas,
# rozszerzone do pełnych N_ITEMS

# %%
subset = sales_wide[
    (sales_wide["dept_id"] == DEPT_ID) & (sales_wide["store_id"] == STORE_ID)
].copy()

day_cols = [c for c in subset.columns if c.startswith("d_")]
subset["total_sales"] = subset[day_cols].sum(axis=1)

chosen_items = subset.sort_values("total_sales", ascending=False).head(N_ITEMS)["item_id"].tolist()
print(f"Wybrano {len(chosen_items)} SKU:", chosen_items)

# %% [markdown]
# ### Melt do formatu długiego (dokładnie jak w prototypie pandas)

# %%
long_df = subset[subset["item_id"].isin(chosen_items)].melt(
    id_vars=["item_id", "store_id", "dept_id"],
    value_vars=day_cols,
    var_name="d",
    value_name="units_sold",
)

long_df = long_df.merge(calendar[["d", "date"]], on="d", how="left")

# %% [markdown]
# ### Zawężenie okresu — ostatnie YEARS_OF_HISTORY lat danych

# %%
max_date = long_df["date"].max()
cutoff_date = max_date - pd.DateOffset(months=int(YEARS_OF_HISTORY * 12))
long_df = long_df[long_df["date"] >= cutoff_date].copy()

print(f"Zakres dat: {long_df['date'].min().date()} -> {long_df['date'].max().date()}")
print(f"Liczba wierszy: {len(long_df)}")

# %% [markdown]
# ### Zapis jako seed — tylko kolumny potrzebne dalej w dbt
# (date/wday dociągniemy w stg_sales przez JOIN z już istniejącym stg_calendar,
# nie duplikujemy tego tutaj)

# %%
output = long_df[["item_id", "store_id", "dept_id", "d", "units_sold"]]
output.to_csv(OUTPUT_PATH, index=False)

print(f"\nZapisano: {OUTPUT_PATH}")
print(f"Kolumn: {output.shape[1]} (dużo poniżej limitu SQL Servera)")
print(f"Wierszy: {output.shape[0]}")
