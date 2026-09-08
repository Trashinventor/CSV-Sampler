# by Moritz Rambold 09/2026

import csv
import math
import tkinter as tk
from tkinter import filedialog, messagebox


# ============================================================
# HEADER SUCHEN
# ============================================================

def find_header(input_file):
    """
    Sucht die erste Zeile, deren erste Spalte 'TIME' ist.
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
# ZAHL FORMATIEREN
# ============================================================

def format_number(value, decimal_places):
    """
    Formatiert einen numerischen Wert mit der gewünschten
    Anzahl Nachkommastellen.

    Unterstützt z.B.:

        123
        123.456
        -123.456
        1e-05
        1.23e-05
        4.5E+06

    Nicht-numerische Werte bleiben unverändert.
    """

    value = value.strip()

    if not value:
        return value

    try:
        number = float(value)

    except ValueError:
        return value

    return f"{number:.{decimal_places}f}"


# ============================================================
# DATENZEILEN IM ZEITBEREICH ZÄHLEN
# ============================================================

def count_data_rows(
    input_file,
    header_line,
    time_factor,
    start_time=None,
    end_time=None
):
    """
    Zählt die Datenzeilen innerhalb des Zeitbereichs.

    WICHTIG:
    Der Zeitbereich wird auf die TIME-Werte NACH Anwendung
    des TIME-Faktors angewendet.
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

            # Alles bis einschließlich Header überspringen
            if line_number <= header_line:
                continue

            # Leere Zeilen überspringen
            if not any(value.strip() for value in row):
                continue

            if len(row) == 0:
                continue

            # ------------------------------------------------
            # Original TIME auslesen
            # ------------------------------------------------

            try:

                original_time = float(
                    row[0]
                )

            except ValueError:

                raise ValueError(
                    f'Ungültiger TIME-Wert in Zeile '
                    f'{line_number + 1}: '
                    f'"{row[0]}"'
                )

            # ------------------------------------------------
            # TIME-Faktor anwenden
            # ------------------------------------------------

            scaled_time = (
                original_time * time_factor
            )

            # ------------------------------------------------
            # Zeitbereich prüfen
            #
            # Prüfung erfolgt auf der skalierten Zeit!
            # ------------------------------------------------

            if start_time is not None:

                if scaled_time < start_time:
                    continue

            if end_time is not None:

                if scaled_time > end_time:
                    continue

            count += 1

    return count


# ============================================================
# CSV VERARBEITEN
# ============================================================

def process_csv(
    input_file,
    output_file,
    desired_samples,
    time_factor,
    decimal_places,
    start_time=None,
    end_time=None
):

    # --------------------------------------------------------
    # Header suchen
    # --------------------------------------------------------

    header_line = find_header(
        input_file
    )

    # --------------------------------------------------------
    # Anzahl der Datenzeilen im Zeitbereich bestimmen
    # --------------------------------------------------------

    number_of_rows = count_data_rows(
        input_file,
        header_line,
        time_factor,
        start_time,
        end_time
    )

    if number_of_rows == 0:

        if start_time is not None or end_time is not None:

            raise ValueError(
                "Im ausgewählten Zeitbereich wurden "
                "keine Daten gefunden."
            )

        raise ValueError(
            "Die CSV-Datei enthält keine Datenzeilen."
        )

    # --------------------------------------------------------
    # Schrittweite berechnen
    # --------------------------------------------------------

    n = max(
        1,
        math.ceil(
            number_of_rows / desired_samples
        )
    )

    # --------------------------------------------------------
    # Dateien öffnen
    # --------------------------------------------------------

    samples_written = 0

    # Index innerhalb des ausgewählten Zeitbereichs
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

            # ------------------------------------------------
            # Zeilenweise Verarbeitung
            # ------------------------------------------------

            for line_number, row in enumerate(reader):

                # --------------------------------------------
                # Alles vor dem Header entfernen
                # --------------------------------------------

                if line_number < header_line:
                    continue

                # --------------------------------------------
                # Header übernehmen
                # --------------------------------------------

                if line_number == header_line:

                    writer.writerow(row)

                    continue

                # --------------------------------------------
                # Leere Zeilen überspringen
                # --------------------------------------------

                if not any(
                    value.strip()
                    for value in row
                ):
                    continue

                if len(row) == 0:
                    continue

                # --------------------------------------------
                # Original TIME lesen
                # --------------------------------------------

                try:

                    original_time = float(
                        row[0]
                    )

                except ValueError:

                    raise ValueError(
                        f'Ungültiger TIME-Wert in Zeile '
                        f'{line_number + 1}: '
                        f'"{row[0]}"'
                    )

                # --------------------------------------------
                # TIME-Faktor anwenden
                # --------------------------------------------

                scaled_time = (
                    original_time * time_factor
                )

                # --------------------------------------------
                # Zeitbereich prüfen
                #
                # WICHTIG:
                # scaled_time wird verwendet!
                # --------------------------------------------

                if start_time is not None:

                    if scaled_time < start_time:
                        continue

                if end_time is not None:

                    if scaled_time > end_time:
                        continue

                # --------------------------------------------
                # Jede n-te Zeile auswählen
                # --------------------------------------------

                if data_index % n == 0:

                    # ----------------------------------------
                    # TIME schreiben
                    # ----------------------------------------

                    row[0] = (
                        f"{scaled_time:.{decimal_places}f}"
                    )

                    # ----------------------------------------
                    # Alle weiteren Spalten formatieren
                    # ----------------------------------------

                    for column in range(
                        1,
                        len(row)
                    ):

                        row[column] = format_number(
                            row[column],
                            decimal_places
                        )

                    # ----------------------------------------
                    # Zeile schreiben
                    # ----------------------------------------

                    writer.writerow(row)

                    samples_written += 1

                # Nur Zeilen innerhalb des Zeitbereichs
                # zählen
                data_index += 1

    # --------------------------------------------------------
    # Ergebnis
    # --------------------------------------------------------

    return {
        "header_line": header_line + 1,
        "data_rows": number_of_rows,
        "step": n,
        "samples": samples_written
    }


