import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os, shutil

# --- Classe Application ---
class MinefutApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minefut - Menu Principal")

        # Icône
        try:
            self.iconbitmap("assets/visuel/Logo.ico")
        except:
            print("⚠️ Impossible de charger Logo.ico")

        # Plein écran
        self.state("zoomed")
        self.resizable(True, True)

        # Pages
        self.frames = {}
        for F in (MenuPage, ModsPage, ModsFacePage, ModDetailPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("MenuPage")

    def show_frame(self, page_name):
        self.frames[page_name].tkraise()

    def show_mod_detail(self, mod, from_page="ModsPage"):
        self.frames["ModDetailPage"].show_mod(mod, from_page)
        self.frames["ModDetailPage"].tkraise()

# --- Page Menu ---
class MenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#1a1a1a")

        # Logo
        try:
            self.logo_img = ImageTk.PhotoImage(file="assets/visuel/Logo.ico")
            logo_label = tk.Label(self, image=self.logo_img, bg="#000000", bd=0)
        except:
            logo_label = tk.Label(self, text="MINEFUT", font=("Arial", 40, "bold"), fg="white", bg="#1a1a1a")
        logo_label.pack(pady=60)

        # Bouton Mods
        mods_btn = tk.Button(self, text="🎮 Mods", font=("Arial", 20), bg="#0078D7", fg="white",
                             width=20, height=2, command=lambda: controller.show_frame("ModsPage"))
        mods_btn.pack(pady=40)

        # Quitter
        quit_btn = tk.Button(self, text="❌ Quitter", font=("Arial", 20), bg="red", fg="white",
                             width=20, height=2, command=controller.destroy)
        quit_btn.pack(pady=20)

# --- Page Mods ---
class ModsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#202020")
        self.controller = controller

        title = tk.Label(self, text="📦 Choisis tes Mods", font=("Arial", 26, "bold"), fg="white", bg="#202020")
        title.pack(pady=40)

        # Bouton Mods Face
        btn_face = tk.Button(self, text="😎 Mods Face", font=("Arial", 18), bg="#2E8B57", fg="white",
                             width=25, height=2, command=lambda: controller.show_frame("ModsFacePage"))
        btn_face.pack(pady=20)

        # Retour
        back_btn = tk.Button(self, text="⬅ Retour", font=("Arial", 16),
                             command=lambda: controller.show_frame("MenuPage"))
        back_btn.pack(pady=50)

# --- Page Mods Face ---
class ModsFacePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#202020")
        self.controller = controller
        self.build_page(os.path.join("assets", "mods", "mods face"), "😎 Mods Face")

    def build_page(self, folder_path, title_text):
        title = tk.Label(self, text=title_text, font=("Arial", 26, "bold"), fg="white", bg="#202020")
        title.pack(pady=20)

        # Canvas scrollable
        canvas = tk.Canvas(self, bg="#202020", highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        self.frame = tk.Frame(canvas, bg="#202020")
        canvas.create_window((0, 0), window=self.frame, anchor="nw")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Charger les packs (chaque sous-dossier = un pack)
        self.mods = []
        for folder in os.listdir(folder_path):
            pack_path = os.path.join(folder_path, folder)
            if os.path.isdir(pack_path):
                # vignette
                vignette = None
                for f in os.listdir(pack_path):
                    if f.lower().endswith((".png", ".jpg", ".jpeg")):
                        vignette = os.path.join(pack_path, f)
                        break
                # description
                description = None
                for f in os.listdir(pack_path):
                    if f.lower().endswith(".txt"):
                        with open(os.path.join(pack_path, f), "r", encoding="utf-8") as desc_file:
                            description = desc_file.read()
                        break
                # fichiers mods
                files = []
                for f in os.listdir(pack_path):
                    if not f.lower().endswith((".png", ".jpg", ".jpeg", ".txt")):
                        files.append(os.path.join(pack_path, f))

                self.mods.append({
                    "name": folder,
                    "image": vignette if vignette else "assets/visuel/default.png",
                    "files": files,
                    "description": description if description else "Aucune description disponible",
                    "price": 0
                })

        # Affichage des packs
        self.images = []
        row = 0
        col = 0
        for mod in self.mods:
            try:
                img = Image.open(mod["image"]).resize((150, 150))
            except:
                img = Image.open("assets/visuel/default.png").resize((150, 150))
            photo = ImageTk.PhotoImage(img)
            self.images.append(photo)

            btn = tk.Button(self.frame, image=photo, text=mod["name"], compound="top",
                            command=lambda m=mod: self.controller.show_mod_detail(m, "ModsFacePage"))
            btn.grid(row=row, column=col, padx=20, pady=20)

            col += 1
            if col > 2:
                col = 0
                row += 1

        self.frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Retour
        back_btn = tk.Button(self, text="⬅ Retour", font=("Arial", 16),
                             command=lambda: self.controller.show_frame("ModsPage"))
        back_btn.pack(pady=20)

# --- Page Mod Détail ---
class ModDetailPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1a1a")
        self.controller = controller
        self.back_page = "ModsFacePage"

        self.title_label = tk.Label(self, font=("Arial", 26, "bold"), fg="white", bg="#1a1a1a")
        self.title_label.pack(pady=20)

        self.image_label = tk.Label(self, bg="#1a1a1a")
        self.image_label.pack(pady=20)

        self.price_label = tk.Label(self, font=("Arial", 18), fg="orange", bg="#1a1a1a")
        self.price_label.pack(pady=10)

        # Frame pour description et fichiers
        self.files_frame = tk.Frame(self, bg="#1a1a1a")
        self.files_frame.pack(pady=20)

        self.back_btn = tk.Button(self, text="⬅ Retour", font=("Arial", 16),
                                  command=self.go_back)
        self.back_btn.pack(pady=30)

    def show_mod(self, mod, from_page):
        self.back_page = from_page
        self.title_label.config(text=mod["name"])

        # Image
        try:
            img = Image.open(mod["image"]).resize((300, 300))
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        except:
            self.image_label.config(text="❌ Image manquante", fg="red")

        # Prix
        self.price_label.config(text="✅ Gratuit" if mod["price"] == 0 else f"💰 {mod['price']} €")

        # Nettoyer anciens widgets
        for widget in self.files_frame.winfo_children():
            widget.destroy()

        # Description
        if mod.get("description"):
            desc_label = tk.Label(self.files_frame, text=mod["description"],
                                  font=("Arial", 12), wraplength=600, fg="white", bg="#1a1a1a", justify="left")
            desc_label.pack(pady=10)

        # Bouton par fichier
        if mod.get("files"):
            for f in mod["files"]:
                filename = os.path.basename(f)
                btn = tk.Button(self.files_frame, text=f"⬇ {filename}",
                                font=("Arial", 14), bg="green", fg="white",
                                command=lambda file=f: self.download_mod(file))
                btn.pack(pady=5)
        else:
            lbl = tk.Label(self.files_frame, text="❌ Aucun fichier trouvé",
                           font=("Arial", 14), fg="red", bg="#1a1a1a")
            lbl.pack()

    def go_back(self):
        self.controller.show_frame(self.back_page)

    def download_mod(self, file):
        target_dir = filedialog.askdirectory(title="Choisis le dossier où installer le mod")
        if not target_dir:
            return
        try:
            shutil.copy(file, target_dir)
            messagebox.showinfo("Succès", f"{os.path.basename(file)} a été installé dans :\n{target_dir}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'installer {os.path.basename(file)} : {e}")

# --- Lancer l'app ---
if __name__ == "__main__":
    app = MinefutApp()
    app.mainloop()
