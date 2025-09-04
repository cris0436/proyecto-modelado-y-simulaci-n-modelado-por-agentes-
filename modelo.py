import random
import math
import time
import asyncio
import flet as ft

# ==============================
#   MODELO (tus reglas)
# ==============================

colores = ["red", "blue", "green", "yellow", "black", "white", "purple", "orange", "pink", "brown"]

class Ciudad:
    def __init__(self):
        self.caminos = set()
        self.carros = set()

    def agregar_carro(self, carro):
        """Agrega un carro a la ciudad y registra su camino"""
        self.carros.add(carro)
        self.caminos.add(carro.camino)
        carro.ciudad = self

    def eliminar_carro(self, carro):
        if carro in self.carros:
            self.carros.remove(carro)

    def agregar_camino(self, camino):
        self.caminos.add(camino)
        camino.ciudad = self

    def mover_todos_carros(self):
        # Copia para evitar modificación durante iteración
        for carro in list(self.carros):
            if carro in self.carros:
                carro.moverse()

class Camino:
    def __init__(self, largo=10, carriles=2, velocida_maxima=13.888 , nombre="Camino"):
        self.nombre = nombre
        self.largo = largo          # en celdas (cada celda ~1 bloque)
        self.carriles = carriles
        self.velocida_maxima = velocida_maxima  # "unidades" por tick (coherente con tu regla)
        self.camino = [["0" for _ in range(largo)] for _ in range(carriles)]
        self.carros = []
        self.caminos_enlases = []
        self.ciudad = None

    def agregar_carros_deportivos_random(self, cantidad:int ,forma_manejar=0.5):
        if cantidad > self.largo * self.carriles:
            raise Exception("Cantidad de carros excede la capacidad del camino")
        for _ in range(cantidad):
            while True:
                carril = random.randint(0, self.carriles - 1)
                posicion = random.randint(0, self.largo - 1)
                if self.camino[carril][posicion] == "0":
                    nuevo_carro = CarroDeportivo(self, [carril, posicion] ,forma_manejar)
                    self.carros.append(nuevo_carro)
                    if self.ciudad:
                        self.ciudad.agregar_carro(nuevo_carro)
                    break

    def agregar_carros_random(self, cantidad:int ,forma_manejar=0.5):
        if cantidad > self.largo * self.carriles:
            
            raise Exception("Cantidad de carros excede la capacidad del camino")
        
        for _ in range(cantidad):
            while True:
                carril = random.randint(0, self.carriles - 1)
                posicion = random.randint(0, self.largo - 1)
                if self.camino[carril][posicion] == "0":
                    nuevo_carro = CarroMovimiento(self, [carril, posicion],forma_manejar)
                    self.carros.append(nuevo_carro)
                    if self.ciudad:
                        self.ciudad.agregar_carro(nuevo_carro)
                    break

    def eliminar_carro(self, carro):
        """Elimina el carro de la grilla y de la lista del camino"""
        for carril in self.camino:
            for i in range(len(carril)):
                if carril[i] == carro:
                    carril[i] = "0"
        if carro in self.carros:
            self.carros.remove(carro)

    def buscar_carro(self, carro):
        for carril_index in range(len(self.camino)):
            for pos_index in range(len(self.camino[carril_index])):
                if self.camino[carril_index][pos_index] == carro:
                    return [carril_index, pos_index]
        return None

    def agregar_carro(self, carro):
        """Agrega un carro existente a este camino, ubicándolo según tus reglas"""
        carriles_libres = False
        for carril in self.camino:
            if carril[0] == "0":
                carriles_libres = True
                
        if carriles_libres:
            
            self.carros.append(carro)
            carro.camino = self
            carro.velocidad_maxima = self.velocida_maxima
            carro.definir_posicion_inicial()
            if self.ciudad:
                self.ciudad.agregar_carro(carro)

    def agregar_camino(self, camino_nuevo):
        self.caminos_enlases.append(camino_nuevo)
     
    def hallar_velocidad_promedio(self):
        if len(self.carros) == 0:
            return self.velocida_maxima
        return sum(c.velocidad_actual for c in self.carros)/len(self.carros)
    def hallar_duracion_camino(self):
        
        if len(self.carros) == 0:
            return self.largo / self.velocida_maxima
        
        velocidad_promedio = (sum(c.velocidad_actual for c in self.carros)/len(self.carros)) 
        
        if velocidad_promedio == 0:
            return math.inf

        dencidad = len(self.carros) / (self.largo * self.carriles)

        if dencidad >= 0.7:
            velocidad_promedio *= 2  # Camino muy congestionado, duración aumenta       

        return self.largo/ velocidad_promedio 

