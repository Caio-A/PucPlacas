from django.shortcuts import render
from django.http import StreamingHttpResponse
from .models import Detections
import boto3
import cv2
import threading
import numpy as np
import os
import datetime

#carregando arquivo de caracteristicas de carros
car_classifier = cv2.CascadeClassifier('./static/src/cars.xml')

#Criar as views 
#classe para fazer a detecção de texto em imagens ja segmentadas
class AwsDetect():
    def __init__(self):
        #threading para fazer assincronamente enquanto o servidor estiver ligado
        
        threading.Thread(target=self.recursivo, args=()).start()

    def guardanobanco(placa, arquivo):
        db = Detections()
        db.placa = placa
        db.ref_img = arquivo
        db.save()

    def recursivo(self):
        loop = 1
        #credenciais aws 
        access_key_id = "AKIAYGCRKJCJOKMJLVGI"
        secret_access_key = "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"
        client = boto3.client('rekognition' , region_name='us-east-1', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
        while loop == True:
            db = Detections()
            arquivos = os.listdir('./')
            i = 0
            #percorre todas as detecções feitas pelo opencv
            for arquivos[i] in arquivos:
                if arquivos[i] == 'done':
                    pass
                else:
                    #abre o arquivo escolhido na iteração
                    with open(arquivos[i], 'rb') as image_file:
                        source_bytes = image_file.read()
                        #print('imagem lida= ' + arquivos[i] +'\n')
                    
                    #chama o serviço da aws
                    detect_text = client.detect_text(Image={'Bytes': source_bytes})
                    detect_text = detect_text["TextDetections"]
                    
                    #tratamento caso a resposta nao ache nenhum texto
                    if detect_text != []:
                        count = 0
                        for detect_text[count] in detect_text:
                            placa = detect_text[count]
                            placa = repr(placa['DetectedText'])
                            placa = placa.replace("'", "")
                            try:
                                os.rename(arquivos[i], f"./done/{arquivos[i]}")
                                AwsDetect.guardanobanco(placa,arquivos[i])
                            except:
                                pass
                    else:
                        try:
                            os.rename(arquivos[i], f"./done/{arquivos[i]}")
                            AwsDetect.guardanobanco('Inconclusivo', arquivos[i])
                        except:
                            pass

#template home
def home(request):
    detection = {'detections':Detections.objects.all()}
    return render(request, 'home.html', detection)
    
#template camera
def camera(cam):
    try:
        #começa o processo de captura e identificação aws(sempre começa quando é chamado pela primeira vez)
        cam = Camera()
        aws = AwsDetect()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    #renderiza a página /camera
    return render(cam)

#objeto camera
class Camera(object):
    def __init__(self):
        #muda a pasta destino das capturas
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        diretorio_atual = os.getcwd()
        diretorio_atual = repr(diretorio_atual)
        diretorio_alvo = "C:\\Users\\Cliente\\Desktop\\placas\\placas\\static\\detections"
        diretorio_alvo = repr(diretorio_alvo)
        #tratamento para f5 caso já esteja na pasta destino
        if diretorio_atual != diretorio_alvo:
            os.chdir('./static/detections')
            diretorio_atual = os.getcwd() 
        #começa o update assincrono da captura de video
        threading.Thread(target=self.update, args=()).start()
    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpeg', image)
        return jpeg.tobytes()

    def update(self):
        i = 0
        #loop para pegar sempre o frame mais atual
        while True:
            #leitura do frame da camera
            (self.grabbed, self.frame) = self.video.read()

            #tratamento em cima do frame coletado
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray,(5,5),0)
            dilated = cv2.dilate(blur,np.ones((3,3)))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel) 

            #chamada do cascade classifier
            cars = car_classifier.detectMultiScale(closing, 1.65,minNeighbors= 2,minSize= [100,100])

            #segmentando imagens conforme a lista de detecções por frame
            for (x,y,w,h) in cars:
                #para não salvar todo frame
                if i>=14:
                    id = datetime.datetime.today()
                    # Formata a data e hora como uma string
                    id = repr(id)
                    id = id.replace(id[0:17], "")
                    id = id.replace("(", "")
                    id = id.replace(")", "")
                    id = id.replace(", ", "-")
                    #função para salvar o frame com um nome especifico(imagem ja segmentada)
                    cv2.imwrite(f"{id}.jpeg", self.frame[y:y+h,x-50:x+w+50])
                    #log de detecção registrada
                    print("detecção registrada " + id)
                    i = 0
                
                #tratamento visual para quem vê o video através do home
                cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
                cv2.putText(self.frame, 'Carro', (x,y-10), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0), thickness=2)
                #passa para o proximo item da lista
                i = i+1

#gerador de camera
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')