import pygame
import pymunk
import pymunk.pygame_util
import sys
import math
import numpy as np

# ----- Configuración inicial -----
pygame.init()
WIDTH, HEIGHT = 1000, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación Física - Análisis de Movimiento")
clock = pygame.time.Clock()

# ----- Espacio físico -----
space = pymunk.Space()
space.gravity = (0, 981)

# Personalizar opciones de dibujo
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Cambiar colores por defecto
pymunk.pygame_util.positive_color = pygame.Color("black")
pymunk.pygame_util.negative_color = pygame.Color("black")
pymunk.pygame_util.CONSTRAINT_COLOR = pygame.Color("black")
pymunk.pygame_util.SHAPE_DYNAMIC_COLOR = pygame.Color("black")

# ----- Variables para seguimiento de movimiento -----
class AnalizadorMovimiento:
    def __init__(self):
        self.posiciones = []
        self.velocidades = []
        self.aceleraciones = []
        self.energias = []
        self.tiempos = []
        self.tiempo_inicio = pygame.time.get_ticks()
        
    def actualizar(self, cuerpo):
        tiempo_actual = (pygame.time.get_ticks() - self.tiempo_inicio) / 1000.0
        
        # Posición
        pos = cuerpo.position
        self.posiciones.append((pos.x, pos.y))
        
        # Velocidad
        vel = cuerpo.velocity
        self.velocidades.append((vel.x, vel.y))
        
        # Aceleración (aproximada)
        if len(self.velocidades) > 1:
            vel_anterior = self.velocidades[-2]
            dt = 1/FPS
            ax = (vel.x - vel_anterior[0]) / dt
            ay = (vel.y - vel_anterior[1]) / dt
            self.aceleraciones.append((ax, ay))
        
        # Energía
        masa = cuerpo.mass
        velocidad = math.sqrt(vel.x**2 + vel.y**2)
        energia_cinetica = 0.5 * masa * velocidad**2
        energia_potencial = masa * 9.81 * (HEIGHT - pos.y)
        energia_total = energia_cinetica + energia_potencial
        self.energias.append(energia_total)
        
        self.tiempos.append(tiempo_actual)
    
    def mostrar_estadisticas(self, screen):
        if not self.posiciones:
            return
            
        # Obtener valores actuales
        pos_actual = self.posiciones[-1]
        vel_actual = self.velocidades[-1]
        energia_actual = self.energias[-1]
        
        # Crear texto para mostrar
        fuente = pygame.font.Font(None, 24)
        textos = [
            f"Posición: ({pos_actual[0]:.1f}, {pos_actual[1]:.1f})",
            f"Velocidad: ({vel_actual[0]:.1f}, {vel_actual[1]:.1f})",
            f"Energía Total: {energia_actual:.1f} J",
            f"Tiempo: {self.tiempos[-1]:.1f} s"
        ]
        
        # Calcular posición en el lado derecho
        margen_derecho = 20
        pos_x = WIDTH - 250  # Ancho aproximado del texto
        
        # Mostrar textos en pantalla
        for i, texto in enumerate(textos):
            superficie = fuente.render(texto, True, (255, 255, 255))
            screen.blit(superficie, (pos_x, 10 + i * 25))

# ----- Crear rampa -----
def crear_rampa():
    segmentos = [
        ((30, 40), (100, 90)),
        ((100, 90), (400, 90)),
        ((430, 141), (110, 230)),
        ((60, 320), (104, 234)),
        ((20, 320), (10, 200)),
        ((60, 380), (400, 395)),
        ((278, 470), (257, 470)),  # base bola 2
        ((210, 550), (240, 550)),  # vaso 1
        ((252, 525), (240, 550)),
        ((200, 525), (210, 550)),
        ((155, 550), (180, 550)),  # vaso 2
        ((180, 550), (190, 525)),
        ((155, 550), (144, 525)),
        ((107, 550), (130, 550)),  # vaso 3
        ((130, 550), (137, 525)),
        ((107, 550), (98, 525)),
    ]
    for a, b in segmentos:
        cuerpo = pymunk.Body(body_type=pymunk.Body.STATIC)
        segmento = pymunk.Segment(cuerpo, a, b, 5)
        segmento.friction = 0.9
        segmento.color = (0, 0, 0, 255)  # negro
        space.add(cuerpo, segmento)

# ----- Crear arcos -----
def crear_arco_curvo(space, centro, radio, angulo_inicio, angulo_fin, pasos=20):
    cuerpo = pymunk.Body(body_type=pymunk.Body.STATIC)
    space.add(cuerpo)

    puntos = []
    for i in range(pasos + 1):
        angulo = math.radians(angulo_inicio + (angulo_fin - angulo_inicio) * i / pasos)
        x = centro[0] + radio * math.cos(angulo)
        y = centro[1] + radio * math.sin(angulo)
        puntos.append((x, y))

    for i in range(len(puntos) - 1):
        seg = pymunk.Segment(cuerpo, puntos[i], puntos[i + 1], 5)
        seg.friction = 0.9
        seg.elasticity = 0.8
        seg.color = (0, 0, 0, 255)  # negro
        space.add(seg)

