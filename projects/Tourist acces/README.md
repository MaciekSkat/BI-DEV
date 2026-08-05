**🌍Turystyka 360° – Kompleksowa Analiza Ruchu Turystycznego w Polsce**

📌 O projekcie

Turystyka 360° to interaktywny dashboard analityczny wizualizujący dane dotyczące ruchu turystycznego w Polsce. Projekt powstał w celu dostarczenia przejrzystych odpowiedzi na pytania dotyczące popularności regionów, preferencji noclegowych oraz trendów sezonowych, bazując na oficjalnych danych statystycznych. Raport łączy zaawansowane modelowanie DAX z optymalizacją i czyszczeniem danych w języku Python.

📷 Podgląd raportu

<img width="1533" height="865" alt="image" src="https://github.com/user-attachments/assets/c59bec72-f62e-480b-8f28-d5abe838111d" /> <img width="1533" height="863" alt="image" src="https://github.com/user-attachments/assets/d4627644-251e-4669-bc44-9951da23162c" />




📊 Główne funkcjonalności
Menu nawigacyjne (UI/UX): Intuicyjny interfejs startowy umożliwiający szybkie przejście do kluczowych modułów analizy bez konieczności przeklikiwania standardowych zakładek.
Analiza historyczna i trendy: Wykorzystanie wykresów do wizualizacji trendów (YoY) oraz wpływu zdarzeń makroekonomicznych (np. pandemia COVID-19) na dynamikę ruchu turystycznego.
Zaawansowane raportowanie: Rozbudowane wskaźniki KPI, formatowanie warunkowe, dynamiczne tytuły wykresów oraz wbudowane zabezpieczenia dla miar czasowych (ukrywanie pustych wartości r/r w widokach zagregowanych).
Zoptymalizowany model danych: Wykorzystanie struktury schematu gwiazdy (Star Schema). Wszystkie miary DAX zostały rygorystycznie uporządkowane w folderach wyświetlania, co zapewnia pełną czytelność modelu deweloperskiego.
🐍 Przygotowanie danych (Python ETL)

W celu zapewnienia najwyższej jakości danych, proces ETL (Extract, Transform, Load) został zautomatyzowany za pomocą skryptów w języku Python. Ze względu na strukturę surowych plików źródłowych, do czyszczenia, deduplikacji i agregacji wykorzystano bibliotekę pandas.

🛠️ Technologie i narzędzia
Power BI (Format .pbip): Projekt zapisany w formacie Power BI Project – pełna kontrola wersji modelu semantycznego i kodu bazowego w Git.
DAX (Data Analysis Expressions): Zaawansowana logika analityczna, w tym niestandardowe zabezpieczenia kalkulacji Time Intelligence.
Python (Pandas): Czyszczenie, deduplikacja i formowanie zestawień przed załadowaniem ich do modelu.
📁 Struktura repozytorium
├── Obiekty/                        # Dane 
├── Tourist report.Report/          # Definicja raportu Power BI (.pbip)
├── Tourist report.SemanticModel/   # Model semantyczny – tabele, relacje, DAX
├── Tourist report.pbip             # Główny plik projektu Power BI
├── clear_data_objects.py           # Skrypt Python – czyszczenie i przygotowanie danych
├── Country_Visit_Poland            # [uzupełnij: co zawiera ten plik]
└── README.md
▶️ Jak uruchomić
Zainstaluj Power BI Desktop (wersja wspierająca format .pbip).
Otwórz plik Tourist report.pbip.
(Opcjonalnie) Aby odtworzyć proces czyszczenia danych: zainstaluj pandas (pip install pandas) i uruchom clear_data_objects.py.
🔍 Nota metodologiczna i Źródła

Dane wykorzystane w raporcie pochodzą z Głównego Urzędu Statystycznego (Baza Danych Lokalnych).

Metodologia liczenia: Należy wziąć pod uwagę, że statystyki turystyczne GUS opierają się na liczbie zameldowań. W przypadku turystyki (szczególnie zagranicznej) dane mogą wykazywać naturalne duplikaty – ten sam turysta odwiedzający Polskę wielokrotnie w ciągu roku lub zmieniający obiekt noclegowy jest zliczany przy każdym kolejnym zameldowaniu.

Zakres bazy noclegowej: Zauważalne różnice w sumach całkowitych na wybranych widokach wynikają bezpośrednio z metodologii GUS, który w szczegółowych zestawieniach (dotyczących m.in. rozbicia na rodzaje obiektów) uwzględnia głównie obiekty posiadające 10 lub więcej miejsc noclegowych.

🔗 Zobacz też
📊 Interaktywny raport:
https://app.powerbi.com/view?r=eyJrIjoiMWVhMTg2ZTgtOGZjOC00NzA4LWExZjQtZjJjZjJhZDcxZWUzIiwidCI6ImQwMzYzN2RmLTdiM2EtNDU2NC04NzBiLTA2MjJhODFhNzY0ZCJ9&pageName=3272f76878996bc1b492

💼 LinkedIn: https://www.linkedin.com/in/maciej-skatuła-388578266/
