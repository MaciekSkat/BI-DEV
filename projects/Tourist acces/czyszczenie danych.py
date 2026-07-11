import pandas as pd
import os

# --- USTAWIENIA ---
folder_path = r"/workspaces/BI-DEV/projects/Tourist acces/Obiekty" # Wpisz właściwą ścieżkę do folderu!
sheet_ogolem = "II.1"      # Upewnij się, że tak dokładnie nazywa się zakładka Ogółem
sheet_zagraniczni = "II.2" # Upewnij się, że tak nazywa się zakładka Zagraniczni
# ------------------

dane_koncowe = []

def wczytaj_i_wyczysc(file_path, sheet_name, value_name):
    # Wczytujemy plik na surowo, bez żadnych założeń o tym, gdzie są nagłówki
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    # Skanujemy wiersz po wierszu, żeby znaleźć ten z miesiącami (I, II ... XII)
    header_idx = None
    for i, row in df_raw.iterrows():
        row_vals = [str(val).strip() for val in row.values]
        if 'I' in row_vals and 'XII' in row_vals:
            header_idx = i
            break
            
    if header_idx is None:
        raise ValueError(f"Nie znaleziono wiersza z miesiącami (I...XII) w arkuszu {sheet_name}")
        
    # Ustawiamy znaleziony wiersz jako nasze oficjalne nagłówki
    df_raw.columns = df_raw.iloc[header_idx]
    
    # Ucinamy wszystkie wiersze powyżej naszych nagłówków
    df = df_raw.iloc[header_idx + 1:].copy()
    
    # Pierwsza kolumna zawsze zawiera typy obiektów, nazywamy ją na sztywno
    df.rename(columns={df.columns[0]: 'Rodzaj_obiektu'}, inplace=True)
    
    # Usuwamy wiersze, które nie mają podanego rodzaju obiektu (np. puste linie na dole pliku)
    df.dropna(subset=['Rodzaj_obiektu'], inplace=True)
    
    # Wybieramy tylko te kolumny, które nas interesują (ignorujemy podsumowania roczne itp.)
    miesiace = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
    
    # Zabezpieczenie na wypadek zduplikowanych kolumn (co GUS lubi robić)
    df = df.loc[:, ~df.columns.duplicated()] 
    df = df[['Rodzaj_obiektu'] + miesiace]
    
    # Zamieniamy miesiące z kolumn na wiersze (Unpivot)
    df_melt = df.melt(id_vars=['Rodzaj_obiektu'], value_vars=miesiace, var_name='Miesiac', value_name=value_name)
    return df_melt

# --- GŁÓWNA PĘTLA ---
for file in os.listdir(folder_path):
    if file.endswith(".xlsx") or file.endswith(".xls"):
        file_path = os.path.join(folder_path, file)
        
        # Wyciągamy rok z nazwy pliku
        rok = ''.join(filter(str.isdigit, file)) 
        print(f"Przetwarzam rok: {rok} z pliku {file}...")

        try:
            df_ogolem_melt = wczytaj_i_wyczysc(file_path, sheet_ogolem, 'Turyści_Ogółem')
            df_zagr_melt = wczytaj_i_wyczysc(file_path, sheet_zagraniczni, 'Turyści_Zagraniczni')

            # Łączymy obie tabele po Rodzaju obiektu i Miesiącu
            df_merged = pd.merge(df_ogolem_melt, df_zagr_melt, on=['Rodzaj_obiektu', 'Miesiac'], how='left')
            df_merged['Rok'] = rok
            dane_koncowe.append(df_merged)
            print(f"Sukces dla {rok}!")
            
        except Exception as e:
            print(f"Błąd przy pliku {file}: {e}")

# --- FINALIZACJA ---
if dane_koncowe:
    df_final = pd.concat(dane_koncowe, ignore_index=True)
    
    # Konwersja na liczby i zastąpienie błędów/braków zerami
    df_final['Turyści_Ogółem'] = pd.to_numeric(df_final['Turyści_Ogółem'], errors='coerce').fillna(0)
    df_final['Turyści_Zagraniczni'] = pd.to_numeric(df_final['Turyści_Zagraniczni'], errors='coerce').fillna(0)
    
    # Wyliczamy turystów krajowych
    df_final['Turyści_Krajowi'] = df_final['Turyści_Ogółem'] - df_final['Turyści_Zagraniczni']
    
    # Zapis
    output_path = os.path.join(folder_path, "gotowe_noclegi.csv")
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n--- GOTOWE! ---")
    print(f"Plik CSV wygenerowany w: {output_path}")
else:
    print("\nNie udało się przetworzyć żadnych danych. Sprawdź nazwy arkuszy w ustawieniach.")