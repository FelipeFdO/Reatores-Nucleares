import pygame
import sys
import math
import random

pygame.init()
tela = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Simulador de Fusão Nuclear - Tokamak")
clock = pygame.time.Clock()

fonte_titulo = pygame.font.SysFont("Arial", 18, bold=True)
fonte_texto = pygame.font.SysFont("Arial", 15, bold=True)
fonte_info = pygame.font.SysFont("Arial", 15)
fonte_alerta = pygame.font.SysFont("Arial", 22, bold=True)
fonte_energia = pygame.font.SysFont("Arial", 28, bold=True)

# Variáveis da Física da Fusão
temp_plasma = 30.0 
campo_magnetico = 50.0 
plasma_ativo = False
pausado = False
disrupcao = False 
msg_disrupcao_timer = 0
fluxo_animacao = 0.0
fluxo_condensador = 0.0 # Fluxo fixo independente para o condensador
potencia_eletrica_mw = 0.0
rotacao_eixo = 0.0

# Botões reajustados para comportar os textos com folga (largura de 175 a 185 pixels)
btn_fusao = pygame.Rect(30, 540, 185, 40)
btn_up = pygame.Rect(230, 540, 175, 40)
btn_down = pygame.Rect(420, 540, 175, 40)
btn_pause = pygame.Rect(610, 540, 160, 40)

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

