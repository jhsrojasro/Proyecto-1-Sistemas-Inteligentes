import imageio
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time
import base64
from selenium.webdriver.common.keys import Keys
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

    # variable que contiene intersecciones ya visitadas
    interseccionesVisitadas = []

    #Pila de opciones por probar en el laberinto
    opciones = []

    #Pila de movimientos necesarios para regresar y probar la siguiente opcion
    regresar = []

    # Constantes que modelan direcciones y acciones.
    ABAJO = 0
    DERECHA = 1
    ARRIBA = 2
    IZQUIERDA = 3
    REGRESAR = 4
    QUIETO = 5
    TERMINAR = 6

    # Variable de estado para determinar si ya se alcanzo la meta
    enCasa = False

    # Dicionario que asocia una direccion con la tecla correspondiente del modulo Keys de selenium.
    keys = {ABAJO: Keys.ARROW_DOWN, DERECHA: Keys.ARROW_RIGHT, ARRIBA: Keys.ARROW_UP, IZQUIERDA: Keys.ARROW_LEFT}

    # Diccionario que asocia una direccion con su representacion numérica
    dirStr_num = {'arriba': ARRIBA, 'abajo': ABAJO, 'derecha': DERECHA, 'izquierda': IZQUIERDA}

    #Tiempo en ms entre el pulsado y liberado de la tecla para moverse.
    p = 0.28
    #Inicializador
    def __init__(self):
        #Inicializar el driver
        self.driver = webdriver.Chrome(executable_path=r'C:/webdrivers/chromedriver.exe')
        self.driver.get("https://www.juegosinfantilespum.com/laberintos-online/12-auto-buhos.php")

        #Esperar a que cargue el juego :p
        time.sleep(5)

        #Ubicar el elemento canvas de la paginas
        self.canvas = self.driver.find_element_by_css_selector("#canvas")


        #Inicial el juego
        self.iniciarJuego()
        time.sleep(1)
        self.nuevoLaberinto()




    def ir_A_Casa(self,p):
        self.p = p
        while not self.enCasa:
            self.actuar(self.pensar(self.sensar()))
        print("Estoy en casa :D")

    #Función que detecta qué hay alrededor del carrito
    def sensar(self):
        self.refreshMundoPNG()
        self.identificarCarro()
        h = self.carro[1][0] - self.carro[0][0]
        w = self.carro[1][1] - self.carro[0][1]

        if self.direccion == self.ABAJO or self.direccion == self.ARRIBA:
            arriba = self.clasificarImagen(((max(self.carro[0][0] - h//2, 0), self.carro[0][1]), (self.carro[0][0], self.carro[1][1])), 2)
            abajo = self.clasificarImagen(((self.carro[1][0], self.carro[0][1]),(min(self.mundo_png.shape[0], self.carro[1][0] + h//2), self.carro[1][1])), 0)
            izquierda = self.clasificarImagen(((self.carro[0][0], max(self.carro[0][1] - w, 0)), (self.carro[1][0], self.carro[0][1])), 3)
            derecha = self.clasificarImagen(((self.carro[0][0], self.carro[1][1]),(self.carro[1][0], min(self.mundo_png.shape[1], self.carro[1][1] + w))), 1)
        else:
            arriba = self.clasificarImagen(((max(self.carro[0][0] - h , 0) , self.carro[0][1] ) ,( self.carro[0][0] , self.carro[1][1])),2)
            abajo = self.clasificarImagen(((self.carro[1][0] , self.carro[0][1] ),(min(self.mundo_png.shape[0], self.carro[1][0] + h) , self.carro[1][1]) ),0)
            izquierda = self.clasificarImagen(((self.carro[0][0],max(self.carro[0][1] - w//2, 0) ),(self.carro[1][0] , self.carro[0][1])), 3)
            derecha = self.clasificarImagen(((self.carro[0][0],self.carro[1][1]),(self.carro[1][0] , min(self.mundo_png.shape[1], self.carro[1][1] + w//2))), 1)


        print("Arriba:", arriba, "Abajo:", abajo,"Izquieda:", izquierda,"Derecha:", derecha)
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
        return [abajo, derecha, arriba, izquierda]

    def pensar(self, percepcion):
        if percepcion[(self.direccion+2) % 4] == "Carretera":
            percepcion[(self.direccion + 2) % 4] = "Pared"
        if percepcion.count("Casa"):
            print("Encontre Casa\n")
            self.enCasa = True
            return percepcion.index("Casa")
        elif percepcion.count("Carretera") == 0:
            if len(self.opciones):
                print("Voy a regresar\n")
                print("Regresar", self.regresar[-1])
                self.opciones.pop()
                return self.REGRESAR
            else:
                return self.TERMINAR
        elif percepcion.count("Carretera") == 1:
            print("Solo puedo ir hacia adelante\n")
            if len(self.opciones) > 1:
                self.regresar[-1].append((percepcion.index("Carretera")+2) % 4)
            return percepcion.index("Carretera")
        else:
            if self.enInterseccionVisitada(self.carro):
                print("Estoy en una intersección visitada\n")
                if self.opciones:
                    if self.interseccion(self.carro,self.opciones[-1][0]):
                        if len(self.opciones) > 1:
                            self.regresar[-1].append((self.opciones[-1][1]+2) % 4)
                        return self.opciones[-1][1]
                    else:
                        print("Regresar",self.regresar[-1])
                        self.opciones.pop()
                        return self.REGRESAR
                else:
                    return self.TERMINAR
            else:
                print("Estoy en una intersección no visitada: ",self.carro,"\n")
                self.interseccionesVisitadas.append(self.carro)
                for i,e in enumerate(percepcion):
                    if e == "Carretera":
                        print("Encole: (",self.carro,",",i,")")
                        self.opciones.append( (self.carro , i) )
                        self.regresar.append([])
                return self.QUIETO

    def actuar(self, accion):
        if accion == self.TERMINAR:
            raise Exception("No pude solucionar el laberinto :c")
        elif accion == self.REGRESAR:
            for a in reversed(self.regresar.pop()):
                self.moverse(a)
        elif accion != self.QUIETO:
                self.moverse(accion)

    # Ubicarse en el canvas y hacer click para iniciar el juego
    def iniciarJuego(self):
        actions = ActionChains(self.driver)
        actions.click(self.canvas)
        actions.perform()

    def enInterseccionVisitada(self,coordenadas):
        for inter in self.interseccionesVisitadas:
            if self.interseccion(coordenadas, inter):
                return True
        return False

    # Función que se debe ejecutar en cada nuevo nivel para identificar nuevamente los objetos
    def nuevoLaberinto(self):
        self.enCasa = False
        self.refreshMundoPNG()
        self.buhos = []
        self.interseccionesVisitadas = []
        self.opciones = []
        self.regresar = []
        self.identificarObjetos()
        primerSensado = self.sensar()
        if primerSensado.count("Carretera")>1:
            self.interseccionesVisitadas.append(self.carro)
            for i, o in enumerate(primerSensado):
                if o == "Carretera":
                    self.opciones.append((self.carro,i))

    def clasificarImagen(self,coordenadas, direccion):
        if self.interseccion(coordenadas, self.casa):
            return "Casa"
        elif self.interseccionBuho(coordenadas):
            return "Buho"
        elif self.esCarretera(coordenadas, self.direccion == direccion or (self.direccion + 2) % 4 == direccion):
            return "Carretera"
        return "Pared"

    #Comparar con un template de carretera
    def esCarretera(self, coordenadas, frente):
        h = coordenadas[1][0] - coordenadas[0][0]
        w = coordenadas[1][1] - coordenadas[0][1]
        imagen = self.mundo_png[coordenadas[0][0]:coordenadas[1][0], coordenadas[0][1]:coordenadas[1][1]]
        pedazo_carretera = np.zeros((h, w, 4), dtype=np.uint8)
        pedazo_carretera[:,:] = ((102, 102, 102, 255))
        res = cv2.matchTemplate(imagen, pedazo_carretera, cv2.TM_SQDIFF_NORMED)
        if frente:
            return res[0][0] <= 0.15#0.15
        else:
            return res[0][0] <= 0.11

    #Averiguar si las coordenadas se intersectan con algún buho
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
                self.direccion = self.dirStr_num[orientacion]
                return

    def identificarBuhos(self):
        for i in range(1,8):
            template = imageio.imread('img/buho_'+str(i)+'.png')
            self.buhos.extend(self.multipleTemplateMatch(template))

    def identificarCasa(self):
        self.casa = self.templateMatch(imageio.imread('img/casa.png'))

    #Función que busca una única ocurrencia de template en la imagen actual del mundo
    def templateMatch(self, template):
        w, h = template.shape[1], template.shape[0]
        res = cv2.matchTemplate(self.mundo_png, template, cv2.TM_CCOEFF_NORMED)
        _, maxVal, _, max_loc = cv2.minMaxLoc(res)
        if maxVal >= 0.7:
            cv2.rectangle(self.mundo_png, max_loc, (max_loc[0] + w, max_loc[1] + h), 255, 2)
            return ((max_loc[1],max_loc[0]),(max_loc[1] + h, max_loc[0] + w))
        return None

    #Función que busca varias ocurrencias de template en la imagen actual del mundo
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

    #Actualizar la imagen actual del mundo
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

    def plotMundoPNG(self):
        plt.imshow(self.mundo_png)
        plt.show()

    def interseccion(self, c1, c2):
        return not (min(c1[1][0],c2[1][0]) < max(c1[0][0], c2[0][0]) or min(c1[1][1], c2[1][1]) < max(c1[0][1],c2[0][1]))

    def moverse(self, direccion, n = 1):
        for i in range(n):
            actions = ActionChains(self.driver)
            actions.key_down(self.keys[direccion]).pause(self.p).key_up(self.keys[direccion]).perform()
            #self.actions.key_up(self.keys[direccion]).perform()



agente = Agente()
while True:
    opcion = input("Ingrese opcion: 1 solucionar el laberinto, 2 Escanear nuevo laberinto\n")
    if opcion == "1":
        p = float(input("Ingrese el valor de p\n"))
        agente.ir_A_Casa(p)
    elif opcion == "2":
        agente.nuevoLaberinto()
    else:
        break
"""
for i in range(200):
    print("t =",i)
    agente.actuar(agente.pensar(agente.sensar()))

while True:
    agente.actuar(agente.pensar(agente.sensar()))
    opcion = input("Seguir o parar 1 o 0\n")
    if not opcion:
        break
"""