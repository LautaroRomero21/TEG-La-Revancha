"""Pruebas de frontera, selector e IA avanzada de dificultad Difícil."""
import unittest
from unittest.mock import patch
from ia_dificil import probabilidad_conquista, transiciones_dados
from logic import JuegoTEG, FASE_ATACAR, FASE_INCORPORAR


class Dificultades(unittest.TestCase):
    def test_normal_por_defecto(self):
        self.assertEqual(JuegoTEG(3).dificultad,'Normal')

    def test_elegir_dificil(self):
        self.assertEqual(JuegoTEG(3,dificultad='Dificil').dificultad,'Dificil')
        with self.assertRaises(ValueError):
            JuegoTEG(3,dificultad='Extrema')

    def test_normal_y_dificil_usan_motores_independientes(self):
        normal=JuegoTEG(3,dificultad='Normal')
        hard=JuegoTEG(3,dificultad='Dificil')
        normal.turno_idx=1
        with patch.object(normal,'_seleccionar_refuerzo_bot',return_value=normal.paises_de(1)[0]):
            self.assertEqual(normal.paso_bot()['accion'],'incorporar')
        hard.turno_idx=1
        with patch.object(hard.ia_dificil,'refuerzo',return_value={'accion':'via_ia_dificil'}):
            self.assertEqual(hard.paso_bot()['accion'],'via_ia_dificil')


class Probabilidades(unittest.TestCase):
    def test_un_dado_contra_un_dado(self):
        p,perdidas=probabilidad_conquista(2,1,'Clásico')
        self.assertAlmostEqual(p,15/36,places=10)
        self.assertGreater(perdidas,0)

    def test_transiciones_suman_uno(self):
        for a in range(1,5):
            for d in range(1,5):
                self.assertAlmostEqual(sum(x[2] for x in transiciones_dados(a,d)),1,places=10)

    def test_doble_fuerza_y_nieve(self):
        self.assertGreater(probabilidad_conquista(12,3,'Clásico')[0],
                           probabilidad_conquista(8,3,'Clásico')[0])
        self.assertLess(probabilidad_conquista(12,5,'Nieve')[0],
                        probabilidad_conquista(12,5,'Clásico')[0])

    def test_viento_no_pierde_mas_ejercitos_de_los_que_tiene(self):
        p,bajas=probabilidad_conquista(2,1,'Viento a favor')
        self.assertGreaterEqual(p,0)
        self.assertLessEqual(bajas,1)


class PropuestaConjunta(unittest.TestCase):
    def setUp(self):
        j=self.j=JuegoTEG(4)
        j.etapa='hostilidades'
        j.fase=FASE_ATACAR
        j.ronda=2
        for nombre,actor in (('Chicago',0),('Oregon',1),('Las Vegas',2)):
            j.tablero[nombre]['propietario']=actor
            j.tablero[nombre]['ejercitos']=10

    def test_clasico_permitido(self):
        self.j.situacion='Clásico'
        j=self.j
        self.assertTrue(j.puede_proponer_agresion_conjunta(0,1,'Chicago','Oregon','Las Vegas'))
        self.assertIsNotNone(j.proponer_agresion_conjunta(0,1,'Chicago','Oregon','Las Vegas'))

    def test_abiertas_rechaza_antes_de_enviar(self):
        j=self.j
        j.situacion='Fronteras abiertas'
        n=len(j.agresiones_pendientes)
        self.assertFalse(j.puede_proponer_agresion_conjunta(0,1,'Chicago','Oregon','Las Vegas'))
        self.assertIsNone(j.proponer_agresion_conjunta(0,1,'Chicago','Oregon','Las Vegas'))
        self.assertEqual(len(j.agresiones_pendientes),n)

    def test_cerradas_acepta_mismo_continente(self):
        j=self.j
        j.situacion='Fronteras cerradas'
        self.assertTrue(j.puede_proponer_agresion_conjunta(0,1,'Chicago','Oregon','Las Vegas'))

    def test_cerradas_rechaza_distinto_continente(self):
        j=self.j
        j.situacion='Fronteras cerradas'
        j.tablero['Chicago']['continente']='Europa'
        self.assertFalse(j.puede_proponer_agresion_conjunta(0,1,'Chicago','Oregon','Las Vegas'))

    def test_abiertas_acepta_si_ambos_cruzan_continentes(self):
        j=self.j
        j.situacion='Fronteras abiertas'
        j.tablero['Chicago']['continente']='Europa'
        j.tablero['Oregon']['continente']='Asia'
        self.assertTrue(j.puede_proponer_agresion_conjunta(0,1,'Chicago','Oregon','Las Vegas'))

    def test_no_envia_si_aliado_no_puede_atacar(self):
        j=self.j
        j.situacion='Fronteras abiertas'
        j.tablero['Chicago']['continente']='Europa'
        self.assertFalse(j.puede_proponer_agresion_conjunta(0,1,'Chicago','Oregon','Las Vegas'))


class EstrategiaAvanzada(unittest.TestCase):
    def setUp(self):
        j=self.j=JuegoTEG(4,dificultad='Dificil')
        j.etapa='hostilidades'
        j.fase=FASE_ATACAR
        j.turno_idx=1
        j.situacion='Clásico'
        j.tablero['Nigeria']['propietario']=1
        j.tablero['Nigeria']['ejercitos']=3
        j.tablero['Angola']['propietario']=2
        j.tablero['Angola']['ejercitos']=20

    def test_evitar_ataques_suicidas(self):
        j=self.j
        ctx=j.ia_dificil.contexto(j.jugadores[1])
        self.assertIsNone(j.ia_dificil.evaluacion_ataque('Nigeria','Angola',j.jugadores[1],ctx))

    def test_anti_ganador_subir_prioridad(self):
        j=self.j
        ctx=j.ia_dificil.contexto(j.jugadores[1])
        base=j.ia_dificil.valor_pais('Angola',j.jugadores[1],ctx)
        ctx['paises'][2]=43
        self.assertGreater(j.ia_dificil.valor_pais('Angola',j.jugadores[1],ctx),base+10)

    def test_no_espiar_objetivos_de_rivales(self):
        j=self.j
        antes=j.ia_dificil.contexto(j.jugadores[1])
        j.jugadores[2].objetivos=[{'tipo':'eliminacion','descripcion':'SECRETO'}]
        despues=j.ia_dificil.contexto(j.jugadores[1])
        self.assertEqual(antes,despues)

    def test_ataque_interno_condominio_respeta_tregua(self):
        j=self.j
        j.condominios['Canada']={1:15,2:1}
        j._sincronizar_condominio('Canada')
        pacto=j._nuevo_pacto('condominio',1,2,pais='Canada')
        with patch.object(j,'paises_de',return_value=['Canada']):
            with patch.object(j.ia_dificil,'_frentes',return_value=[]):
                self.assertIsNone(j.ia_dificil.candidato_ataque(j.jugadores[1]))
                pacto['activo']=False
                resultado=j.ia_dificil.candidato_ataque(j.jugadores[1])
                self.assertIsNotNone(resultado)
                self.assertEqual(resultado[-2:],('Canada','Canada'))

    def test_bot_avanza_con_acciones_legales(self):
        j=self.j
        j.fase=FASE_INCORPORAR
        j.ejercitos_a_colocar=8
        j.refuerzos_continente={}
        for _ in range(80):
            if j.turno_idx!=1 or j.fase=='VICTORIA':break
            estado=j.paso_bot()
            self.assertTrue(estado is None or isinstance(estado,dict))


if __name__=='__main__':
    unittest.main()
