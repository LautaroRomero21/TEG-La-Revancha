"""Regresiones v25: visor de P y alertas ante rupturas diplomáticas."""
import os
import unittest
from unittest.mock import Mock
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
import pygame
from logic import JuegoTEG
from renderer import Renderer
from main import mostrar_aviso_pacto_pendiente


def partida():
    juego=JuegoTEG(4,orden_inicial=[0,1,2,3])
    juego.etapa='hostilidades'
    juego.ronda=3
    return juego


def vista_basica(juego):
    pygame.font.init()
    r=Renderer.__new__(Renderer)
    r.pais_seleccionado=None
    r.pais_objetivo=None
    r.popup=None
    r.menu_contextual=None
    r.vista_tarjetas=None
    r.screen=pygame.Surface((r.WIN_W,r.WIN_H))
    for nombre,size in (('font_xl',30),('font_md',19),
                        ('font_sm',16),('font_lg',23),('font_micro',13)):
        setattr(r,nombre,pygame.font.Font(None,size))
    return r


class AvisosDeRuptura(unittest.TestCase):
    def test_bot_anuncia_y_humano_recibe_aviso_sin_perder_proteccion(self):
        j=partida()
        p=j._nuevo_pacto('mundial',0,1)
        self.assertTrue(j.romper_pacto(p['id'],1))
        self.assertTrue(p['activo'])
        self.assertTrue(j._prohibido_por_pacto(0,1,'Nigeria','Angola'))
        self.assertEqual(len(j.avisos_pactos),1)
        aviso=j.avisos_pactos[0]
        self.assertEqual(aviso['tipo'],'ruptura_anunciada')
        self.assertEqual(aviso['por_idx'],1)
        self.assertEqual(aviso['pacto_id'],p['id'])
        self.assertEqual(aviso['turno_liberacion'],(0,1))

    def test_bot_no_puede_continuar_hasta_que_se_acepte_popup(self):
        j=partida()
        p=j._nuevo_pacto('mundial',0,1)
        j.romper_pacto(p['id'],1)
        renderer=Mock()
        renderer.popup=None
        renderer.vista_tarjetas=None
        self.assertTrue(mostrar_aviso_pacto_pendiente(j,renderer))
        self.assertEqual(len(j.avisos_pactos),0)
        renderer.mostrar_alerta_ruptura.assert_called_once()
        renderer.popup={'obligatorio':True}
        self.assertFalse(mostrar_aviso_pacto_pendiente(j,renderer))

    def test_mensaje_muestra_plazo_y_exige_confirmacion(self):
        j=partida()
        p=j._nuevo_pacto('mundial',0,1)
        j.romper_pacto(p['id'],1)
        r=vista_basica(j)
        r.mostrar_alerta_ruptura(j,j.avisos_pactos[0])
        self.assertEqual(r.popup['tipo'],'aviso_ruptura')
        self.assertTrue(r.popup['obligatorio'])
        self.assertIn('TERMINE TU PRÓXIMO TURNO',r.popup['mensaje'])
        self.assertIn(j.jugadores[1].color_nombre,r.popup['mensaje'])
        self.assertEqual(r.popup['botones'],[('ENTENDIDO','ok')])

    def test_aviso_al_terminar_proteccion_en_tu_turno(self):
        j=partida()
        p=j._nuevo_pacto('mundial',0,2)
        j.romper_pacto(p['id'],2)
        self.assertEqual(len(j.avisos_pactos),1)
        j._cierre_turno_diplomatico(1)
        self.assertTrue(p['activo'])
        j._cierre_turno_diplomatico(0)
        self.assertFalse(p['activo'])
        self.assertFalse(j._prohibido_por_pacto(0,2,'Nigeria','Angola'))
        self.assertEqual([a['tipo'] for a in j.avisos_pactos],
                         ['ruptura_anunciada','ruptura_efectiva'])
        r=vista_basica(j)
        r.mostrar_alerta_ruptura(j,j.avisos_pactos[1])
        self.assertIn('ya puede atacarte',r.popup['mensaje'])
        self.assertTrue(r.popup['obligatorio'])

    def test_si_rompe_humano_no_genera_alerta_de_rival(self):
        j=partida()
        p=j._nuevo_pacto('mundial',0,1)
        self.assertTrue(j.romper_pacto(p['id'],0))
        j._cierre_turno_diplomatico(1)
        self.assertEqual(j.avisos_pactos,[])

    def test_no_duplica_alertas_por_ruptura_repetida(self):
        j=partida()
        p=j._nuevo_pacto('mundial',0,1)
        self.assertTrue(j.romper_pacto(p['id'],1))
        self.assertFalse(j.romper_pacto(p['id'],1))
        self.assertEqual(len(j.avisos_pactos),1)


