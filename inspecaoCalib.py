# coding=utf-8
import cv2 as cv
import numpy as np


# Author: Lucas Costa Ferreira
# Project: Projeto Integrador VI
# Sistema de Inspeção de Arame
# Informações importantes:
# Os arrays numpy são regidos por coordenadas (linhas, colunas) e não o padrão (x,y), ou seja leia-se (y,x)
# O DebugMode deve ser ativado apenas para Calibração fina nos filtros de imagem ou testes sem câmera.


def nothing():
    pass


def mouse_call(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDBLCLK:
        print(x, y)


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
    except Exception as e:
        print("Não há contorno " + "Erro: " + str(e))
        return 0, None

def initializeCapture(camera):
    cv.namedWindow("Wire Inspection")
    isValidFrame, preCameraFrame = camera.read()
    rows, cols = preCameraFrame.shape[:2]
    M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
    cameraFrame = cv.warpAffine(preCameraFrame, M, (cols, rows))
    if not isValidFrame:
        print("Frame failure")
        return -1
    frameHeight, frameWidth = cameraFrame.shape[:2]
    cv.createTrackbar("Dist 1", "Wire Inspection", 0, frameHeight, nothing)
    cv.createTrackbar("Dist 2", "Wire Inspection", 0, frameHeight, nothing)
    return frameWidth, frameHeight


def calibrationMode(debugMode, doCalibration, CONST_CALIBRATION, camera, frameWidth):
    font = cv.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText1 = (0, 430)
    bottomLeftCornerOfText2 = (0, 450)
    fontScale = 0.7
    fontColor = (200, 0, 0)
    lineType = 2
    workingImage = None

    if not doCalibration:
        return 115

    while doCalibration == CONST_CALIBRATION:
        isValidFrame, preCameraFrame = camera.read()
        rows, cols = preCameraFrame.shape[:2]
        M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
        cameraFrame = cv.warpAffine(preCameraFrame, M, (cols, rows))
        if not isValidFrame:
            print("Frame failure")
            return -1
        cv.putText(cameraFrame, "Pressione 'f' para tirar a foto com o gabarito graduado", bottomLeftCornerOfText1,
                   font, fontScale, fontColor, lineType)
        cv.putText(cameraFrame, "Posicione o arame sem a tocha no enquadro mostrado", bottomLeftCornerOfText2,
                   font, fontScale, fontColor, lineType)
        cv.rectangle(cameraFrame, (160, 60), (480, 420), (0, 255, 0), 1)
        if cv.waitKey(1) == ord('f'):
            isValidFrame, preCameraFrame = camera.read()
            rows, cols = preCameraFrame.shape[:2]
            M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
            workingImage = cv.warpAffine(preCameraFrame, M, (cols, rows))
            if not isValidFrame:
                print("Frame failure")
                return -1
            break
        cv.imshow("Wire Inspection", cameraFrame)
    while doCalibration == CONST_CALIBRATION:
        auxImage = workingImage.copy()
        trackDist1 = cv.getTrackbarPos("Dist 1", "Wire Inspection")
        trackDist2 = cv.getTrackbarPos("Dist 2", "Wire Inspection")
        cv.line(auxImage, (0, trackDist1), (frameWidth, trackDist1), (255, 0, 0), 1)
        cv.line(auxImage, (0, trackDist2), (frameWidth, trackDist2), (0, 0, 255), 1)
        if trackDist1 == 0 and trackDist2 == 0:
            cv.putText(auxImage, "Pressione 'c' para calibrar", bottomLeftCornerOfText2, font, fontScale, fontColor,
                       lineType)
        if cv.waitKey(1) == ord('c'):
            cmInPixels = abs(trackDist1 - trackDist2)
            if debugMode:
                print(cmInPixels)
            return cmInPixels
        cv.imshow("Wire Inspection", auxImage)


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
            print("Contorno Inválido")
            cv.imshow('Wire Inspection', cameraFrame)
            wireLengthMm = 0
        tecla = cv.waitKey(500)
    return wireLengthMm


def endProgram(camera):
    camera.release()
    cv.destroyAllWindows()


def main():
    # Program Parameters
    CONST_CALIBRATION = True
    debugMode = False
    doCalibration = True
    camera = cv.VideoCapture(0, cv.CAP_DSHOW)
    DBCP = 20
    dbcpTol = 0.5

    # Program Sequence
    frameWidth, frameHeight = initializeCapture(camera)
    cmInPixels = calibrationMode(debugMode, doCalibration, CONST_CALIBRATION, camera, frameWidth)
    wireLengthMm = inspectionMode(debugMode, camera, cmInPixels)
    print(cmInPixels)
    endProgram(camera)

main()
