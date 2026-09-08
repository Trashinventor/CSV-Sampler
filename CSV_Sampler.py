#Moritz Rambold 09/2026

import csv
import math
import tkinter as tk
from tkinter import filedialog, messagebox


# ============================================================
# Header suchen
# ============================================================

def find_header(input_file):
    """
    Sucht die erste Zeile, deren erste Spalte 'TIME' ist.
    Der restliche Header ist beliebig.
    """

    with open(
        input_file,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.reader(f)

        for line_number, row in enumerate(reader):

            if not row:
                continue

            if row[0].strip().upper() == "TIME":
                return line_number

    raise ValueError(
        'Keine Header-Zeile mit "TIME" als erster Spalte gefunden.'
    )


# ============================================================
# Datenzeilen zählen
# ============================================================

def count_data_rows(input_file, header_line):
    """
    Zählt die nicht-leeren Datenzeilen nach dem Header.
    """

    count = 0

    with open(
        input_file,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.reader(f)

        for line_number, row in enumerate(reader):

            if line_number <= header_line:
                continue

            if not any(value.strip() for value in row):
                continue

            count += 1

    return count


# ============================================================
# CSV verarbeiten
# ============================================================

def process_csv(
    input_file,
    output_file,
    desired_samples,
    time_factor
):

    # --------------------------------------------------------
    # Header suchen
    # --------------------------------------------------------

    header_line = find_header(input_file)

    # --------------------------------------------------------
    # Anzahl Datenzeilen bestimmen
    # --------------------------------------------------------

    number_of_rows = count_data_rows(
        input_file,
        header_line
    )

    if number_of_rows == 0:
        raise ValueError(
            "Die CSV-Datei enthält keine Datenzeilen."
        )

    # --------------------------------------------------------
    # Schrittweite berechnen
    # --------------------------------------------------------

    n = max(
        1,
        math.ceil(number_of_rows / desired_samples)
    )

    # --------------------------------------------------------
    # Datei zeilenweise verarbeiten
    # --------------------------------------------------------

    samples_written = 0
    data_index = 0

    with open(
        input_file,
        "r",
        encoding="utf-8",
        newline=""
    ) as infile:

        reader = csv.reader(infile)

        with open(
            output_file,
            "w",
            encoding="utf-8",
            newline=""
        ) as outfile:

            writer = csv.writer(outfile)

            for line_number, row in enumerate(reader):

                # Alles vor dem Header ignorieren
                if line_number < header_line:
                    continue

                # Header unverändert übernehmen
                if line_number == header_line:
                    writer.writerow(row)
                    continue

                # Leere Zeilen überspringen
                if not any(value.strip() for value in row):
                    continue

                # Jede n-te Datenzeile auswählen
                if data_index % n == 0:

                    if len(row) == 0:
                        continue

                    # ------------------------------------------------
                    # TIME auslesen
                    # Unterstützt z.B.:
                    #
                    # 0.00001
                    # 1e-05
                    # 1.23e-05
                    # 4.5E-06
                    # ------------------------------------------------

                    try:
                        time_value = float(row[0])

                    except ValueError:
                        raise ValueError(
                            f'Ungültiger TIME-Wert in Zeile '
                            f'{line_number + 1}: "{row[0]}"'
                        )

                    # ------------------------------------------------
                    # TIME mit variablem Faktor multiplizieren
                    # ------------------------------------------------

                    time_value *= time_factor

                    # ------------------------------------------------
                    # TIME formatieren
                    # ------------------------------------------------

                    if time_value.is_integer():

                        row[0] = str(int(time_value))

                    else:

                        row[0] = (
                            f"{time_value:.10f}"
                            .rstrip("0")
                            .rstrip(".")
                        )

                    # ------------------------------------------------
                    # Zeile schreiben
                    # ------------------------------------------------

                    writer.writerow(row)

                    samples_written += 1

                data_index += 1

    # --------------------------------------------------------
    # Ergebnis zurückgeben
    # --------------------------------------------------------

    return {
        "header_line": header_line + 1,
        "data_rows": number_of_rows,
        "step": n,
        "samples": samples_written
    }


# ============================================================
# Eingabedatei auswählen
# ============================================================

def select_input():

    filename = filedialog.askopenfilename(
        title="CSV-Eingabedatei auswählen",
        filetypes=[
            ("CSV-Dateien", "*.csv"),
            ("Alle Dateien", "*.*")
        ]
    )

    if filename:

        input_path.set(filename)

        # Automatischen Ausgabepfad erzeugen
        if not output_path.get():

            if filename.lower().endswith(".csv"):

                suggested = (
                    filename[:-4]
                    + "_sampled.csv"
                )

            else:

                suggested = (
                    filename
                    + "_sampled.csv"
                )

            output_path.set(suggested)


# ============================================================
# Ausgabedatei auswählen
# ============================================================

def select_output():

    filename = filedialog.asksaveasfilename(
        title="CSV-Ausgabedatei auswählen",
        defaultextension=".csv",
        filetypes=[
            ("CSV-Dateien", "*.csv"),
            ("Alle Dateien", "*.*")
        ]
    )

    if filename:
        output_path.set(filename)


# ============================================================
# Verarbeitung starten
# ============================================================

def start_processing():

    input_file = input_path.get().strip()
    output_file = output_path.get().strip()
    samples_text = samples_entry.get().strip()
    time_factor_text = time_factor_entry.get().strip()

    # --------------------------------------------------------
    # Eingabedatei prüfen
    # --------------------------------------------------------

    if not input_file:

        messagebox.showerror(
            "Fehler",
            "Bitte eine Eingabedatei auswählen."
        )

        return

    # --------------------------------------------------------
    # Ausgabedatei prüfen
    # --------------------------------------------------------

    if not output_file:

        messagebox.showerror(
            "Fehler",
            "Bitte eine Ausgabedatei auswählen."
        )

        return

    # --------------------------------------------------------
    # Sample-Anzahl prüfen
    # --------------------------------------------------------

    if not samples_text:

        messagebox.showerror(
            "Fehler",
            "Bitte die gewünschte Anzahl Samples eingeben."
        )

        return

    try:

        desired_samples = int(samples_text)

    except ValueError:

        messagebox.showerror(
            "Fehler",
            "Die Sample-Anzahl muss eine ganze Zahl sein."
        )

        return

    if desired_samples <= 0:

        messagebox.showerror(
            "Fehler",
            "Die Sample-Anzahl muss größer als 0 sein."
        )

        return

    # --------------------------------------------------------
    # TIME-Faktor prüfen
    # --------------------------------------------------------

    if not time_factor_text:

        messagebox.showerror(
            "Fehler",
            "Bitte einen TIME-Faktor eingeben."
        )

        return

    try:

        # Erlaubt z.B.:
        #
        # 1000000
        # 1000
        # 0.001
        # 1e6
        # 1E-3

        time_factor = float(
            time_factor_text
        )

    except ValueError:

        messagebox.showerror(
            "Fehler",
            "Der TIME-Faktor muss eine Zahl sein."
        )

        return

    if time_factor == 0:

        messagebox.showerror(
            "Fehler",
            "Der TIME-Faktor darf nicht 0 sein."
        )

        return

    # --------------------------------------------------------
    # Eingabe- und Ausgabedatei vergleichen
    # --------------------------------------------------------

    if input_file.lower() == output_file.lower():

        messagebox.showerror(
            "Fehler",
            "Eingabe- und Ausgabedatei dürfen nicht identisch sein."
        )

        return

    # --------------------------------------------------------
    # CSV verarbeiten
    # --------------------------------------------------------

    try:

        result = process_csv(
            input_file,
            output_file,
            desired_samples,
            time_factor
        )

    except Exception as error:

        messagebox.showerror(
            "Fehler bei der Verarbeitung",
            str(error)
        )

        return

    # --------------------------------------------------------
    # Ergebnistext erzeugen
    # --------------------------------------------------------

    result_text = (
        "Verarbeitung erfolgreich!\n"
        "\n"
        f"Header:              Zeile {result['header_line']}\n"
        f"Datenzeilen:         {result['data_rows']:,}\n"
        f"Gewünschte Samples:  {desired_samples:,}\n"
        f"Schrittweite:        {result['step']:,}\n"
        f"Erzeugte Samples:    {result['samples']:,}\n"
        f"TIME-Faktor:         {time_factor:g}\n"
        "\n"
        f"Ausgabedatei:\n"
        f"{output_file}"
    )

    # --------------------------------------------------------
    # Ergebnisbox aktualisieren
    # --------------------------------------------------------

    result_textbox.config(
        state="normal"
    )

    result_textbox.delete(
        "1.0",
        tk.END
    )

    result_textbox.insert(
        "1.0",
        result_text
    )

    result_textbox.config(
        state="disabled"
    )

    result_textbox.see("1.0")

    # --------------------------------------------------------
    # Fertigmeldung
    # --------------------------------------------------------

    messagebox.showinfo(
        "Fertig",
        "CSV-Datei erfolgreich erstellt.\n\n"
        f"{result['samples']:,} Samples geschrieben."
    )


# ============================================================
# GUI erstellen
# ============================================================

root = tk.Tk()

root.title(
    "CSV Sample Tool"
)

# Fenstergröße
root.geometry(
    "1000x650"
)

# Mindestgröße
root.minsize(
    900,
    600
)

# Fenster darf vergrößert werden
root.resizable(
    True,
    True
)


# ============================================================
# GUI-Variablen
# ============================================================

input_path = tk.StringVar()
output_path = tk.StringVar()


# ============================================================
# Haupt-Frame
# ============================================================

main_frame = tk.Frame(
    root
)

main_frame.pack(
    fill="both",
    expand=True,
    padx=40,
    pady=30
)


# ============================================================
# Überschrift
# ============================================================

tk.Label(
    main_frame,
    text="CSV Sample Tool",
    font=("Arial", 24, "bold")
).pack(
    pady=(0, 30)
)


# ============================================================
# Eingabedatei
# ============================================================

input_frame = tk.Frame(
    main_frame
)

input_frame.pack(
    fill="x",
    pady=8
)


tk.Label(
    input_frame,
    text="Eingabedatei:",
    width=20,
    anchor="w",
    font=("Arial", 11)
).pack(
    side="left"
)


tk.Entry(
    input_frame,
    textvariable=input_path,
    font=("Arial", 11)
).pack(
    side="left",
    fill="x",
    expand=True,
    padx=10
)


tk.Button(
    input_frame,
    text="Durchsuchen...",
    command=select_input,
    font=("Arial", 10),
    padx=10
).pack(
    side="right"
)


# ============================================================
# Ausgabedatei
# ============================================================

output_frame = tk.Frame(
    main_frame
)

output_frame.pack(
    fill="x",
    pady=8
)


tk.Label(
    output_frame,
    text="Ausgabedatei:",
    width=20,
    anchor="w",
    font=("Arial", 11)
).pack(
    side="left"
)


tk.Entry(
    output_frame,
    textvariable=output_path,
    font=("Arial", 11)
).pack(
    side="left",
    fill="x",
    expand=True,
    padx=10
)


tk.Button(
    output_frame,
    text="Durchsuchen...",
    command=select_output,
    font=("Arial", 10),
    padx=10
).pack(
    side="right"
)


# ============================================================
# Sample-Anzahl
# ============================================================

samples_frame = tk.Frame(
    main_frame
)

samples_frame.pack(
    fill="x",
    pady=(25, 8)
)


tk.Label(
    samples_frame,
    text="Gewünschte Samples:",
    width=20,
    anchor="w",
    font=("Arial", 11)
).pack(
    side="left"
)


samples_entry = tk.Entry(
    samples_frame,
    width=20,
    font=("Arial", 11)
)

samples_entry.pack(
    side="left",
    padx=10
)

samples_entry.insert(
    0,
    "10000"
)


# ============================================================
# TIME-Faktor
# ============================================================

time_factor_frame = tk.Frame(
    main_frame
)

time_factor_frame.pack(
    fill="x",
    pady=8
)


tk.Label(
    time_factor_frame,
    text="TIME-Faktor:",
    width=20,
    anchor="w",
    font=("Arial", 11)
).pack(
    side="left"
)


time_factor_entry = tk.Entry(
    time_factor_frame,
    width=20,
    font=("Arial", 11)
)

time_factor_entry.pack(
    side="left",
    padx=10
)

# Standardwert
time_factor_entry.insert(
    0,
    "1000000"
)


tk.Label(
    time_factor_frame,
    text="z.B. 1000000, 1000, 0.001 oder 1e6",
    font=("Arial", 9),
    fg="gray"
).pack(
    side="left",
    padx=5
)


# ============================================================
# Start-Button
# ============================================================

tk.Button(
    main_frame,
    text="CSV verarbeiten",
    command=start_processing,
    font=("Arial", 13, "bold"),
    bg="#4CAF50",
    fg="white",
    padx=40,
    pady=12
).pack(
    pady=25
)


# ============================================================
# Ergebnisüberschrift
# ============================================================

tk.Label(
    main_frame,
    text="Ergebnis",
    font=("Arial", 14, "bold"),
    anchor="w"
).pack(
    fill="x",
    pady=(10, 5)
)


# ============================================================
# Ergebnisbereich
# ============================================================

result_frame = tk.Frame(
    main_frame,
    bd=1,
    relief="solid"
)

result_frame.pack(
    fill="both",
    expand=True
)


# ============================================================
# Ergebnis-Textfeld
# ============================================================

result_textbox = tk.Text(
    result_frame,
    wrap="none",
    font=("Consolas", 11),
    bg="#f5f5f5",
    padx=15,
    pady=15,
    state="disabled"
)

result_textbox.grid(
    row=0,
    column=0,
    sticky="nsew"
)


# ============================================================
# Vertikale Scrollbar
# ============================================================

vertical_scrollbar = tk.Scrollbar(
    result_frame,
    orient="vertical",
    command=result_textbox.yview
)

vertical_scrollbar.grid(
    row=0,
    column=1,
    sticky="ns"
)


# ============================================================
# Horizontale Scrollbar
# ============================================================

horizontal_scrollbar = tk.Scrollbar(
    result_frame,
    orient="horizontal",
    command=result_textbox.xview
)

horizontal_scrollbar.grid(
    row=1,
    column=0,
    sticky="ew"
)


# ============================================================
# Textfeld mit Scrollbars verbinden
# ============================================================

result_textbox.configure(
    yscrollcommand=vertical_scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set
)


# ============================================================
# Grid-Verhalten
# ============================================================

result_frame.grid_rowconfigure(
    0,
    weight=1
)

result_frame.grid_columnconfigure(
    0,
    weight=1
)


# ============================================================
# GUI starten
# ============================================================

root.mainloop()
