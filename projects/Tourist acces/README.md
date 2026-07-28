# Turystyka 360° – Kompleksowa Analiza Ruchu Turystycznego w Polsce

## 📌 O projekcie
**Turystyka 360°** to profesjonalny dashboard analityczny wizualizujący dane dotyczące ruchu turystycznego w Polsce. Projekt powstał w celu dostarczenia przejrzystych odpowiedzi na pytania dotyczące popularności regionów, preferencji noclegowych oraz trendów sezonowych, bazując na oficjalnych danych statystycznych. Raport łączy zaawansowane modelowanie DAX z optymalizacją i czyszczeniem danych w języku Python.

## 📊 Główne funkcjonalności
* **Menu nawigacyjne (UI/UX):** Intuicyjny interfejs startowy umożliwiający szybkie przejście do kluczowych modułów analizy bez konieczności przeklikiwania standardowych zakładek.
* **Analiza historyczna i trendy:** Wykorzystanie wykresów do wizualizacji trendów (YoY) oraz wpływu zdarzeń makroekonomicznych (np. pandemia COVID-19) na dynamikę ruchu turystycznego.
* **Zaawansowane raportowanie:** Rozbudowane wskaźniki KPI, formatowanie warunkowe, dynamiczne tytuły wykresów oraz wbudowane zabezpieczenia dla miar czasowych (ukrywanie pustych wartości r/r w widokach zagregowanych).
* **Zoptymalizowany model danych:** Wykorzystanie struktury schematu gwiazdy (Star Schema). Wszystkie miary DAX zostały rygorystycznie uporządkowane w folderach wyświetlania, co zapewnia pełną czytelność modelu deweloperskiego.

## 🐍 Przygotowanie danych (Python ETL)
W celu zapewnienia najwyższej jakości danych, proces ETL (Extract, Transform, Load) został zautomatyzowany za pomocą skryptów w języku Python. Ze względu na strukturę surowych plików źródłowych, do czyszczenia, deduplikacji i agregacji wykorzystano bibliotekę `pandas`.

🛠️ Technologie i narzędzia
Power BI (Format .pbip): Projekt został zapisany w nowoczesnym formacie Power BI Project, co pozwala na pełną kontrolę wersji modelu semantycznego oraz kodu bazowego.

DAX (Data Analysis Expressions): Zaawansowana logika analityczna, w tym niestandardowe zabezpieczenia kalkulacji Time Intelligence.

Python (Pandas): Integracja narzędzi programistycznych do czyszczenia i formowania zestawień przed zaczytaniem ich do modelu.

🔍 Nota metodologiczna i Źródła
Dane wykorzystane w raporcie pochodzą z Głównego Urzędu Statystycznego (Baza Danych Lokalnych).

Metodologia liczenia: Należy wziąć pod uwagę, że statystyki turystyczne GUS opierają się na liczbie zameldowań. W przypadku turystyki (szczególnie zagranicznej) dane mogą wykazywać naturalne duplikaty – ten sam turysta odwiedzający Polskę wielokrotnie w ciągu roku lub zmieniający obiekt noclegowy jest zliczany przy każdym kolejnym zameldowaniu.

Zakres bazy noclegowej: Zauważalne różnice w sumach całkowitych na wybranych widokach wynikają bezpośrednio z metodologii GUS, który w szczegółowych zestawieniach (dotyczących m.in. rozbicia na rodzaje obiektów) uwzględnia głównie obiekty posiadające 10 lub więcej miejsc noclegowych.