import imageio
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

#Metodos: cv.TM_CCOEFF cv.TM_CCOEFF_NORMED cv.TM_CCORR cv.TM_CCORR_NORMED cv.TM_SQDIFF cv.TM_SQDIFF_NORMED

class Agente:
    #lista que contiene las coordenadas de los buhos detectados
    buhos = []

    # variable que contiene las coordenadas del carro (puede ser encontrado varias veces pero difiere en uno o dos pixeles)
    carro = []

    # variable que contiene las coordenadas de la casa ()
    casa = []

    #Inicializador
    def __init__(self):
        #Inicializar el driver
        self.driver = webdriver.Chrome(executable_path=r'C:/webdrivers/chromedriver.exe')
        self.driver.get("https://www.juegosinfantilespum.com/laberintos-online/12-auto-buhos.php")
        #Esperar a que cargue el juego :p
        time.sleep(3)

        #Ubicarse en el canvas y hacer click para iniciar el juego
        self.canvas = self.driver.find_element_by_css_selector("#canvas")
        actions = ActionChains(self.driver)
        actions.click(self.canvas)
        actions.perform()
        time.sleep(2)

        #Obtener la imagen del canvas
        self.refreshMundoPNG()

        #Identificar los objetos en el mundo (buhos, carro, casa)
        self.identificarObjetos()

        #Sensar lo que hay alrededor
        self.sensar()
        #self.plotMundoPNG()

    def sensar(self):
        self.refreshMundoPNG()
        self.identificarCarro()
        h = self.carro[1][0] - self.carro[0][0]
        w = self.carro[1][1] - self.carro[0][1]
        arriba = ((max(self.carro[0][0] - h , 0) , self.carro[0][1] ) ,( self.carro[0][0] , self.carro[1][1]))
        abajo = ((self.carro[1][0] , self.carro[0][1] ),(min(self.mundo_png.shape[0], self.carro[1][0] + h) , self.carro[1][1]) )
        izquierda = ((self.carro[0][0],max(self.carro[0][1] - w, 0) ),(self.carro[1][0] , self.carro[0][1]))
        derecha = ((self.carro[0][0],self.carro[1][1]),(self.carro[1][0] , min(self.mundo_png.shape[1], self.carro[1][1] + w)))

        print("Arriba:", self.clasificarImagen(arriba))
        print("Abajo:", self.clasificarImagen(abajo))
        print("Izquieda:", self.clasificarImagen(izquierda))
        print("Derecha:", self.clasificarImagen(derecha))
        """
        cv2.rectangle(self.mundo_png, arriba[0][::-1], arriba[1][::-1], 255, 2)
        cv2.rectangle(self.mundo_png, abajo[0][::-1], abajo[1][::-1], 255, 2)
        cv2.rectangle(self.mundo_png, izquierda[0][::-1], izquierda[1][::-1], 255, 2)
        cv2.rectangle(self.mundo_png, derecha[0][::-1], derecha[1][::-1], 255, 2)
        print(arriba)
        print(abajo)
        print(izquierda)
        print(derecha)
        """
    def clasificarImagen(self,coordenadas):
        if self.interseccion(coordenadas, self.casa):
            return "Casa"
        elif self.interseccionBuho(coordenadas):
            return "Buho"
        elif self.esCarretera(coordenadas):
            return "Carretera"
        return "Pared"

    def esCarretera(self, coordenadas):
        h = coordenadas[1][0] - coordenadas[0][0]
        w = coordenadas[1][1] - coordenadas[0][1]
        imagen = self.mundo_png[coordenadas[0][0]:coordenadas[1][0], coordenadas[0][1]:coordenadas[1][1]]
        pedazo_carretera = np.zeros((h, w, 4), dtype=np.uint8)
        pedazo_carretera[:,:] = ((102, 102, 102, 255))
        res = cv2.matchTemplate(imagen, pedazo_carretera, cv2.TM_SQDIFF_NORMED)
        return res[0][0] <= 0.1

    def interseccionBuho(self, coordenadas):
        for buho in self.buhos:
            if self.interseccion(coordenadas, buho):
                return True
        return False

    def identificarCarro(self):
        for orientacion in ['arriba', 'abajo', 'derecha', 'izquierda']:
            template = imageio.imread('img/carro_'+str(orientacion)+'.png')
            self.carro = self.templateMatch(template)
            if self.carro:
                return

    def identificarBuhos(self):
        for i in range(1,8):
            template = imageio.imread('img/buho_'+str(i)+'.png')
            self.buhos.extend(self.multipleTemplateMatch(template))

    def identificarCasa(self):
        self.casa = self.templateMatch(imageio.imread('img/casa.png'))

    def templateMatch(self, template):
        w, h = template.shape[1], template.shape[0]
        res = cv2.matchTemplate(self.mundo_png, template, cv2.TM_CCOEFF_NORMED)
        _, maxVal, _, max_loc = cv2.minMaxLoc(res)
        if maxVal >= 0.8:
            cv2.rectangle(self.mundo_png, max_loc, (max_loc[0] + w, max_loc[1] + h), 255, 2)
            return ((max_loc[1],max_loc[0]),(max_loc[1] + h, max_loc[0] + w))
        return None

    def multipleTemplateMatch(self, template):
        ocurrencias = []
        w, h = template.shape[1], template.shape[0]
        res = cv2.matchTemplate(self.mundo_png, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            ocurrencias.append((pt[::-1], (pt[1] + h, pt[0] + w)))
            cv2.rectangle(self.mundo_png, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)
        return ocurrencias


    def refreshMundoPNG(self):
        # get the canvas as a PNG base64 string
        mundo_base64 = self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", self.canvas)
        # decode
        self.mundo_png = base64.b64decode(mundo_base64)
        self.saveMundoPNG()
        self.mundo_png = imageio.imread('mundo.png')

    def saveMundoPNG(self):
        # save to a file
        with open(r"mundo.png", 'wb') as f:
            f.write(self.mundo_png)

    def identificarObjetos(self):
        self.identificarCarro()
        self.identificarCasa()
        self.identificarBuhos()

    def nuevoMundo(self):
        self.refreshMundoPNG()
        self.buhos = []
        self.identificarObjetos()
        #self.plotMundoPNG()

    def plotMundoPNG(self):
        plt.imshow(self.mundo_png)
        plt.show()

    def interseccion(self, c1, c2):
        return not (min(c1[1][0],c2[1][0]) < max(c1[0][0], c2[0][0]) or min(c1[1][1], c2[1][1]) < max(c1[0][1],c2[0][1]))
agente = Agente()
while(True):
    opcion = input("Sensar, Nuevo nivel o Parar (1, 2 o 0)\n")
    if opcion == '1':
        agente.sensar()
    elif opcion == '2':
        agente.nuevoMundo()
    else: break