"""
visualizar_coords.py - Herramienta de verificacion visual de coordenadas.
Muestra el mapa con todos los tokens posicionados y permite ajustar
haciendo clic en el mapa (imprime las coordenadas al hacer clic).

USO: python visualizar_coords.py
     - Clic izquierdo: imprime coordenadas en espacio 1280x960
     - Clic derecho: sale
     - Rueda raton: zoom (no implementado, referencia visual)
"""
import pygame
import sys
import os
import math

# Importar datos del tablero
sys.path.insert(0, os.path.dirname(__file__))
from data import PAISES_DATA, PLAYER_COLORS

MAP_W = 960
MAP_H = 720

pygame.init()
screen = pygame.display.set_mode((MAP_W + 300, MAP_H))
pygame.display.set_caption("Verificador de Coordenadas TEG")
clock  = pygame.time.Clock()
font_sm = pygame.font.SysFont("Segoe UI", 10)
font_md = pygame.font.SysFont("Segoe UI", 12, bold=True)

# Cargar mapa
map_path = os.path.join(os.path.dirname(__file__), "mapa.jpg")
mapa_raw = pygame.image.load(map_path)
mapa     = pygame.transform.scale(mapa_raw, (MAP_W, MAP_H))

def escalar(coords):
    x, y = coords
    return (int(x * MAP_W / 1280), int(y * MAP_H / 960))

selected = None
log_lines = []

running = True
while running:
    screen.fill((15, 20, 35))
    screen.blit(mapa, (0, 0))

    # Dibujar todos los tokens
    for i, (nombre, datos) in enumerate(PAISES_DATA.items()):
        cx, cy = escalar(datos["coords"])
        color  = PLAYER_COLORS[i % len(PLAYER_COLORS)]

        pygame.draw.circle(screen, (0,0,0), (cx+1, cy+1), 12)
        pygame.draw.circle(screen, color,   (cx, cy), 12)
        pygame.draw.circle(screen, (20,20,20), (cx, cy), 12, 2)

        # Nombre abreviado con contraste
        abrev = nombre[:3]
        lum = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        txt_col = (15, 15, 15) if lum > 150 else (255, 255, 255)
        txt = font_sm.render(abrev, True, txt_col)
        screen.blit(txt, txt.get_rect(center=(cx, cy)))

    # Panel derecho
    pygame.draw.rect(screen, (20, 28, 48), (MAP_W, 0, 300, MAP_H))
    y = 10
    header = font_md.render("CLIC = ver coords", True, (255,180,0))
    screen.blit(header, (MAP_W + 10, y)); y += 20
    header2 = font_md.render("Clic Der = salir", True, (200,200,200))
    screen.blit(header2, (MAP_W + 10, y)); y += 30

    for line in log_lines[-25:]:
        lt = font_sm.render(line, True, (200,220,200))
        screen.blit(lt, (MAP_W + 10, y)); y += 14

    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if event.button == 3:   # clic derecho = salir
                running = False
            elif event.button == 1 and mx < MAP_W:
                # Convertir a espacio 1280x960
                x_data = round(mx * 1280 / MAP_W)
                y_data = round(my * 960  / MAP_H)

                # Encontrar el pais mas cercano
                mejor = None
                mejor_dist = 999
                for nombre, datos in PAISES_DATA.items():
                    cx, cy = escalar(datos["coords"])
                    d = math.hypot(mx - cx, my - cy)
                    if d < mejor_dist:
                        mejor_dist = d
                        mejor = nombre

                msg = f"{mejor}: ({x_data}, {y_data}) dist={mejor_dist:.0f}px"
                print(msg)
                log_lines.append(msg)

pygame.quit()
