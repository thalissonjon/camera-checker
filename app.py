# from camera import CameraRTSP
# import cv2
# import time

# camera1 = CameraRTSP('rtsp://localhost:8554/calcada', 0.5)
# # frame = camera1.get_frame()


# try:
#     while True: 
#         camera1.update_timer()
#         # camera1.update_timer()  # Atualiza o temporizador e chama o método check() quando o tempo é atingido
#         if cv2.waitKey(1) & 0xFF == ord('q'):  # Pressione 'q' para sair
#             break
#         time.sleep(5)
# except KeyboardInterrupt:
#     print("Encerrando o monitoramento...")
# finally:
#     camera1.release()  # Libera os recursos da câmera quando o loop termina
#     cv2.destroyAllWindows()