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

    # lista que contiene las coordenadas del carro (puede ser encontrado varias veces pero difiere en uno o dos pixeles)
    carro = []

    # lista que contiene las coordenadas de la casa ()
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
        #identificar buhos
        for i in range(1,8):
            template = imageio.imread('img/buho_'+str(i)+'.png')
            self.buhos.extend(self.templateMatch(template))


        #identificar carro
        for orientacion in ['arriba', 'abajo', 'derecha', 'izquierda']:
            template = imageio.imread('img/carro_'+str(orientacion)+'.png')
            self.carro = self.templateMatch(template)

        #identificar casa
        self.casa = self.templateMatch(imageio.imread('img/casa.png'))
        print(self.carro)
        print(self.casa)
        self.plotMundoPNG()


    def templateMatch(self, template):
        ocurrencias = []
        w, h = template.shape[1], template.shape[0]
        res = cv2.matchTemplate(self.mundo_png, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            ocurrencias.append((pt, (pt[0] + w, pt[1] + h)))
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


    def plotMundoPNG(self):
        plt.imshow(self.mundo_png)
        plt.show()

agente = Agente()