class VisorPactos(unittest.TestCase):
    def test_rupturas_primero_con_plazo_vigente(self):
        j=partida()
        p1=j._nuevo_pacto('mundial',0,1)
        p2=j._nuevo_pacto('continente',0,2,continente='Africa')
        j._nuevo_pacto('mundial',1,2)
        j.romper_pacto(p2['id'],2)
        grupos=Renderer._secciones_resumen_pactos(j)
        self.assertEqual(grupos[0]['titulo'],'RUPTURAS ANUNCIADAS · TODAVÍA PROTEGEN')
        self.assertEqual(grupos[0]['filas'][0]['estado'],'RUPTURA ANUNCIADA')
        self.assertIn('Protege hasta terminar turno',grupos[0]['filas'][0]['detalle'])
        self.assertEqual(grupos[0]['filas'][0]['jugadores'],p2['jugadores'])
        propio=next(g for g in grupos if g['titulo']=='PACTOS VIGENTES CON VOS')
        self.assertIn(f'#{p1["id"]}',propio['filas'][0]['titulo'])
        self.assertTrue(any(g['titulo']=='PACTOS ENTRE LOS DEMÁS COLORES' for g in grupos))

    def test_acuerdos_finalizados_no_se_muestran_como_vigentes(self):
        j=partida()
        p=j._nuevo_pacto('mundial',0,1)
        j.romper_pacto(p['id'],1)
        j._cierre_turno_diplomatico(0)
        grupos=Renderer._secciones_resumen_pactos(j)
        finalizados=next(g for g in grupos if 'FINALIZADOS' in g['titulo'])
        self.assertEqual(finalizados['filas'][0]['estado'],'FINALIZADO')
        self.assertFalse(any(f['estado']=='VIGENTE' for g in grupos for f in g['filas']))

    def test_listado_largo_no_se_trunca_y_permita_scroll(self):
        j=partida()
        for _ in range(18):
            j._nuevo_pacto('mundial',0,1)
        r=vista_basica(j)
        r.mostrar_pactos(j)
        self.assertEqual(r.popup['tipo'],'resumen_pactos')
        self.assertEqual(sum(len(g['filas']) for g in r.popup['secciones']),18)
        r._dibujar_popup_resumen_pactos(j)
        self.assertGreater(r.popup['scroll_max'],0)
        r.desplazar_pactos(3)
        self.assertGreater(r.popup['scroll'],0)
        self.assertEqual(r.screen.get_clip(),r.screen.get_rect())
        self.assertTrue(r.popup['_btn_rects'])

    def test_botones_se_mantienen_funcionales_en_la_ventana(self):
        j=partida()
        r=vista_basica(j)
        r.mostrar_pactos(j)
        r._dibujar_popup_resumen_pactos(j)
        cerrar=next(rect for rect,accion in r.popup['_btn_rects'] if accion=='ok')
        self.assertEqual(r.click_popup(cerrar.center),'ok')
        self.assertIsNone(r.popup)

    def test_pactos_muestran_colores_y_zonas_sin_repetirse(self):
        j=partida()
        j._nuevo_pacto('mundial',0,2)
        j.zonas_internacionales.append({
            'id':77,'pais':'Nigeria','jugadores':(1,3),
            'activa':True,'pendiente':1})
        grupos=Renderer._secciones_resumen_pactos(j)
        filas=[f for g in grupos for f in g['filas']]
        self.assertTrue(any(f['jugadores']==(0,2) for f in filas))
        self.assertTrue(any(f['jugadores']==(1,3) for f in filas))
        self.assertEqual(len(filas),2)

    def test_sin_pactos_se_puede_abrir(self):
        j=partida()
        r=vista_basica(j)
        r.mostrar_pactos(j)
        self.assertEqual(r.popup['secciones'][0]['titulo'],'SIN PACTOS REGISTRADOS')
        r._dibujar_popup_resumen_pactos(j)


if __name__=='__main__':
    unittest.main()
