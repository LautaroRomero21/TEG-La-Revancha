"""Regresiones para reagrupamientos contextuales y cuarto dado visible."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
from logic import JuegoTEG, FASE_REAGRUPAR, FASE_ATACAR

def cargar_modulos():
    fake=types.ModuleType('pygame')
    fake.time=types.SimpleNamespace(get_ticks=lambda:1000)
    mods={}
    with patch.dict(sys.modules,{'pygame':fake}):
        for nombre in ('renderer','main'):
            spec=importlib.util.spec_from_file_location('prueba_reagrupe_'+nombre,Path(__file__).with_name(nombre+'.py'))
            mod=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mods[nombre]=mod
    return mods['renderer'],mods['main']

def partida(tropas=21):
    j=JuegoTEG(n_jugadores=2,orden_inicial=[0,1])
    j.turno_idx=0
    j.fase=FASE_REAGRUPAR
    j.etapa='hostilidades'
    j.situacion='Clásico'
    j.tablero['Nigeria']['propietario']=0
    j.tablero['Nigeria']['ejercitos']=tropas
    j.tablero['Angola']['propietario']=0
    j.tablero['Angola']['ejercitos']=2
    j.reagrupados_recibidos={}
    return j

class ReagruparYDados(unittest.TestCase):
    def test_atajos_en_menu(self):
        renderer,_=cargar_modulos()
        j=partida()
        r=renderer.Renderer.__new__(renderer.Renderer)
        r.pais_seleccionado='Nigeria'
        r.pais_objetivo=None
        r.abrir_menu_contextual('Angola',(550,350),j)
        acts=[a for _,a in r.menu_contextual['items']]
        self.assertEqual([a for a in acts if a.startswith('ctx_reagrupar_')],
            ['ctx_reagrupar_1','ctx_reagrupar_5','ctx_reagrupar_max'])
        self.assertIn('reagrupar',acts)
        self.assertEqual((r.pais_seleccionado,r.pais_objetivo),('Nigeria','Angola'))

    def test_movimientos_sucesivos_y_seleccion_conservada(self):
        _,main=cargar_modulos()
        j=partida()
        registros=[]
        r=types.SimpleNamespace(pais_seleccionado='Nigeria',pais_objetivo='Angola',
            registrar_reagrupe=lambda *a,**kw:registros.append((a,kw)),
            construir_botones=lambda j:None)
        for n in ('1','5','max'):
            self.assertTrue(main.mover_reagrupe_rapido(j,r,n))
        self.assertEqual(j.tablero['Nigeria']['ejercitos'],1)
        self.assertEqual(j.tablero['Angola']['ejercitos'],22)
        self.assertEqual((r.pais_seleccionado,r.pais_objetivo),('Nigeria','Angola'))
        self.assertFalse(main.mover_reagrupe_rapido(j,r,'1'))
        self.assertEqual(len(registros),3)

    def test_no_mover_mas_de_disponible(self):
        _,main=cargar_modulos()
        j=partida(5)
        r=types.SimpleNamespace(pais_seleccionado='Nigeria',pais_objetivo='Angola',
            registrar_reagrupe=lambda *a,**k:None,construir_botones=lambda j:None)
        self.assertFalse(main.mover_reagrupe_rapido(j,r,'5'))
        self.assertEqual(j.tablero['Nigeria']['ejercitos'],5)
        self.assertEqual(main.maximo_reagrupe(j,'Nigeria','Angola'),4)

    def test_ejercitos_recibidos_no_salen(self):
        _,main=cargar_modulos()
        j=partida(10)
        j.reagrupados_recibidos['Nigeria']=8
        self.assertEqual(main.maximo_reagrupe(j,'Nigeria','Angola'),1)

    def test_popup_inicial_muestra_uno(self):
        renderer,_=cargar_modulos()
        r=renderer.Renderer.__new__(renderer.Renderer)
        captured={}
        r.mostrar_popup=lambda title,message,buttons:captured.update(mensaje=message)
        r.mostrar_popup_reagrupar('Nigeria','Angola',7)
        self.assertEqual(r._reagrupar_state['cantidad_actual'],1)
        self.assertIn('cantidad a mover: 1',captured['mensaje'])

    def test_cuatro_dados_visibles_con_ventaja(self):
        renderer,_=cargar_modulos()
        j=partida()
        j.fase=FASE_ATACAR
        j.tablero['Angola']['propietario']=1
        j.tablero['Angola']['ejercitos']=3
        with patch('logic.random.randint',return_value=3):
            result=j.atacar('Nigeria','Angola')
        self.assertTrue(result['ok'])
        self.assertEqual(len(renderer.Renderer._dados_visibles_hud(result,'dados_atk')),4)
        self.assertEqual(len(renderer.Renderer._dados_visibles_hud(result,'dados_def')),3)
        self.assertIn('DOBLE FUERZA',result['razon_4_dados'])

if __name__=='__main__':
    unittest.main()
