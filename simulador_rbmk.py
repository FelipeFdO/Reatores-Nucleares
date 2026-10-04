import pygame
import sys
import math
import random

pygame.init()
tela = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Simulador Nuclear RBMK - Moderado a Grafite")
clock = pygame.time.Clock()

fonte_titulo = pygame.font.SysFont("Arial", 18, bold=True)
fonte_texto = pygame.font.SysFont("Arial", 15, bold=True)
fonte_info = pygame.font.SysFont("Arial", 15)
fonte_alerta = pygame.font.SysFont("Arial", 28, bold=True)
fonte_energia = pygame.font.SysFont("Arial", 28, bold=True)

# Variáveis da Física Termodinâmica (RBMK)
temp_nucleo = 30.0    
insercao_hastes = 80.0
fissao_ativa = False
pausado = False
modo_chernobyl = False
nucleo_destruido = False
fluxo_animacao = 0.0
potencia_eletrica_mw = 0.0
rotacao_eixo = 0.0

PONTO_EBULICAO = 285.0 

btn_fissao = pygame.Rect(20, 540, 130, 40)
btn_up = pygame.Rect(160, 540, 130, 40)
btn_down = pygame.Rect(300, 540, 130, 40)
btn_pause = pygame.Rect(440, 540, 130, 40)
btn_reset = pygame.Rect(580, 540, 140, 40)
btn_az5 = pygame.Rect(740, 540, 240, 40) 
btn_reset_destruido = pygame.Rect(350, 460, 300, 55)

def reiniciar():
    global temp_nucleo, insercao_hastes, fissao_ativa, pausado, modo_chernobyl, nucleo_destruido, fluxo_animacao, potencia_eletrica_mw, rotacao_eixo
    temp_nucleo = 30.0
    insercao_hastes = 80.0
    fissao_ativa = False
    pausado = False
    modo_chernobyl = False
    nucleo_destruido = False
    fluxo_animacao = 0.0
    potencia_eletrica_mw = 0.0
    rotacao_eixo = 0.0

rodando = True

def desenhar_tubo_animado(superficie, cor_particulas, inicio, fim, offset, raio=4, espacamento=25):
    pygame.draw.line(superficie, (140, 145, 150), inicio, fim, 14)
    dx = fim[0] - inicio[0]
    dy = fim[1] - inicio[1]
    distancia = math.hypot(dx, dy)
    if distancia == 0: return
    dir_x, dir_y = dx / distancia, dy / distancia
    pos = offset % espacamento
    while pos < distancia:
        px = inicio[0] + dir_x * pos
        py = inicio[1] + dir_y * pos
        pygame.draw.circle(superficie, cor_particulas, (int(px), int(py)), raio)
        pos += espacamento

def desenhar_casa(superficie, x, y, energia_suficiente):
    pygame.draw.rect(superficie, (180, 170, 160), (x, y, 40, 30))
    pygame.draw.polygon(superficie, (150, 50, 50), [(x-5, y), (x+20, y-20), (x+45, y)])
    cor_janela = (255, 255, 100) if energia_suficiente else (50, 50, 60)
    pygame.draw.rect(superficie, cor_janela, (x+10, y+5, 20, 15))
    pygame.draw.line(superficie, (100, 100, 100), (x+20, y+5), (x+20, y+20), 2)
    pygame.draw.line(superficie, (100, 100, 100), (x+10, y+12), (x+30, y+12), 2)
    if energia_suficiente:
        pygame.draw.rect(superficie, (255, 255, 150), (x+8, y+3, 24, 19), 1)

def desenhar_botao(superficie, rect, texto, cor_base, mouse_pos):
    if rect.collidepoint(mouse_pos):
        cor = (min(255, cor_base[0] + 30), min(255, cor_base[1] + 30), min(255, cor_base[2] + 30))
    else:
        cor = cor_base
    pygame.draw.rect(superficie, cor, rect, border_radius=8)
    pygame.draw.rect(superficie, (50, 50, 50), rect, 2, border_radius=8)
    surf_texto = fonte_texto.render(texto, True, (255, 255, 255))
    rect_texto = surf_texto.get_rect(center=rect.center)
    superficie.blit(surf_texto, rect_texto)

# Função para desenhar texto com contorno (outline) para leitura perfeita
def desenhar_texto_contornado(superficie, texto, fonte, cor_texto, cor_contorno, x, y):
    surf_contorno = fonte.render(texto, True, cor_contorno)
    surf_texto = fonte.render(texto, True, cor_texto)
    # Desenha o contorno deslocando 2 pixels para todos os lados
    for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2), (-2,0), (2,0), (0,-2), (0,2)]:
        superficie.blit(surf_contorno, (x + dx, y + dy))
    superficie.blit(surf_texto, (x, y))

