import flet as ft
import asyncio
from datetime import datetime
from condifiones_iniciales import construir_ciudad_inicial

# ==============================
#   UI (Flet) con animaciones
# ==============================

TAM_CELDA = 40
PADDING = 6  # margen interno para que el carro no “toque” los bordes

def grid_to_px(carril, columna):
    """Convierte posición [carril, columna] a coordenadas absolutas (left, top)"""
    left = columna * TAM_CELDA + PADDING
    top = carril * TAM_CELDA + PADDING
    return left, top

import flet as ft
import asyncio
from datetime import datetime

# Tamaño de celdas (ajustable)
TAM_CELDA = 40
PADDING = 4

def main(page: ft.Page):
    page.title = "Simulación de Tráfico con Flet (gráficos)"
    page.window_width = 1300
    page.window_height = 800
    page.padding = 20
    

    # Estado UI/simulación
    texto_info_colores = ft.Text()
    mi_ciudad = None
    stacks_por_camino = {}   # Camino -> Stack
    stats_por_camino = {}    # Camino -> Text
    carro_control = {}       # Carro -> Control (Container) posicionado en Stack
    carro_camino_actual = {} # Carro -> Camino del Stack en el que está su control
    loop_activo = False
    historial_vel_ciudad = []          # [(t, vel_prom_ciudad)]
    historial_vel_por_camino = {}      # Camino -> [(t, vel_prom_camino)]

    # Contenedores principales
    panel_caminos = ft.Column(spacing=25, expand=True , scroll=True)

    # Panel de estadísticas gráficas
    panel_stats = ft.Column(spacing=20, width=450)
    txt_stats_ciudad = ft.Text("Ciudad | Carros: 0 | Velocidad prom.: 0.00", size=16, weight=ft.FontWeight.BOLD)
    
    grafico_linea = ft.LineChart(
        data_series=[],
        border=ft.border.all(1, "black"),
        left_axis=ft.ChartAxis(labels_size=30),
        bottom_axis=ft.ChartAxis(labels_size=20),
        tooltip_bgcolor="white",
        expand=True,
    )

    grafico_vel_caminos = ft.LineChart(
        data_series=[],
        border=ft.border.all(1, "black"),
        left_axis=ft.ChartAxis(labels_size=30),
        bottom_axis=ft.ChartAxis(labels_size=20),
        tooltip_bgcolor="white",
        expand=True,
    )

    panel_stats.controls.extend([
        txt_stats_ciudad,
        ft.Text("Velocidad ciudad"),
        grafico_linea,
        ft.Text("Velocidades por camino"),
        grafico_vel_caminos,
        texto_info_colores
    ])

    layout = ft.Row(
        controls=[
            panel_caminos,
            ft.Container(width=1, height=1, expand=False),
            panel_stats
        ],
        expand=True
    )
    page.add(layout)

    # ------------------------------------------------
    #   Construcción visual de caminos y carros
    # ------------------------------------------------
    def crear_stack_camino(camino):
        fondo = ft.Container(
            width=camino.largo * TAM_CELDA,
            height=camino.carriles * TAM_CELDA,
            bgcolor="#281a1a",
            border=ft.border.all(2, "black"),
        )

        # Texto con nombre + datos del camino
        texto_info = ft.Text(
            f"{camino.nombre} | Vel.: {camino.hallar_velocidad_promedio():.2f} | Duración: {camino.hallar_duracion_camino():.2f}",
            color=ft.colors.WHITE,
            size=14,
            weight=ft.FontWeight.BOLD
        )

        # líneas de carril
        lineas = []
        for c in range(1, camino.carriles):
            linea = ft.Container(
                width=fondo.width,
                height=2,
                top=c*TAM_CELDA,
                left=0,
                bgcolor="#eaff00",
            )
            lineas.append(linea)

        # Guardamos un diccionario de stats por camino
        stats_por_camino[camino] = texto_info

        # Armamos el Stack: texto arriba, fondo, líneas
        stk = ft.Stack([fondo] + lineas + [ft.Container(content=texto_info)], 
                       width=fondo.width, height=fondo.height+30)
        return stk


    def crear_ui_carro(carro):
        """Crea el control UI del carro y lo pone en el Stack correcto"""
        icono = carro.optener_icono()
        left, top = grid_to_px(carro.posicion[0], carro.posicion[1])
        ctrl = ft.Container(
            content=ft.Text(icono, color=ft.colors.BLACK,size=24),
            width=TAM_CELDA - 2*PADDING,
            height=TAM_CELDA - 2*PADDING,
            bgcolor=ft.colors.TRANSPARENT,  # carro.color,
            border_radius=10,
            left=left,
            top=top,
            animate_position=ft.animation.Animation(280, "linear"),
        )
        stk = stacks_por_camino[carro.camino]
        stk.controls.append(ctrl)
        carro_control[carro] = ctrl
        carro_camino_actual[carro] = carro.camino

    def poblar_ui_inicial():
        # Crear stacks
        panel_caminos.controls.clear()
        for camino in mi_ciudad.caminos:
            stk = crear_stack_camino(camino)
            stacks_por_camino[camino] = stk
            panel_caminos.controls.append(stk)

        # Crear controles de carros
        for camino in mi_ciudad.caminos:
            for carro in camino.carros:
                if carro.posicion:
                    crear_ui_carro(carro)

    # ------------------------------------------------
    #   Actualización de estadísticas y UI
    # ------------------------------------------------
    def actualizar_stats():
        nonlocal historial_vel_ciudad, historial_vel_por_camino

        
        # Ciudad
        total = len(mi_ciudad.carros)
        vel_prom_ciudad = (sum(c.velocidad_actual for c in mi_ciudad.carros)/total) if total > 0 else 0
        txt_stats_ciudad.value = f"Ciudad | Carros: {total} | Velocidad prom.: {vel_prom_ciudad:.2f}"

        # Actualizar historial de línea (ciudad)
        t = len(historial_vel_ciudad)
        historial_vel_ciudad.append((t, vel_prom_ciudad))

        grafico_linea.data_series = [
            ft.LineChartData(
                data_points=[ft.LineChartDataPoint(x, y) for x, y in historial_vel_ciudad],
                stroke_width=2,
                color=ft.colors.BLUE,
                curved=True
            )
        ]

        # (NUEVO) Actualizar velocidades por camino
        colores_caminos = [
            ft.colors.RED, ft.colors.GREEN, ft.colors.ORANGE, ft.colors.PURPLE,
            ft.colors.CYAN, ft.colors.PINK, ft.colors.BROWN, ft.colors.AMBER
        ]
        series = []
        text = ""
        for i, camino in enumerate(mi_ciudad.caminos):
            if len(camino.carros) > 0:
                vel_prom_camino = sum(c.velocidad_actual for c in camino.carros)/len(camino.carros)
            else:
                vel_prom_camino = 0.0
            # agregar punto a la serie del camino
            historial_vel_por_camino.setdefault(camino, [])
            historial_vel_por_camino[camino].append((t, vel_prom_camino))
            if len(historial_vel_por_camino[camino]) > 200:
                historial_vel_por_camino[camino] = historial_vel_por_camino[camino][-200:]
            text += f"{camino.nombre} color : {colores_caminos[i % len(colores_caminos)]} "
            series.append(
                ft.LineChartData(
                    data_points=[ft.LineChartDataPoint(x, y) for x, y in historial_vel_por_camino[camino]],
                    stroke_width=2,
                    color=colores_caminos[i % len(colores_caminos)],
                    curved=True
                )
            )
        texto_info_colores.value = text
        grafico_vel_caminos.data_series = series

    def actualizar_ui_movimientos():
        # actualizar los textos de velocidad y duración en cada stack
        for camino, texto in stats_por_camino.items():
            texto.value = f"{camino.nombre} | Vel.: {camino.hallar_velocidad_promedio():.2f} | Duración: {camino.hallar_duracion_camino():.2f}"
        
        for carro in list(carro_control.keys()):
            if carro not in mi_ciudad.carros:
                stk_actual = stacks_por_camino.get(carro_camino_actual.get(carro))
                if stk_actual and carro_control[carro] in stk_actual.controls:
                    stk_actual.controls.remove(carro_control[carro])
                del carro_control[carro]
                carro_camino_actual.pop(carro, None)

        for carro in mi_ciudad.carros:
            if not carro.posicion:
                continue
            if carro not in carro_control:
                crear_ui_carro(carro)
            if carro_camino_actual.get(carro) is not carro.camino:
                old_stk = stacks_por_camino.get(carro_camino_actual.get(carro))
                new_stk = stacks_por_camino[carro.camino]
                ctrl = carro_control[carro]
                if old_stk and ctrl in old_stk.controls:
                    old_stk.controls.remove(ctrl)
                if ctrl not in new_stk.controls:
                    new_stk.controls.append(ctrl)
                carro_camino_actual[carro] = carro.camino
            left, top = grid_to_px(carro.posicion[0], carro.posicion[1])
            ctrl = carro_control[carro]
            ctrl.left = left
            ctrl.top = top

    async def bucle():
        nonlocal loop_activo
        while loop_activo:
            mi_ciudad.mover_todos_carros()
            actualizar_ui_movimientos()
            actualizar_stats()
            page.update()
            await asyncio.sleep(0.28)

    # ------------------------------------------------
    #   Controles de simulación
    # ------------------------------------------------
    btn_iniciar = ft.ElevatedButton("Iniciar", icon=ft.icons.PLAY_ARROW)
    btn_pausar = ft.ElevatedButton("Pausar", icon=ft.icons.PAUSE)
    btn_reiniciar = ft.ElevatedButton("Reiniciar", icon=ft.icons.RESTART_ALT)
    forma_manejar = ft.Slider(min=0, max=100, divisions=10, value= 50,label="{value}%")
    forma_manejar_label = ft.Container(content=
                ft.Column([ft.Text("Forma de manejar (0=realista, 100=ireal)", size=12, weight=ft.FontWeight.BOLD),
                           forma_manejar]), padding=ft.padding.only(left=10))
    async_task_ref = None

    def iniciar_simulacion(e=None):
        nonlocal loop_activo, async_task_ref
        if loop_activo: return
        loop_activo = True
        async_task_ref = page.run_task(bucle)
        btn_iniciar.disabled = True
        btn_pausar.disabled = False
        page.update()

    def pausar_simulacion(e=None):
        nonlocal loop_activo
        loop_activo = False
        btn_iniciar.disabled = False
        btn_pausar.disabled = True
        page.update()

    def reiniciar_simulacion(e=None):
        nonlocal mi_ciudad, loop_activo, async_task_ref, historial_vel_ciudad, historial_vel_por_camino
        loop_activo = False
        stacks_por_camino.clear()
        stats_por_camino.clear()
        carro_control.clear()
        carro_camino_actual.clear()
        historial_vel_ciudad.clear()
        historial_vel_por_camino.clear()
        mi_ciudad = construir_ciudad_inicial(forma_manejar.value)
        # reconstruir historial por camino
        for cam in mi_ciudad.caminos:
            historial_vel_por_camino[cam] = []
        poblar_ui_inicial()
        actualizar_stats()
        btn_iniciar.disabled = False
        btn_pausar.disabled = True
        page.update()

    btn_iniciar.on_click = iniciar_simulacion
    btn_pausar.on_click = pausar_simulacion
    btn_reiniciar.on_click = reiniciar_simulacion

    page.controls.insert(0, ft.Row([btn_iniciar, btn_pausar, btn_reiniciar ,forma_manejar_label], spacing=10))

    # ------------------------------------------------
    #   Inicialización
    # ------------------------------------------------
    mi_ciudad = construir_ciudad_inicial(forma_manejar.value)
    # inicializar historial por camino con las claves correctas
    for cam in mi_ciudad.caminos:
        historial_vel_por_camino[cam] = []
    poblar_ui_inicial()
    actualizar_stats()
    btn_pausar.disabled = True
    page.update()

