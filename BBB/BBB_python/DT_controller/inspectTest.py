# coding=utf-8
import cv2 as cv
import numpy as np
import modbus


# Author: Lucas Costa Ferreira
# Project: Projeto Integrador VI
# Sistema de Inspeção de Arame
# Informações importantes:
# Os arrays numpy são regidos por coordenadas (linhas, colunas) e não o padrão (x,y), ou seja leia-se (y,x)
# O DebugMode deve ser ativado apenas para Calibração fina nos filtros de imagem ou testes sem câmera.
#
#Módulo não padronizado devido a incompatibilidade e inconsistências

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

    isValidFrame, preCameraFrame = camera.read()
    rows, cols = preCameraFrame.shape[:2]
    M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
    cameraFrame = cv.warpAffine(preCameraFrame, M, (cols, rows))
    if not isValidFrame:
        print("Frame failure")
        return -1
    frameHeight, frameWidth = cameraFrame.shape[:2]
    return frameWidth, frameHeight

def inspectionMode( camera, cmInPixels):

    isValidFrame, preCameraFrame = camera.read()
    rows, cols = preCameraFrame.shape[:2]
    M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
    cameraFrame = cv.warpAffine(preCameraFrame, M, (cols, rows))
    if not isValidFrame:
        print("Frame failure")
        return -1
    wireLengthMm, wire = getWireLengthFromImage(cameraFrame, cmInPixels)
    try:
        box = np.int0(cv.boxPoints(cv.minAreaRect(wire)))
        processedImage = cameraFrame[60:420, 160:480]
        cv.drawContours(processedImage, [box], 0, (0, 0, 255), 2)
        print(wireLengthMm)
    except:
        print("Contorno Inválido")
        wireLengthMm = 0
    cv.waitKey(1)
    return wireLengthMm


def endProgram(camera):
    camera.release()


def operate_wire(MB, camera, DBCP, dbcpTol):
    MB.writeActivateInspect()
    avanco = False
    add_fwrd = 0
    MB.setTimer(125)
    MB.writeFwdWire()
    while True:

        wireLengthMm = inspectionMode(camera, 115)
        error = DBCP - wireLengthMm
        if (abs(error)<dbcpTol) and not avanco:
            #Envia inspec_ok para o supervisório
            #Envia modbus modo_inspecao = False
            #Envia mesa_end_op = True e depois reseta depois de 100ms
            print "Inspeçao finalizada"
            MB.writeDeactivateInspect()
            return True
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



def main():
    MB = modbus.Modbus()
    camera = cv.VideoCapture(1)
    cmInPixels = 115
    DBCP = 20
    dbcpTol = 2

    # Program Sequence
    initializeCapture(camera)
    operate_wire(MB, camera, DBCP, dbcpTol)

    print(cmInPixels)
    endProgram(camera)

main()