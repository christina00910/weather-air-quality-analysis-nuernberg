# 📑 Projekt-Fahrplan: "Luft & Wetter Bayern"


## 🎯 Projekt-Übersicht & Architektur
* **Restlaufzeit:** 2 Wochen (3x 1 Stunde koordiniertes Treffen pro Woche)
* **Team:** 3 Personen (Frank = Frontend/Streamlit; Christina & Markus = Backend/Machine Learning)
* **Architektur-Prinzip (Hybrid-Ansatz):**
  1. **Live-Daten (Pandas in App):** Vollständige `train_ready_data.csv` (ca. 400.000 Zeilen) für interaktive, nutzergefilterte Ansichten (Tab 1: Washout, Tab 2: Ozon-Paradoxon). Gecached über `@st.cache_data`.
  2. **Pre-Calculated Daten (Mini-CSVs aus Notebook):** Hochgradig aggregierte Kleinstdateien für statische, historische Gesamtübersichten (Tab 3: Chronobiologie, Tab 4: Langzeittrend), um Ladezeiten beim App-Start zu minimieren.

---

## 📅 Granularer 10-Schritte-Fahrplan

### 🏗️ Phase 1: Fundament & Datenaufbereitung (Tage 1–4)

#### 1. Schritt: Das Sync-Meeting (Morgen)
* **Zuständigkeit:** Gesamtes Team (Frank, Christina, Markus)
* **Ziel:** Definitiver Abgleich der Spaltennamen zwischen Rohdaten und Frontend (z. B. `temperatur`, `niederschlagshoehe_mm`, `o3`, `no2`, `pm10`), damit während der parallelen Arbeit keine Schnittstellenfehler entstehen.

#### 2. Schritt: Live-Daten-Pipeline bauen
* **Zuständigkeit:** Gesamtes Team (Frank, Christina, Markus)
* **Fokus:** Arbeiten in `01_EDA_und_Feature_Engineering.ipynb`.
* **Aufgaben:** * Behebung von fehlenden Werten (NaNs) bei Wetter- und Schadstoffdaten mittels Vorwärts-Auffüllen (`ffill()`) oder linearer Interpolation.
  * Zusammenführen von `datum` und `stunde` zu einem echten Pandas-Datetime-Objekt.
  * Extraktion zyklischer Zeit-Features (`Monat`, `Stunde`) und Generierung von Wind-Features (z. B. gleitende Durchschnitte der Windgeschwindigkeit zur Abbildung der Schadstoff-Dispersion).
* **Output:** Export der bereinigten `train_ready_data.csv` (400.000 Zeilen) nach `/data`.

#### 3. Schritt: Pre-Calculated-Daten exportieren
* **Zuständigkeit:** Gesamtes Team (Frank, Christina, Markus)
* **Fokus:** Ergänzung am Ende von Notebook 1 zur Entlastung des Frontends.
* **Aufgaben:** Einmalige Berechnung schwerer historischer Aggregationen über die vollen 44 Jahre.
* **Output:** * `klimatrend_1980_2024.csv` (Jahresmittelwerte für Tab 4).
  * `chronobiologie_heatmap.csv` (Mittelwerte pro Kombination aus Monat und Stunde für Tab 3).

#### 4. Schritt: Dashboard-Gerüst & UI-Layout aufsetzen
* **Zuständigkeit:** Gesamtes Team (Frank, Christina, Markus)
* **Fokus:** Arbeiten in `app.py`.
* **Aufgaben:** Erstellung der vier primären Tabs ("🌧️ Washout-Effekt", "☀️ Ozon-Paradoxon", "⏱️ Chronobiologie", "📈 Langzeittrend"). Einbau des Plotly-Darkthemes und Vorbereitung der Ladefunktionen. Testlauf mit den ungefilterten Rohdaten oder synthetischen Platzhaltern.

---

### 🧪 Phase 2: Zusammenführung & Machine Learning (Tage 5–9)

