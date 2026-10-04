"""
Animação Didática de Fusão Nuclear em Tokamak com Manim
Para renderizar:
    manim -pql animacao_tokamak.py TokamakExplicacao   (qualidade baixa/rápida para teste)
    manim -pqh animacao_tokamak.py TokamakExplicacao   (alta qualidade 1080p 60fps)
"""

from manim import *
import numpy as np

class TokamakExplicacao(ThreeDScene):
    def construct(self):
        # ========================================================
        # CENA 1: TÍTULO E A REAÇÃO D-T (2D)
        # ========================================================
        titulo = Text("Fusão Nuclear: Reator Tokamak", font_size=36, color=BLUE_C)
        subtitulo = Text("Princípios de Confinamento Magnético e Física de Plasmas", font_size=20, color=GRAY)
        subtitulo.next_to(titulo, DOWN)

        self.play(Write(titulo), FadeIn(subtitulo))
        self.wait(1.5)
        self.play(FadeOut(titulo), FadeOut(subtitulo))

        # Reação D-T: 2H + 3H -> 4He (3.5 MeV) + n (14.1 MeV)
        txt_reacao = Text("Reação de Fusão Deutério-Trítio (D-T):", font_size=24, color=YELLOW)
        txt_reacao.to_edge(UP)

        equacao = Text(
            "²H + ³H  ⟶  ⁴He (3.5 MeV) + n (14.1 MeV) + 17.6 MeV",
            font_size=24,
            color=WHITE
        )
        equacao.next_to(txt_reacao, DOWN, buff=0.4)

        # Partículas visuais
        deuterio = VGroup(
            Dot(color=RED, radius=0.18),  # Próton
            Dot(color=GRAY, radius=0.18).shift(RIGHT * 0.25)  # Nêutron
        ).move_to(LEFT * 3.5 + DOWN * 0.5)
        lbl_d = Text("Deutério (D)", font_size=18, color=RED).next_to(deuterio, DOWN)

        tritio = VGroup(
            Dot(color=RED, radius=0.18),  # Próton
            Dot(color=GRAY, radius=0.18).shift(RIGHT * 0.25 + UP * 0.15),
            Dot(color=GRAY, radius=0.18).shift(RIGHT * 0.25 + DOWN * 0.15)
        ).move_to(RIGHT * 3.5 + DOWN * 0.5)
        lbl_t = Text("Trítio (T)", font_size=18, color=BLUE).next_to(tritio, DOWN)

        self.play(Write(txt_reacao), Write(equacao))
        self.play(FadeIn(deuterio), FadeIn(lbl_d), FadeIn(tritio), FadeIn(lbl_t))
        self.wait(1)

        # Colisão em altíssima energia
        flash = Flash(ORIGIN + DOWN * 0.5, color=YELLOW, flash_radius=1.5, num_lines=20)
        self.play(
            deuterio.animate.move_to(ORIGIN + DOWN * 0.5),
            tritio.animate.move_to(ORIGIN + DOWN * 0.5),
            FadeOut(lbl_d), FadeOut(lbl_t),
            run_time=1.2,
            rate_func=rush_into
        )
        self.play(flash, run_time=0.4)

        # Produtos formados
        alfa = VGroup(
            Dot(color=RED, radius=0.18).shift(LEFT * 0.15 + UP * 0.15),
            Dot(color=RED, radius=0.18).shift(RIGHT * 0.15 + DOWN * 0.15),
            Dot(color=GRAY, radius=0.18).shift(RIGHT * 0.15 + UP * 0.15),
            Dot(color=GRAY, radius=0.18).shift(LEFT * 0.15 + DOWN * 0.15)
        ).move_to(ORIGIN + DOWN * 0.5)
        neutron = Dot(color=WHITE, radius=0.12).move_to(ORIGIN + DOWN * 0.5)

        lbl_alfa = Text("Alfa (Partícula 4He)", font_size=16, color=YELLOW).next_to(UP * 1.5, UP)
        lbl_neut = Text("Nêutron Rápido (14.1 MeV)", font_size=16, color=WHITE).next_to(DOWN * 2.5, DOWN)

        self.remove(deuterio, tritio)
        self.play(
            alfa.animate.shift(LEFT * 2.5 + UP * 1.0),
            neutron.animate.shift(RIGHT * 4.0 + DOWN * 1.5),
            FadeIn(lbl_alfa), FadeIn(lbl_neut),
            run_time=1.2
        )
        self.wait(1.5)

        self.play(
            FadeOut(txt_reacao), FadeOut(equacao),
            FadeOut(alfa), FadeOut(neutron),
            FadeOut(lbl_alfa), FadeOut(lbl_neut)
        )

        # ========================================================
        # CENA 2: TRANSIÇÃO PARA O REATOR 3D (CÂMARA DE VÁCUO)
        # ========================================================
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        # Criação do Toroide (Câmara de Vácuo do Tokamak)
        R_maior = 2.6  # Raio maior do toro
        r_menor = 0.9  # Raio menor do toro

        toro_camara = Surface(
            lambda u, v: np.array([
                (R_maior + r_menor * np.cos(v)) * np.cos(u),
                (R_maior + r_menor * np.cos(v)) * np.sin(u),
                r_menor * np.sin(v)
            ]),
            u_range=[0, TAU],
            v_range=[0, TAU],
            resolution=(32, 16),
            fill_opacity=0.25,
            fill_color=BLUE_E,
            stroke_color=BLUE_B,
            stroke_width=0.5
        )

        # Núcleo de Plasma no interior
        r_plasma = 0.45
        plasma_torus = Surface(
            lambda u, v: np.array([
                (R_maior + r_plasma * np.cos(v)) * np.cos(u),
                (R_maior + r_plasma * np.cos(v)) * np.sin(u),
                r_plasma * np.sin(v)
            ]),
            u_range=[0, TAU],
            v_range=[0, TAU],
            resolution=(32, 16),
            fill_opacity=0.75,
            fill_color=PURPLE_A,
            stroke_color=PINK,
            stroke_width=0.8
        )

        # Bobinas toroidais (anéis externos)
        bobinas = VGroup()
        num_bobinas = 12
        for i in range(num_bobinas):
            ang = i * (TAU / num_bobinas)
            centro = np.array([R_maior * np.cos(ang), R_maior * np.sin(ang), 0])
            bobina = Circle(radius=r_menor + 0.15, color=ORANGE, stroke_width=4)
            bobina.rotate(PI / 2, axis=RIGHT)
            bobina.rotate(ang + PI / 2, axis=OUT, about_point=ORIGIN)
            bobina.move_to(centro)
            bobinas.add(bobina)

        self.play(Create(bobinas), run_time=1.8)
        self.play(FadeIn(toro_camara), run_time=1.5)
        self.play(FadeIn(plasma_torus), run_time=1.5)

        # Linhas de Campo Magnético Helicoidais (Fator de segurança q = 3)
        # O campo toroidal + campo poloidal cria uma hélice que fecha em si mesma
        q_fator = 3.0
        linhas_campo = VGroup()
        for offset_phi in [0, PI / 2, PI, 3 * PI / 2]:
            curva_helice = ParametricFunction(
                lambda t: np.array([
                    (R_maior + (r_plasma + 0.08) * np.cos(q_fator * t + offset_phi)) * np.cos(t),
                    (R_maior + (r_plasma + 0.08) * np.cos(q_fator * t + offset_phi)) * np.sin(t),
                    (r_plasma + 0.08) * np.sin(q_fator * t + offset_phi)
                ]),
                t_range=[0, TAU],
                color=YELLOW,
                stroke_width=2.5
            )
            linhas_campo.add(curva_helice)

        self.play(Create(linhas_campo), run_time=2.0)

        # Rotação suave da câmera para visualizar o confinamento tridimensional
        self.begin_ambient_camera_rotation(rate=0.25)
        self.wait(5)
        self.stop_ambient_camera_rotation()

        self.play(
            FadeOut(linhas_campo),
            FadeOut(plasma_torus),
            FadeOut(toro_camara),
            FadeOut(bobinas)
        )
        self.wait(1)
