# -*- coding: utf-8 -*-
# @Authors: Christina Dürrbeck, Markus Edelhoff
# @Project: Abschlussprojekt DSI - app_aufbau
# @Date:    11.05.2026 bis 29.05.2026

import streamlit as st
import pandas as pd
import os
from pathlib import Path 
import plotly.express as px
import plotly.graph_objects as go
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import seaborn as sns
import styling

import analysePM as an
import randomForest as ran
import openMeteo as op
import stPrognosis as pr
import O3
import korrelation as kor
import silvester as sil
import tabs as t

# Globales Styling für alle matplotlib/seaborn-Charts aktivieren
styling.apply_global_style()

# ============================================================
# 00 SEITENKONFIGURATION & CACHING
# ============================================================
custom_svg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' height='24px' viewBox='0 -960 960 960' width='24px' fill='%231f1f1f'><path d='M131.5-131.5Q120-143 120-160v-40q0-17 11.5-28.5T160-240q17 0 28.5 11.5T200-200v40q0 17-11.5 28.5T160-120q-17 0-28.5-11.5Zm160 0Q280-143 280-160v-220q0-17 11.5-28.5T320-420q17 0 28.5 11.5T360-380v220q0 17-11.5 28.5T320-120q-17 0-28.5-11.5Zm160 0Q440-143 440-160v-140q0-17 11.5-28.5T480-340q17 0 28.5 11.5T520-300v140q0 17-11.5 28.5T480-120q-17 0-28.5-11.5Zm160 0Q600-143 600-160v-200q0-17 11.5-28.5T640-400q17 0 28.5 11.5T680-360v200q0 17-11.5 28.5T640-120q-17 0-28.5-11.5Zm160 0Q760-143 760-160v-360q0-17 11.5-28.5T800-560q17 0 28.5 11.5T840-520v360q0 17-11.5 28.5T800-120q-17 0-28.5-11.5ZM560-481q-16 0-30.5-6T503-504L400-607 188-395q-12 12-28.5 11.5T131-396q-11-12-10.5-28.5T132-452l211-211q12-12 26.5-17.5T400-686q16 0 31 5.5t26 17.5l103 103 212-212q12-12 28.5-11.5T829-771q11 12 10.5 28.5T828-715L617-504q-11 11-26 17t-31 6Z'/></svg>"

st.set_page_config(
    page_title="Schadstoff/Wetter-Korrelation am Beispiel der Stadt Nürnberg",
    page_icon=custom_svg,
    layout="wide")

# Mapping: Anzeige-Label im Radio -> Spaltenname im DataFrame
STOFF_MAP = {
    "Ozon (O₃)": "o3",
    "Stickstoffdioxid (NO₂)": "no2",
    "Feinstaub (PM10 & PM2.5)": "pm10",
}

def showEDAPlots (df_prepared, stoff):        
    """
    Zeigt alle EDA-Plots hochperformant in Streamlit an.
    Wichtig: Übergeben Sie hier das zentral über 'prepare_base_data' 
    vorbereitete DataFrame, nicht das rohe Original!
    """

    st.divider()
    
