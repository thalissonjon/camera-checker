import cv2
import time
from skimage.metrics import structural_similarity as ssim
import numpy as np

class CameraRTSP:
    def __init__(self, link, timer):
        if not self.is_valid_rtsp(link):
            raise ValueError(f"O link fornecido não é um RTSP válido ou não foi possível abrir a transmissão: {link}")
        self.link = link
        # self.timer = timer * 60
        self.timer = timer
        self.start_time = time.time()

        self.cap = cv2.VideoCapture(self.link, cv2.CAP_FFMPEG)
        self.comp_frame = self.get_frame() # pegar o primeiro frame pra usar como comparativo


    def check(self):
        # img1 = cv2.imread("test/bubu1.jpg")
        # img2 = cv2.imread("test/bubu2.jpg")
        frame = self.get_frame()
        gray_img1 = cv2.cvtColor(self.comp_frame, cv2.COLOR_BGR2GRAY)
        gray_img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ts = time.strftime("%Y%m%d-%H%M%S")
        cv2.imwrite(f"comp_frame{ts}.png", gray_img2)
        score, diff = ssim(gray_img1, gray_img2, full=True)
        
        # diff tem as diferenças normalizadas entre as imagens
        # diff = (diff * 255).astype("uint8")

        score = round(score * 100, 2)
        is_ok = True

        if score < 10:
            is_ok = False
        
        print(score)
                # print(f"similaridade das imagens: {score*100:.2f}%")
        # cv2.imshow("diferença entre as imagens imagens", diff)

        # cv2.imwrite("diff_image.png", diff)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        return is_ok, score


    def change_timer(self, new_timer):
        self.timer = new_timer * 60
        self.start_time = time.time()
    

    def update_timer(self):
        self.is_valid_rtsp(self.link)
        current_time = time.time()
        elapsed_time = current_time - self.start_time  # tempo que passou desde que iniciou
        if elapsed_time >= self.timer: 
            self.check()
            self.start_time = time.time()  


    def is_valid_rtsp(self, link):
        if not link.startswith('rtsp://'):
            return False
        cap = cv2.VideoCapture(link)
        if not cap.isOpened() or cap is None:
            # raise ValueError(f"Erro ao abrir o link RTSP: {link}")
            return False
        cap.release()
        return True
    

    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            print("Frame capturado com sucesso!")
            return frame
        else:
            raise ValueError(f"Erro ao capturar o frame")
        
    def release(self):
        # liberar os recursos do video cappture
        if self.cap.isOpened():
            self.cap.release()