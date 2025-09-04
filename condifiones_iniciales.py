from modelo import Ciudad, Camino, CarroMarca ,CarroDeportivo ,CarroDescompuesto
def construir_ciudad_inicial(forma_manejar=0.5):
    """Crea una ciudad de ejemplo (puedes ajustar libremente)"""
    ciudad = Ciudad()
    """    

    camino1 = Camino(largo=10, carriles=2, velocida_maxima=2,nombre="Carretera principal")
    camino2 = Camino(largo=7, carriles=2, velocida_maxima=2,nombre="Camino secundaria")
    camino3 = Camino(largo=6, carriles=1, velocida_maxima=3)

    # Enlaces (como tenías)
    camino1.agregar_camino(camino2)
    camino1.agregar_camino(camino3)
    camino3.agregar_camino(camino1)
    camino2.agregar_camino(camino1)

    ciudad.agregar_camino(camino1)
    ciudad.agregar_camino(camino2)
    ciudad.agregar_camino(camino3)
    
    CarroMarca(camino1)
    camino1.agregar_carros_random(9 ,forma_manejar)
    camino2.agregar_carros_deportivos_random(3 ,forma_manejar)"""

    
    # sumulacion haid line con autos descopuestos
    """
    camino1 = Camino(largo=20, carriles=5, velocida_maxima=9,nombre="Carretera principal")
    camino2 = Camino(largo=9, carriles=2, velocida_maxima=2,nombre="Camino secundaria")

    camino1.agregar_camino(camino2)
    camino2.agregar_camino(camino1)

    ciudad.agregar_camino(camino1)
    ciudad.agregar_camino(camino2)

    CarroDescompuesto(camino1,[0,15])
    CarroDescompuesto(camino1,[1,8])
    CarroDescompuesto(camino1,[3,10])
    CarroDescompuesto(camino1,[2,9])

    camino1.agregar_carros_random(30 ,forma_manejar)
    camino1.agregar_carros_deportivos_random(5 ,forma_manejar)
    
    CarroMarca(camino1)"""


    # paradoja de Bryce.

    camino0 = Camino(largo=20, carriles=2, velocida_maxima=1,nombre="Camino 0")

    camino1 = Camino(largo=30, carriles=5, velocida_maxima=8,nombre="Camino 1")
    camino2 = Camino(largo=20, carriles=2, velocida_maxima=3,nombre="Camino 2")

    camino3 = Camino(largo=20, carriles=2, velocida_maxima=3,nombre="Camino 3")
    camino4 = Camino(largo=30, carriles=5, velocida_maxima=8,nombre="Camino 4")

    caminoConeccion = Camino(largo=5, carriles=2, velocida_maxima=10,nombre="Camino Coneccion")

    camino0.agregar_camino(camino1)
    camino0.agregar_camino(camino3)
    camino1.agregar_camino(camino2)

    caminoConeccion.agregar_camino(camino3)
    camino1.agregar_camino(caminoConeccion)

    camino3.agregar_camino(camino4)

    camino4.agregar_camino(camino0)
    camino2.agregar_camino(camino0)

    
    ciudad.agregar_camino(camino0)
    ciudad.agregar_camino(camino1)
    ciudad.agregar_camino(camino2)
    ciudad.agregar_camino(camino3)
    ciudad.agregar_camino(camino4)
    ciudad.agregar_camino(caminoConeccion)
    CarroMarca(camino0)
    camino0.agregar_carros_random(30 ,forma_manejar)
    camino0.agregar_carros_deportivos_random(5 ,forma_manejar)
    
    
    return ciudad