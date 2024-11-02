import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import struct
import json
import os
import shutil
import subprocess
import time
import pickle
from PIL import Image, ImageTk  # Importer Pillow pour gérer les PNG

CONFIG_FILE = 'config.pkl'

BASE_DIR = r"Base_pas_edit\Rivals2\Content\Characters"

# Initialisation des variables globales
unrealpak_script_path = None
mods_folder_path = None
json_data = None
uexp_file_path = None
color_entries = {}
color_displays = {}
character_icons = {}
file_type_codes = {'Element/Energy': 'PE', 'Skin': 'PS'}


def save_config():
    # Sauvegarde de la configuration dans un fichier pickle
    config = {
        'unrealpak_script_path': unrealpak_script_path,
        'mods_folder_path': mods_folder_path
    }
    with open(CONFIG_FILE, 'wb') as f:
        pickle.dump(config, f)


def load_config():
    # Chargement de la configuration depuis le fichier pickle
    global unrealpak_script_path, mods_folder_path, preset_dir
    project_root = os.path.dirname(
        os.path.abspath(__file__))  # Chemin du projet racine

    # Chemin de UnrealPak-With-Compression.bat dans Upack
    unrealpak_script_path = os.path.join(
        project_root, "Upack", "UnrealPak-With-Compression.bat")

    # Chemin du dossier Preset à la racine du projet
    preset_dir = os.path.join(project_root, "Preset")

    # Charger le dossier mods depuis le fichier de configuration si disponible
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'rb') as f:
            config = pickle.load(f)
            mods_folder_path = config.get('mods_folder_path')


def get_output_and_unrealpak_dirs():
    # Obtient les chemins des dossiers de sortie pour UnrealPak
    character = selected_character.get()
    skin = selected_skin.get()
    color = selected_color.get()
    file_type = selected_file_type.get()

    # Dossier à utiliser pour UnrealPak
    unrealpak_folder_path = os.path.join(
        os.path.dirname(unrealpak_script_path), f"{character}_P")

    # Dossier de sortie pour copier le fichier UEXP avec toute la hiérarchie
    output_folder_path = os.path.join(
        unrealpak_folder_path,
        "Rivals2", "Content", "Characters", character, "Skins", skin, "Data", "Palettes", color
    )

    # Création du dossier de sortie si nécessaire
    os.makedirs(output_folder_path, exist_ok=True)
    return output_folder_path, unrealpak_folder_path


def save_preset():
    # Sauvegarde le preset actuel dans un fichier JSON
    if json_data is None:
        messagebox.showerror("Erreur", "Aucun fichier JSON chargé.")
        return
    preset_file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[
                                               ("JSON files", "*.json")], initialdir=preset_dir)
    if preset_file:
        for entry in json_data:
            if "Properties" in entry and "CustomColorSlotDefinitions" in entry["Properties"]:
                for color in entry["Properties"]["CustomColorSlotDefinitions"]:
                    key = color["Key"]
                    if key in color_entries:
                        hex_color = color_entries[key].get().lstrip('#')
                        if len(hex_color) == 6:
                            r = int(hex_color[0:2], 16) / 255.0
                            g = int(hex_color[2:4], 16) / 255.0
                            b = int(hex_color[4:6], 16) / 255.0
                            color["Value"] = {"R": r, "G": g, "B": b}

        with open(preset_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)
        messagebox.showinfo("Succès", "Preset sauvegardé avec succès.")


