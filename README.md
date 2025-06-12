<!--
SPDX-FileCopyrightText: Copyright (c) 2025 Software GmbH, Darmstadt, Germany and/or its subsidiaries and/or its affiliates
SPDX-FileContributor: Dr. Gerald Ristow
SPDX-FileContributor: René Walter

SPDX-License-Identifier: Apache-2.0
-->

# opcua-browser
   - Dieses Projekt 
        - sucht innerhalb eines opcua-Baums nach Knoten mit dynamischen Werten
        - sammelt bei jedem selektierten Knoten über einen Zeitraum Messdaten, um jeweils eine Zeitreihe zu erstellen
        - klassifiziert jeden Knoten mithilfe eines auf [Machine Learning basierenden Modells](https://github.softwareag.com/y509314/KI4ETA/tree/main/ts-classificator/data-preprocessing)
        - generiert eine GUI, welche eine Expertenanalyse -und Korrektur bezüglich der Klassifizierung der Knoten zulässt.
        - Abschließend wird ein device-template für Cumulocity erstellt.

- Files
  - /rest
    - Hier werden die Blueprint-Templates eingelesen, welches vom Projekt modifiziert wird.
  - /output
    - Die generierten Cumulocity-templates werden hier gesichert
  - /history
    - Hier werden Funktionen gesichert, welche im aktuellen Projekt nicht mehr benötigt werden
  - browsing
    - Dieses Skript behandelt alle Schritte, um die dynamischen Knoten zu erfassen, eine Timeseries jeweils aufzubauen und anschließend diese zu klassifizieren
  - GUI
    - Wird von browsing aufgerufen und bekommt alle Werte, um eine GUI aufzubauen, welche eine Expertenmeinung für den labeling-Prozess zulässt.
