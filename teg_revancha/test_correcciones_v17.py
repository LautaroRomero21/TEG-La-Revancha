"""Regresiones v17: selección, ataques repetidos y condominios (reglamento pp. 31–34)."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from logic import JuegoTEG, FASE_ATACAR, FASE_REAGRUPAR


def interfaz():
    falso = types.ModuleType('pygame')
    falso.time = types.SimpleNamespace(get_ticks=lambda: 1500)
    falso.Rect = lambda rect: tuple(rect)
    with patch.dict(sys.modules, {'pygame': falso}):
        spec = importlib.util.spec_from_file_location('_v17_renderer', Path(__file__).with_name('renderer.py'))
        render = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(render)
        with patch.dict(sys.modules, {'renderer': render}):
            spec = importlib.util.spec_from_file_location('_v17_main', Path(__file__).with_name('main.py'))
            main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main)
    return main, render


def partida():
    j = JuegoTEG(4, orden_inicial=[0, 1, 2, 3])
    j.etapa = 'hostilidades'
    j.etapa_ronda = 'ATAQUE'
    j.ronda = 3
    j.fase = FASE_ATACAR
    j.turno_idx = 0
    j.situacion = 'Clásico'
    for pais in j.tablero:
        j.tablero[pais]['propietario'] = 3
        j.tablero[pais]['ejercitos'] = 1
        j.tablero[pais]['misiles'] = 0
    j.tablero['Alaska']['propietario'] = 0
    j.tablero['Alaska']['ejercitos'] = 30
    j.tablero['Canada']['propietario'] = 1
    j.tablero['Canada']['ejercitos'] = 10
    j.tablero['Oregon']['propietario'] = 0
    j.tablero['Oregon']['ejercitos'] = 20
    return j


def condominio():
    j = partida()
    j.condominios['Canada'] = {0: 12, 1: 6}
    j._sincronizar_condominio('Canada')
    pacto = j._nuevo_pacto('condominio', 0, 1, pais='Canada')
    return j, pacto


class ClicsYCombate(unittest.TestCase):
    def setUp(self):
        self.main, self.renderer = interfaz()
        self.j = partida()
        self.r = types.SimpleNamespace(
            pais_seleccionado='Alaska', pais_objetivo='Canada',
            pais_en_pos=lambda *args: None, construir_botones=lambda *args: None,
            registrar_combate=lambda *args, **kwargs: None,
            mostrar_resultado_dados=lambda *args, **kwargs: None,
            mostrar_popup=lambda *args, **kwargs: None,
            mostrar_popup_conquista=lambda *args, **kwargs: None)

    def test_clic_vacio_borra_dos_selecciones(self):
        self.main.manejar_clic_mapa((690, 600), self.j, self.r)
        self.assertIsNone(self.r.pais_seleccionado)
        self.assertIsNone(self.r.pais_objetivo)

    def test_clic_vacio_borra_solo_origen(self):
        self.r.pais_objetivo = None
        self.main.manejar_clic_mapa((690, 600), self.j, self.r)
        self.assertIsNone(self.r.pais_seleccionado)

    def test_ataques_repetidos_mantienen_seleccion(self):
        self.j.tablero['Canada']['ejercitos'] = 12
        with patch('logic.random.randint', return_value=3):
            self.main.manejar_boton('atacar_4', self.j, self.r)
            self.assertEqual((self.r.pais_seleccionado,self.r.pais_objetivo),('Alaska','Canada'))
            self.main.manejar_boton('atacar_4', self.j, self.r)
        self.assertEqual((self.r.pais_seleccionado,self.r.pais_objetivo),('Alaska','Canada'))

    def test_panel_habilita_ataque_desde_condominio(self):
        j, _ = condominio()
        r = self.renderer.Renderer.__new__(self.renderer.Renderer)
        r.pais_seleccionado='Canada'
        r.pais_objetivo='Isla Victoria'
        r.botones=[]
        r.velocidad_bot_idx=1
        r.velocidades_bot=[('PAUSA',None),('1x',1100)]
        r.font_md=None
        r.font_micro=None
        r.construir_botones(j)
        boton=next(b for b in r.botones if b.accion=='atacar_4')
        self.assertTrue(boton.activo)

    def test_menu_condominio_permita_ataque_interno(self):
        j, _ = condominio()
        r = self.renderer.Renderer.__new__(self.renderer.Renderer)
        r.pais_seleccionado=None
        r.pais_objetivo=None
        r.abrir_menu_contextual('Canada',(590,350),j)
        self.assertIn('ctx_atacar_interno',[a for _,a in r.menu_contextual['items']])

    def test_comando_ataque_interno(self):
        j,pacto=condominio()
        self.assertTrue(j.romper_pacto(pacto['id'],0))
        j._cierre_turno_diplomatico(1)
        r=types.SimpleNamespace(_contexto_pais='Canada',
            pais_seleccionado=None,pais_objetivo=None,
            construir_botones=lambda *args: None,
            registrar_combate=lambda *args, **kwargs: None,
            mostrar_resultado_dados=lambda *args, **kwargs: None,
            mostrar_popup=lambda *args, **kwargs: None,
            mostrar_popup_conquista=lambda *args, **kwargs: None)
        with patch('pactos.random.randint',return_value=4):
            self.main.manejar_boton('ctx_atacar_interno',j,r)
        self.assertEqual((r.pais_seleccionado,r.pais_objetivo),('Canada','Canada'))


class ReglasDeCondominio(unittest.TestCase):
    def test_ruptura_diferida(self):
        j,pacto=condominio()
        self.assertTrue(j.romper_pacto(pacto['id'],0))
        self.assertFalse(j.atacar('Canada','Canada')['ok'])
        j._cierre_turno_diplomatico(0)
        self.assertFalse(j.atacar('Canada','Canada')['ok'])
        j._cierre_turno_diplomatico(1)
        self.assertFalse(pacto['activo'])
        with patch('pactos.random.randint',return_value=4):
            self.assertTrue(j.atacar('Canada','Canada')['ok'])

    def test_aliado_original_no_ataca_desde_exterior(self):
        j,pacto=condominio()
        j.romper_pacto(pacto['id'],0)
        j._cierre_turno_diplomatico(1)
        self.assertFalse(j.atacar('Alaska','Canada')['ok'])

    def test_ataque_desde_condominio_contra_tercero(self):
        j,_=condominio()
        j.tablero['Isla Victoria']['propietario']=2
        j.tablero['Isla Victoria']['ejercitos']=8
        with patch('logic.random.randint',return_value=3):
            resultado=j.atacar('Canada','Isla Victoria')
        self.assertTrue(resultado['ok'])
        self.assertEqual(j.condominios['Canada'][0],12-resultado['bajas_atk'])
        self.assertEqual(j.condominios['Canada'][1],6)

    def test_desde_condominio_no_se_ataca_pais_del_socio(self):
        j,_=condominio()
        j.tablero['Isla Victoria']['propietario']=1
        self.assertFalse(j.atacar('Canada','Isla Victoria')['ok'])

    def test_reagrupar_ambos_sentidos_con_guarniciones_separadas(self):
        j,_=condominio()
        j.fase=FASE_REAGRUPAR
        j.tablero['Alaska']['ejercitos']=15
        self.assertTrue(j.reagrupar('Alaska','Canada',3))
        self.assertEqual(j.condominios['Canada'],{0:15,1:6})
        self.assertTrue(j.reagrupar('Canada','Alaska',2))
        self.assertEqual(j.condominios['Canada'],{0:13,1:6})
        self.assertEqual(j.tablero['Canada']['ejercitos'],19)

    def test_refuerzos_recibidos_no_vuelven_a_moverse(self):
        j,_=condominio()
        j.fase=FASE_REAGRUPAR
        j.tablero['Alaska']['ejercitos']=4
        self.assertTrue(j.reagrupar('Canada','Alaska',3))
        self.assertFalse(j.reagrupar('Alaska','Canada',4))
        self.assertTrue(j.reagrupar('Alaska','Canada',3))

    def test_tropas_recibidas_fuera_no_entran_al_condominio(self):
        j,_=condominio()
        j.fase=FASE_REAGRUPAR
        j.reagrupados_recibidos['Oregon']=19
        self.assertFalse(j.reagrupar('Oregon','Canada',1))

    def test_descanso_impide_reagrupacion_normal(self):
        j,_=condominio()
        j.fase=FASE_REAGRUPAR
        j.situacion=f'Descanso {j.jugador_actual().color_nombre}'
        self.assertFalse(j.reagrupar('Alaska','Canada',1))
        self.assertFalse(j.reagrupar('Canada','Alaska',1))

    def test_bot_considera_combate_interno_tras_tregua(self):
        j,pacto=condominio()
        j.turno_idx=1
        j.condominios['Canada']={0:2,1:15}
        j._sincronizar_condominio('Canada')
        j.jugadores[1].estilo_bot='Agresivo'
        posiciones=lambda: [(a,b) for _,a,b in j._ataques_posibles_bot(j.jugadores[1])]
        self.assertNotIn(('Canada','Canada'),posiciones())
        j.romper_pacto(pacto['id'],1)
        j._cierre_turno_diplomatico(0)
        self.assertIn(('Canada','Canada'),posiciones())


if __name__=='__main__':
    unittest.main()