# ============================================================
# Grafiken der EDA-Analyse
# ============================================================  
# 1. Jahrestrend (Läuft in Millisekunden aus dem Cache)
    fig_year = an.calcMeanYear(df_prepared, stoff)

    if fig_year:

        # Grafik kleiner und kompakter anzeigen
        fig_year.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achsen der bestehenden Grafik holen
        ax = fig_year.axes[0]

        # Titel anpassen
        ax.set_title(
            f"Jahresmittelwert Trend für {stoff.upper()}",
            fontsize=TITLE_SIZE,
            fontweight="bold",
            color="white",
            pad=15)

        # Achsenbeschriftungen anpassen
        ax.set_xlabel(
            "Jahr",
            fontsize=LABEL_SIZE,
            fontweight="bold")

        ax.set_ylabel(
            "Mittlere Konzentration [µg/m³]",
            fontsize=LABEL_SIZE,
            fontweight="bold")

        # Zahlen auf den Achsen
        ax.tick_params(
            axis='both',
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_year, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen langfristigen Anstieg der durchschnittlichen Ozonkonzentration seit den 1980er-Jahren. Besonders in den letzten Jahren sind erhöhte Ozonwerte erkennbar, was auf den Einfluss steigender Temperaturen und intensiver Sonneneinstrahlung hinweisen kann.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen langfristigen Rückgang der durchschnittlichen NO₂-Konzentrationen seit den 1990er-Jahren. Besonders in den letzten Jahren sind deutlich sinkende Werte erkennbar, was unter anderem auf strengere Emissionsgrenzwerte und technologische Entwicklungen im Verkehrssektor hinweisen könnte. Der starke Rückgang im Jahr 1993 stellt hingegen einen auffälligen Ausreißer innerhalb der Zeitreihe dar und könnte auf eine daten- oder messtechnische Besonderheit hinweisen.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen langfristigen Rückgang der PM10-Konzentrationen seit den 1980er-Jahren. Besonders ab den 2000er-Jahren sind deutlich sinkende Werte erkennbar, was auf strengere Umweltauflagen, technische Entwicklungen im Verkehrs- und Industriesektor sowie verbesserte Luftreinhaltemaßnahmen hinweisen könnte. Auch die PM2.5-Werte zeigen seit Beginn der verfügbaren Messreihe ab 2008 eine insgesamt rückläufige Entwicklung.
            </div>
            """, unsafe_allow_html=True)

    # Abstand zur nächsten Grafik
    st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True)

    st.divider()

    # 2. Saisonales Muster (Jahrzehntvergleich)
    fig_saison = an.calcMeanSaisonYear(df_prepared, stoff)

    if fig_saison:

        # Grafikgröße einheitlich
        fig_saison.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12 
        TICK_SIZE = 10

        # Achsen holen
        ax = fig_saison.axes[0]

        # Jahreszahlen rechts größer machen
        for text in ax.texts:
            text.set_fontsize(10.5)

        # Titel anpassen
        ax.set_title(
            f"Saisonales {stoff.upper()}-Muster im Jahrzehntvergleich",
            fontsize=TITLE_SIZE,
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            "Monat",
            fontsize=LABEL_SIZE,
            fontweight="bold")

        ax.set_ylabel(
            "Mittlere Konzentration [µg/m³]",
            fontsize=LABEL_SIZE,
            fontweight="bold")

        # Zahlen auf Achsen kleiner
        ax.tick_params(
            axis='both',
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_saison, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt ein deutlich saisonales Ozonmuster mit erhöhten Konzentrationen in den Frühjahrs- und Sommermonaten. Besonders in den neueren Jahrzehnten treten höhere Ozonwerte auf, was auf den Einfluss steigender Temperaturen und intensiver Sonneneinstrahlung hinweisen kann.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt insgesamt sinkende NO₂-Konzentrationen über die Jahrzehnte hinweg. Gleichzeitig sind besonders in den Wintermonaten höhere Werte erkennbar, was auf verstärkte Emissionen durch Verkehr und Heizungen sowie ungünstigere meteorologische Bedingungen für den Schadstoffabbau hinweisen kann.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt deutliche saisonale Unterschiede der PM10-Konzentrationen im Jahrzehntvergleich. Während in den 1980er- und 2000er-Jahren teilweise höhere Belastungen in einzelnen Herbst- und Wintermonaten auftreten, liegen die Werte im Jahr 2020 insgesamt deutlich niedriger. Dies deutet langfristig auf eine Verbesserung der Luftqualität sowie auf den Einfluss verschärfter Umwelt- und Emissionsmaßnahmen hin.
            </div>
            """, unsafe_allow_html=True)

    # Abstand zur nächsten Grafik
    st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True)
    
    st.divider()

    # 3. Rush-Hour-Effekt (Tagesverlauf)
    fig_rush = an.rushHourEffekt(df_prepared, stoff)

    if fig_rush:

        # Grafik kompakter machen
        fig_rush.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_rush.axes[0]

        # Titel anpassen
        ax.set_title(
            f"Mittlerer {stoff.upper()}-Tagesverlauf (Rush-Hour-Effekt)",
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            "Uhrzeit (Stunde)",
            fontsize=LABEL_SIZE,
            fontweight="normal")

        ax.set_ylabel(
            f"{stoff.upper()} [µg/m³]",
            fontsize=LABEL_SIZE,
            fontweight="normal")

        # Zahlen auf Achsen
        ax.tick_params(
            axis='both',
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_rush, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen deutlichen Tagesverlauf der Ozonkonzentration mit niedrigen Werten in den frühen Morgenstunden und einem Maximum am Nachmittag. Dies deutet auf den Einfluss photochemischer Prozesse sowie die Wechselwirkung zwischen Sonneneinstrahlung und Stickoxiden bei der Ozonbildung hin.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt deutliche NO₂-Spitzen während der morgendlichen und abendlichen Hauptverkehrszeiten. Besonders in den Abendstunden steigen die Konzentrationen stark an, was auf erhöhte Verkehrsemissionen sowie eine geringere Verdünnung und Durchmischung der Schadstoffe in der Luft hinweist.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen typischen Tagesverlauf der PM10- und PM2.5-Konzentrationen mit erhöhten Werten in den frühen Morgen- und Abendstunden. Besonders bei PM10 sind Spitzen während der Hauptverkehrszeiten erkennbar, was auf den Einfluss des Straßenverkehrs und weiterer menschlicher Aktivitäten hinweist. In den Nachmittagsstunden sinken die Konzentrationen dagegen deutlich ab.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True)

    st.divider()

    # 4. Inversionswetterlage
    fig_inversion = an.inversionswetter(df_prepared, stoff)

    if fig_inversion:

        # Grafik kompakter machen
        fig_inversion.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_inversion.axes[0]

        # oberen Zusatztitel entfernen
        fig_inversion.suptitle("")

        # Titel anpassen
        ax.set_title(
            ax.get_title(),
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            ax.get_xlabel(),
            fontsize=LABEL_SIZE,
            fontweight="bold")

        ax.set_ylabel(
            ax.get_ylabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal")

        # Zahlen auf Achsen
        ax.tick_params(
            axis='both',
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_inversion, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt deutlich niedrigere Ozonkonzentrationen während Inversionslagen mit windstillen und wolkenlosen Wetterbedingungen. Dies weist darauf hin, dass Ozon in bodennahen Smogsituationen durch Stickoxide verstärkt abgebaut wird.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die niedrigeren NO₂-Konzentrationen bei wolkenlosen und windstillen Wetterlagen deuten auf photochemische Umwandlungsprozesse hin. Unter intensiver Sonneneinstrahlung wird Stickstoffdioxid verstärkt in Ozon umgewandelt, wodurch die gemessenen NO₂-Werte trotz stabiler Wetterlage sinken können.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt, dass die PM10-Konzentrationen während Inversionslagen deutlich höher ausfallen als bei normalen Wetterbedingungen. Besonders bei windstillem und wolkenlosem Wetter können sich Feinstaubpartikel stärker in Bodennähe ansammeln, da die Luft schlechter durchmischt wird. Dadurch steigt die Belastung durch Feinstaub spürbar an.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
        """
        <div style="margin-top: 50px;"></div>
        """,
        unsafe_allow_html=True)

    st.divider()

    # 5. Jährliche LQI-Überschreitungen
    fig_exceed = an.getExceedancesPerYear(df_prepared, stoff)

    if fig_exceed:

        # Grafik kompakter machen
        fig_exceed.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_exceed.axes[0]

        # Titel anpassen
        ax.set_title(
            ax.get_title(),
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            ax.get_xlabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal")

        ax.set_ylabel(
            ax.get_ylabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal")

        # Zahlen auf Achsen
        ax.tick_params(
            axis="both",
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_exceed, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3"):

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Anzahl der Stunden mit mindestens mäßiger Ozonbelastung ist seit den 1980er-Jahren deutlich angestiegen. Besonders in den letzten Jahren treten erhöhte Ozonkonzentrationen häufiger auf, was auf veränderte klimatische und meteorologische Bedingungen hinweist.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2"):

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Anzahl der Stunden mit mindestens mäßiger NO₂-Belastung steigt zunächst bis in die frühen 2000er-Jahre an. Anschließend zeigt sich ein deutlicher Rückgang, besonders seit etwa 2010. Dies deutet auf eine langfristige Verbesserung der Luftqualität hin, die unter anderem mit strengeren Emissionsvorgaben und moderneren Fahrzeug- und Heiztechnologien zusammenhängen könnte.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10"):

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt einen langfristigen Rückgang der Stunden mit mindestens mäßiger Feinstaubbelastung für PM10 und PM2.5. Besonders seit den 2000er-Jahren treten belastete Stunden deutlich seltener auf, was auf Verbesserungen der Luftqualität sowie auf strengere Emissions- und Umweltmaßnahmen hinweisen kann. Trotz einzelner Schwankungen ist insgesamt ein klarer positiver Trend erkennbar.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
            """
            <div style="margin-top: 50px;"></div>
            """,
            unsafe_allow_html=True)

    st.divider()

    # 6. Jahreszeit
    fig_season, fig_weekend = an.analyzeSeasonAndWeekend(df_prepared, stoff)

    if fig_season:

        # Grafik kompakter machen
        fig_season.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_season.axes[0]

        # Titel anpassen
        ax.set_title(
            ax.get_title(),
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            ax.get_xlabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal")

        ax.set_ylabel(
            ax.get_ylabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal")

        # Zahlen auf Achsen
        ax.tick_params(
            axis="both",
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_season, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die höchsten Ozonkonzentrationen treten im Sommer und Frühjahr auf, während im Herbst und Winter deutlich niedrigere Werte gemessen werden. Dies verdeutlicht den starken Einfluss von Sonneneinstrahlung und höheren Temperaturen auf die Ozonbildung.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die NO₂-Werte sind im Sommer am niedrigsten und im Winter am höchsten. Ursache dafür sind im Sommer stärkere Sonneneinstrahlung, intensivere photochemische Prozesse und eine bessere Durchmischung der Luft, während sich Schadstoffe im Winter durch geringere Sonneneinstrahlung, stabilere Luftschichten und zusätzliche Emissionen aus dem Heizungs- und Verkehrssektor höhere Konzentrationen anreichern können.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt höhere PM10- und PM2.5-Werte in den Herbst- und Wintermonaten, während die niedrigsten Konzentrationen im Sommer auftreten. Besonders im Winter kann sich Feinstaub durch Heizungen, Verkehr und schlechtere Luftdurchmischung stärker in Bodennähe ansammeln. Im Sommer sorgen günstigere Wetterbedingungen dagegen meist für niedrigere Belastungen.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
            """
            <div style="margin-top: 50px;"></div>
            """,
            unsafe_allow_html=True)

    st.divider()
    
    # 7. Werktag/Wochenende
    if fig_weekend:

        # Grafik kompakter machen
        fig_weekend.set_size_inches(10, 5.5)

        # Einheitliche Schriftgrößen
        TITLE_SIZE = 19
        LABEL_SIZE = 12
        TICK_SIZE = 10

        # Achse holen
        ax = fig_weekend.axes[0]

        # Titel anpassen
        ax.set_title(
            ax.get_title(),
            fontsize=TITLE_SIZE,
            fontweight="normal",
            color="white",
            pad=15)

        # Achsenbeschriftungen
        ax.set_xlabel(
            ax.get_xlabel(),
            fontsize=LABEL_SIZE,
            fontweight="bold")

        ax.set_ylabel(
            ax.get_ylabel(),
            fontsize=LABEL_SIZE,
            fontweight="normal")

        # Zahlen auf Achsen
        ax.tick_params(
            axis="both",
            labelsize=TICK_SIZE)

        # Grafik anzeigen
        st.pyplot(fig_weekend, use_container_width=False)

        # Beschreibung unter der Grafik
        if (stoff == "o3") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt höhere durchschnittliche Ozonkonzentrationen an Wochenenden im Vergleich zu Werktagen. Dies könnte auf geringere Stickoxid-Emissionen durch den Straßenverkehr und damit einen verminderten Ozonabbau zurückzuführen sein.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "no2") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die NO₂-Konzentrationen sind an Werktagen höher als am Wochenende. Dies deutet auf den Einfluss des Berufs- und Pendlerverkehrs hin, da Stickstoffdioxid hauptsächlich durch Verbrennungsprozesse im Straßenverkehr entsteht.
            </div>
            """, unsafe_allow_html=True)

        elif (stoff == "pm10") :

            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt höhere PM10- und PM2.5-Konzentrationen an Werktagen im Vergleich zum Wochenende. Dies deutet darauf hin, dass vor allem Verkehr und andere menschliche Aktivitäten während der Arbeitswoche zur erhöhten Feinstaubbelastung beitragen. Am Wochenende fallen die Konzentrationen dagegen insgesamt etwas niedriger aus.
            </div>
            """, unsafe_allow_html=True)

        # Abstand zur nächsten Grafik
        st.markdown(
            """
            <div style="margin-top: 50px;"></div>
            """,
            unsafe_allow_html=True)

    st.divider()

    # 8. Silvester-Effekt (nur für PM10)
    if (stoff == "pm10"):

        fig_silvester = sil.analyseSilvesterTime(df_prepared, stoff)

        if fig_silvester is not None:

            # Grafik kompakter machen
            fig_silvester.set_size_inches(10, 5.5)

            # Einheitliche Schriftgrößen
            TITLE_SIZE = 19
            LABEL_SIZE = 12
            TICK_SIZE = 10

            # Achse holen
            ax = fig_silvester.axes[0]

            # Titel anpassen
            ax.set_title(
                ax.get_title(),
                fontsize=TITLE_SIZE,
                fontweight="normal",
                color="white",
                pad=15)

            # Achsenbeschriftungen
            ax.set_xlabel(
                ax.get_xlabel(),
                fontsize=LABEL_SIZE,
                fontweight="normal")

            ax.set_ylabel(
                ax.get_ylabel(),
                fontsize=LABEL_SIZE,
                fontweight="normal")

            # Zahlen auf Achsen
            ax.tick_params(
                axis="both",
                labelsize=TICK_SIZE)

            # Grafik anzeigen
            st.pyplot(fig_silvester, use_container_width=False)

            # Beschreibung unter der Grafik
            st.markdown("""
            <div style='max-width: 1000px; font-size: 0.95rem; color: #B8B8B8;'>
            Die Grafik zeigt den Verlauf der PM10-Konzentrationen rund um den Jahreswechsel. Während der Weihnachtstage (24.12.–26.12.) sinken die Feinstaubwerte zunächst, was unter anderem auf geringeres Verkehrsaufkommen und reduzierte Aktivitäten während der Feiertage hinweisen könnte.<br><br>

            Ab dem 27.12. steigen die Werte wieder an. Besonders auffällig ist der starke Peak am 01.01., der wahrscheinlich auf Feuerwerkskörper und erhöhte Feinstaubemissionen in der Silvesternacht zurückzuführen ist. Bereits kurz danach sinken die Werte wieder deutlich ab.
            </div>
            """, unsafe_allow_html=True)

            # Abstand zur nächsten Grafik
            st.markdown(
                """
                <div style="margin-top: 50px;"></div>
                """,
                unsafe_allow_html=True)
    return


# ============================================================
# Datensatz laden und vorbereiten (wird im gesamten Projekt verwendet)
# ============================================================
@st.cache_data
def load ():
    """
    Lädt die kombinierten Wetter- und Schadstoffdaten aus der CSV-Datei.
    """
    base_dir = Path(__file__).parent
    data_pfad = base_dir / 'data' / 'Schadstoff_Wetter.csv'

    dfRead = pd.read_csv(data_pfad)

    dfRead['datum'] = pd.to_datetime(dfRead['datum'])
    
    dfRead ['datumstunde'] = pd.to_datetime(
        dfRead ['datumstunde'].astype(str), 
        format='%Y%m%d%H', 
        errors='coerce')
    
    spaltenList = ['datum', 'stunde', 'temperatur', 'luftfeuchtigkeit',  'windgeschwindigkeit', 'windrichtung',  'luftdruck', 'niederschlagshoehe_mm', 'sonnenscheindauer_minuten', 'relative_luftfeuchtigkeit', 'gesamtbewoelkung', 'no2', 'o3', 'pm10', 'pm2x5']
    dfO = dfRead[spaltenList].copy()
    return dfO 

# ============================================================
# Laden der Daten
# ============================================================
dfOrginal = load()

# ============================================================
# SIDEBAR-KONFIGURATION
# ============================================================
with st.sidebar:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] > div {
        padding-top: 1.2rem !important;}
    
    .sidebar-item {
    margin-bottom: 16px;}
                
    .sidebar-title {
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 8px;}

    .sidebar-section-title {
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 4px;}

    .sidebar-divider {
        margin: 14px 0 14px 0;
        border-top: 1px solid rgba(255,255,255,0.16);}

    div[role="radiogroup"] label {
        padding: 0px 0 !important;
        margin: 0px 0 !important;}

    div[role="radiogroup"] p {
        font-size: 17px !important;
        line-height: 1.2 !important;
        font-weight: 600 !important;}

    .sidebar-text {
        font-size: 14px;
        line-height: 1.45;}

    .sidebar-text b {
        font-size: 15px;}

    .sidebar-gap {
        height: 10px;}

    .sidebar-data-box {
        background-color: rgba(3, 149, 176, 0.1);
        padding: 9px 11px;
        border-radius: 0.5rem;
        border: 1px solid rgba(1, 132, 157, 0.8);
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        color: #FAFAFA;
        line-height: 1.35;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>🌦️ Filter</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-title'>Schadstoff-Auswahl:</div>", unsafe_allow_html=True)

    schadstoff_auswahl = st.radio(
        "",
        ["Ozon (O₃)", "Stickstoffdioxid (NO₂)", "Feinstaub (PM10 & PM2.5)"],
        label_visibility="collapsed")

    stoff_spalte = STOFF_MAP.get(schadstoff_auswahl, "no2")

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="sidebar-data-box">
            ✅ Daten erfolgreich geladen:<br>
            {len(dfOrginal):,} Zeilen
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    st.markdown("""
<div class="sidebar-text">

<div class="sidebar-item">
<b>Projekt:</b><br>
Analyse und Vorhersage von Wetter- und Luftqualitätsdaten
</div>

<div class="sidebar-item">
<b>Region:</b><br>
Nürnberg
</div>

<div class="sidebar-item">
<b>Projektzeitraum:</b><br>
11.05.2026 – 29.05.2026
</div>

<div class="sidebar-item">
<b>Projektteam:</b><br>
Christina Dürbeck<br>
Markus Edelhoff                
</div>

</div>
""", unsafe_allow_html=True)

# ============================================================
# TAB-DESIGN ANPASSEN
# ============================================================

st.markdown("""
<style>

/* TAB LEISTE */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px;
}

/* EINZELNE TABS */
button[data-baseweb="tab"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    min-height: 54px !important;

    /* WICHTIG */
    padding: 0 12px !important;

    background-color: transparent !important;

    border: none !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;

    transition: all 0.2s ease-in-out;
}

/* LETZTE LINIE WEG */
button[data-baseweb="tab"]:last-child {
    border-right: none !important;}

/* TAB TEXT */
button[data-baseweb="tab"] p {
    font-size: 15px !important;
    font-weight: 600 !important;

    margin: 0 !important;
    text-align: center !important;

    line-height: 1.2 !important;}

/* AKTIVER TAB */
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #00B5E2 !important;}

/* HOVER */
button[data-baseweb="tab"]:hover {
    background-color: rgba(255,255,255,0.025) !important;}

</style>
""", unsafe_allow_html=True)

# ============================================================
# 02 TABS DEFINIEREN & SEITENSTRUKTUR
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(
    ["Startseite", "Wetterdaten", "Explorative Analyse", "Korrelationsanalyse",
     "Multiple Regression", "Random Forest", "Vorhersage Live", "Vorhersage", "Fazit", "Technische Insights"])

# ------------------------------------------------------------
# TAB 1: Einleitung & Überblick
# ------------------------------------------------------------
# =========================
# TITEL & EINLEITUNG
# =========================
with tab1:
    t.showTab1 ()
# ------------------------------------------------------------
# TAB 2: WETTERDATEN
# ------------------------------------------------------------
with tab2:
    t.showTab2 ()
# ============================================================
# TAB 3: EXPLORATIVE ANALYSE / LUFTQUALITÄT
# ============================================================
with tab3:
    t.showTab3 ()
# ============================================================
# TAB 4: KORRELATIONSANALYSE
# ============================================================
with tab4:
    t.showTab4 ()
# ============================================================
# TAB 5: MULTIPLE REGRESSION
# ============================================================
with tab5:
    t.showTab5 ()
# ============================================================
# TAB 6: RANDOM FOREST
# ============================================================
with tab6:
    t.showTab6 ()
# ============================================================
# TAB 7: VORHERSAGE1
# ============================================================
with tab7:
    t.showTab8 ()
# ============================================================
# TAB 8: VORHERSAGE2
# ============================================================
with tab8:
    t.showTab7 ()
# ============================================================
# TAB 9: FAZIT
# ============================================================
with tab9:
    st.header("Fazit und Ausblick")

    st.markdown("""
    Die Analyse zeigt, dass Wetterbedingungen einen messbaren Einfluss auf die Luftqualität in Nürnberg haben. 
    Besonders deutlich werden die Zusammenhänge bei Ozon, während Stickstoffdioxid und Feinstaub zusätzlich stark 
    durch weitere Einflussfaktoren geprägt werden.
    """)

    st.divider()

    st.subheader("Zentrale Erkenntnisse")

    st.markdown("""
    #### 🌞 Ozon (O₃)
    Steigt vor allem bei hohen Temperaturen und intensiver Sonneneinstrahlung an.  
    Die Analyse zeigt, dass Ozon stark durch meteorologische Bedingungen beeinflusst wird. Aufgrund steigender Temperaturen und zunehmender Hitzeperioden könnten Ozonbelastungen künftig weiter an Bedeutung gewinnen. 
    
    Zusätzlich besteht eine enge Wechselwirkung zwischen Ozon und Stickstoffdioxid. Obwohl sinkende NO₂-Werte grundsätzlich positiv sind, können sie unter bestimmten Bedingungen dazu führen, dass Ozon langsamer abgebaut wird und dadurch höhere Ozonkonzentrationen entstehen.

    ### 🚗 Stickstoffdioxid (NO₂)
    Zeigt langfristig eher sinkende Werte.  
    Dies kann unter anderem auf technische Entwicklungen, strengere Emissionsvorgaben und Veränderungen im Verkehrssektor hindeuten.

    ### 🌫️ Feinstaub (PM10 und PM2.5)
    Weist ebenfalls rückläufige Tendenzen auf.  
    Gleichzeitig zeigen die Analysen, dass Feinstaub besonders bei Inversionslagen, geringer Luftdurchmischung und verkehrsnahen Situationen erhöht auftreten kann.

    ### ❤️ Gesundheitliche Bedeutung
    Trotz teilweise sinkender Schadstoffwerte bleibt Luftverschmutzung weiterhin ein relevantes Gesundheitsthema. Besonders erhöhte Ozonwerte können die Atemwege belasten und stehen in Zusammenhang mit gesundheitlichen Risiken für empfindliche Personengruppen.

    ### 🌍 Regionale Unterschiede
    Die Analyse verdeutlicht außerdem, dass Luftqualität regional sehr unterschiedlich ausfallen kann. Während in Nürnberg teilweise rückläufige Entwicklungen erkennbar sind, können Luftschadstoffbelastungen in anderen Regionen oder Großstädten deutlich stärker ausfallen.

    ### 📊 Grenzen der Wetterdaten
    Wetterdaten allein erklären die Luftqualität nur teilweise. Die multiple Regression zeigt, dass meteorologische Variablen zwar signifikante Zusammenhänge aufweisen, die Erklärungskraft jedoch begrenzt bleibt.

    ### ⏱️ Zeitliche Muster
    Zeitliche Variablen verbessern die Vorhersage deutlich. Durch Faktoren wie Stunde, Monat, Wochenende oder Rush Hour können typische Tages- und Jahresmuster besser abgebildet werden.
    """)

    st.divider()

    st.subheader("Ausblick")

    st.markdown("""
    * Das Projekt zeigt, dass datenbasierte Verfahren wie Korrelationsanalysen, multiple lineare Regression und Random-Forest-Modelle geeignet sind, Zusammenhänge zwischen Wetter und Luftqualität sichtbar zu machen.
                
    * Die Analyse bezieht sich ausschließlich auf die Region Nürnberg. Für zukünftige Untersuchungen könnten weitere Städte, Regionen oder internationale Datensätze integriert werden, um Unterschiede zwischen verschiedenen Umwelt- und Klimabedingungen besser vergleichen zu können.
                
    * Für präzisere Vorhersagen sollten zusätzlich weitere Einflussfaktoren wie Verkehrsdaten, Industrieemissionen, Heizverhalten oder historische Schadstoffwerte ergänzt werden. Dadurch könnten insbesondere die Vorhersagen von Stickstoffdioxid und Feinstaub weiter verbessert werden.
                
    * Insgesamt verdeutlicht das Projekt, dass Luftqualität ein komplexes Zusammenspiel aus Wetter, menschlichen Aktivitäten und zeitlichen Mustern darstellt und weiterhin eine wichtige Rolle für Umwelt und Gesundheit spielt.
    """)


    with st.expander("💡 Mögliche Erweiterungen für zukünftige Analysen"):

        st.markdown("""
        - Einbindung zusätzlicher Verkehrsdaten zur Verbesserung der Vorhersage von Stickstoffdioxid (NO₂)
        - Berücksichtigung weiterer Emissionsquellen wie Industrieanlagen, Heizsysteme oder Baustellen
        - Integration historischer Schadstoffmesswerte zur Verbesserung kurzfristiger Vorhersagen
        - Erweiterung der Analyse auf weitere Städte und Regionen zur Untersuchung regionaler Unterschiede
        - Vergleich unterschiedlicher Messstationen innerhalb Nürnbergs oder Bayerns
        - Berücksichtigung detaillierter meteorologischer Einflussfaktoren wie Inversionslagen, Luftaustausch oder Windströmungen
        - Einsatz weiterer Machine-Learning-Verfahren wie Gradient Boosting oder neuronaler Netze
        - Entwicklung eines automatisierten Warnsystems für erhöhte Luftschadstoffbelastungen
        - Verknüpfung von Luftqualitäts- und Gesundheitsdaten zur Untersuchung möglicher gesundheitlicher Auswirkungen
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    st.success("""
    Zusammenfassend zeigt das Dashboard: Wetter- und Zeitfaktoren liefern wichtige Hinweise auf die Entwicklung der Luftqualität. 
    Für präzisere Vorhersagen müssen jedoch zusätzliche Emissionsquellen und lokale Einflussfaktoren berücksichtigt werden.
    """)

# ============================================================
# TAB 10: TECHNISCHE INSIGHTS
# ============================================================
with tab10:
    st.header("Technische Insights")

    def render_tech_tab():
        skript_ordner = Path(__file__).parent
        css_datei = skript_ordner / "tech_tab.css"
        html_datei = skript_ordner / "tech_tab_content.html"  # JETZT KORREKT
        try:
            # 1. CSS laden und rendern
            css_inhalt = css_datei.read_text(encoding="utf-8")
            st.markdown(f"<style>{css_inhalt}</style>", unsafe_allow_html=True)
    
            # 2. HTML-Content laden und rendern
            html_inhalt = html_datei.read_text(encoding="utf-8")
            st.html(html_inhalt)  # st.html rendert reines HTML sauber
        except FileNotFoundError:
              st.error(f"Die Datei '{css_datei.name}' wurde nicht gefunden.")

    render_tech_tab()
