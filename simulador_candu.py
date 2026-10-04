import pygame
import sys
import math

pygame.init()
tela = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Simulador Nuclear CANDU - Água Pesada (D2O)")
clock = pygame.time.Clock()

fonte_titulo = pygame.font.SysFont("Arial", 18, bold=True)
fonte_texto = pygame.font.SysFont("Arial", 15, bold=True)
fonte_info = pygame.font.SysFont("Arial", 15)
fonte_alerta = pygame.font.SysFont("Arial", 22, bold=True)
fonte_energia = pygame.font.SysFont("Arial", 28, bold=True)

# Variáveis da Física Termodinâmica (CANDU)
temp_primaria = 30.0    # Água Pesada
temp_secundaria = 30.0  # Água Leve comum
insercao_hastes = 80.0
fissao_ativa = False
pausado = False
fluxo_animacao = 0.0
potencia_eletrica_mw = 0.0
rotacao_eixo = 0.0

# Rects dos botões interativos
btn_fissao = pygame.Rect(40, 540, 150, 40)
btn_up = pygame.Rect(210, 540, 150, 40)
btn_down = pygame.Rect(380, 540, 150, 40)
btn_pause = pygame.Rect(550, 540, 150, 40)

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

while rodando:
    mouse_pos = pygame.mouse.get_pos()
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
            
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: 
                if btn_fissao.collidepoint(evento.pos):
                    fissao_ativa = not fissao_ativa
                elif btn_up.collidepoint(evento.pos):
                    insercao_hastes = max(0, insercao_hastes - 5)
                elif btn_down.collidepoint(evento.pos):
                    insercao_hastes = min(100, insercao_hastes + 5)
                elif btn_pause.collidepoint(evento.pos):
                    pausado = not pausado

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_w:
                insercao_hastes = max(0, insercao_hastes - 5)
            elif evento.key == pygame.K_s:
                insercao_hastes = min(100, insercao_hastes + 5)
            elif evento.key == pygame.K_SPACE:
                fissao_ativa = not fissao_ativa
            elif evento.key == pygame.K_p:
                pausado = not pausado

    if not pausado:
        if fissao_ativa:
            fator_fissao = (100 - insercao_hastes) * 0.11 
            temp_primaria += fator_fissao
        
        troca_calor = (temp_primaria - temp_secundaria) * 0.015
        temp_primaria -= troca_calor
        temp_primaria -= 0.5 
        
        temp_secundaria += troca_calor
        temp_secundaria -= (temp_secundaria - 30) * 0.01
        
        temp_primaria = max(30, min(temp_primaria, 1200))
        temp_secundaria = max(30, min(temp_secundaria, 400))
        
        pressao_prim = 100.0 + (temp_primaria / 60.0) 
        fluxo_animacao += 2 + (temp_primaria / 150)

        if temp_secundaria > 100:
            energia_termica_disponivel = (temp_secundaria - 100) * 8.5 
            eficiencia_termica = 0.31 
            potencia_eletrica_mw = energia_termica_disponivel * eficiencia_termica
            velocidade_rotacao = (temp_secundaria - 100) / 10
            rotacao_eixo += velocidade_rotacao
        else:
            potencia_eletrica_mw = 0.0
            rotacao_eixo = 0.0

    tela.fill((230, 235, 240))

    # NOVA COR: Água Pesada (Ciano escuro esfriado -> Verde Limão superaquecido)
    r_prim = min(255, max(0, int((temp_primaria - 30) / 700 * 200)))
    g_prim = min(255, max(150, int((temp_primaria - 30) / 700 * 105 + 150)))
    b_prim = min(150, max(0, int(150 - (temp_primaria - 30) / 700 * 150)))
    cor_primaria = (r_prim, g_prim, b_prim) 
    
    cor_particulas_frias = (0, 160, 160) # Ciano para a água pesada de retorno

    if temp_secundaria >= 100:
        cor_secundaria = (220, 220, 230)
    else:
        r_sec = min(255, max(100, int((temp_secundaria - 30) / 70 * 155 + 100)))
        cor_secundaria = (r_sec, 200, 255)

    # Tubulações do Circuito Primário ALINHADAS com os tubos horizontais!
    # Quente: Sai do tubo Y=295
    desenhar_tubo_animado(tela, cor_primaria, (320, 295), (450, 295), fluxo_animacao)
    # Frio: Volta pro tubo Y=415
    desenhar_tubo_animado(tela, cor_particulas_frias, (450, 415), (320, 415), fluxo_animacao)
    
    # Circuito Secundário
    desenhar_tubo_animado(tela, cor_secundaria, (550, 260), (700, 260), fluxo_animacao * 1.5)
    desenhar_tubo_animado(tela, (50, 180, 255), (700, 440), (550, 440), fluxo_animacao)
    desenhar_tubo_animado(tela, cor_secundaria, (720, 350), (720, 420), fluxo_animacao * 1.5)

    # 1. NÚCLEO CANDU (Calandria)
    pygame.draw.rect(tela, cor_primaria, (80, 270, 240, 170), border_radius=15)
    pygame.draw.rect(tela, (80, 80, 80), (80, 270, 240, 170), 4, border_radius=15)
    tela.blit(fonte_texto.render("NÚCLEO CANDU (Calandria)", True, (50, 50, 50)), (95, 450))
    
    # Tubos de Pressão perfeitamente alinhados
    pygame.draw.line(tela, (60, 60, 60), (90, 295), (310, 295), 8) # Alinhado com tubo superior
    pygame.draw.line(tela, (60, 60, 60), (90, 335), (310, 335), 8)
    pygame.draw.line(tela, (60, 60, 60), (90, 375), (310, 375), 8)
    pygame.draw.line(tela, (60, 60, 60), (90, 415), (310, 415), 8) # Alinhado com tubo inferior
    
    # Mecanismo superior das hastes de controle
    pygame.draw.rect(tela, (100, 100, 100), (130, 255, 140, 12), border_radius=4)
    
    # Hastes de Controle descendo entre os tubos de pressão
    altura_haste = (insercao_hastes / 100.0) * 170
    pygame.draw.rect(tela, (40, 40, 40), (145, 267, 10, altura_haste))
    pygame.draw.rect(tela, (40, 40, 40), (195, 267, 10, altura_haste))
    pygame.draw.rect(tela, (40, 40, 40), (245, 267, 10, altura_haste))

    # 2. Gerador de Vapor
    pygame.draw.rect(tela, (130, 140, 150), (450, 190, 100, 280), border_radius=15)
    pygame.draw.rect(tela, cor_secundaria, (460, 200, 80, 260), border_radius=10)
    tela.blit(fonte_texto.render("GERADOR DE", True, (50,50,50)), (455, 480))
    tela.blit(fonte_texto.render("VAPOR", True, (50,50,50)), (475, 495))

    # 3. Turbina e Gerador
    pygame.draw.polygon(tela, (160, 160, 170), [(700, 230), (770, 190), (770, 350), (700, 310)])
    pygame.draw.polygon(tela, (100, 100, 100), [(700, 230), (770, 190), (770, 350), (700, 310)], 3)
    tela.blit(fonte_texto.render("TURBINA", True, (50,50,50)), (705, 170))
    
    pygame.draw.rect(tela, (80, 80, 80), (770, 265, 40, 10))
    
    pygame.draw.rect(tela, (200, 150, 50), (810, 210, 90, 120), border_radius=10)
    pygame.draw.rect(tela, (120, 90, 30), (810, 210, 90, 120), 4, border_radius=10)
    tela.blit(fonte_texto.render("GERADOR", True, (50,50,50)), (820, 190))
    
    pos_y_rotor = 270 + math.sin(math.radians(rotacao_eixo)) * 40
    pygame.draw.line(tela, (100, 60, 20), (815, int(pos_y_rotor)), (895, int(pos_y_rotor)), 6)

    # 4. Transmissão e Casas
    if potencia_eletrica_mw > 0:
        cor_energia = (255, 215, 0)
        brilho = int(abs(math.sin(math.radians(rotacao_eixo * 2))) * 255)
        pygame.draw.line(tela, (brilho, brilho, 0), (900, 270), (950, 270), 4) 
        pygame.draw.line(tela, (brilho, brilho, 0), (950, 200), (950, 430), 2)
    else:
        cor_energia = (100, 100, 100)
        pygame.draw.line(tela, cor_energia, (900, 270), (950, 270), 4)
        pygame.draw.line(tela, cor_energia, (950, 200), (950, 430), 2)

    desenhar_casa(tela, 930, 170, potencia_eletrica_mw > 1)
    desenhar_casa(tela, 930, 280, potencia_eletrica_mw > 250)
    desenhar_casa(tela, 930, 390, potencia_eletrica_mw > 500)
    tela.blit(fonte_texto.render("CIDADE", True, (50,50,50)), (925, 440))
    
    # 5. Condensador
    pygame.draw.rect(tela, (100, 150, 200), (660, 420, 120, 80), border_radius=8)
    tela.blit(fonte_texto.render("CONDENSADOR", True, (50, 50, 50)), (665, 510))

    # --- C. PAINEL DE INFORMAÇÕES (HUD) ---
    pygame.draw.rect(tela, (255, 255, 255), (20, 20, 960, 140), border_radius=10)
    pygame.draw.rect(tela, (180, 180, 180), (20, 20, 960, 140), 2, border_radius=10)

    # HUD CORRIGIDO COM HASTES E D2O
    tela.blit(fonte_titulo.render("1. CIRCUITO PRIMÁRIO (Calandria)", True, (40, 140, 100)), (40, 25))
    tela.blit(fonte_info.render(f"Temperatura da Água: {temp_primaria:.1f} °C", True, (30, 30, 30)), (40, 50))
    tela.blit(fonte_info.render(f"Combustível: Urânio Natural (0.7% U-235)", True, (30, 30, 30)), (40, 70))
    tela.blit(fonte_info.render(f"Moderador: Água Pesada (D2O)", True, (30, 30, 30)), (40, 90)) 
    
    estado = "ATIVA" if fissao_ativa else "PARADA"
    tela.blit(fonte_info.render(f"Fissão: {estado} (Hastes: {insercao_hastes:.0f}%)", True, (30, 30, 30)), (40, 110))

    tela.blit(fonte_titulo.render("2. CIRCUITO SECUNDÁRIO", True, (50, 120, 180)), (380, 25))
    tela.blit(fonte_info.render(f"Temperatura (Água Leve): {temp_secundaria:.1f} °C", True, (30, 30, 30)), (380, 50))
    if temp_secundaria >= 100:
        texto_estado = "VAPOR (Girando a Turbina)" 
        cor_estado = (200, 100, 0)
    else:
        texto_estado = "LÍQUIDO (Absorvendo Calor)"
        cor_estado = (50, 120, 180)
    tela.blit(fonte_info.render(texto_estado, True, cor_estado), (380, 70))
    
    tela.blit(fonte_titulo.render("3. REDE ELÉTRICA", True, (200, 150, 50)), (700, 25))
    tela.blit(fonte_energia.render(f"{potencia_eletrica_mw:.1f} MW", True, cor_energia), (700, 55))
    if potencia_eletrica_mw > 0:
        tela.blit(fonte_info.render(f"Eficiência Térmica: 31%", True, (30, 150, 30)), (700, 95))
    else:
        tela.blit(fonte_info.render(f"Sem geração (Aguardando vapor)", True, (150, 30, 30)), (700, 95))

    if temp_primaria > 800:
        tela.blit(fonte_alerta.render("ALERTA: RISCO DE DERRETIMENTO DO NÚCLEO (MELTDOWN)!", True, (255, 0, 0)), (280, 170))

    # --- D. DESENHAR BOTÕES ---
    cor_btn_fissao = (200, 80, 80) if fissao_ativa else (80, 180, 80)
    texto_btn_fissao = "PARAR FISSÃO" if fissao_ativa else "INICIAR FISSÃO"
    desenhar_botao(tela, btn_fissao, texto_btn_fissao, cor_btn_fissao, mouse_pos)
    
    desenhar_botao(tela, btn_up, "↑ PUXAR HASTES", (120, 120, 140), mouse_pos)
    desenhar_botao(tela, btn_down, "↓ DESCER HASTES", (120, 120, 140), mouse_pos)
    
    cor_btn_pause = (200, 150, 50) if pausado else (100, 100, 100)
    texto_btn_pause = "RETOMAR SIM." if pausado else "PAUSAR SIM."
    desenhar_botao(tela, btn_pause, texto_btn_pause, cor_btn_pause, mouse_pos)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()