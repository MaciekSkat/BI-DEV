import pandas as pd
import os

# --- USTAWIENIA ---
folder_path = r"/workspaces/BI-DEV/projects/Tourist acces/Obiekty" 
sheet_ogolem = "II.1"      
sheet_zagraniczni = "II.2" 
# ------------------

dane_koncowe = []

def wczytaj_i_wyczysc(file_path, sheet_name, value_name):
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    header_idx = None
    format_miesiecy = None
    
    for i, row in df_raw.iterrows():
        # czyszczenie: zdejmujemy ".0" i wiodące zera (np. "01" -> "1")
        czyste_wartosci = []
        for val in row.values:
            v = str(val).strip()
            if v.endswith('.0'): 
                v = v[:-2]
            if v.isdigit(): 
                v = str(int(v)) # konwersja '01' na '1'
            czyste_wartosci.append(v)
            
        if 'I' in czyste_wartosci and 'XII' in czyste_wartosci:
            header_idx = i
            format_miesiecy = 'rzymskie'
            break
        elif '1' in czyste_wartosci and '12' in czyste_wartosci:
            header_idx = i
            format_miesiecy = 'arabskie'
            break
            
    if header_idx is None:
        raise ValueError(f"Nie znaleziono wiersza z nagłówkami miesięcy w arkuszu {sheet_name}")
        
    # Ustawiamy wyczyszczone nagłówki, żebyśmy mieli pewność co do ich nazw
    wyczyszczone_naglowki = []
    for val in df_raw.iloc[header_idx].values:
        v = str(val).strip()
        if v.endswith('.0'): v = v[:-2]
        if v.isdigit(): v = str(int(v))
        wyczyszczone_naglowki.append(v)
        
    df_raw.columns = wyczyszczone_naglowki
    df = df_raw.iloc[header_idx + 1:].copy()
    
    df.rename(columns={df.columns[0]: 'Rodzaj_obiektu'}, inplace=True)
    df.dropna(subset=['Rodzaj_obiektu'], inplace=True)
    df = df.loc[:, ~df.columns.duplicated()] 
    
    if format_miesiecy == 'rzymskie':
        kolumny = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
    else:
        kolumny = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        
    df = df[['Rodzaj_obiektu'] + kolumny]
    
    # Standaryzacja na cyfry rzymskie
    if format_miesiecy == 'arabskie':
        mapa_na_rzymskie = {
            '1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V', '6': 'VI',
            '7': 'VII', '8': 'VIII', '9': 'IX', '10': 'X', '11': 'XI', '12': 'XII'
        }
        df.rename(columns=mapa_na_rzymskie, inplace=True)
        
    standardowe_miesiace = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
    
    df_melt = df.melt(id_vars=['Rodzaj_obiektu'], value_vars=standardowe_miesiace, var_name='Miesiac', value_name=value_name)
    return df_melt

#  GŁÓWNA PĘTLA 
for file in os.listdir(folder_path):
    if file.lower().endswith(".xlsx") or file.lower().endswith(".xls"):
        file_path = os.path.join(folder_path, file)
        
        rok = ''.join(filter(str.isdigit, file)) 
        print(f"Przetwarzam rok: {rok} z pliku {file}...")

        try:
            df_ogolem_melt = wczytaj_i_wyczysc(file_path, sheet_ogolem, 'Turyści_Ogółem')
            df_zagr_melt = wczytaj_i_wyczysc(file_path, sheet_zagraniczni, 'Turyści_Zagraniczni')

            df_merged = pd.merge(df_ogolem_melt, df_zagr_melt, on=['Rodzaj_obiektu', 'Miesiac'], how='left')
            df_merged['Rok'] = rok
            dane_koncowe.append(df_merged)
            print(f"Sukces dla {rok}!")
            
        except Exception as e:
            print(f"Błąd przy pliku {file}: {e}")

#  FINALIZACJA 
if dane_koncowe:
    df_final = pd.concat(dane_koncowe, ignore_index=True)
    
    df_final['Turyści_Ogółem'] = pd.to_numeric(df_final['Turyści_Ogółem'], errors='coerce').fillna(0)
    df_final['Turyści_Zagraniczni'] = pd.to_numeric(df_final['Turyści_Zagraniczni'], errors='coerce').fillna(0)
    
    df_final['Turyści_Krajowi'] = df_final['Turyści_Ogółem'] - df_final['Turyści_Zagraniczni']
    
    output_path = os.path.join(folder_path, "gotowe_noclegi.csv")
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n--- GOTOWE! ---")
    print(f"Plik CSV wygenerowany w: {output_path}")
else:
    print("\nNie udało się przetworzyć żadnych danych.")
