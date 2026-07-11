import pandas as pd
import os

# 1. USTAWIENIA - TUTAJ WPISZ SWOJE DANE
folder_path = r'C:\Users\skatm\OneDrive - Wyższa Szkoła Biznesu - National Louis University z siedzibą w Nowym Sączu\Dane\Obiekty' # Podaj ścieżkę do folderu
sheet_ogolem = "II.1"      # np. "Tabl. II.1" - sprawdź dokładnie w Excelu
sheet_zagraniczni = "II.2" # np. "Tabl. II.2"
wiersze_do_pominiecia = 6 # Liczba wierszy z tytułami do odcięcia z góry (zależnie od pliku)

dane_koncowe = []

# 2. PĘTLA PRZEZ WSZYSTKIE PLIKI W FOLDERZE
for file in os.listdir(folder_path):
    if file.endswith(".xlsx") or file.endswith(".xls"):
        file_path = os.path.join(folder_path, file)
        
        # Wyciągamy rok z nazwy pliku (zakładam, że rok jest w nazwie, np. "noclegi_2020.xlsx")
        # Możesz to dostosować, jeśli nazwy są inne
        rok = ''.join(filter(str.isdigit, file)) 
        print(f"Przetwarzam rok: {rok} z pliku {file}...")

        try:
            # Wczytywanie Arkusza 1 (Ogółem)
            df_ogolem = pd.read_excel(file_path, sheet_name=sheet_ogolem, skiprows=wiersze_do_pominiecia)
            # Zmiana nazwy pierwszej kolumny na 'Rodzaj obiektu'
            df_ogolem.rename(columns={df_ogolem.columns[0]: 'Rodzaj_obiektu'}, inplace=True)
            # Unpivot (Melt) - zamiana miesięcy na wiersze
            df_ogolem_melt = df_ogolem.melt(id_vars=['Rodzaj_obiektu'], 
                                            value_vars=['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'],
                                            var_name='Miesiac', value_name='Turyści_Ogółem')

            # Wczytywanie Arkusza 2 (Zagraniczni)
            df_zagraniczni = pd.read_excel(file_path, sheet_name=sheet_zagraniczni, skiprows=wiersze_do_pominiecia)
            df_zagraniczni.rename(columns={df_zagraniczni.columns[0]: 'Rodzaj_obiektu'}, inplace=True)
            df_zagraniczni_melt = df_zagraniczni.melt(id_vars=['Rodzaj_obiektu'], 
                                                      value_vars=['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'],
                                                      var_name='Miesiac', value_name='Turyści_Zagraniczni')

            # 3. ŁĄCZENIE DANYCH (Ogółem + Zagraniczni)
            df_merged = pd.merge(df_ogolem_melt, df_zagraniczni_melt, on=['Rodzaj_obiektu', 'Miesiac'], how='left')
            
            # Dodanie kolumny z rokiem
            df_merged['Rok'] = rok
            
            dane_koncowe.append(df_merged)
            
        except Exception as e:
            print(f"Błąd przy pliku {file}: {e}")

# 4. ZŁOŻENIE WSZYSTKIEGO W JEDNĄ TABELĘ I OBLICZENIA
if dane_koncowe:
    df_final = pd.concat(dane_koncowe, ignore_index=True)
    
    # Czyszczenie danych (usuwanie pustych wierszy, ewentualnych braków)
    df_final.dropna(subset=['Rodzaj_obiektu'], inplace=True)
    
    # Obliczanie turystów krajowych
    # Wypełniamy puste wartości zerami, żeby uniknąć błędów przy odejmowaniu
    df_final['Turyści_Ogółem'] = pd.to_numeric(df_final['Turyści_Ogółem'], errors='coerce').fillna(0)
    df_final['Turyści_Zagraniczni'] = pd.to_numeric(df_final['Turyści_Zagraniczni'], errors='coerce').fillna(0)
    
    df_final['Turyści_Krajowi'] = df_final['Turyści_Ogółem'] - df_final['Turyści_Zagraniczni']

    # 5. ZAPIS DO CZYSTEGO PLIKU CSV
    output_path = os.path.join(folder_path, "gotowe_noclegi.csv")
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Gotowe! Plik zapisany w: {output_path}")
else:
    print("Nie udało się przetworzyć żadnych danych.")