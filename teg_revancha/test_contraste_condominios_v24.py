"""Regresiones: números de condominios legibles sobre blanco y oscuro."""
import os
import unittest

os.environ.setdefault('SDL_VIDEODRIVER','dummy')

import pygame
from renderer import Renderer


class ContrasteNumerosCondominio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()
        cls.fuente=pygame.font.Font(None,26)

    def superficie(self,izquierda,derecha):
        s=pygame.Surface((90,70))
        s.fill(izquierda)
        pygame.draw.rect(s,derecha,(45,0,45,70))
        return s

    def test_contorno_oscuro_es_visible_en_mitad_blanca(self):
        s=self.superficie((255,255,255),(22,33,48))
        Renderer._dibujar_numero_condominio(s,'2/4',self.fuente,(45,35))
        # En el fondo blanco los glifos blancos no destacarían sin el borde.
        oscuros=0
        for x in range(20,45):
            for y in range(20,51):
                r,g,b=s.get_at((x,y))[:3]
                if (r,g,b)==(10,19,31):oscuros+=1
        self.assertGreater(oscuros,5)

    def test_numero_blanco_visible_sobre_mitad_negra(self):
        s=self.superficie((255,255,255),(22,33,48))
        Renderer._dibujar_numero_condominio(s,'2/4',self.fuente,(45,35))
        claros=0
        for x in range(45,70):
            for y in range(20,51):
                r,g,b=s.get_at((x,y))[:3]
                if (r,g,b)==(255,255,255):claros+=1
        self.assertGreater(claros,5)

    def test_contenido_centrado_sin_pintar_fuera_de_ficha(self):
        s=self.superficie((250,250,250),(25,35,50))
        antes=s.get_at((2,2))
        Renderer._dibujar_numero_condominio(s,'7/8',self.fuente,(45,35))
        self.assertEqual(s.get_at((2,2)),antes)
        self.assertNotEqual(s.get_at((45,35)),s.get_at((2,2)))

    def test_aplica_a_varias_cantidades(self):
        for texto in ('1/1','2/4','12/25','100/3'):
            with self.subTest(texto=texto):
                s=self.superficie((250,250,250),(30,30,30))
                Renderer._dibujar_numero_condominio(s,texto,self.fuente,(45,35))
                oscuros=sum(s.get_at((x,y))[:3]==(10,19,31)
                            for x in range(15,45) for y in range(18,52))
                self.assertGreater(oscuros,0)


if __name__=='__main__':
    unittest.main()