#### 5. Schritt: Daten-Hochzeit (Schnittstellen-Integration)
* **Zuständigkeit:** Gesamtes Team (Frank, Christina, Markus)
* **Fokus:** Integration der Backend-Ergebnisse in `app.py`.
* **Aufgaben:** Einlesen der drei aus Phase 1 resultierenden CSV-Dateien aus dem Ordner `data/`. Verknüpfung der Datenströme mit den Visualisierungen:
  * **Tab 1 (Washout):** Boxplot (Regen vs. Trockenheit) auf Basis der Live-Daten.
  * **Tab 2 (Ozon-Paradoxon):** Dual-Axis Chart (Temperatur, Ozon, NO₂) gefiltert über Jahres-Auswahl.
  * **Tab 3 (Chronobiologie):** 2D-Heatmap (Monat vs. Stunde) basierend auf der voraggregierten Mini-CSV.
  * **Tab 4 (Langzeittrend):** Liniendiagramme der Jahresmittelwerte basierend auf der voraggregierten Mini-CSV.

#### 6. Schritt: Modell-Training & Evaluierung
* **Zuständigkeit:** Gesamtes Team (Frank, Christina, Markus)
* **Fokus:** Arbeiten in `02_Model_Training_und_Evaluation.ipynb`.
* **Aufgaben:** * Definition der Feature-Matrix `X` (inklusive der hergeleiteten Wind- und Zeit-Features) und der Zielvariable `y` (Schadstoffkonzentration).
  * Durchführung eines strikt chronologischen Train/Test-Splits (z. B. Training: 1980–2020, Test: 2021–2024) zur Vermeidung von Data Leakage.
  * Training einer linearen Baseline sowie komplexerer Baum-Modelle (`RandomForestRegressor` oder `XGBoost`).
  * Berechnung und Dokumentation von Validierungsmetriken (RMSE, MAE, R²).

#### 7. Schritt: Interaktivitätsschliff & Edge Cases
* **Zuständigkeit:** Frontend (Frank)
* **Fokus:** Optimierung der Benutzererfahrung in `app.py`.
* **Aufgaben:** Absicherung der App gegen fehlerhafte oder leere Zustände bei extremen Filtereinstellungen (z. B. Abfangen leerer Datenrahmen mittels `st.warning("Keine Messwerte für diese Auswahl vorhanden")`). Verfeinerung der Plotly-Layouts (Achsenbeschriftungen, Legenden-Positionierung).

---

### 🚀 Phase 3: KI-Integration & Projektabschluss (Tage 10–14)

#### 8. Schritt: Finaler Modell-Export & Dokumentation der Schnittstelle
* **Zuständigkeit:** Backend (Christina & Markus & Frank)
* **Fokus:** Arbeiten in `03_Model_Export_Pipeline.ipynb`.
* **Aufgaben:** * Erneutes Training des in Schritt 6 ermittelten Gewinner-Modells auf **100 % der verfügbaren Daten** (kein erneuter Test-Split), um das maximale historische Wissen zu nutzen.
  * Serialisierung des Modells mittels `joblib.dump()` als `wetter_schadstoff_model.pkl` im Ordner `/models`.
  * Bereitstellung einer exakten Dokumentation über die erwartete Reihenfolge und Skalierung der Eingabe-Features (API-Schnittstelle für Frank).

#### 9. Schritt: Prognose-Modul einbauen
* **Zuständigkeit:** Frontend (Frank)
* **Fokus:** Erweiterung der `app.py` um ein interaktives Vorhersage-Feature.
* **Aufgaben:** * Implementierung eines zusätzlichen Tabs oder Bereichs ("🔮 KI-Luftprognose").
  * Laden des Modells im Frontend mittels `joblib.load()` unter Verwendung des performanten `@st.cache_resource` Dekorators.
  * Bereitstellung von Streamlit-Eingabeelementen (`st.slider` oder `st.number_input`) für die Wetter-Features (Temperatur, Windgeschwindigkeit, etc.).
  * Übergabe der Nutzereingaben an die `model.predict()` Funktion und visuelle Aufbereitung der prognostizierten Schadstoffwerte.

#### 10. Schritt: Code Freeze, Review & Dokumentation
* **Zuständigkeit:** Gesamtes Team (Frank, Christina, Markus)
* **Fokus:** Qualitätssicherung (mindestens 48 Stunden vor der finalen Abgabe).
* **Aufgaben:** * Vollständiger Code Freeze (keine Implementierung neuer Features mehr).
  * Gemeinsames Durchklicken der Applikation auf verschiedenen Endgeräten/Browsern, um Laufzeitfehler oder Layout-Verschiebungen auszuschließen.
  * Finales Refactoring: Bereinigung von redundantem Code, Überprüfung aller Code-Kommentare auf Verständlichkeit und Finalisierung des Handover-Protokolls für die Abgabe der Abschlussarbeit.
