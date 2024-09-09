import cv2
import time
from skimage.metrics import structural_similarity as ssim
import numpy as np
import threading

class CameraRTSP:
    def __init__(self, name, link, timer, threshold):
        if not self.is_valid_rtsp(link):
            raise ValueError(f"O link fornecido não é um RTSP válido ou não foi possível abrir a transmissão: {link}")
        self.link = link
        self.name = name
        self.threshold = threshold
        self.timer = timer * 60
        self.start_time = time.time()
        self.frame = None  
        self.lock = threading.Lock()  # trava para acessar o frame de forma segura
        self.is_running = True  # controle da thread
        
        # inicia a thread p capturar os frames de forma continua
        self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()

        while self.frame is None:
            print("Aguardando captura do primeiro frame...")
            time.sleep(1)  # aguarda um pequeno tempo ate pegar o frame inicial

        # primeiro frame p comparaçao
        self.comp_frame = self.get_frame()

    def _capture_frames(self):
        cap = cv2.VideoCapture(self.link, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            raise ValueError(f"Erro ao abrir o link RTSP: {self.link}")

        while self.is_running:
            ret, frame = cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
            time.sleep(0.01)  # delay p evitar uso execssivo de cpu

        cap.release()

    def get_frame(self):
        # retorna o frame atual capturado pela thread
        with self.lock:
            if self.frame is not None:
                return self.frame
            else:
                raise ValueError("Nenhum frame disponível no momento")
            
    def check(self):
        frame = self.get_frame() # pega o frame atual

        gray_img1 = cv2.cvtColor(self.comp_frame, cv2.COLOR_BGR2GRAY)
        gray_img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ts = time.strftime("%Y%m%d-%H%M%S")
        # cv2.imwrite(f"comp_frame_{ts}.png", gray_img2)
        
        # calculo de similaridade
        score, diff = ssim(gray_img1, gray_img2, full=True)
        score = round(score * 100, 2)

        is_ok = True
        if score < self.threshold:
            is_ok = False

        print(f"Similaridade: {score}%")
        return is_ok, score

    def update_timer(self):
        # atualiza o temporizador e verifica a hora
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= self.timer:
            status, _ = self.check()
            self.start_time = time.time()
            return status

    def is_valid_rtsp(self, link):
        if not link.startswith('rtsp://'):
            return False
        cap = cv2.VideoCapture(link)
        if not cap.isOpened() or cap is None:
            return False
        cap.release()
        return True

    def change_timer(self, new_timer):
        self.timer = new_timer * 60
        self.start_time = time.time()

    def change_name(self, new_name):
        self.name = new_name

    def change_threshold(self, new_threshold):
        self.threshold = new_threshold

    def release(self):
        self.is_running = False
        self.capture_thread.join()
        print("Captura encerrada e thread finalizada.")