def load_preset():
    # Charge un preset depuis un fichier JSON et met à jour les couleurs dans l'interface
    preset_file = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")], initialdir=preset_dir)
    if preset_file:
        with open(preset_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                global json_data
                json_data = data
                populate_color_selectors(data)
                for entry in data:
                    if "Properties" in entry and "CustomColorSlotDefinitions" in entry["Properties"]:
                        for color in entry["Properties"]["CustomColorSlotDefinitions"]:
                            key = color["Key"]
                            value = color["Value"]
                            hex_color = f"#{int(value['R'] * 255):02X}{int(value['G'] * 255):02X}{int(value['B'] * 255):02X}"
                            if key in color_entries:
                                color_entries[key].delete(0, tk.END)
                                color_entries[key].insert(0, hex_color)
                                update_color_display(key)
                messagebox.showinfo("Succès", "Preset chargé avec succès.")
            except json.JSONDecodeError:
                messagebox.showerror(
                    "Erreur", "Erreur de chargement du preset.")


def precise_float_to_hex(value):
    # Convertit un float en représentation hexadécimale précise
    binary = struct.unpack('>I', struct.pack('>f', value))[0]
    hex_value = f'{binary:08X}'
    return hex_value


def invert_hex(hex_value):
    # Inverse les octets dans une chaîne hexadécimale
    return ''.join([hex_value[i:i+2] for i in range(0, len(hex_value), 2)][::-1])


def hex_to_linear_rgb(color_hex):
    # Convertit une couleur hexadécimale en valeurs RGB linéaires
    color_hex = color_hex.lstrip('#')
    r = int(color_hex[0:2], 16) / 255.0
    g = int(color_hex[2:4], 16) / 255.0
    b = int(color_hex[4:6], 16) / 255.0

    def linearize(value):
        # Applique la correction gamma pour obtenir une valeur linéaire
        if value <= 0.04045:
            return value / 12.92
        else:
            return ((value + 0.055) / 1.055) ** 2.4

    r_lin = linearize(r)
    g_lin = linearize(g)
    b_lin = linearize(b)

    return r_lin, g_lin, b_lin


def load_json():
    # Charge le fichier JSON associé au fichier UEXP et met à jour l'interface
    global json_data
    json_file_path = uexp_file_path.replace(".uexp", ".json")

    # Vérifier si le fichier JSON existe
    if not os.path.exists(json_file_path):
        messagebox.showerror(
            "Erreur", f"Fichier JSON introuvable : {json_file_path}")
        return False

    # Charger le fichier JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            # Vérifier que le JSON est une liste avec au moins deux éléments
            if isinstance(data, list) and len(data) > 1:
                json_data = filter_colors_in_uexp(
                    data)  # Appliquer le filtrage
                # Afficher les couleurs filtrées
                populate_color_selectors(json_data)
                # Définir les couleurs de base à partir du JSON
                set_initial_colors(json_data)
                print(f"Fichier JSON chargé et filtré : {json_file_path}")
                return True
            else:
                messagebox.showerror("Erreur", "Format JSON inattendu.")
                return False
        except json.JSONDecodeError:
            messagebox.showerror("Erreur", "Erreur de décodage JSON.")
            return False

# Définir les couleurs initiales des entrées à partir du JSON (affiche uniquement dans les carrés)


def set_initial_colors(data):
    # Initialise les couleurs affichées dans l'interface à partir des données JSON
    for entry in data:
        if "Properties" in entry and "CustomColorSlotDefinitions" in entry["Properties"]:
            for color in entry["Properties"]["CustomColorSlotDefinitions"]:
                key = color["Key"]
                if "Hex" in color["Value"]:
                    # Ajouter le '#' pour Tkinter
                    hex_color = f'#{color["Value"]["Hex"]}'
                    if key in color_displays:
                        # Mettre à jour le fond avec la couleur initiale
                        color_displays[key].config(bg=hex_color)
                    # Laisser l'entrée vide (ne rien insérer dans color_entries)
                    if key in color_entries:
                        # S'assurer que le champ est vide
                        color_entries[key].delete(0, tk.END)


def load_files():
    # Charge le fichier UEXP et le JSON associé
    if load_uexp():
        load_json()


def filter_colors_in_uexp(data):
    """
    Filtre les clés du JSON qui correspondent aux couleurs présentes dans le fichier UEXP,
    en respectant l'ordre des valeurs et en ne prenant qu'une occurrence par couleur.
    """
    with open(uexp_file_path, 'rb') as f:
        uexp_data = f.read().hex().upper()

    filtered_data = []
    current_position = 0  # Position actuelle dans uexp_data pour l'analyse séquentielle

    for entry in data:
        if "Properties" in entry and "CustomColorSlotDefinitions" in entry["Properties"]:
            filtered_colors = []
            for color in entry["Properties"]["CustomColorSlotDefinitions"]:
                key = color["Key"]
                value = color["Value"]

                # Convertir chaque composante RGB en hexadécimale
                hex_r = invert_hex(precise_float_to_hex(value["R"]))
                hex_g = invert_hex(precise_float_to_hex(value["G"]))
                hex_b = invert_hex(precise_float_to_hex(value["B"]))
                color_hex = hex_r + hex_g + hex_b

                # Rechercher séquentiellement la première occurrence de color_hex après current_position
                position = uexp_data.find(color_hex, current_position)
                if position != -1:
                    # Si trouvé, enregistrer la couleur avec la position actuelle
                    color["UEXP_Hex"] = color_hex
                    # Conserver les couleurs trouvées
                    filtered_colors.append(color)
                    # Mettre à jour current_position pour poursuivre après cet emplacement
                    current_position = position + len(color_hex)

                    # Afficher les détails de la correspondance
                    print(f"Correspondance trouvée pour '{key}':")
                    print(f"  Valeur dans UEXP : {color_hex}")
                    print(f"  Position dans UEXP : {position}")
                else:
                    print(
                        f"Valeur {color_hex} non trouvée pour la couleur {key}, passage à la suivante.")

            if filtered_colors:
                # Si des couleurs filtrées ont été trouvées, conserver l'entrée
                filtered_entry = entry.copy()
                filtered_entry["Properties"]["CustomColorSlotDefinitions"] = filtered_colors
                filtered_data.append(filtered_entry)
    return filtered_data


def populate_color_selectors(data):
    """
    Crée les champs d'affichage pour chaque couleur ayant une correspondance dans le fichier UEXP.
    """
    # Effacer les widgets précédents
    for widget in color_frame.winfo_children():
        widget.destroy()

    global color_entries, color_displays
    color_entries = {}
    color_displays = {}

    row = 0
    col = 0
    for entry in data:
        if "Properties" in entry and "CustomColorSlotDefinitions" in entry["Properties"]:
            for color in entry["Properties"]["CustomColorSlotDefinitions"]:
                key = color["Key"]

                # Afficher les informations de la couleur qui va être ajoutée
                print(
                    f"Affichage de la couleur '{key}' avec correspondance trouvée")

                # Créer les champs pour chaque clé filtrée
                label = tk.Label(color_frame, text=key,
                                 font=("Arial", 10, "bold"))
                label.grid(row=row, column=col*4, padx=5, pady=5, sticky="w")

                color_entry = tk.Entry(
                    color_frame, width=10, font=("Arial", 10))
                color_entry.grid(row=row, column=col*4 + 1, padx=5, pady=5)
                color_entries[key] = color_entry
                color_entry.bind("<KeyRelease>", lambda e,
                                 k=key: update_color_display(k))

                color_display = tk.Label(
                    color_frame, width=2, height=1, bg="#FFFFFF", relief="solid", borderwidth=1)
                color_display.grid(row=row, column=col*4 + 2, padx=5, pady=5)
                color_displays[key] = color_display

                choose_button = tk.Button(
                    color_frame, text="🎨", command=lambda k=key: choose_color(k), font=("Arial", 8))
                choose_button.grid(row=row, column=col*4 + 3, padx=5, pady=5)

                col += 1
                if col >= 2:
                    col = 0
                    row += 1


def choose_color(key):
    # Ouvre un sélecteur de couleurs pour choisir une couleur
    color_code = colorchooser.askcolor(title="Choisir une couleur")[1]
    if color_code:
        color_entries[key].delete(0, tk.END)
        color_entries[key].insert(0, color_code)
        update_color_display(key)


def update_color_display(key):
    # Met à jour le carré de couleur en fonction de l'entrée utilisateur
    hex_color = color_entries[key].get()
    if hex_color.startswith('#') and len(hex_color) == 7:
        color_displays[key].config(bg=hex_color)


def load_uexp():
    # Charge le fichier UEXP basé sur la sélection de l'utilisateur
    global uexp_file_path
    character = selected_character.get()
    skin = selected_skin.get()
    color = selected_color.get()
    file_type_code = file_type_codes.get(selected_file_type.get())

    # Construction du nom de fichier selon le format
    # Prend les 3 premières lettres avec la 1ère en majuscule
    character_prefix = character[:3].capitalize()
    uexp_filename = f"{file_type_code}_{character_prefix}_{skin}_{color}.uexp"

    # Construction du chemin complet du fichier UEXP
    uexp_file_path = os.path.join(
        BASE_DIR, character, "Skins", skin, "Data", "Palettes", color, uexp_filename)

    # Vérification de l'existence du fichier
    if not os.path.exists(uexp_file_path):
        messagebox.showerror(
            "Erreur", f"Fichier UEXP introuvable : {uexp_file_path}")
        return False
    print(f"Fichier UEXP chargé : {uexp_file_path}")
    return True


def replace_colors_in_uexp():
    # Remplace les couleurs dans le fichier UEXP en fonction des entrées utilisateur
    if json_data is None:
        messagebox.showerror("Erreur", "Aucun fichier JSON chargé.")
        return

    try:
        # Obtenir les chemins de sortie et de UnrealPak
        output_folder_path, unrealpak_folder_path = get_output_and_unrealpak_dirs()

        # Copier le fichier UEXP dans le dossier de sortie avec la hiérarchie complète
        modified_uexp_path = os.path.join(
            output_folder_path, os.path.basename(uexp_file_path))
        shutil.copy(uexp_file_path, modified_uexp_path)
        print(
            f"Fichier UEXP copié dans le dossier de sortie : {modified_uexp_path}")

        # Charger les données de la copie du fichier UEXP en hexadécimal pour modification
        with open(modified_uexp_path, 'rb') as f:
            uexp_data = f.read().hex().upper()

        modified_data = uexp_data
        current_position = 0  # Position de départ pour les remplacements séquentiels

        for key, entry in color_entries.items():
            hex_color_input = entry.get()
            if not hex_color_input:
                continue

            # Conversion de la couleur hex en valeurs linéaires RGB pour remplacement
            r, g, b = hex_to_linear_rgb(hex_color_input)
            hex_r = invert_hex(precise_float_to_hex(r))
            hex_g = invert_hex(precise_float_to_hex(g))
            hex_b = invert_hex(precise_float_to_hex(b))
            new_hex = hex_r + hex_g + hex_b

            # Rechercher la couleur d'origine à partir du JSON filtré
            selected_color_entry = None
            for item in json_data:
                if "Properties" in item and "CustomColorSlotDefinitions" in item["Properties"]:
                    for color in item["Properties"]["CustomColorSlotDefinitions"]:
                        if color["Key"] == key and "UEXP_Hex" in color:
                            selected_color_entry = color
                            break

            # Si la couleur d'origine existe, procéder au remplacement séquentiel
            if selected_color_entry:
                original_hex = selected_color_entry["UEXP_Hex"]
                # Rechercher la première occurrence après la position courante
                position = modified_data.find(original_hex, current_position)
                if position != -1:
                    # Remplacer cette occurrence uniquement et afficher les informations de modification
                    modified_data = (
                        modified_data[:position] + new_hex +
                        modified_data[position + len(original_hex):]
                    )
                    # Afficher les détails de la modification
                    print(f"Modification pour la clé '{key}':")
                    print(f"  Couleur d'origine : {original_hex}")
                    print(f"  Nouvelle couleur  : {new_hex}")
                    print(f"  Position de remplacement : {position}")

                    # Mettre à jour la position courante pour continuer après cet emplacement
                    current_position = position + len(new_hex)

        # Convertir les données modifiées en bytes et les écrire dans le fichier UEXP modifié
        uexp_bytes = bytes.fromhex(modified_data)
        with open(modified_uexp_path, 'wb') as f:
            f.write(uexp_bytes)

        ask_for_pak_directory_and_create(unrealpak_folder_path)
        # Informer l'utilisateur en cas d'erreur
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


def configure_script_and_mods_folder():
    # Permet à l'utilisateur de sélectionner le dossier mods
    global mods_folder_path
    # Demander uniquement le dossier mods
    mods_folder_path = filedialog.askdirectory(
        title="Choisir le dossier mods existant")
    save_config()
    messagebox.showinfo("Succès", "Dossier mods configuré.")


def ask_for_pak_directory_and_create(unrealpak_folder_path):
    # Exécute UnrealPak pour créer le fichier .pak et le déplace dans le dossier mods
    character = selected_character.get()
    # Construire le chemin du dossier de sortie pour UnrealPak basé sur le personnage sélectionné
    unrealpak_folder_path = os.path.join(
        os.path.dirname(unrealpak_script_path), f"{character}_P")

    # Créer le dossier si nécessaire
    os.makedirs(unrealpak_folder_path, exist_ok=True)

    try:
        # Exécuter UnrealPak-With-Compression.bat en utilisant le dossier unrealpak_folder_path
        subprocess.run(
            [unrealpak_script_path, unrealpak_folder_path], check=True)
        time.sleep(0.2)  # Pause pour s'assurer que le fichier est créé

        # Rechercher le fichier .pak dans le répertoire UnrealPak
        generated_pak = None
        for file in os.listdir(os.path.dirname(unrealpak_script_path)):
            if file.endswith(".pak"):
                generated_pak = os.path.join(
                    os.path.dirname(unrealpak_script_path), file)
                break

        if generated_pak and os.path.exists(generated_pak):
            destination = os.path.join(
                mods_folder_path, os.path.basename(generated_pak))
            shutil.move(generated_pak, destination)
            messagebox.showinfo(
                "Succès", f"Fichier .pak créé et déplacé vers le dossier mods : {mods_folder_path}")
        else:
            messagebox.showerror(
                "Erreur", "Le fichier .pak n'a pas été trouvé.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Échec de l'exécution du script : {e}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de la création du .pak : {e}")


def load_character_icons():
    # Charge les icônes des personnages depuis le dossier 'icons'
    characters_path = os.path.join(BASE_DIR)
    characters = [name for name in os.listdir(
        characters_path) if os.path.isdir(os.path.join(characters_path, name))]
    for character in characters:
        image_path = f"icons/{character}.png"  # Chemin de chaque icône PNG
        if os.path.exists(image_path):  # Vérifie si l'image existe
            try:
                # Ajustez la taille si nécessaire
                img = Image.open(image_path).resize((32, 32))
                character_icons[character] = ImageTk.PhotoImage(
                    img)  # Convertir en PhotoImage pour Tkinter
            except Exception as e:
                print(
                    f"Erreur : Impossible de charger l'image {image_path}. {e}")
        else:
            print(f"Image non trouvée pour le personnage {character}")
    return characters


def update_selected_character_icon(*args):
    # Met à jour l'icône affichée du personnage sélectionné
    selected_character_name = selected_character.get()
    # Mettre à jour l'icône dans le Label
    selected_character_icon_label.config(
        image=character_icons.get(selected_character_name))
    selected_character_icon_label.image = character_icons.get(
        selected_character_name)  # Référence pour éviter le garbage collection
    # Mettre à jour le menu des skins
    update_skin_menu()


def update_skin_menu(*args):
    # Met à jour le menu des skins en fonction du personnage sélectionné
    character_name = selected_character.get()
    skins_path = os.path.join(BASE_DIR, character_name, 'Skins')
    if os.path.exists(skins_path):
        skins = [name for name in os.listdir(
            skins_path) if os.path.isdir(os.path.join(skins_path, name))]
        # Trier les skins pour un affichage cohérent
        skins.sort()
        # Effacer les anciennes options du menu
        skin_menu['menu'].delete(0, 'end')
        for skin in skins:
            skin_menu['menu'].add_command(
                label=skin, command=tk._setit(selected_skin, skin))
        # Sélectionner 'Default' si disponible, sinon le premier skin
        if 'Default' in skins:
            selected_skin.set('Default')
        elif skins:
            selected_skin.set(skins[0])
        else:
            selected_skin.set('')
    else:
        selected_skin.set('')
        skin_menu['menu'].delete(0, 'end')
    # Mettre à jour le menu des couleurs
    update_color_menu()


def update_color_menu(*args):
    # Met à jour le menu des couleurs en fonction du skin sélectionné
    character_name = selected_character.get()
    skin_name = selected_skin.get()
    palettes_path = os.path.join(
        BASE_DIR, character_name, 'Skins', skin_name, 'Data', 'Palettes')
    if os.path.exists(palettes_path):
        colors = [name for name in os.listdir(palettes_path) if os.path.isdir(
            os.path.join(palettes_path, name))]
        colors.sort()
        # Effacer les anciennes options du menu
        color_menu['menu'].delete(0, 'end')
        for color in colors:
            color_menu['menu'].add_command(
                label=color, command=tk._setit(selected_color, color))
        if colors:
            # Sélectionner la première couleur par défaut
            selected_color.set(colors[0])
        else:
            selected_color.set('')
    else:
        selected_color.set('')
        color_menu['menu'].delete(0, 'end')
    # Mettre à jour le menu des types de fichiers
    update_file_type_menu()


def update_file_type_menu(*args):
    # Met à jour le menu des types de fichiers en fonction de la couleur sélectionnée
    character_name = selected_character.get()
    skin_name = selected_skin.get()
    color_name = selected_color.get()
    data_path = os.path.join(BASE_DIR, character_name,
                             'Skins', skin_name, 'Data', 'Palettes', color_name)
    file_types_found = []

    if os.path.exists(data_path):
        files = os.listdir(data_path)
        for file in files:
            if file.startswith('PE_'):
                file_types_found.append('Element/Energy')
            elif file.startswith('PS_'):
                file_types_found.append('Skin')

        # Supprimer les doublons
        file_types_found = list(set(file_types_found))
        file_types_found.sort()
    else:
        print(f"Chemin non trouvé : {data_path}")

    # Mettre à jour le dictionnaire des codes de type de fichier
    global file_type_codes
    file_type_codes = {'Element/Energy': 'PE', 'Skin': 'PS'}

    # Effacer les anciennes options du menu
    file_type_menu['menu'].delete(0, 'end')
    for file_type in file_types_found:
        file_type_menu['menu'].add_command(
            label=file_type, command=tk._setit(selected_file_type, file_type))
    # Sélectionner 'Skin' si disponible, sinon le premier type de fichier
    if 'Skin' in file_types_found:
        selected_file_type.set('Skin')
    elif file_types_found:
        selected_file_type.set(file_types_found[0])
    else:
        selected_file_type.set('')


def create_character_menu(characters):
    # Crée le menu déroulant des personnages avec icônes
    character_menu = tk.Menubutton(
        header_frame, textvariable=selected_character, indicatoron=True, borderwidth=1, relief="raised")
    character_menu.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    character_menu.menu = tk.Menu(character_menu, tearoff=False)
    character_menu["menu"] = character_menu.menu

    for character in characters:
        character_icon = character_icons.get(character)
        character_menu.menu.add_radiobutton(
            label=character,
            image=character_icon,
            compound='left',
            variable=selected_character,
            value=character,
            command=lambda c=character: selected_character.set(c)
        )
    return character_menu


# Créer la fenêtre Tkinter
root = tk.Tk()
root.title("ROA 2 Colorswap")
root.geometry("800x600")
root.configure(bg="#f2f2f2")

# Variables pour les menus déroulants (après création de root)
selected_character = tk.StringVar()
selected_skin = tk.StringVar()
selected_color = tk.StringVar()
selected_file_type = tk.StringVar()

# Charger les icônes et les personnages
characters = load_character_icons()

# Charger la configuration au démarrage
load_config()

# Frame d'en-tête pour les menus et la configuration
header_frame = tk.Frame(root, bg="#f2f2f2")
header_frame.pack(pady=10)

# Label pour afficher l'icône sélectionnée
selected_character_icon_label = tk.Label(header_frame, bg="#f2f2f2")
selected_character_icon_label.grid(row=0, column=0, padx=5, pady=5)

# Menu déroulant pour le personnage avec icônes
tk.Label(header_frame, text="Personnage:", font=("Arial", 10)).grid(
    row=0, column=1, padx=5, pady=5, sticky="e")

character_menu = create_character_menu(characters)
selected_character.trace("w", update_selected_character_icon)
selected_character.set(characters[0])

# Label et menu pour le skin
tk.Label(header_frame, text="Skin:", font=("Arial", 10)).grid(
    row=0, column=3, padx=5, pady=5, sticky="e")
skin_menu = tk.OptionMenu(header_frame, selected_skin, '')
skin_menu.grid(row=0, column=4, padx=5, pady=5, sticky="w")
selected_skin.trace('w', update_color_menu)

# Menus déroulants pour la couleur et le type de fichier
tk.Label(header_frame, text="Couleur:", font=("Arial", 10)).grid(
    row=0, column=5, padx=5, pady=5, sticky="e")
color_menu = tk.OptionMenu(header_frame, selected_color, '')
color_menu.grid(row=0, column=6, padx=5, pady=5, sticky="w")
selected_color.trace('w', update_file_type_menu)

tk.Label(header_frame, text="Type de fichier:", font=("Arial", 10)).grid(
    row=0, column=7, padx=5, pady=5, sticky="e")
file_type_menu = tk.OptionMenu(header_frame, selected_file_type, '')
file_type_menu.grid(row=0, column=8, padx=5, pady=5, sticky="w")

# Mettre à jour l'icône du personnage initial
update_selected_character_icon()

# Appeler la fonction une première fois pour initialiser le menu des skins
update_skin_menu()

# Bouton pour charger les fichiers UEXP et JSON
load_button = tk.Button(header_frame, text="Charger fichiers",
                        command=load_files, font=("Arial", 10), bg="#4CAF50", fg="white")
load_button.grid(row=1, column=0, columnspan=9, pady=10)

# Bouton unique de configuration pour UnrealPak et Mods
config_button = tk.Button(header_frame, text="Configurer le dossier Mods",
                          command=configure_script_and_mods_folder, font=("Arial", 10), bg="#FFC107", fg="black")
config_button.grid(row=2, column=0, columnspan=9, pady=10)

# Boutons pour sauvegarder et charger des presets
save_preset_button = tk.Button(header_frame, text="Sauvegarder Preset",
                               command=save_preset, font=("Arial", 9), bg="#2196F3", fg="white")
save_preset_button.grid(row=3, column=0, padx=(5, 5), pady=5, sticky="w")

load_preset_button = tk.Button(header_frame, text="Charger Preset",
                               command=load_preset, font=("Arial", 9), bg="#2196F3", fg="white")
load_preset_button.grid(row=3, column=1, padx=(5, 5), pady=5, sticky="w")

# Frame pour afficher les couleurs
color_frame = tk.Frame(root, bg="#ffffff", borderwidth=1, relief="solid")
color_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Frame pour le bouton d'action
action_frame = tk.Frame(root, bg="#f2f2f2")
action_frame.pack(pady=5)

replace_button = tk.Button(action_frame, text="Remplacer les couleurs",
                           command=replace_colors_in_uexp, font=("Arial", 10), bg="#4CAF50", fg="white")
replace_button.grid(row=0, column=0, padx=5, pady=2)

root.mainloop()
