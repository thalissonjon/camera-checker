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
        add_window.geometry("420x350")

        label_name = tk.Label(add_window, text="Nome da Câmera:", font=("Arial", 12))
        label_name.pack(pady=5)

        entry_name = tk.Entry(add_window, font=("Arial", 12), width=40)
        entry_name.pack(pady=5)

        label_link = tk.Label(add_window, text="RTSP Link:", font=("Arial", 12))
        label_link.pack(pady=5)

        entry_link = tk.Entry(add_window, font=("Arial", 12), width=40)
        entry_link.pack(pady=5)

        label_timer = tk.Label(add_window, text="Tempo de Check (min):", font=("Arial", 12))
        label_timer.pack(pady=5)

        entry_timer = tk.Entry(add_window, font=("Arial", 12), width=10)
        entry_timer.pack(pady=5)

        label_threshold = tk.Label(add_window, text="Threshold de Similaridade (%):", font=("Arial", 12))
        label_threshold.pack(pady=5)

        entry_threshold = tk.Entry(add_window, font=("Arial", 12), width=10)
        entry_threshold.pack(pady=5)

        add_button = tk.Button(add_window, text="Adicionar", font=("Arial", 12), command=lambda: self.add_camera(entry_name.get(), entry_link.get(), entry_timer.get(), entry_threshold.get(), add_window))
        add_button.pack(pady=20)

    def add_camera(self, name, link, timer, threshold, window):
        if not link or not timer.isdigit() or not threshold.isdigit():
            messagebox.showwarning("Entrada Inválida", "Por favor, insira um link RTSP válido, tempo de check e threshold em minutos.")
            return

        try:
            camera = CameraRTSP(name, link, int(timer), int(threshold))
            threading.Thread(target=self.init_camera, args=(camera, name, timer, window), daemon=True).start()

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def init_camera(self, camera, name, timer, window):
        try:
            # esperar carregamento do primeiro frame
            while camera.frame is None:
                time.sleep(1)

            # assim q for cap o frame ir pra interface
            self.cameras.append(camera)
            self.add_camera_to_list(name, timer, camera)
            window.destroy()

            # inicia o monitoramento
            threading.Thread(target=self.monitor_camera, args=(camera,), daemon=True).start()

        except Exception as e:
            # se der erro antes de capturar o primeiro frame
            messagebox.showerror("Erro", f"Erro ao carregar a câmera: {str(e)}")
            window.destroy()

    def add_camera_to_list(self, name, timer, camera):
        bg_color = "#ffffff" if len(self.cameras) % 2 == 0 else "#e0e0e0"

        # frame da cam
        camera_frame = tk.Frame(self.camera_list_frame, bg=bg_color, bd=2, relief="groove")
        camera_frame.pack(fill="x", pady=5, padx=10)

        # info
        camera_label = tk.Label(camera_frame, text=f"Câmera: {name} | Check: {timer} min", font=("Arial", 12), bg=bg_color)
        camera_label.pack(side="left", padx=10)

        # status
        status_label = tk.Label(camera_frame, text="●", font=("Arial", 16), fg="green", bg=bg_color)
        status_label.pack(side="left", padx=10)

        # botão de configuração
        config_button = tk.Button(camera_frame, text="Config", command=lambda: self.open_config_window(camera, camera_label), font=("Arial", 10), bg="#f7f7f7")
        config_button.pack(side="right", padx=10, pady=5)

        # remoção da cam
        remove_button = tk.Button(camera_frame, text="X", command=lambda: self.remove_camera(camera, camera_frame), font=("Arial", 10), bg="red", fg="white")
        remove_button.pack(side="right", padx=5, pady=5)

        # vincula o status ao monitoramento da cam
        camera.status_label = status_label


    def remove_camera(self, camera, camera_frame):
        # encerra a thread da camera e remove da lista
        camera.release()  
        camera_frame.destroy()
        self.cameras.remove(camera) 

    def open_config_window(self, camera, camera_label):
        # abrir janela de config para nome, tempo e threshold
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurações da Câmera")
        config_window.geometry("420x250")

        label_name = tk.Label(config_window, text="Nome da Câmera:", font=("Arial", 12))
        label_name.pack(pady=5)

        entry_name = tk.Entry(config_window, font=("Arial", 12), width=40)
        entry_name.insert(0, camera.name)
        entry_name.pack(pady=5)

        label_timer = tk.Label(config_window, text="Tempo de Check (min):", font=("Arial", 12))
        label_timer.pack(pady=5)

        entry_timer = tk.Entry(config_window, font=("Arial", 12), width=10)
        entry_timer.insert(0, str(camera.timer // 60))
        entry_timer.pack(pady=5)

        label_threshold = tk.Label(config_window, text="Threshold de Similaridade (%):", font=("Arial", 12))
        label_threshold.pack(pady=5)

        entry_threshold = tk.Entry(config_window, font=("Arial", 12), width=10)
        entry_threshold.insert(0, str(camera.threshold))
        entry_threshold.pack(pady=5)

        config_button = tk.Button(config_window, text="Salvar", font=("Arial", 12), command=lambda: self.update_camera_config(camera, entry_name.get(), entry_timer.get(), entry_threshold.get(), camera_label, config_window))
        config_button.pack(pady=10)


    def update_camera_config(self, camera, new_name, new_timer, new_threshold, camera_label, window):
        if not new_timer.isdigit() or not new_threshold.isdigit():
            messagebox.showwarning("Entrada Inválida", "Por favor, insira valores válidos para o tempo de check e o threshold.")
            return

        # att as config da camera
        camera.change_name(new_name)
        camera.change_timer(int(new_timer))
        camera.change_threshold(int(new_threshold))

        # att label da cam 
        camera_label.config(text=f"Câmera: {new_name} | Check: {new_timer} min")
        window.destroy()

    def monitor_camera(self, camera):
        while camera.is_running:
            try:
                is_ok = camera.update_timer()

                if is_ok is not None: 
                    if is_ok:
                        camera.status_label.config(fg="green")  
                    else:
                        camera.status_label.config(fg="red") 
                        messagebox.showwarning("Alerta", f"Câmera {camera.name} com problemas. Checar transmissão! Em caso de falso alerta, por favor, adicione a câmera novamente.")

            except Exception as e:
                camera.status_label.config(fg="red")  
                messagebox.showerror("Erro", f"Erro na câmera {camera.name}: {str(e)}")
            
            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    interface = CameraInterface(root)
    root.mainloop()
