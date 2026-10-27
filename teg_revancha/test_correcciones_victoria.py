"""Regresiones: resultado final detalla la condición que hizo ganar la partida."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from logic import JuegoTEG, _objetivos_oficiales


def partida(n=4):
    juego=JuegoTEG(n_jugadores=n)
    juego.etapa='hostilidades'
    juego.fase='ATACAR'
    juego.ronda=2
    return juego


def asignar_misiones(juego, indice, misiones):
    jugador=juego.jugadores[indice]
    jugador.objetivos=misiones
    jugador.objetivo=misiones[0]
    return jugador


class TestMotivoVictoria(unittest.TestCase):
    def test_general_45_territorios_y_persistencia(self):
        j=partida()
        for i,p in enumerate(j.tablero):
            j.tablero[p]['propietario']=0 if i<45 else 1
        self.assertTrue(j._verificar_victoria(j.jugadores[0]))
        self.assertEqual(j.detalle_victoria,{
            'tipo':'general','objetivos':['Ocupar al menos 45 países'],'paises':45})
        self.assertFalse(j._verificar_victoria(j.jugadores[0]))
        self.assertEqual(j.detalle_victoria['tipo'],'general')

    def test_mision_de_ocupacion_con_descripcion_exacta(self):
        j=partida()
        m=next(o for o in _objetivos_oficiales() if o['descripcion']=='Europa y América del Sur')
        jugador=asignar_misiones(j,0,[m])
        for p,d in j.tablero.items():
            d['propietario']=0 if d['continente'] in ('Europa','America del Sur') else 1
        self.assertTrue(j._verificar_victoria(jugador))
        self.assertEqual(j.detalle_victoria['tipo'],'personal')
        self.assertEqual(j.detalle_victoria['objetivos'],['Europa y América del Sur'])
        self.assertLess(j.detalle_victoria['paises'],45)

    def test_dos_misiones_en_partida_de_dos_jugadores(self):
        j=partida(2)
        objetivos=_objetivos_oficiales()
        descripciones=('Europa y América del Sur',
                       'Europa, 4 países de Asia y 4 de América del Sur')
        misiones=[next(o for o in objetivos if o['descripcion']==nombre) for nombre in descripciones]
        jugador=asignar_misiones(j,0,misiones)
        for p,d in j.tablero.items():
            d['propietario']=0 if d['continente'] in ('Europa','America del Sur') else 1
        self.assertFalse(j._verificar_victoria(jugador))
        self.assertIsNone(j.detalle_victoria)
        for p in [p for p,d in j.tablero.items() if d['continente']=='Asia'][:4]:
            j.tablero[p]['propietario']=0
        self.assertTrue(j._verificar_victoria(jugador))
        self.assertEqual(j.detalle_victoria['objetivos'],list(descripciones))

    def test_eliminacion_identifica_al_rival(self):
        j=partida()
        enemigo=j.jugadores[1]
        objetivo={'tipo':'eliminacion','objetivo_idx':1,
                  'descripcion':f'Destruir ejército Rojo ({enemigo.nombre})'}
        ganador=asignar_misiones(j,0,[objetivo])
        enemigo.eliminado=True
        j._ultimo_atacante=0
        self.assertTrue(j._verificar_victoria(ganador))
        self.assertIn(enemigo.nombre,j.detalle_victoria['objetivos'][0])

    def test_no_hay_anuncio_antes_de_cumplir_condiciones(self):
        j=partida()
        for i,p in enumerate(j.tablero):
            j.tablero[p]['propietario']=0 if i<44 else 1
        asignar_misiones(j,0,[{'tipo':'ocupacion','descripcion':'Europa y América del Sur',
            'completos':['Europa','America del Sur']}])
        europa=next(p for p,d in j.tablero.items() if d['continente']=='Europa')
        j.tablero[europa]['propietario']=1
        self.assertFalse(j._verificar_victoria(j.jugadores[0]))
        self.assertIsNone(j.detalle_victoria)
        self.assertIsNone(j.ganador_idx)

    def test_ganador_puede_ser_bot(self):
        j=partida()
        for i,p in enumerate(j.tablero):
            j.tablero[p]['propietario']=1 if i<45 else 0
        self.assertTrue(j._verificar_victoria(j.jugadores[1]))
        self.assertEqual(j.ganador_idx,1)
        self.assertEqual(j.detalle_victoria['tipo'],'general')


class _Font:
    def size(self,text):
        return len(text)*12,24


class _Renderer:
    WIN_W,WIN_H=1880,900
    font_title=font_hero=font_lg=font_md=font_sm=_Font()

    def __init__(self):
        self.textos=[]
        self.screen=types.SimpleNamespace(fill=lambda *a:None)
        self.clock=types.SimpleNamespace(tick=lambda *a:None)

    def _texto(self,texto,*args,**kwargs):
        self.textos.append(str(texto))

    def _tarjeta(self,*args,**kwargs):
        pass

    def _ajustar_lineas(self,texto,font,ancho):
        lineas=[]
        actual=''
        for palabra in texto.split():
            siguiente=(actual+' '+palabra).strip()
            if font.size(siguiente)[0]>ancho and actual:
                lineas.append(actual)
                actual=palabra
            else:
                actual=siguiente
        if actual:lineas.append(actual)
        return lineas


class TestPantallaVictoria(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg=types.ModuleType('pygame')
        pg.QUIT,pg.KEYDOWN,pg.MOUSEBUTTONDOWN=3,4,5
        pg.draw=types.SimpleNamespace(rect=lambda *a,**k:None,
                                      circle=lambda *a,**k:None,
                                      line=lambda *a,**k:None)
        pg.display=types.SimpleNamespace(flip=lambda:None)
        pg.event=types.SimpleNamespace(get=lambda:[types.SimpleNamespace(type=4)])
        rendermod=types.ModuleType('renderer')
        rendermod.Renderer=_Renderer
        spec=importlib.util.spec_from_file_location('_test_victoria_main',
                                                     Path(__file__).with_name('main.py'))
        with patch.dict(sys.modules,{'pygame':pg,'renderer':rendermod}):
            mod=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        cls.pantalla=staticmethod(mod.pantalla_victoria)

    def test_ganador_bot_y_objetivo_general_en_pantalla(self):
        j=partida()
        for i,p in enumerate(j.tablero):
            j.tablero[p]['propietario']=1 if i<45 else 0
        j._verificar_victoria(j.jugadores[1])
        r=_Renderer()
        self.pantalla(r,j,j.jugadores[1].nombre)
        salida=' | '.join(r.textos)
        self.assertIn('GANÓ '+j.jugadores[1].nombre,salida)
        self.assertIn('OBJETIVO GENERAL CUMPLIDO',salida)
        self.assertIn('Ocupar al menos 45 países',salida)
        self.assertIn('45 / 45',salida)

    def test_mision_personal_en_pantalla(self):
        j=partida()
        m=next(o for o in _objetivos_oficiales() if o['descripcion']=='Europa y América del Sur')
        ganador=asignar_misiones(j,0,[m])
        for p,d in j.tablero.items():
            d['propietario']=0 if d['continente'] in ('Europa','America del Sur') else 1
        j._verificar_victoria(ganador)
        r=_Renderer()
        self.pantalla(r,j,ganador.nombre)
        salida=' | '.join(r.textos)
        self.assertIn('OBJETIVO PERSONAL CUMPLIDO',salida)
        self.assertIn('Europa y América del Sur',salida)


if __name__=='__main__':
    unittest.main()