class Carro:
    def __str__(self):
        return self.color

    def __init__(self, camino , posicion=None):
        self.color = random.choice(colores)
        self.velocidad_maxima = camino.velocida_maxima
        self.velocidad_actual = 1
        self.camino = camino
        self.posicion = posicion  # [carril, columna]
        self.ciudad = None
        if posicion is not None:
            if camino.camino[posicion[0]][posicion[1]] == "0":
                camino.camino[posicion[0]][posicion[1]] = self
                self.posicion = posicion
            else:
                pass
        else:
            self.camino.agregar_carro(self)

    def aumentar_velocidad(self):
        if self.velocidad_actual + 1 <= self.velocidad_maxima:
            self.velocidad_actual += 1

    def disminuir_velocidad(self, nueva_velocidad=1):
        self.velocidad_actual = max(0, nueva_velocidad)

    def velocidades_distancias(self, velocidad):
        # Tu función de separación
        return max(1, round(0.15 * velocidad))

    def ver_espacios_libres(self, carril=0, posicion=0):
        carretera = self.camino.camino
        espacios_libres = 0
        if not (0 <= carril < len(carretera)):
            return 0
        if posicion >= len(carretera[carril]) - 1:
            return -1  # final del camino
        for i in range(posicion + 1, len(carretera[carril])):
            if carretera[carril][i] == "0":
                espacios_libres += 1
            else:
                break
        return espacios_libres

    def verificar_carro_delantero_detenido(self, carril, posicion):
        carretera = self.camino.camino
        if posicion + 1 >= len(carretera[carril]):
            return False
        siguiente_celda = carretera[carril][posicion + 1]
        if siguiente_celda != "0" and hasattr(siguiente_celda, 'velocidad_actual'):
            return siguiente_celda.velocidad_actual == 0
        return False

    def definir_posicion_inicial(self):
        carriles_libres = []
        for carril in range(len(self.camino.camino)):
            espacios = self.ver_espacios_libres(carril, -1)  # cuenta desde 0
            if espacios == -1:
                espacios = 0
            carriles_libres.append(espacios)

        if not carriles_libres or max(carriles_libres) == 0:
            print("No hay espacio para colocar el carro")
            raise Exception("No hay espacio para colocar el carro")

        mejor_carril = carriles_libres.index(max(carriles_libres))
        if self.camino.camino[mejor_carril][0] != "0":
            print("No hay espacio para colocar el carro")
            raise Exception("No hay espacio para colocar el carro")

        self.camino.camino[mejor_carril][0] = self
        self.posicion = [mejor_carril, 0]
        return self.posicion

