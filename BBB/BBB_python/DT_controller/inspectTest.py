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

class Inspec:

    def __init__(self):
        self.camera = cv.VideoCapture(1)
        time.sleep(1)
        self.MB = modbus.Modbus()
        self.DBCP = 25
        self.dbcpTol = 2

    def returnLargestContour(self, contours):
        biggestArea = 0
        selectContour = None
        for contour in contours:
            if cv.contourArea(contour) > biggestArea:
                biggestArea = cv.contourArea(contour)
                selectContour = contour
        return selectContour


    def getWireLengthFromImage(self, debugMode, cameraFrame, cmInPixels):
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
            wire = self.returnLargestContour(contours)
            (x, y), (w, h), angle = cv.minAreaRect(wire)
            if w > h:
                h = w
            wireLengthMm = ((h / cmInPixels) * 10)

            return wireLengthMm, wire
        except:
            return 0, None


    def inspectionMode(self, debugMode, cmInPixels, camera):

        cv.namedWindow('Wire Inspection')
        isValidFrame, preCameraFrame = camera.read()
        if not isValidFrame:
            print("Frame failure")
            return -1
        rows, cols = preCameraFrame.shape[:2]
        M = cv.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
        cameraFrame = cv.warpAffine(preCameraFrame, M, (cols, rows))
        wireLengthMm, wire = self.getWireLengthFromImage(debugMode, cameraFrame, cmInPixels)
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

    def operate_wire(self):
        self.MB.writeActivateInspect()
        add_fwrd = 0
        while True:
            wireLengthMm = self.inspectionMode(False, 115, self.camera)
            error = self.DBCP - wireLengthMm
            if abs(error)<self.dbcpTol:
                #Envia inspec_ok para o supervisório
                #Envia modbus modo_inspecao = False
                #Envia mesa_end_op = True e depois reseta depois de 100ms
                print "Inspeçao finalizada"
                self.MB.writeDeactivateInspect()
                return True
            else:
                if error<0:
                    value = 19.5*abs(error) +111 #Função que resulta o tempo de recuo para um determinado erro
                    if value<125:
                        value=125
                    self.MB.setTimer(value)
                    self.MB.writeBackWire()
                else:
                    if add_fwrd >= 3:
                        #Envia erro de inspeção para o supervisório
                        print "Avançou 3 vezes"
                        self.MB.writeDeactivateInspect()
                        return False
                    else:
                        self.MB.setTimer(125)
                        self.MB.writeFwdWire()
                        add_fwrd+=1


    def __del__(self):
        self.endProgram(self.camera)

Ins = Inspec()

Ins.operate_wire()


