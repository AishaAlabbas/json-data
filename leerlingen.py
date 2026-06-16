# Importeert tkinter voor de grafische interface
import tkinter as tk
# Importeert extra widgets zoals Treeview en Combobox + meldingsvensters
from tkinter import ttk, messagebox
# Importeert SQLite om met de database te werken
import sqlite3

# Functie om het leerlingenbeheer venster te openen
def open_leerlingenbeheer():

    venster = tk.Toplevel()
    venster.title("Leerlingenbeheer")
    venster.geometry("1100x700")
    venster.config(bg="#e8f5e9")

    tk.Label(venster, text="Leerlingenbeheer", font=("Arial", 24, "bold"), bg="#e8f5e9", fg="#1b5e20").pack(pady=10)

    frame = tk.Frame(venster, bg="#e8f5e9")
    frame.pack(pady=10)

    labels = ["Voornaam", "Achternaam", "Leeftijd", "Email", "Telefoonnummer", "Klas"]
    entries = {}
    klassen = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B", "5A", "5B", "6A", "6B"]

    for i, label in enumerate(labels):
        tk.Label(frame, text=label, bg="#e8f5e9", fg="#1b5e20", font=("Arial", 10, "bold")).grid(row=i, column=0, padx=5, pady=5)
        if label == "Klas":
            entry = ttk.Combobox(frame, values=klassen, state="readonly")
        else:
            entry = tk.Entry(frame)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[label] = entry

    kolommen = ("id", "voornaam", "achternaam", "leeftijd", "email", "telefoonnummer", "klas")
    tabel = ttk.Treeview(venster, columns=kolommen, show="headings")

    for kolom in kolommen:
        tabel.heading(kolom, text=kolom)
        tabel.column(kolom, width=140)

    tabel.pack(pady=20)

    def laad_leerlingen():
        for rij in tabel.get_children():
            tabel.delete(rij)
        verbinding = sqlite3.connect("school.db")
        cursor = verbinding.cursor()
        cursor.execute("SELECT * FROM leerlingen")
        leerlingen = cursor.fetchall()
        for leerling in leerlingen:
            tabel.insert("", tk.END, values=leerling)
        verbinding.close()

    def velden_leegmaken():
        for entry in entries.values():
            entry.delete(0, tk.END)
        entries["Klas"].set("")

    def valideer_gegevens():
        voornaam = entries["Voornaam"].get()
        achternaam = entries["Achternaam"].get()
        leeftijd = entries["Leeftijd"].get()
        email = entries["Email"].get()
        telefoon = entries["Telefoonnummer"].get()
        klas = entries["Klas"].get()
        if voornaam == "" or achternaam == "" or leeftijd == "" or klas == "":
            messagebox.showerror("Fout", "Voornaam, achternaam, leeftijd en klas zijn verplicht")
            return None
        if email == "" and telefoon == "":
            messagebox.showerror("Fout", "Vul een email of telefoonnummer in")
            return None
        if not leeftijd.isdigit():
            messagebox.showerror("Fout", "Leeftijd moet een getal zijn")
            return None
        if telefoon != "" and not telefoon.isdigit():
            messagebox.showerror("Fout", "Telefoonnummer moet een getal zijn")
            return None
        if voornaam.isdigit() or achternaam.isdigit():
            messagebox.showerror("Fout", "Naam mag geen cijfers bevatten")
            return None
        if email != "" and "@" not in email:
            messagebox.showerror("Fout", "Geen geldig emailadres")
            return None
        return voornaam, achternaam, leeftijd, email, telefoon, klas

    def leerling_toevoegen():
        gegevens = valideer_gegevens()
        if gegevens is None:
            return
        verbinding = sqlite3.connect("school.db")
        cursor = verbinding.cursor()
        cursor.execute("""
        INSERT INTO leerlingen
        (voornaam, achternaam, leeftijd, email, telefoonnummer, klas)
        VALUES (?, ?, ?, ?, ?, ?)
        """, gegevens)
        verbinding.commit()
        verbinding.close()
        messagebox.showinfo("Succes", "Leerling succesvol toegevoegd")
        velden_leegmaken()
        laad_leerlingen()

    def leerling_selecteren(event):
        geselecteerd = tabel.selection()
        if not geselecteerd:
            return
        leerling = tabel.item(geselecteerd)
        waarden = leerling["values"]
        velden_leegmaken()
        entries["Voornaam"].insert(0, waarden[1])
        entries["Achternaam"].insert(0, waarden[2])
        entries["Leeftijd"].insert(0, waarden[3])
        entries["Email"].insert(0, waarden[4])
        entries["Telefoonnummer"].insert(0, waarden[5])
        entries["Klas"].set(waarden[6])

    def leerling_wijzigen():
        geselecteerd = tabel.selection()
        if not geselecteerd:
            messagebox.showerror("Fout", "Selecteer eerst een leerling")
            return
        gegevens = valideer_gegevens()
        if gegevens is None:
            return
        leerling = tabel.item(geselecteerd)
        leerling_id = leerling["values"][0]
        verbinding = sqlite3.connect("school.db")
        cursor = verbinding.cursor()
        cursor.execute("""
        UPDATE leerlingen
        SET voornaam=?, achternaam=?, leeftijd=?, email=?, telefoonnummer=?, klas=?
        WHERE id=?
        """, gegevens + (leerling_id,))
        verbinding.commit()
        verbinding.close()
        messagebox.showinfo("Succes", "Leerling succesvol gewijzigd")
        velden_leegmaken()
        laad_leerlingen()

    def leerling_verwijderen():
        geselecteerd = tabel.selection()
        if not geselecteerd:
            messagebox.showerror("Fout", "Selecteer eerst een leerling")
            return
        leerling = tabel.item(geselecteerd)
        leerling_id = leerling["values"][0]
        antwoord = messagebox.askyesno("Bevestigen", "Ben je zeker dat je deze leerling wilt verwijderen?")
        if antwoord:
            verbinding = sqlite3.connect("school.db")
            cursor = verbinding.cursor()
            cursor.execute("DELETE FROM leerlingen WHERE id=?", (leerling_id,))
            verbinding.commit()
            verbinding.close()
            messagebox.showinfo("Succes", "Leerling verwijderd")
            velden_leegmaken()
            laad_leerlingen()

    def leerling_zoeken():
        zoekterm = zoek_entry.get()
        for rij in tabel.get_children():
            tabel.delete(rij)
        verbinding = sqlite3.connect("school.db")
        cursor = verbinding.cursor()
        cursor.execute("""
        SELECT * FROM leerlingen
        WHERE voornaam LIKE ? OR achternaam LIKE ? OR klas LIKE ?
        """, ("%" + zoekterm + "%", "%" + zoekterm + "%", "%" + zoekterm + "%"))
        resultaten = cursor.fetchall()
        for leerling in resultaten:
            tabel.insert("", tk.END, values=leerling)
        verbinding.close()

    zoek_frame = tk.Frame(venster, bg="#e8f5e9")
    zoek_frame.pack(pady=5)
    tk.Label(zoek_frame, text="Zoeken:", bg="#e8f5e9", fg="#1b5e20", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
    zoek_entry = tk.Entry(zoek_frame)
    zoek_entry.grid(row=0, column=1, padx=5)
    tk.Button(zoek_frame, text="Zoeken", bg="#2e7d32", fg="white", command=leerling_zoeken).grid(row=0, column=2, padx=5)
    tk.Button(zoek_frame, text="Alles tonen", bg="#66bb6a", fg="white", command=laad_leerlingen).grid(row=0, column=3, padx=5)

    tabel.bind("<<TreeviewSelect>>", leerling_selecteren)

    button_frame = tk.Frame(venster, bg="#e8f5e9")
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Leerling toevoegen", command=leerling_toevoegen, width=20, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Leerling wijzigen", command=leerling_wijzigen, width=20, bg="#2196F3", fg="white").grid(row=0, column=1, padx=10)
    tk.Button(button_frame, text="Leerling verwijderen", command=leerling_verwijderen, width=20, bg="#f44336", fg="white").grid(row=0, column=2, padx=10)

    laad_leerlingen()