while rodando:
    mouse_pos = pygame.mouse.get_pos()
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if nucleo_destruido:
                    if btn_reset_destruido.collidepoint(evento.pos):
                        reiniciar()
                else:
                    if btn_fissao.collidepoint(evento.pos): fissao_ativa = not fissao_ativa
                    elif btn_up.collidepoint(evento.pos): insercao_hastes = max(0, insercao_hastes - 5)
                    elif btn_down.collidepoint(evento.pos): insercao_hastes = min(100, insercao_hastes + 5)
                    elif btn_pause.collidepoint(evento.pos): pausado = not pausado
                    elif btn_reset.collidepoint(evento.pos): reiniciar()
                    elif btn_az5.collidepoint(evento.pos): 
                        modo_chernobyl = True
                        fissao_ativa = True

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                reiniciar()
            elif not nucleo_destruido:
                if evento.key == pygame.K_w: insercao_hastes = max(0, insercao_hastes - 5)
                elif evento.key == pygame.K_s: insercao_hastes = min(100, insercao_hastes + 5)
                elif evento.key == pygame.K_SPACE: fissao_ativa = not fissao_ativa
                elif evento.key == pygame.K_p: pausado = not pausado

    # --- A. CÁLCULO TERMODINÂMICO (RBMK) ---
    if not pausado and not nucleo_destruido:
        
        if modo_chernobyl:
            insercao_hastes = min(100, insercao_hastes + 2)
            
            # FÍSICA DESACELERADA DIDÁTICA: O crescimento é exponencial, mas mais lento
            fator_fissao = (temp_nucleo * 0.012) + 5 
            temp_nucleo += fator_fissao
            
            if temp_nucleo > 3000:
                nucleo_destruido = True
                potencia_eletrica_mw = 0.0
        else:
            if fissao_ativa:
                fator_fissao = (100 - insercao_hastes) * 0.14
                if temp_nucleo > PONTO_EBULICAO:
                    fator_fissao += (temp_nucleo - PONTO_EBULICAO) * 0.01 
                temp_nucleo += fator_fissao
            
            temp_nucleo -= (temp_nucleo - 40) * 0.012
            temp_nucleo = max(30, min(temp_nucleo, 1500))
        
        fluxo_animacao += 2 + (temp_nucleo / 150)

        if temp_nucleo >= PONTO_EBULICAO and not nucleo_destruido:
            energia_termica = (temp_nucleo - PONTO_EBULICAO) * 10.0 
            potencia_eletrica_mw = energia_termica * 0.32 
            rotacao_eixo += (temp_nucleo - PONTO_EBULICAO) / 8
        else:
            potencia_eletrica_mw = 0.0
            rotacao_eixo = 0.0

    # --- B. RENDERIZAÇÃO GRÁFICA ---
    tela.fill((230, 235, 240)) # Fundo cinza constante para leitura limpa

    r_nuc = min(255, max(80, int((temp_nucleo - 30) / 1000 * 255 + 80)))
    g_nuc = min(255, max(80, int((temp_nucleo - 500) / 1000 * 255 + 80)) if temp_nucleo > 500 else 80)
    b_nuc = min(255, max(80, int((temp_nucleo - 800) / 1000 * 255 + 80)) if temp_nucleo > 800 else 80)
    cor_nucleo = (r_nuc, g_nuc, b_nuc)

    if temp_nucleo >= PONTO_EBULICAO:
        cor_fluido = (220, 220, 230) 
    else:
        cor_fluido = (100, 150, 255) 

    if not nucleo_destruido:
        desenhar_tubo_animado(tela, cor_fluido, (340, 240), (600, 240), fluxo_animacao * 1.5)
        desenhar_tubo_animado(tela, cor_fluido, (635, 310), (635, 340), fluxo_animacao * 1.5)
        desenhar_tubo_animado(tela, (50, 180, 255), (635, 410), (635, 440), fluxo_animacao)
        desenhar_tubo_animado(tela, (50, 180, 255), (635, 440), (340, 440), fluxo_animacao)

    # 1. NÚCLEO RBMK
    if nucleo_destruido:
        # Fumaça/Fogo restritos ao espaço do núcleo
        for _ in range(40):
            pygame.draw.circle(tela, (40,40,40), (260 + random.randint(-120, 120), 340 + random.randint(-150, 100)), random.randint(30, 50))
            pygame.draw.circle(tela, (255,80,0), (260 + random.randint(-80, 80), 340 + random.randint(-80, 60)), random.randint(15, 35))
        
        # Alerta com contorno grosso e legível sobre qualquer coisa
        texto_alerta_dest = fonte_alerta.render("EXPLOSÃO TÉRMICA! NÚCLEO EXPOSTO!", True, (255, 50, 50))
        texto_alerta_cont = fonte_alerta.render("EXPLOSÃO TÉRMICA! NÚCLEO EXPOSTO!", True, (0, 0, 0))
        # Desenha contorno
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2), (-2,0), (2,0), (0,-2), (0,2)]:
            tela.blit(texto_alerta_cont, (350 + dx, 300 + dy))
        tela.blit(texto_alerta_dest, (350, 300))
        
    else:
        pygame.draw.rect(tela, cor_nucleo, (180, 190, 160, 300), border_radius=10)
        for x in range(180, 340, 40):
            pygame.draw.line(tela, (40, 40, 40), (x, 190), (x, 490), 2)
        for y in range(190, 490, 40):
            pygame.draw.line(tela, (40, 40, 40), (180, y), (340, y), 2)
            
        pygame.draw.rect(tela, (80, 80, 80), (180, 190, 160, 300), 6, border_radius=10)
        tela.blit(fonte_texto.render("NÚCLEO (Grafite)", True, (50, 50, 50)), (195, 500))
        
        altura_haste = (insercao_hastes / 100.0) * 260
        pygame.draw.rect(tela, (40, 40, 40), (215, 190, 10, altura_haste)) 
        if altura_haste > 0: pygame.draw.rect(tela, (150, 150, 150), (215, 190 + altura_haste, 10, 15))
        pygame.draw.rect(tela, (40, 40, 40), (255, 190, 10, altura_haste))
        if altura_haste > 0: pygame.draw.rect(tela, (150, 150, 150), (255, 190 + altura_haste, 10, 15))
        pygame.draw.rect(tela, (40, 40, 40), (295, 190, 10, altura_haste))
        if altura_haste > 0: pygame.draw.rect(tela, (150, 150, 150), (295, 190 + altura_haste, 10, 15))

    # 2. Turbina, Gerador e Casas (só desenha se não explodiu)
    if not nucleo_destruido:
        pygame.draw.polygon(tela, (160, 160, 170), [(600, 210), (680, 170), (680, 330), (600, 290)])
        pygame.draw.polygon(tela, (100, 100, 100), [(600, 210), (680, 170), (680, 330), (600, 290)], 3)
        tela.blit(fonte_texto.render("TURBINA", True, (50,50,50)), (605, 145))
        
        pygame.draw.rect(tela, (80, 80, 80), (680, 245, 40, 10))
        pygame.draw.rect(tela, (200, 150, 50), (720, 190, 90, 120), border_radius=10)
        pygame.draw.rect(tela, (120, 90, 30), (720, 190, 90, 120), 4, border_radius=10)
        tela.blit(fonte_texto.render("GERADOR", True, (50,50,50)), (730, 170))
        
        pos_y_rotor = 250 + math.sin(math.radians(rotacao_eixo)) * 40
        pygame.draw.line(tela, (100, 60, 20), (725, int(pos_y_rotor)), (805, int(pos_y_rotor)), 6)

        if potencia_eletrica_mw > 0:
            cor_energia = (255, 215, 0)
            brilho = int(abs(math.sin(math.radians(rotacao_eixo * 2))) * 255)
            pygame.draw.line(tela, (brilho, brilho, 0), (810, 250), (950, 250), 4) 
            pygame.draw.line(tela, (brilho, brilho, 0), (950, 200), (950, 430), 2)
        else:
            cor_energia = (100, 100, 100)
            pygame.draw.line(tela, cor_energia, (810, 250), (950, 250), 4)
            pygame.draw.line(tela, cor_energia, (950, 200), (950, 430), 2)

        desenhar_casa(tela, 930, 170, potencia_eletrica_mw > 1)
        desenhar_casa(tela, 930, 280, potencia_eletrica_mw > 250)
        desenhar_casa(tela, 930, 390, potencia_eletrica_mw > 500)
        tela.blit(fonte_texto.render("CIDADE", True, (50,50,50)), (925, 440))
        
        pygame.draw.rect(tela, (100, 150, 200), (590, 340, 90, 70), border_radius=8)
        tela.blit(fonte_texto.render("CONDENSADOR", True, (50, 50, 50)), (580, 420))

    # --- C. PAINEL DE INFORMAÇÕES (HUD) ---
    pygame.draw.rect(tela, (255, 255, 255), (20, 20, 960, 140), border_radius=10)
    pygame.draw.rect(tela, (180, 180, 180), (20, 20, 960, 140), 2, border_radius=10)

    tela.blit(fonte_titulo.render("1. CIRCUITO PRIMÁRIO (Núcleo RBMK)", True, (100, 100, 100)), (40, 25))
    tela.blit(fonte_info.render(f"Temp. do Núcleo: {temp_nucleo:.1f} °C", True, (30, 30, 30)), (40, 50))
    tela.blit(fonte_info.render(f"Combustível: Urânio Levemente Enriquecido", True, (30, 30, 30)), (40, 70))
    tela.blit(fonte_info.render(f"Moderador: Blocos de Grafite Sólido", True, (30, 30, 30)), (40, 90)) 
    estado = "ATIVA" if fissao_ativa else "PARADA"
    tela.blit(fonte_info.render(f"Fissão: {estado} (Hastes: {insercao_hastes:.0f}%)", True, (30, 30, 30)), (40, 110))

    tela.blit(fonte_titulo.render("2. ESPECIFICAÇÕES DE RISCO", True, (180, 50, 50)), (380, 25))
    tela.blit(fonte_info.render(f"Pressão Operacional: ~70 atm", True, (30, 30, 30)), (380, 50))
    tela.blit(fonte_info.render(f"Coeficiente de Vazio: POSITIVO", True, (180, 0, 0)), (380, 70))
    tela.blit(fonte_info.render(f"Física: Vapor no núcleo ACELERA a fissão", True, (30, 30, 30)), (380, 90))
    tela.blit(fonte_info.render(f"Falha AZ-5: Pontas de grafite geram pico", True, (30, 30, 30)), (380, 110))
    
    tela.blit(fonte_titulo.render("3. REDE ELÉTRICA", True, (200, 150, 50)), (740, 25))
    tela.blit(fonte_energia.render(f"{potencia_eletrica_mw:.1f} MW", True, (200, 150, 50) if not nucleo_destruido else (100,100,100)), (740, 55))
    if potencia_eletrica_mw > 0:
        tela.blit(fonte_info.render(f"Operação Instável", True, (180, 100, 30)), (740, 95))
    else:
        tela.blit(fonte_info.render(f"Sem geração", True, (150, 30, 30)), (740, 95))

    # Alertas antes da destruição (com contorno para leitura)
    if not nucleo_destruido:
        if modo_chernobyl:
            desenhar_texto_contornado(tela, "AZ-5 ACIONADO! CICLO EXPONENCIAL!", fonte_alerta, (255, 50, 50), (0,0,0), 380, 300)
        elif temp_nucleo > 600:
            desenhar_texto_contornado(tela, "ALERTA: INSTABILIDADE TÉRMICA DETECTADA!", fonte_alerta, (255, 100, 0), (0,0,0), 350, 300)

    # --- D. DESENHAR BOTÕES ---
    if not nucleo_destruido:
        cor_btn_fissao = (200, 80, 80) if fissao_ativa else (80, 180, 80)
        texto_btn_fissao = "PARAR FISSÃO" if fissao_ativa else "INICIAR"
        desenhar_botao(tela, btn_fissao, texto_btn_fissao, cor_btn_fissao, mouse_pos)
        
        desenhar_botao(tela, btn_up, "↑ PUXAR", (120, 120, 140), mouse_pos)
        desenhar_botao(tela, btn_down, "↓ DESCER", (120, 120, 140), mouse_pos)
        
        cor_btn_pause = (200, 150, 50) if pausado else (100, 100, 100)
        texto_btn_pause = "RETOMAR SIM." if pausado else "PAUSAR"
        desenhar_botao(tela, btn_pause, texto_btn_pause, cor_btn_pause, mouse_pos)

        desenhar_botao(tela, btn_reset, "REINICIAR", (70, 130, 180), mouse_pos)

        cor_az5 = (220, 50, 50)
        desenhar_botao(tela, btn_az5, "SIMULAR CHERNOBYL", cor_az5, mouse_pos)
    else:
        desenhar_botao(tela, btn_reset_destruido, "🔄 REINICIAR REATOR (R)", (40, 160, 60), mouse_pos)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()