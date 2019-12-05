# coding=utf-8
import cv2 as cv
import numpy as np
import modbus
import time


# Author: Lucas Costa Ferreira
# Project: Projeto Integrador VI
# Sistema de Inspeção de Arame
# Informações importantes:
# Os arrays numpy são regidos por coordenadas (linhas, colunas) e não o padrão (x,y), ou seja leia-se (y,x)
# O DebugMode deve ser ativado apenas para Calibração fina nos filtros de imagem ou testes sem câmera.


def nothing():
    pass


def returnLargestContour(contours):
    biggestArea = 0
    selectContour = None
    for contour in contours:
        if cv.contourArea(contour) > biggestArea:
            biggestArea = cv.contourArea(contour)
            selectContour = contour
    return selectContour


def getWireLengthFromImage(debugMode, cameraFrame, cmInPixels):
    try:
        imageROI = cameraFrame[60:420, 160:480]
        grayImage = cv.cvtColor(imageROI, cv.COLOR_BGR2GRAY)
        if debugMode:
            cv.namedWindow('gray')
            cv.imshow('gray', grayImage)
        kernel = np.ones((5, 5), np.float32) / 25
        filteredImage = cv.filter2D(grayImage, -1, kernel)
        blurredImage = cv.blur(filteredImage, (5, 5))
        if debugMode:
            cv.namedWindow('filter')
            cv.imshow('filter', blurredImage)
        threshImage = cv.adaptiveThreshold(blurredImage, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 2)
        if debugMode:
            cv.namedWindow('thresh')
            cv.imshow('thresh', threshImage)
        contours, hierarchy = cv.findContours(threshImage, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        wire = returnLargestContour(contours)
        (x, y), (w, h), angle = cv.minAreaRect(wire)
        if w > h:
            h = w
        wireLengthMm = ((h / cmInPixels) * 10)

        return wireLengthMm, wire
    except:
        return 0, None

def initializeCapture(camera):
    cv.namedWindow("Wire Inspection")
    isValidFrame, preCameraFrame = camera.read()
    try:
        rows, cols = preCameraFrame.shape[:2]
        M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
        cameraFrame = cv.warpAffine(preCameraFrame, M, (cols, rows))
        if not isValidFrame:
            print("Frame failure")
            return -1
        frameHeight, frameWidth = cameraFrame.shape[:2]
        return frameWidth, frameHeight
    except Exception as e:
        print ("Erro: " + str(e))

def inspectionMode(debugMode, camera, cmInPixels):
    cv.namedWindow('Wire Inspection')
    tecla = ''
    while tecla != 't':
        isValidFrame, preCameraFrame = camera.read()
        rows, cols = preCameraFrame.shape[:2]
        M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
        cameraFrame = cv.warpAffine(preCameraFrame, M, (cols, rows))
        if not isValidFrame:
            print("Frame failure")
            return -1
        wireLengthMm, wire = getWireLengthFromImage(debugMode, cameraFrame, cmInPixels)
        try:
            box = np.int0(cv.boxPoints(cv.minAreaRect(wire)))
            processedImage = cameraFrame[60:420, 160:480]
            cv.drawContours(processedImage, [box], 0, (0, 0, 255), 2)
            cv.imshow('Wire Inspection', processedImage)
            print(wireLengthMm)
        except:
            processedImage = cameraFrame[60:420, 160:480]
            cv.imshow('Wire Inspection', processedImage)
            wireLengthMm = 0
        cv.waitKey(1)
    return wireLengthMm


def endProgram(camera):
    camera.release()
    cv.destroyAllWindows()


def main():
    # Program Parameters
    CONST_CALIBRATION = True
    debugMode = False
    camera = cv.VideoCapture(0, cv.CAP_DSHOW)
    DBCP = 20
    dbcpTol = 0.5

    # Program Sequence
    frameWidth, frameHeight = initializeCapture(camera)
    wireLengthMm = inspectionMode(debugMode, camera, 115)
    print wireLengthMm
    '''
    mb = modbus.Modbus() #Para o teste a classe é instanciada aqui,mas no final será chamada passada como parâmetro pelo main
    while mb.writeInspectionParams([DBCP,wireLengthMm,dbcpTol])!=3:
        time.sleep(0.5)
    while not mb.writeActivateInspect():
        time.sleep(0.5)

    inspec_ok = False
    mb.writeActivateInspect()
    while not inspec_ok:
        wireLengthMm = inspectionMode(debugMode, camera, 115)
        mb.writeUpdateWireLenght(wireLengthMm) #Tratar caso de envio mal sucedido?
        mb.readCell_control() #Caso a leitura seja mal sucedida, a variável continuará em False
        inspec_ok = mb.INSPECAO_OK
    '''

    endProgram(camera)


main()