# ============================================================
# EINGABEDATEI AUSWÄHLEN
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

        input_path.set(
            filename
        )

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

            output_path.set(
                suggested
            )


# ============================================================
# AUSGABEDATEI AUSWÄHLEN
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

        output_path.set(
            filename
        )


# ============================================================
# ZEITBEREICH AKTIVIEREN / DEAKTIVIEREN
# ============================================================

def toggle_time_range():

    if all_time_var.get():

        # ALL aktiviert

        start_time_entry.config(
            state="disabled"
        )

        end_time_entry.config(
            state="disabled"
        )

    else:

        # ALL deaktiviert

        start_time_entry.config(
            state="normal"
        )

        end_time_entry.config(
            state="normal"
        )


# ============================================================
# ERGEBNIS ANZEIGEN
# ============================================================

def show_result(text):

    result_textbox.config(
        state="normal"
    )

    result_textbox.delete(
        "1.0",
        tk.END
    )

    result_textbox.insert(
        "1.0",
        text
    )

    result_textbox.config(
        state="disabled"
    )

    result_textbox.see(
        "1.0"
    )


# ============================================================
# VERARBEITUNG STARTEN
# ============================================================

def start_processing():

    input_file = (
        input_path.get().strip()
    )

    output_file = (
        output_path.get().strip()
    )

    samples_text = (
        samples_entry.get().strip()
    )

    time_factor_text = (
        time_factor_entry.get().strip()
    )

    decimal_places_text = (
        decimal_places_entry.get().strip()
    )

    # ========================================================
    # EINGABEDATEI PRÜFEN
    # ========================================================

    if not input_file:

        messagebox.showerror(
            "Fehler",
            "Bitte eine Eingabedatei auswählen."
        )

        return

    # ========================================================
    # AUSGABEDATEI PRÜFEN
    # ========================================================

    if not output_file:

        messagebox.showerror(
            "Fehler",
            "Bitte eine Ausgabedatei auswählen."
        )

        return

    # ========================================================
    # SAMPLES PRÜFEN
    # ========================================================

    if not samples_text:

        messagebox.showerror(
            "Fehler",
            "Bitte die gewünschte Anzahl Samples eingeben."
        )

        return

    try:

        desired_samples = int(
            samples_text
        )

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

    # ========================================================
    # TIME-FAKTOR PRÜFEN
    # ========================================================

    if not time_factor_text:

        messagebox.showerror(
            "Fehler",
            "Bitte einen TIME-Faktor eingeben."
        )

        return

    try:

        time_factor = float(
            time_factor_text
        )

    except ValueError:

        messagebox.showerror(
            "Fehler",
            "Der TIME-Faktor muss eine Zahl sein.\n\n"
            "Beispiele:\n"
            "1000000\n"
            "1000\n"
            "0.001\n"
            "1e6"
        )

        return

    if time_factor == 0:

        messagebox.showerror(
            "Fehler",
            "Der TIME-Faktor darf nicht 0 sein."
        )

        return

    # ========================================================
    # NACHKOMMASTELLEN PRÜFEN
    # ========================================================

    if not decimal_places_text:

        messagebox.showerror(
            "Fehler",
            "Bitte die Anzahl der Nachkommastellen eingeben."
        )

        return

    try:

        decimal_places = int(
            decimal_places_text
        )

    except ValueError:

        messagebox.showerror(
            "Fehler",
            "Die Anzahl der Nachkommastellen muss "
            "eine ganze Zahl sein."
        )

        return

    if decimal_places < 0:

        messagebox.showerror(
            "Fehler",
            "Die Anzahl der Nachkommastellen darf "
            "nicht negativ sein."
        )

        return

    if decimal_places > 15:

        messagebox.showerror(
            "Fehler",
            "Bitte maximal 15 Nachkommastellen verwenden."
        )

        return

    # ========================================================
    # ZEITBEREICH
    # ========================================================

    start_time = None
    end_time = None

    if not all_time_var.get():

        start_text = (
            start_time_entry.get().strip()
        )

        end_text = (
            end_time_entry.get().strip()
        )

        # ----------------------------------------------------
        # Startzeit
        # ----------------------------------------------------

        if start_text:

            try:

                start_time = float(
                    start_text
                )

            except ValueError:

                messagebox.showerror(
                    "Fehler",
                    "Die Startzeit muss eine Zahl sein.\n\n"
                    "Beispiele:\n"
                    "0.5\n"
                    "1e-5\n"
                    "2.5E-04"
                )

                return

        # ----------------------------------------------------
        # Endzeit
        # ----------------------------------------------------

        if end_text:

            try:

                end_time = float(
                    end_text
                )

            except ValueError:

                messagebox.showerror(
                    "Fehler",
                    "Die Endzeit muss eine Zahl sein.\n\n"
                    "Beispiele:\n"
                    "1.0\n"
                    "1e-3\n"
                    "2.5E-02"
                )

                return

        # ----------------------------------------------------
        # Mindestens ein Grenzwert
        # ----------------------------------------------------

        if (
            start_time is None
            and end_time is None
        ):

            messagebox.showerror(
                "Fehler",
                "Bitte eine Startzeit oder Endzeit eingeben."
            )

            return

        # ----------------------------------------------------
        # Start <= Ende
        # ----------------------------------------------------

        if (
            start_time is not None
            and end_time is not None
            and start_time > end_time
        ):

            messagebox.showerror(
                "Fehler",
                "Die Startzeit darf nicht größer "
                "als die Endzeit sein."
            )

            return

    # ========================================================
    # DATEIEN VERGLEICHEN
    # ========================================================

    if (
        input_file.lower()
        == output_file.lower()
    ):

        messagebox.showerror(
            "Fehler",
            "Eingabe- und Ausgabedatei dürfen "
            "nicht identisch sein."
        )

        return

    # ========================================================
    # CSV VERARBEITEN
    # ========================================================

    try:

        result = process_csv(
            input_file,
            output_file,
            desired_samples,
            time_factor,
            decimal_places,
            start_time,
            end_time
        )

    except Exception as error:

        messagebox.showerror(
            "Fehler bei der Verarbeitung",
            str(error)
        )

        return

    # ========================================================
    # ZEITBEREICH TEXT
    # ========================================================

    if all_time_var.get():

        time_range_text = "ALL"

    else:

        if start_time is None:

            start_text = "-∞"

        else:

            start_text = f"{start_time:g}"

        if end_time is None:

            end_text = "+∞"

        else:

            end_text = f"{end_time:g}"

        time_range_text = (
            f"{start_text} bis {end_text}"
        )

    # ========================================================
    # ERGEBNIS
    # ========================================================

    result_text = (
        "Verarbeitung erfolgreich!\n"
        "\n"
        f"Header:              Zeile "
        f"{result['header_line']}\n"
        f"Datenzeilen:         "
        f"{result['data_rows']:,}\n"
        f"Gewünschte Samples:  "
        f"{desired_samples:,}\n"
        f"Schrittweite:        "
        f"{result['step']:,}\n"
        f"Erzeugte Samples:    "
        f"{result['samples']:,}\n"
        f"Zeitbereich:         "
        f"{time_range_text}\n"
        f"TIME-Faktor:         "
        f"{time_factor:g}\n"
        f"Nachkommastellen:    "
        f"{decimal_places}\n"
        "\n"
        "Zeitbereich basiert auf TIME "
        "nach Anwendung des TIME-Faktors.\n"
        "\n"
        f"Ausgabedatei:\n"
        f"{output_file}"
    )

    # ========================================================
    # ERGEBNIS ANZEIGEN
    # ========================================================

    show_result(
        result_text
    )

    # ========================================================
    # FERTIG
    # ========================================================

    messagebox.showinfo(
        "Fertig",
        "CSV-Datei erfolgreich erstellt.\n\n"
        f"{result['samples']:,} Samples geschrieben."
    )


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "CSV Sample Tool"
)