def desenhar_texto_contornado(superficie, texto, fonte, cor_texto, cor_contorno, x, y):
    surf_contorno = fonte.render(texto, True, cor_contorno)
    surf_texto = fonte.render(texto, True, cor_texto)
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
                if btn_fusao.collidepoint(evento.pos): 
                    plasma_ativo = not plasma_ativo
                    if plasma_ativo: disrupcao = False
                elif btn_up.collidepoint(evento.pos): campo_magnetico = min(100, campo_magnetico + 5)
                elif btn_down.collidepoint(evento.pos): campo_magnetico = max(0, campo_magnetico - 5)
                elif btn_pause.collidepoint(evento.pos): pausado = not pausado
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_w: campo_magnetico = min(100, campo_magnetico + 5)
            elif evento.key == pygame.K_s: campo_magnetico = max(0, campo_magnetico - 5)
            elif evento.key == pygame.K_SPACE: 
                plasma_ativo = not plasma_ativo
                if plasma_ativo: disrupcao = False
            elif evento.key == pygame.K_p: pausado = not pausado

    # --- A. CÁLCULO DA FÍSICA DO PLASMA ---
    instabilidade_x, instabilidade_y = 0, 0
    espessura_plasma = 0

    if not pausado:
        if plasma_ativo:
            temp_plasma += 1_500_000 
            temp_plasma = min(temp_plasma, 160_000_000)
        else:
            temp_plasma -= 3_000_000
            temp_plasma = max(30, temp_plasma)
        
        pressao_expansao = (temp_plasma / 2_500_000)
        compressao_mag = (campo_magnetico * 0.8)
        
        espessura_plasma = max(2, pressao_expansao - compressao_mag + 20)

        erro_campo = abs(campo_magnetico - 75)
        if temp_plasma > 50_000_000:
            forca_instabilidade = int((erro_campo / 3) + (temp_plasma / 40_000_000))
            instabilidade_x = random.randint(-forca_instabilidade, forca_instabilidade)
            instabilidade_y = random.randint(-forca_instabilidade, forca_instabilidade)

        if (espessura_plasma / 2) + max(abs(instabilidade_x), abs(instabilidade_y)) > 45 and temp_plasma > 1_000_000:
            plasma_ativo = False
            disrupcao = True
            msg_disrupcao_timer = 90 
            temp_plasma = 30 
            potencia_eletrica_mw = 0
            
        fluxo_animacao += 2 + (temp_plasma / 10_000_000)
        fluxo_condensador += 3 # Fluxo estável unidirecional

        if temp_plasma >= 100_000_000 and not disrupcao:
            energia_termica = (temp_plasma - 100_000_000) / 100_000
            potencia_eletrica_mw = energia_termica * 0.40 
            rotacao_eixo += (temp_plasma / 10_000_000)
        else:
            potencia_eletrica_mw = 0.0
            rotacao_eixo = 0.0
            
    if msg_disrupcao_timer > 0:
        msg_disrupcao_timer -= 1

    # --- B. RENDERIZAÇÃO GRÁFICA ---
    tela.fill((230, 235, 240)) 

    if temp_plasma > 100_000_000:
        cor_plasma = (255, 200, 255) 
    elif temp_plasma > 10_000_000:
        cor_plasma = (255, 50, 200) 
    else:
        cor_plasma = (150, 0, 150) 

    if temp_plasma > 100_000_000:
        cor_fluido = (220, 220, 230) 
    else:
        cor_fluido = (100, 150, 255) 

    # Tubulações (usando fluxo_animacao para o vapor e fluxo_condensador para o retorno estável)
    desenhar_tubo_animado(tela, cor_fluido, (440, 250), (600, 250), fluxo_animacao * 1.5)
    desenhar_tubo_animado(tela, cor_fluido, (635, 310), (635, 340), fluxo_animacao * 1.5)
    desenhar_tubo_animado(tela, (50, 180, 255), (635, 410), (635, 440), fluxo_condensador)
    desenhar_tubo_animado(tela, (50, 180, 255), (635, 440), (440, 440), fluxo_condensador)

    # 1. TOKAMAK
    centro_x, centro_y = 250, 340
    
    pygame.draw.circle(tela, (80, 80, 80), (centro_x, centro_y), 160)
    pygame.draw.circle(tela, (120, 120, 130), (centro_x, centro_y), 150)
    
    pygame.draw.circle(tela, (80, 80, 80), (centro_x, centro_y), 60)
    pygame.draw.circle(tela, (60, 60, 60), (centro_x, centro_y), 50)
    
    for angulo in range(0, 360, 45):
        rad = math.radians(angulo)
        cx = centro_x + math.cos(rad) * 105
        cy = centro_y + math.sin(rad) * 105
        pygame.draw.circle(tela, (200, 100, 30), (int(cx), int(cy)), 12) 
        
    tela.blit(fonte_texto.render("TOKAMAK (Vista Superior)", True, (50, 50, 50)), (160, 510))
    
    if temp_plasma > 1000 and not disrupcao:
        pos_p_x = centro_x + instabilidade_x
        pos_p_y = centro_y + instabilidade_y
        
        pygame.draw.circle(tela, (cor_plasma[0], cor_plasma[1], cor_plasma[2], 100), 
                           (int(pos_p_x), int(pos_p_y)), 105, int(espessura_plasma))
        
        if temp_plasma > 50_000_000:
            pygame.draw.circle(tela, (255, 255, 255), 
                               (int(pos_p_x), int(pos_p_y)), 105, max(1, int(espessura_plasma/3)))

    # 2. Turbina, Gerador e Casas 
    pygame.draw.polygon(tela, (160, 160, 170), [(600, 220), (680, 180), (680, 340), (600, 300)])
    pygame.draw.polygon(tela, (100, 100, 100), [(600, 220), (680, 180), (680, 340), (600, 300)], 3)
    tela.blit(fonte_texto.render("TURBINA", True, (50,50,50)), (605, 155))
    
    pygame.draw.rect(tela, (80, 80, 80), (680, 255, 40, 10))
    pygame.draw.rect(tela, (200, 150, 50), (720, 200, 90, 120), border_radius=10)
    pygame.draw.rect(tela, (120, 90, 30), (720, 200, 90, 120), 4, border_radius=10)
    tela.blit(fonte_texto.render("GERADOR", True, (50,50,50)), (730, 180))
    
    pos_y_rotor = 260 + math.sin(math.radians(rotacao_eixo)) * 40
    pygame.draw.line(tela, (100, 60, 20), (725, int(pos_y_rotor)), (805, int(pos_y_rotor)), 6)

    if potencia_eletrica_mw > 0:
        cor_energia = (255, 215, 0)
        brilho = int(abs(math.sin(math.radians(rotacao_eixo * 2))) * 255)
        pygame.draw.line(tela, (brilho, brilho, 0), (810, 260), (950, 260), 4) 
        pygame.draw.line(tela, (brilho, brilho, 0), (950, 200), (950, 430), 2)
    else:
        cor_energia = (100, 100, 100)
        pygame.draw.line(tela, cor_energia, (810, 260), (950, 260), 4)
        pygame.draw.line(tela, cor_energia, (950, 200), (950, 430), 2)

    desenhar_casa(tela, 930, 170, potencia_eletrica_mw > 1)
    desenhar_casa(tela, 930, 280, potencia_eletrica_mw > 200)
    desenhar_casa(tela, 930, 390, potencia_eletrica_mw > 400)
    tela.blit(fonte_texto.render("CIDADE", True, (50,50,50)), (925, 440))
    
    pygame.draw.rect(tela, (100, 150, 200), (590, 340, 90, 70), border_radius=8)
    tela.blit(fonte_texto.render("CONDENSADOR", True, (50, 50, 50)), (580, 420))

    # --- C. PAINEL DE INFORMAÇÕES (HUD) ---
    pygame.draw.rect(tela, (255, 255, 255), (20, 20, 960, 110), border_radius=10)
    pygame.draw.rect(tela, (180, 180, 180), (20, 20, 960, 110), 2, border_radius=10)

    tela.blit(fonte_titulo.render("1. CÂMARA DE VÁCUO (Tokamak)", True, (150, 50, 180)), (40, 20))
    tela.blit(fonte_info.render(f"Temperatura do Plasma: {temp_plasma:,.0f} °C".replace(",", "."), True, (30, 30, 30)), (40, 45))
    tela.blit(fonte_info.render(f"Combustível: Isótopos Deutério + Trítio", True, (30, 30, 30)), (40, 65))
    estado = "CONFINADO" if plasma_ativo else "DESLIGADO"
    tela.blit(fonte_info.render(f"Estado do Plasma: {estado}", True, (30, 30, 30)), (40, 85))

    tela.blit(fonte_titulo.render("2. ESPECIFICAÇÕES DE CONTROLE", True, (50, 120, 180)), (380, 20))
    tela.blit(fonte_info.render(f"Força Magnética: {campo_magnetico:.0f}%", True, (30, 30, 30)), (380, 45))
    tela.blit(fonte_info.render(f"Desafio: Equilibrar magnetismo e expansão", True, (30, 30, 30)), (380, 65))
    tela.blit(fonte_info.render(f"Meta de Fusão: 150.000.000 °C", True, (30, 30, 30)), (380, 85))
    
    tela.blit(fonte_titulo.render("3. REDE ELÉTRICA", True, (200, 150, 50)), (740, 20))
    tela.blit(fonte_energia.render(f"{potencia_eletrica_mw:.1f} MW", True, cor_energia), (740, 50))
    if potencia_eletrica_mw > 0:
        tela.blit(fonte_info.render(f"Fusão Ocorrendo (Q > 1)!", True, (50, 180, 50)), (740, 85))
    else:
        tela.blit(fonte_info.render(f"Aguardando Temperatura", True, (150, 30, 30)), (740, 85))

    if msg_disrupcao_timer > 0:
        desenhar_texto_contornado(tela, "DISRUPÇÃO! PLASMA TOCOU A PAREDE!", fonte_alerta, (255, 100, 100), (0,0,0), 280, 300)
        desenhar_texto_contornado(tela, "O REATOR RESFRIOU COM SEGURANÇA.", fonte_info, (200, 200, 200), (0,0,0), 320, 340)

    # --- D. DESENHAR BOTÕES ---
    cor_btn_fusao = (200, 80, 180) if plasma_ativo else (80, 180, 200)
    texto_btn_fusao = "PARAR AQUECIMENTO" if plasma_ativo else "INJETAR PLASMA"
    desenhar_botao(tela, btn_fusao, texto_btn_fusao, cor_btn_fusao, mouse_pos)
    
    desenhar_botao(tela, btn_up, "↑ AUMENTAR CAMPO", (120, 120, 140), mouse_pos)
    desenhar_botao(tela, btn_down, "↓ REDUZIR CAMPO", (120, 120, 140), mouse_pos)
    
    cor_btn_pause = (200, 150, 50) if pausado else (100, 100, 100)
    texto_btn_pause = "RETOMAR SIM." if pausado else "PAUSAR SIM."
    desenhar_botao(tela, btn_pause, texto_btn_pause, cor_btn_pause, mouse_pos)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()