# ----- Crear bola (roja) -----
def crear_bola():
    masa = 1
    radio = 15
    inercia = pymunk.moment_for_circle(masa, 0, radio)
    cuerpo = pymunk.Body(masa, inercia)
    cuerpo.position = (55, 10)
    circulo = pymunk.Circle(cuerpo, radio)
    circulo.friction = 0.5
    circulo.elasticity = 0.6
    circulo.color = (255, 0, 0, 255)  # rojo
    space.add(cuerpo, circulo)
    return cuerpo

# ----- Crear bola inferior (naranja) -----
def crear_bola2():
    masa = 1
    radio = 15
    inercia = pymunk.moment_for_circle(masa, 0, radio)
    cuerpo = pymunk.Body(masa, inercia)
    cuerpo.position = (276, 470)
    circulo = pymunk.Circle(cuerpo, radio)
    circulo.friction = 0.5
    circulo.elasticity = 0.6
    circulo.color = (255, 165, 0, 255)  # naranja
    space.add(cuerpo, circulo)
    return cuerpo

# ----- Crear péndulo (verde-lila pastel) -----
def crear_pendulo(space, punto_fijo, longitud=100, masa=0.1, radio=15):
    inercia = pymunk.moment_for_circle(masa, 0, radio)
    cuerpo_bola = pymunk.Body(masa, inercia)
    cuerpo_bola.position = (punto_fijo[0], punto_fijo[1] - longitud)
    
    # Agregar amortiguamiento al cuerpo
    cuerpo_bola.angular_damping = 0.8  # Amortiguamiento angular
    cuerpo_bola.linear_damping = 0.1   # Amortiguamiento lineal

    bola = pymunk.Circle(cuerpo_bola, radio)
    bola.friction = 0.5
    bola.elasticity = 0.7
    bola.color = (170, 255, 200, 255)  # verde-lila pastel

    # Crear junta con amortiguamiento
    junta = pymunk.PinJoint(cuerpo_bola, space.static_body, (0, 0), punto_fijo)
    junta.damping = 0.8  # Amortiguamiento de la junta
    junta.max_force = 1000  # Fuerza máxima de la junta

    space.add(cuerpo_bola, bola, junta)

    return cuerpo_bola, punto_fijo  # Para dibujar cuerda visual

# ----- Crear escena inicial -----
def crear_escena():
    # Limpiar el espacio actual
    for shape in space.shapes:
        space.remove(shape)
    for body in space.bodies:
        space.remove(body)
    for constraint in space.constraints:
        space.remove(constraint)
        
    crear_rampa()
    bola = crear_bola()
    crear_bola2()
    crear_arco_curvo(space, centro=(430, 100), radio=40, angulo_inicio=-70, angulo_fin=90, pasos=220)
    crear_arco_curvo(space, centro=(60, 340), radio=40, angulo_inicio=180, angulo_fin=90, pasos=220)
    pendulo_bola, punto_fijo_pendulo = crear_pendulo(space, punto_fijo=(400, 470))
    return bola, pendulo_bola, punto_fijo_pendulo

# ----- Bucle principal -----
def main():
    running = True
    bola, pendulo_bola, punto_fijo_pendulo = crear_escena()
    analizador = AnalizadorMovimiento()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Tecla R para reiniciar
                    bola, pendulo_bola, punto_fijo_pendulo = crear_escena()
                    analizador = AnalizadorMovimiento()  # Reiniciar el analizador

        screen.fill((160, 120, 80))  # Fondo café oscuro

        space.step(1 / FPS)
        
        # Actualizar análisis de movimiento
        analizador.actualizar(bola)
        
        # Dibujar cuerda del péndulo
        pygame.draw.line(screen, (0, 0, 0), punto_fijo_pendulo, pendulo_bola.position, 2)
        
        # Mostrar estadísticas
        analizador.mostrar_estadisticas(screen)
        
        # Mostrar instrucciones
        fuente = pygame.font.Font(None, 24)
        instrucciones = [
            "Presiona 'R' para reiniciar la simulación"
        ]
        
        # Mostrar instrucciones en la esquina inferior derecha
        for i, texto in enumerate(instrucciones):
            superficie = fuente.render(texto, True, (255, 255, 255))
            screen.blit(superficie, (WIDTH - 300, HEIGHT - 30))

        space.debug_draw(draw_options)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
