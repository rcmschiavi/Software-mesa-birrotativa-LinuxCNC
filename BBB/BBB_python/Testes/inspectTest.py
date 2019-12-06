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

    isValidFrame, preCameraFrame = camera.read()
    if not isValidFrame:
        print("Frame failure")
        return -1
    rows, cols = preCameraFrame.shape[:2]
    M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
    cameraFrame = cv.warpAffine(preCameraFrame, M, (cols, rows))
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

def wire_operation(wireLength,DBCP,dbcpTol, mb):

    can_operate = mb.readBBBWainting()

    if not can_operate:
        if wireLength<(DBCP-dbcpTol):
            mb.writeFwdWire()
            return 1
        elif wireLength>(DBCP+dbcpTol):
            mb.writeBackWire()
            return 1
        else:
            mb.writeDeactivateInspect()
            return 2
    else:
        return 0
lstCompfio = [10,20,12,19,14,18,15,17,16]



def main():
    # Program Parameters
    CONST_CALIBRATION = True
    debugMode = False
    ##camera = cv.VideoCapture(1)
    DBCP = 16
    dbcpTol = 0.5
    # Program Sequence
    ##frameWidth, frameHeight = initializeCapture(camera)

    ##wireLengthMm = inspectionMode(debugMode, camera, 115)
    ##print wireLengthMm


    mb = modbus.Modbus() #Para o teste a classe é instanciada aqui,mas no final será chamada passada como parâmetro pelo main
    mb.writeActivateInspect()
    op = 0
    i = 0
    while op<2:
        #wireLengthMm = inspectionMode(debugMode, camera, 115)
        wireLengthMm = lstCompfio[i]
        wire_operation(wireLengthMm,DBCP,dbcpTol,mb)
        i+=1
        #time.sleep(2)


    ##endProgram(camera)


main()
