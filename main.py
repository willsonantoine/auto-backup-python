import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import json
import time
import threading
import datetime
import pymysql
import io
import shutil
import winsound
import winreg
import sys

class MySQLBackupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mlinzi Auto Backup")
        self.geometry("800x650")
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "mlinzi_icon.ico")
        self.iconbitmap(icon_path)
        self.config_file = "config.json"
        self.log_file = "app.log"
        self.load_config()
        self.auto_backup_thread = None
        self.running_backup = False
        self.auto_backup_loop_stop_event = threading.Event()
        self.next_backup_time = None
        self.create_widgets()
        self.grid_columnconfigure(0, weight=1)
        self.rowconfigure(1,weight=1)

    def create_widgets(self):
        # Style
        style = ttk.Style(self)
        style.configure('TLabel', font=('Arial', 10), padding=5)
        style.configure('TEntry', font=('Arial', 10), padding=5)
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TCheckbutton', font=('Arial', 10), padding=5)
        style.configure('TFrame', background="white")

        # Bouton pour afficher la doc
        doc_button = ttk.Button(self, text="Help", command=self.open_documentation)
        doc_button.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        
        # Créer un Canvas pour la zone scrollable
        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        # Ajouter une barre de défilement verticale
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        # Configurer le Canvas pour la barre de défilement
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Créer un Frame intérieur pour contenir les widgets
        self.scrollable_frame = ttk.Frame(self.canvas, style='TFrame')
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Frame pour les paramètres de connexion
        connection_frame = ttk.LabelFrame(self.scrollable_frame, text="Connection Settings", padding=10)
        connection_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        connection_frame.grid_columnconfigure(1, weight=1)
        
         # Chemin MySQL Executable
        ttk.Label(connection_frame, text="MySQL Executable Path:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.mysql_path_entry = ttk.Entry(connection_frame, width=50)
        self.mysql_path_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        self.mysql_path_entry.insert(0, self.config.get("mysql_path", ""))
        select_mysql_path_button = ttk.Button(connection_frame, text="Select", command=self.select_mysql_path)
        select_mysql_path_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Hostname
        ttk.Label(connection_frame, text="Hostname:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.hostname_entry = ttk.Entry(connection_frame)
        self.hostname_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.hostname_entry.insert(0, self.config.get("hostname", "localhost"))
        
        # Port
        ttk.Label(connection_frame, text="Port:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.port_entry = ttk.Entry(connection_frame)
        self.port_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        self.port_entry.insert(0, self.config.get("port", "3306"))

        # Nom d'utilisateur
        ttk.Label(connection_frame, text="Username:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.username_entry = ttk.Entry(connection_frame)
        self.username_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        self.username_entry.insert(0, self.config.get("username", ""))

        # Mot de passe
        ttk.Label(connection_frame, text="Password:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.password_entry = ttk.Entry(connection_frame, show="*")
        self.password_entry.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        self.password_entry.insert(0, self.config.get("password", ""))

        # Bouton Connect
        connect_button = ttk.Button(connection_frame, text="Connect", command=self.update_database_list)
        connect_button.grid(row=4, column=2, padx=5, pady=5)
       
        # Frame pour la configuration de la base de données
        database_frame = ttk.LabelFrame(self.scrollable_frame, text="Database Settings", padding=10)
        database_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        database_frame.grid_columnconfigure(1, weight=1)

         # Selection de la base de données
        ttk.Label(database_frame, text="Select Database:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.database_combobox = ttk.Combobox(database_frame, values=[], state="readonly", width=50)
        self.database_combobox.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        if self.config.get("database"):
            self.database_combobox.set(self.config.get("database"))
        
         # Chemin du Backup
        ttk.Label(database_frame, text="Backup Path:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        path_frame = ttk.Frame(database_frame)
        path_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.backup_path_entry = ttk.Entry(path_frame, state="readonly", width=40)
        self.backup_path_entry.pack(side="left",fill="x", expand=True)
        select_backup_path_button = ttk.Button(path_frame, text="Select Path", command=self.select_backup_path)
        select_backup_path_button.pack(side="left")
        
        # Liste des sauvegardes
        ttk.Label(database_frame, text="Backups in directory:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.backup_listbox = tk.Listbox(database_frame, height=5, width=60)
        self.backup_listbox.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        self.update_backup_list()

        # Bouton exporter sauvegarde selectionée
        export_backup_button = ttk.Button(database_frame, text="Export Backup", command=self.export_selected_backup)
        export_backup_button.grid(row=3, column=1, pady=5, sticky="w", padx=10)

        # Frame pour la configuration de la sauvegarde auto
        auto_backup_frame = ttk.LabelFrame(self.scrollable_frame, text="Auto Backup Settings", padding=10)
        auto_backup_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        auto_backup_frame.grid_columnconfigure(1, weight=1)

        # Backup Automatique
        self.auto_backup_var = tk.BooleanVar(value=self.config.get("auto_backup", False))
        auto_backup_check = ttk.Checkbutton(auto_backup_frame, text="Enable Auto Backup", variable=self.auto_backup_var, command=self.toggle_auto_backup)
        auto_backup_check.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        ttk.Label(auto_backup_frame, text="Backup Interval (minutes):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.backup_interval_entry = ttk.Entry(auto_backup_frame, width=10)
        self.backup_interval_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.backup_interval_entry.insert(0, self.config.get("backup_interval", "30"))

        # Label pour afficher le temps avant la prochaine sauvegarde automatique
        self.next_backup_label = ttk.Label(auto_backup_frame, text="Next backup in: N/A", font=('Arial', 10))
        self.next_backup_label.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew", padx=10)

        # Bouton de backup manuel
        backup_button = ttk.Button(self.scrollable_frame, text="Start Backup", command=self.perform_backup_wrapper)
        backup_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.scrollable_frame, orient="horizontal", length=300, mode="determinate", maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        
        # Bouton Save Config
        save_config_button = ttk.Button(self.scrollable_frame, text="Save Configuration", command=self.save_config)
        save_config_button.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        
         # Checkbox Lancer avec windows
        self.start_with_windows_var = tk.BooleanVar(value=self.config.get("start_with_windows", False))
        start_with_windows_check = ttk.Checkbutton(self.scrollable_frame, text="Start with Windows", variable=self.start_with_windows_var)
        start_with_windows_check.grid(row=6, column=0, sticky="w", padx=10, pady=5)
      

        # Message de Status
        self.status_label = ttk.Label(self.scrollable_frame, text="", font=('Arial', 10))
        self.status_label.grid(row=7, column=0, columnspan=2, pady=10, sticky="ew")
        
        # Zone de log
        ttk.Label(self.scrollable_frame, text="Logs:").grid(row=8, column=0, sticky="w", padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(self.scrollable_frame, height=8, width=80)
        self.log_text.grid(row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.log_text.config(state="disabled")# pour eviter l'edition du log

        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Met à jour la région de défilement du canvas lorsque sa taille change."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def select_mysql_path(self):
        file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if file_path:
            self.mysql_path_entry.delete(0, tk.END)
            self.mysql_path_entry.insert(0, file_path)

    def select_backup_path(self):
        file_path = filedialog.askdirectory()
        if file_path:
            self.backup_path_entry.config(state="normal")
            self.backup_path_entry.delete(0, tk.END)
            self.backup_path_entry.insert(0, file_path)
            self.backup_path_entry.config(state="readonly")
            self.update_backup_list()

    def update_backup_list(self):
        backup_path = self.get_backup_path()
        self.backup_listbox.delete(0, tk.END)
        if backup_path and os.path.exists(backup_path):
           try:
             files = os.listdir(backup_path)
             for file in files:
                if file.lower().endswith(".sql"):
                    self.backup_listbox.insert(tk.END,file)
           except Exception as e:
               self.log_message("Error loading backup file list : " + str(e))
               messagebox.showerror("Error", "Error loading backup file list")

    def export_selected_backup(self):
        selected_index = self.backup_listbox.curselection()
        if not selected_index:
           messagebox.showerror("Error", "Please select a backup file to export.")
           return
        backup_path = self.get_backup_path()
        selected_file = self.backup_listbox.get(selected_index[0])
        source_path = os.path.join(backup_path,selected_file)
        if not os.path.exists(source_path):
          messagebox.showerror("Error", "The selected backup file doesn't exist.")
          return
        target_path = filedialog.askdirectory(title="Select export destination")
        if not target_path:
            return
        try:
            shutil.copy2(source_path, target_path)
            messagebox.showinfo("Success", f"Backup {selected_file} exported to {target_path} with success!")
            self.log_message(f"Backup {selected_file} exported to {target_path} with success!")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting backup: {e}")
            self.log_message(f"Error exporting backup: {e}")

    def get_backup_path(self):
        return self.backup_path_entry.get()

    def update_database_list(self):
        hostname = self.hostname_entry.get()
        port = self.port_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not all([hostname, port, username, password]):
            self.database_combobox.config(values=[])
            return
        try:
             mydb = pymysql.connect(
                host=hostname,
                port=int(port),
                user=username,
                password=password,
            )
             cursor = mydb.cursor()
             cursor.execute("SHOW DATABASES")
             databases = [db[0] for db in cursor.fetchall()]
             self.database_combobox.config(values=databases)
             mydb.close()
        except pymysql.Error as e:
            self.database_combobox.config(values=[])
            messagebox.showerror("Error", f"Could not retrieve databases, please check hostname, port, username and password. Error:{e}")
            self.log_message(f"Could not retrieve databases, please check hostname, port, username and password. Error:{e}")

    def perform_backup_wrapper(self):
        if self.running_backup:
            messagebox.showerror("Error", "A backup is already running.")
            return
        self.running_backup = True
        self.status_label.config(text="Backup in progress...")
        self.progress_bar["value"] = 0
        self.update()
        threading.Thread(target=self.perform_backup).start()

    def perform_backup(self):
        mysql_path = self.mysql_path_entry.get()
        hostname = self.hostname_entry.get()
        port = self.port_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        database = self.database_combobox.get()
        backup_path = self.get_backup_path()

        if not all([mysql_path, hostname, port, username, password, database, backup_path]):
            messagebox.showerror("Error", "Please fill in all the fields.")
            self.running_backup = False
            self.status_label.config(text="Backup failed.")
            return
        
        timestamp = datetime.datetime.now().strftime("%d_%m_%Y_a_%H_h_%M_min")
        backup_filename = f"{database}_{timestamp}.sql"
        full_backup_path = os.path.join(backup_path,backup_filename)
        cmd = f'"{mysql_path}" -h{hostname} -P{port} -u{username} -p{password} {database} --add-drop-table --complete-insert --no-tablespaces --result-file="{full_backup_path}"'
       
        try:
            process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1, text=False)
            self.update_progress(process)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                self.status_label.config(text="Backup completed successfully!")
                self.log_message("Backup completed successfully!")
                self.update_backup_list()
                winsound.Beep(2500, 1000) # Bip
            else:
                self.status_label.config(text="Backup failed. See error details in console.")
                self.log_message(f"Backup failed. See error details in console. Error:{stderr.decode()}")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}")
            self.log_message(f"Error:{e}")
        finally:
             self.running_backup = False

    def update_progress(self, process):
        total_size = 0
        if process.stdout:
           try:
              while True:
                  chunk = process.stdout.read(1024)
                  if not chunk:
                     break
                  total_size += len(chunk)
                  progress_percentage = min(total_size / 1000000, 100)
                  self.progress_bar['value'] = progress_percentage
                  self.update()
           except Exception as e:
                print("Error on update progress " + str(e))
        self.progress_bar['value'] = 100
        self.update()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}

    def save_config(self):
        self.config["mysql_path"] = self.mysql_path_entry.get()
        self.config["hostname"] = self.hostname_entry.get()
        self.config["port"] = self.port_entry.get()
        self.config["username"] = self.username_entry.get()
        self.config["password"] = self.password_entry.get()
        self.config["database"] = self.database_combobox.get()
        self.config["backup_path"] = self.get_backup_path()
        self.config["auto_backup"] = self.auto_backup_var.get()
        self.config["backup_interval"] = self.backup_interval_entry.get()
        self.config["start_with_windows"] = self.start_with_windows_var.get()
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving configuration: {e}")
            self.log_message(f"Error saving configuration: {e}")
            return
        messagebox.showinfo("Success", "Configuration Saved.")
        self.start_auto_backup()
        self.update_next_backup_label()
        self.update_start_with_windows_registry()

    def toggle_auto_backup(self):
        self.start_auto_backup()
        self.update_next_backup_label()

    def start_auto_backup(self):
        if self.auto_backup_thread and self.auto_backup_thread.is_alive():
            self.auto_backup_loop_stop_event.set()
            self.auto_backup_thread.join()
            self.auto_backup_thread = None
            self.auto_backup_loop_stop_event.clear()

        if self.auto_backup_var.get():
            try:
                interval = int(self.backup_interval_entry.get())
                if interval <= 0:
                    messagebox.showerror("Error", "Please enter a valid backup interval greater than 0.")
                    return
                self.auto_backup_thread = threading.Thread(target=self.auto_backup_loop, args=(interval * 60,))
                self.auto_backup_thread.start()
                self.update_next_backup_label()
            except ValueError:
                 messagebox.showerror("Error", "Please enter a valid integer for backup interval.")

    def auto_backup_loop(self, interval):
        while not self.auto_backup_loop_stop_event.is_set():
            self.next_backup_time = datetime.datetime.now() + datetime.timedelta(seconds=interval)
            self.perform_backup()
            for _ in range(interval):
               if self.auto_backup_loop_stop_event.is_set():
                   break
               time.sleep(1)
            if not self.auto_backup_var.get():
               break

    def update_next_backup_label(self):
        if self.auto_backup_var.get() and self.next_backup_time:
           now = datetime.datetime.now()
           time_left = self.next_backup_time - now
           if time_left.total_seconds() > 0:
                minutes = time_left.seconds // 60
                seconds = time_left.seconds % 60
                self.next_backup_label.config(text=f"Next backup in: {minutes:02d}:{seconds:02d}")
           else:
               self.next_backup_label.config(text="Next backup in: Now!")
        else:
             self.next_backup_label.config(text="Next backup in: N/A")
        self.after(1000, self.update_next_backup_label)

    def open_documentation(self):
        doc_window = tk.Toplevel(self)
        doc_window.title("Documentation")
            
        # Description et manuel
        description = "Mlinzi Auto Backup est une application de bureau pour automatiser les sauvegardes de bases de données MySQL.\n" \
                      "Elle permet de configurer la connexion à votre serveur MySQL, de choisir une base de données à sauvegarder, de définir le chemin de sauvegarde,\n" \
                      "de planifier des sauvegardes automatiques à des intervalles réguliers, et d'exporter les sauvegardes vers un support externe.\n" \
                      "Manuel d'utilisation:\n" \
                      "1. Renseignez le chemin vers 'mysqldump.exe'\n" \
                      "2. Renseignez les informations de connexion à MySQL.\n" \
                      "3. Cliquez sur 'Connect' pour charger la liste des bases de données.\n" \
                      "4. Sélectionnez une base de données, et le chemin de sauvegarde.\n" \
                      "5. Activez ou désactivez la sauvegarde automatique avec son intervalle.\n" \
                      "6. Cliquez sur 'Save Configuration' pour enregistrer vos préférences et activer/désactiver les sauvegardes automatiques.\n" \
                      "7. Cliquez sur 'Start Backup' pour démarrer une sauvegarde manuelle.\n" \
                      "8.  La liste des backups se trouvant dans le chemin de sauvegarde s'affichera a coté du select backup path.\n" \
                      "9. Selectionner un backup puis cliquer sur export backup pour choisir la destination de la sauvegarde\n\nConcepteur :\nNom : WILLSON VULEMBERE ANTOINE\nEmail : willsonantoine@gmail.com\nTéléphone : +243990084881\nProfil Linkedin : https://www.linkedin.com/in/cedryson-vulembere-368a76ba/"
        description_label = ttk.Label(doc_window, text=description, justify="left", wraplength=600)
        description_label.pack(padx=20, pady=20)

    def log_message(self, message):
        """Ajoute un message au log, met a jour le log_file"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}\n"
        try:
          with open(self.log_file, "a") as f:
              f.write(log_entry)
        except Exception as e :
          print("Error on log message : " + str(e))
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, log_entry)
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)

    def update_start_with_windows_registry(self):
         app_path = os.path.abspath(__file__)
         app_path = app_path.replace(".py",".exe") if app_path.endswith(".py") else app_path
         key_name = "MlinziAutoBackup"
         try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                                0, winreg.KEY_ALL_ACCESS) as reg_key:
              if self.start_with_windows_var.get():
                 winreg.SetValueEx(reg_key,key_name,0,winreg.REG_SZ,app_path)
                 self.log_message(f"Application added to windows start with path {app_path}")
              else:
                try:
                  winreg.DeleteValue(reg_key,key_name)
                  self.log_message(f"Application removed from windows start")
                except FileNotFoundError:
                  pass
         except Exception as e:
            messagebox.showerror("Error", f"Error modifying registry {e}")
            self.log_message(f"Error modifying registry: {e}")


if __name__ == "__main__":
    app = MySQLBackupApp()
    app.mainloop()