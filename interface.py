import tkinter as tk
from tkinter import messagebox
from camera import CameraRTSP
import threading
import time

class CameraInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitoramento de Câmeras")
        self.root.geometry("600x500")
        self.root.config(bg="#f0f0f0")

        self.cameras = []

        menubar = tk.Menu(self.root)
        camera_menu = tk.Menu(menubar, tearoff=0)
        camera_menu.add_command(label="Adicionar Câmera", command=self.open_add_camera_window)
        menubar.add_cascade(label="Câmeras", menu=camera_menu)
        self.root.config(menu=menubar)

        self.camera_list_label = tk.Label(self.root, text="Câmeras Monitoradas", font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.camera_list_label.pack(pady=10)

        self.camera_list_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.camera_list_frame.pack(pady=10, fill="both", expand=True)

    def open_add_camera_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Adicionar Câmera")
        add_window.geometry("400x200")

        label_link = tk.Label(add_window, text="RTSP Link:", font=("Arial", 12))
        label_link.pack(pady=5)

        entry_link = tk.Entry(add_window, font=("Arial", 12), width=40)
        entry_link.pack(pady=5)

        label_timer = tk.Label(add_window, text="Tempo de Check (min):", font=("Arial", 12))
        label_timer.pack(pady=5)

        entry_timer = tk.Entry(add_window, font=("Arial", 12), width=10)
        entry_timer.pack(pady=5)

        add_button = tk.Button(add_window, text="Adicionar", font=("Arial", 12), command=lambda: self.add_camera(entry_link.get(), entry_timer.get(), add_window))
        add_button.pack(pady=20)

    def add_camera(self, link, timer, window):
        if not link or not timer.isdigit():
            messagebox.showwarning("Entrada Inválida", "Por favor, insira um link RTSP válido e um tempo de check em minutos.")
            return

        try:
            camera = CameraRTSP(link, int(timer))
            threading.Thread(target=self.init_camera, args=(camera, link, timer, window), daemon=True).start()

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def init_camera(self, camera, link, timer, window):
        try:
            # esperar carregamentoo do primeiro frame
            while camera.frame is None:
                time.sleep(1)

            # Se o frame foi capturado, adiciona à interface
            self.cameras.append(camera)
            self.add_camera_to_list(link, timer, camera)
            window.destroy()

            # inicia o monitoramento
            threading.Thread(target=self.monitor_camera, args=(camera,), daemon=True).start()

        except Exception as e:
            # se der erro antes de capturar o primeiro frame,
            messagebox.showerror("Erro", f"Erro ao carregar a câmera: {str(e)}")
            window.destroy()

    def add_camera_to_list(self, link, timer, camera):
        bg_color = "#ffffff" if len(self.cameras) % 2 == 0 else "#e0e0e0"

        # frame da cam
        camera_frame = tk.Frame(self.camera_list_frame, bg=bg_color, bd=2, relief="groove")
        camera_frame.pack(fill="x", pady=5, padx=10)

        # info
        camera_label = tk.Label(camera_frame, text=f"Câmera: {link} | Check: {timer} min", font=("Arial", 12), bg=bg_color)
        camera_label.pack(side="left", padx=10)

        # status
        status_label = tk.Label(camera_frame, text="●", font=("Arial", 16), fg="green", bg=bg_color)
        status_label.pack(side="left", padx=10)

        # alterar tempo de check
        change_timer_button = tk.Button(camera_frame, text="Alterar Tempo", command=lambda: self.open_change_timer_window(camera, camera_label, timer), font=("Arial", 10), bg="#f7f7f7")
        change_timer_button.pack(side="right", padx=10, pady=5)

        # remoçao da cam
        remove_button = tk.Button(camera_frame, text="X", command=lambda: self.remove_camera(camera, camera_frame), font=("Arial", 10), bg="red", fg="white")
        remove_button.pack(side="right", padx=5, pady=5)

        # vincula o status ao monitoramento da cam
        camera.status_label = status_label


    def remove_camera(self, camera, camera_frame):
        # encerra a thread da camera e adiciona um novo na lista
        camera.release()  
        camera_frame.destroy()
        self.cameras.remove(camera) 

    def open_change_timer_window(self, camera, camera_label, old_timer):
        # mudar tempo de check
        change_window = tk.Toplevel(self.root)
        change_window.title("Alterar Tempo de Check")
        change_window.geometry("300x150")

        label_timer = tk.Label(change_window, text="Novo Tempo de Check (min):", font=("Arial", 12))
        label_timer.pack(pady=5)

        entry_timer = tk.Entry(change_window, font=("Arial", 12), width=10)
        entry_timer.insert(0, str(old_timer))
        entry_timer.pack(pady=5)

        change_button = tk.Button(change_window, text="Alterar", font=("Arial", 12), command=lambda: self.change_camera_timer(camera, entry_timer.get(), camera_label, change_window))
        change_button.pack(pady=10)

    def change_camera_timer(self, camera, new_timer, camera_label, window):
        if not new_timer.isdigit():
            messagebox.showwarning("Entrada Inválida", "Por favor, insira um tempo de check válido em minutos.")
            return

        camera.change_timer(int(new_timer))

        # alterar label com novo tempo
        camera_label.config(text=f"Câmera: {camera.link} | Check: {new_timer} min")
        window.destroy()

    def monitor_camera(self, camera):
        while True:
            try:
                is_ok = camera.update_timer()

                if is_ok is not None: 
                    if is_ok:
                        camera.status_label.config(fg="green")  
                    else:
                        camera.status_label.config(fg="red") 
                        messagebox.showwarning("Alerta", f"Câmera {camera.link} com problemas. Checar transmissão! Em caso de falso alerta, por favor, adicione a câmera novamente.")

            except Exception as e:
                camera.status_label.config(fg="red")  # Se ocorrer um erro, status vermelho
                messagebox.showerror("Erro", f"Erro na câmera {camera.link}: {str(e)}")
            
            time.sleep(1)  # verificar a cada seg baetu o check

if __name__ == "__main__":
    root = tk.Tk()
    interface = CameraInterface(root)
    root.mainloop()