class CarroMovimiento(Carro):
    def __init__(self, camino, posicion=None, forma_manejar=0.5):
        super().__init__(camino, posicion)
        self.forma_manejar = forma_manejar
    def optener_icono(self):
        return "🚗"
    def mover_direccion(self, direccion):
        if not self.posicion:
            return False
        nuevo_carril = self.posicion[0] + direccion
        pos_actual = self.posicion[1]
        if not (0 <= nuevo_carril < len(self.camino.camino)):
            return False
        if self.camino.camino[nuevo_carril][pos_actual] == "0":
            self.camino.camino[self.posicion[0]][self.posicion[1]] = "0"
            self.camino.camino[nuevo_carril][pos_actual] = self
            self.posicion[0] = nuevo_carril
            return True
        return False

    def salir_camino(self):
        def bucar_el_mejor_camino(camino,duraciones):

            duraciones_copia = duraciones.copy()
            duraciones_copia = [d if d != 0 else math.inf for d in duraciones_copia]
            compia_caminos = camino.caminos_enlases.copy()
            for _ in range(len(duraciones)):
                mejor_camino = [x for x in compia_caminos if x != '']
                mejor_camino = compia_caminos[duraciones_copia.index(min(duraciones_copia))]
                # valida si el camino tiene espacio
               
                for carril in mejor_camino.camino:
                    if carril[0] == "0":
                        return camino.caminos_enlases[duraciones.index(min(duraciones_copia))]
                    
                indice_duracion = duraciones_copia.index(min(duraciones_copia))  # Encuentra el índice del elemento
                duraciones_copia[indice_duracion] = math.inf  # Asigna un valor alto para ignorarlo en la próxima iteración      
                
                indice_camino = compia_caminos.index(mejor_camino)
                compia_caminos[indice_camino] = ''
            return False # No hay caminos con espacio            
            
        """Salida o cambio al mejor camino enlazado"""
        if len(self.camino.caminos_enlases) > 0:
            duraciones = [c.hallar_duracion_camino() for c in self.camino.caminos_enlases]
            
            try:
                mejor_camino = bucar_el_mejor_camino(self.camino,duraciones)
            except Exception as e:
                print(f"Error al buscar el mejor camino: {e}")
                mejor_camino = False
                
            if mejor_camino != False:
                self.camino.eliminar_carro(self)

            # Intentar entrar al nuevo camino
                try:
                    mejor_camino.agregar_carro(self)
                except Exception as e:

                    print(f"No se pudo agregar al nuevo camino: {e}")
                    # 🚗 No hay espacio en el nuevo camino:
                    # en vez de eliminar el carro lo detenemos en la salida
                    self.velocidad_actual = 0
                    # ⬇️ Si quieres eliminarlo de la simulación, descomenta:
                    # if self.ciudad:
                    #     self.ciudad.eliminar_carro(self)
                    return
                else:
                    self.velocidad_actual = 0
                    
            # Eliminar del camino actual
            
        else:
            # 🚫 No hay caminos siguientes: el carro se detiene en la salida
            self.velocidad_actual = 0
            # ⬇️ Si quieres que desaparezca de la simulación, descomenta:
            # if self.ciudad:
            #     self.camino.eliminar_carro(self)
            #     self.ciudad.eliminar_carro(self)

    def mover_adelante(self, distancia):
        if not self.posicion:
            return False
        carril_actual = self.posicion[0]
        pos_actual = self.posicion[1]
        nueva_pos = pos_actual + distancia

        if nueva_pos >= self.camino.largo:
            self.salir_camino()
            return True

        if self.camino.camino[carril_actual][nueva_pos] == "0":
            self.camino.camino[carril_actual][pos_actual] = "0"
            self.camino.camino[carril_actual][nueva_pos] = self
            self.posicion[1] = nueva_pos
            return True
        return False

    def moverse(self):
        if not self.posicion:
            return

        carril, pos = self.posicion
        espacios_libres = self.ver_espacios_libres(carril, pos)

        if espacios_libres == -1:
            self.salir_camino()
            return

        derecha = 0
        if carril + 1 < self.camino.carriles:
            der_espacios = self.ver_espacios_libres(carril + 1, pos)
            derecha = der_espacios if der_espacios != -1 else 0

        izquierda = 0
        if carril - 1 >= 0:
            izq_espacios = self.ver_espacios_libres(carril - 1, pos)
            izquierda = izq_espacios if izq_espacios != -1 else 0

        # Caso 1: carro detenido adelante
        if self.verificar_carro_delantero_detenido(carril, pos):
            self.disminuir_velocidad(0)
            if espacios_libres == 0 and derecha == 0 and izquierda == 0 :
                if not self.camino.caminos_enlases:
                    self.velocidad_actual = 0
                    return
                duraciones = [c.hallar_duracion_camino() for c in self.camino.caminos_enlases]
                mejor_camino = self.camino.caminos_enlases[duraciones.index(min(duraciones))]
                if not mejor_camino :
                    self.camino.eliminar_carro(self)
                else:
                    self.velocidad_actual = 0
                    return
                try:
                    mejor_camino.agregar_carro(self)
                except Exception:
                    print("No se pudo agregar al nuevo camino")
                    self.velocidad_actual = 0
                return

            if derecha > izquierda and derecha > 0:
                if self.mover_direccion(1):
                    return
            elif izquierda > 0:
                if self.mover_direccion(-1):
                    return
            return

        # Caso 2: normal
        distancia_segura = self.velocidades_distancias(self.velocidad_actual)

        if espacios_libres >= distancia_segura:
            if random.random() < self.forma_manejar: # emular dos formas de conducir y de 
                self.aumentar_velocidad()
                distancia_movimiento = min(self.velocidad_actual, espacios_libres)
                self.mover_adelante(distancia_movimiento)
            else:
                distancia_movimiento = 0
                if self.velocidad_actual > espacios_libres-distancia_segura:
                    self.disminuir_velocidad(espacios_libres-distancia_segura)
                    distancia_movimiento = espacios_libres-distancia_segura
                else:
                    self.aumentar_velocidad()
                    distancia_movimiento = min(self.velocidad_actual, espacios_libres)
                    self.mover_adelante(distancia_movimiento)

        elif derecha > espacios_libres or izquierda > espacios_libres:
            if derecha > izquierda and derecha > espacios_libres:
                if self.mover_direccion(1):
                    if derecha >= distancia_segura:
                        self.aumentar_velocidad()
                    else:
                        self.disminuir_velocidad(derecha)
            elif izquierda > espacios_libres:
                if self.mover_direccion(-1):
                    if izquierda >= distancia_segura:
                        self.aumentar_velocidad()
                    else:
                        self.disminuir_velocidad(izquierda)
        else:
            self.disminuir_velocidad(max(1, espacios_libres-distancia_segura))
            if espacios_libres > 0:
                self.mover_adelante( espacios_libres-distancia_segura)