root.geometry(
    "1000x800"
)

root.minsize(
    900,
    700
)

root.resizable(
    True,
    True
)


# ============================================================
# VARIABLEN
# ============================================================

input_path = tk.StringVar()
output_path = tk.StringVar()

# ALL standardmäßig aktiviert
all_time_var = tk.BooleanVar(
    value=True
)


# ============================================================
# HAUPT-FRAME
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
# ÜBERSCHRIFT
# ============================================================

tk.Label(
    main_frame,
    text="CSV Sample Tool",
    font=("Arial", 24, "bold")
).pack(
    pady=(0, 25)
)


# ============================================================
# EINGABEDATEI
# ============================================================

input_frame = tk.Frame(
    main_frame
)

input_frame.pack(
    fill="x",
    pady=6
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
# AUSGABEDATEI
# ============================================================

output_frame = tk.Frame(
    main_frame
)

output_frame.pack(
    fill="x",
    pady=6
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
# SAMPLES
# ============================================================

samples_frame = tk.Frame(
    main_frame
)

samples_frame.pack(
    fill="x",
    pady=(18, 6)
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
# TIME-FAKTOR
# ============================================================

time_factor_frame = tk.Frame(
    main_frame
)

time_factor_frame.pack(
    fill="x",
    pady=6
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
# NACHKOMMASTELLEN
# ============================================================

decimal_places_frame = tk.Frame(
    main_frame
)

decimal_places_frame.pack(
    fill="x",
    pady=6
)

tk.Label(
    decimal_places_frame,
    text="Nachkommastellen:",
    width=20,
    anchor="w",
    font=("Arial", 11)
).pack(
    side="left"
)

decimal_places_entry = tk.Entry(
    decimal_places_frame,
    width=20,
    font=("Arial", 11)
)

decimal_places_entry.pack(
    side="left",
    padx=10
)

decimal_places_entry.insert(
    0,
    "6"
)

tk.Label(
    decimal_places_frame,
    text="gilt für alle numerischen Spalten",
    font=("Arial", 9),
    fg="gray"
).pack(
    side="left",
    padx=5
)


# ============================================================
# ZEITBEREICH
# ============================================================

time_range_frame = tk.LabelFrame(
    main_frame,
    text=" Zeitbereich (nach TIME-Faktor) ",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=10
)

time_range_frame.pack(
    fill="x",
    pady=(15, 5)
)


# ============================================================
# ALL
# ============================================================

all_time_check = tk.Checkbutton(
    time_range_frame,
    text="ALL",
    variable=all_time_var,
    command=toggle_time_range,
    font=("Arial", 11, "bold")
)

all_time_check.grid(
    row=0,
    column=0,
    padx=(0, 25),
    pady=5,
    sticky="w"
)


# ============================================================
# STARTZEIT
# ============================================================

tk.Label(
    time_range_frame,
    text="Startzeit:",
    font=("Arial", 10)
).grid(
    row=0,
    column=1,
    padx=(0, 5),
    sticky="e"
)

start_time_entry = tk.Entry(
    time_range_frame,
    width=18,
    font=("Arial", 10)
)

start_time_entry.grid(
    row=0,
    column=2,
    padx=(0, 25),
    sticky="w"
)


# ============================================================
# ENDZEIT
# ============================================================

tk.Label(
    time_range_frame,
    text="Endzeit:",
    font=("Arial", 10)
).grid(
    row=0,
    column=3,
    padx=(0, 5),
    sticky="e"
)

end_time_entry = tk.Entry(
    time_range_frame,
    width=18,
    font=("Arial", 10)
)

end_time_entry.grid(
    row=0,
    column=4,
    sticky="w"
)


# ============================================================
# HINWEIS
# ============================================================

tk.Label(
    time_range_frame,
    text=(
        "Start- und Endzeit beziehen sich auf "
        "TIME nach Anwendung des TIME-Faktors"
    ),
    font=("Arial", 9),
    fg="gray"
).grid(
    row=1,
    column=1,
    columnspan=4,
    padx=5,
    pady=(5, 0),
    sticky="w"
)


# ============================================================
# ALL STANDARDMÄSSIG AKTIV
# ============================================================

toggle_time_range()


# ============================================================
# START-BUTTON
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
    pady=20
)


# ============================================================
# ERGEBNIS ÜBERSCHRIFT
# ============================================================

tk.Label(
    main_frame,
    text="Ergebnis",
    font=("Arial", 14, "bold"),
    anchor="w"
).pack(
    fill="x",
    pady=(5, 5)
)


# ============================================================
# ERGEBNISBEREICH
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
# ERGEBNIS-TEXTFELD
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
# VERTIKALE SCROLLBAR
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
# HORIZONTALE SCROLLBAR
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
# SCROLLBARS VERBINDEN
# ============================================================

result_textbox.configure(
    yscrollcommand=vertical_scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set
)


# ============================================================
# GRID VERHALTEN
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
# GUI STARTEN
# ============================================================

root.mainloop()
