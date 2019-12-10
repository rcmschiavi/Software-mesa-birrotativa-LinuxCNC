# coding=utf-8

# Author: Lucas Costa Ferreira
# Fixes e implementação BBB: Rodolfo Cavour Moretti Schiavi
# Project: Projeto Integrador VI
# Sistema de Inspeção de Arame
# Informações importantes:
# Os arrays numpy são regidos por coordenadas (linhas, colunas) e não o padrão (x,y), ou seja leia-se (y,x)
# O DebugMode deve ser ativado apenas para Calibração fina nos filtros de imagem ou testes sem câmera.
#
#Módulo não padronizado devido a incompatibilidade e inconsistências
#
#Foram necessárias algumas modificações para funcionar na BBB, o readMe tem informações para resolução de problemas

import cv2 as cv
import numpy as np
import v4l2capture
import modbus
import os
import numpy as np
import select, time, json

def returnLargestContour(contours):
    biggestArea = 0
    selectContour = None
    for contour in contours:
        if cv.contourArea(contour) > biggestArea:
            biggestArea = cv.contourArea(contour)
            selectContour = contour
    return selectContour


def getWireLengthFromImage(cameraFrame, cmInPixels):
    try:
        imageROI = cameraFrame[60:420, 160:480]
        grayImage = cv.cvtColor(imageROI, cv.COLOR_BGR2GRAY)
        kernel = np.ones((5, 5), np.float32) / 25
        filteredImage = cv.filter2D(grayImage, -1, kernel)
        blurredImage = cv.blur(filteredImage, (5, 5))
        threshImage = cv.adaptiveThreshold(blurredImage, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 2)
        contours, hierarchy = cv.findContours(threshImage, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        wire = returnLargestContour(contours)
        (x, y), (w, h), angle = cv.minAreaRect(wire)
        if w > h:
            h = w
        wireLengthMm = ((h / cmInPixels) * 10)

        return wireLengthMm, wire
    except Exception as e:
        print("Não há contorno " + "Erro: " + str(e))
        return 0, None

def initializeCapture(camera):

    size_x, size_y = camera.set_format(640, 480, fourcc='MJPG')
    camera.create_buffers(1)
    camera.queue_all_buffers()
    camera.start()


def inspectionMode(camera, cmInPixels, MB, qRec):
    frame = None

    while frame == None:
        if not qRec.empty():
            data = qRec.get()
            data = json.loads(data)
            if data[0]["mode"]=="EXTESTOP":
                MB.writeESTOP(False)

        select.select((camera,), (), ())
        image_data = camera.read_and_queue()
        frame = cv.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv.cv.CV_LOAD_IMAGE_COLOR)
        rows, cols = frame.shape[:2]
        M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
        frame = cv.warpAffine(frame, M, (cols, rows))
        wireLengthMm, wire = getWireLengthFromImage(frame, cmInPixels)

        print wireLengthMm
        try:
            processedImage = frame[60:420, 160:480]
            cv.imwrite("processed.jpg", processedImage)
            print(wireLengthMm)
        except Exception as e:
            print("Contorno Inválido" + str(e))
            wireLengthMm = 0
        return wireLengthMm

def operate_wire(MB, camera, DBCP, dbcpTol,time_trying, qRec):
    MB.writeActivateInspect()
    avanco = False
    MB.setTimer(125)
    MB.writeFwdWire()
    t_i = time.time()

    while True:
        if time.time()<t_i+60*time_trying:
            # Tenta ajustar o arame durante n minutos indicados pelo default
            MB.writeDeactivateInspect()
            return 0

        if not qRec.empty():
            #Verifica se a parada de emergência foi ativada na gui
            data = qRec.get()
            data = json.loads(data)
            if data[0]["mode"]=="EXTESTOP":
                MB.writeESTOP(False)

        wireLengthMm = inspectionMode(camera, 115)
        error = DBCP - wireLengthMm
        if (abs(error)<dbcpTol) and not avanco:
            #Envia inspec_ok para o supervisório
            #Envia modbus modo_inspecao = False
            #Envia mesa_end_op = True e depois reseta depois de 100ms
            print "Inspeçao finalizada"
            MB.writeDeactivateInspect()
            return 1
        else:
            if error<0:
                print "Recua"
                value =150 #Função que resulta o tempo de recuo para um determinado erro
                MB.setTimer(value)
                MB.writeBackWire()
                avanco = False
            else:
                print "Avanca"
                MB.setTimer(100)
                MB.writeFwdWire()
                avanco = True



def main(MB,cmInPixels,DBCP,dbcpTol,time_trying,qRec):
    ''' O retorno dessa função indica o que ocorreu
    -1: Câmera não encontrada
    0: Não foi possível ajustar o comprimento do arame com os valores recebidos
    1: Arame ajustado como esperado
    '''
    #Verificação 10 endereços da camera
    for i in range(10):
        try:
            camera = v4l2capture.Video_device("/dev/video{}".format(i))
            break
        except:
            pass

    if camera == None:
        # Se nenhuma câmera for encontrada, retorna -1
        return -1

    # Program Sequence
    initializeCapture(camera)
    inspectionMode(camera,cmInPixels, MB, qRec)
    result = operate_wire(MB,camera,DBCP,dbcpTol,time_trying,qRec)
    camera.close()

    return result