class CarroDeportivo(CarroMovimiento):
    def optener_icono(self):
        return "🏎️"
    def aumentar_velocidad(self):
        if self.velocidad_actual + 2 <= self.velocidad_maxima:
            self.velocidad_actual += 2
        else:
            self.velocidad_actual = self.velocidad_maxima

class CarroMarca(CarroMovimiento):
    caminos_recorridos = []
    timpo_ultimo_cambio = time.time()



    @property
    def camino(self):
            return self._camino
    
    @camino.setter
    def camino(self, nuevo_camino):
        self._camino = nuevo_camino  # Actualiza el valor del camino
        self.cambio_de_camino(nuevo_camino)      # Ejecuta el método cuando se cambia el valor
    def cambio_de_camino(self,nuevo_camino):
        if nuevo_camino not in self.caminos_recorridos:
            self.caminos_recorridos.append(nuevo_camino)
        else:
            self.caminos_recorridos.clear()
            print("El carro Duro ",time.time() - self.timpo_ultimo_cambio,"en dar la vuelta")
            self.timpo_ultimo_cambio = time.time()
    def optener_icono(self):
        return "🚙"
    


class CarroDescompuesto(CarroMovimiento):
    def __init__(self, camino, posicion=None):
        super().__init__(camino, posicion)
        self.velocidad_actual = 0
        self.camino.carros.append(self)
        if self.camino.ciudad:
            self.camino.ciudad.agregar_carro(self)
    def mover_direccion(self, direccion):
        pass  # No puede moverse
    def optener_icono(self):
        return "🚚"
    def aumentar_velocidad(self):
        self.velocidad_actual = 0
        pass  # No puede aumentar velocidad