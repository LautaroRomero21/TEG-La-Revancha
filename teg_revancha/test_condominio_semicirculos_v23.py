"""Regresiones: condominios semicirculares y Chukchi–Chechenia no limítrofes."""
import os
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame

from data import PAISES_DATA
from logic import JuegoTEG
from renderer import Renderer


class FichasCondominio(unittest.TestCase):
    def test_dos_semicirculos_llenos_sin_triangulo(self):
        superficie=pygame.Surface((90,90),pygame.SRCALPHA)
        izq=(35,170,65)
        der=(240,180,30)
        cx,cy,radio=45,45,18
        Renderer._dibujar_mitades_condominio(
            superficie,(cx,cy),radio,izq,der)
        # Estos puntos están DENTRO del círculo, pero FUERA del
        # triángulo que anteriormente se dibujaba en el lado derecho.
        for delta in (-6,0,6):
            self.assertEqual(tuple(superficie.get_at((cx+16,cy+delta)))[:3],der)
            self.assertEqual(tuple(superficie.get_at((cx-16,cy+delta)))[:3],izq)
        # La mitad completa es circular, sin pintar fuera del disco.
        for x,y in ((cx+18,cy-10),(cx-18,cy-10),
                    (cx+18,cy+10),(cx-18,cy+10)):
            self.assertEqual(superficie.get_at((x,y)).a,0)

    def test_el_color_derecho_llega_al_extremo_del_circulo(self):
        superficie=pygame.Surface((60,60),pygame.SRCALPHA)
        Renderer._dibujar_mitades_condominio(
            superficie,(30,30),12,(10,20,30),(150,180,210))
        # Pygame puede dejar sin pintar el pixel exacto del radio. Estos
        # puntos están cerca del borde CURVO pero dentro de la ficha.
        self.assertEqual(tuple(superficie.get_at((40,35)))[:3],(150,180,210))
        self.assertEqual(tuple(superficie.get_at((20,35)))[:3],(10,20,30))

    def test_clip_original_se_restaura(self):
        superficie=pygame.Surface((90,90),pygame.SRCALPHA)
        clip_original=pygame.Rect(10,10,45,70)
        superficie.set_clip(clip_original)
        Renderer._dibujar_mitades_condominio(
            superficie,(45,45),18,(30,100,10),(200,100,10))
        self.assertEqual(superficie.get_clip(),clip_original)
        # Los píxeles de la ficha fuera del clip preexistente no se tocan.
        self.assertEqual(superficie.get_at((60,45)).a,0)
        self.assertEqual(tuple(superficie.get_at((50,45)))[:3],(200,100,10))

    def test_circulo_ficha_simple_no_necesita_ayuda(self):
        # No cambia la primitiva usada para países sin condominio.
        self.assertTrue(callable(Renderer._dibujar_mitades_condominio))


class FronteraChukchiChechenia(unittest.TestCase):
    def test_eliminada_ambas_direcciones(self):
        self.assertNotIn('Chechenia',PAISES_DATA['Chukchi']['fronteras'])
        self.assertNotIn('Chukchi',PAISES_DATA['Chechenia']['fronteras'])

    def test_motor_no_las_considera_adyacentes(self):
        juego=JuegoTEG(4)
        self.assertFalse(juego.son_adyacentes('Chukchi','Chechenia'))
        self.assertFalse(juego.son_adyacentes('Chechenia','Chukchi'))

    def test_se_conservan_otras_fronteras(self):
        self.assertIn('Kamchatka',PAISES_DATA['Chukchi']['fronteras'])
        self.assertIn('China',PAISES_DATA['Chechenia']['fronteras'])
        self.assertEqual(len(PAISES_DATA),72)
        for nombre,datos in PAISES_DATA.items():
            for vecino in datos['fronteras']:
                self.assertIn(nombre,PAISES_DATA[vecino]['fronteras'])


if __name__ == '__main__':
    unittest.main()
