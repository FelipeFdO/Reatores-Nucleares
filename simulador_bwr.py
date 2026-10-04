import pygame
import sys
import math

pygame.init()
tela = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Simulador Nuclear BWR - Água Fervente")
clock = pygame.time.Clock()

fonte_titulo = pygame.font.SysFont("Arial", 18, bold=True)
fonte_texto = pygame.font.SysFont("Arial", 15, bold=True)
fonte_info = pygame.font.SysFont("Arial", 15)
fonte_alerta = pygame.font.SysFont("Arial", 22, bold=True)
fonte_energia = pygame.font.SysFont("Arial", 28, bold=True)

# Variáveis da Física do BWR
temp_nucleo = 30.0
insercao_hastes = 80.0
fissao_ativa = False
pausado = False
fluxo_animacao = 0.0
potencia_eletrica_mw = 0.0
rotacao_eixo = 0.0

PONTO_EBULICAO = 285.0 

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
            fator_fissao = (100 - insercao_hastes) * 0.15 
            temp_nucleo += fator_fissao
        
        resfriamento_agua = (temp_nucleo - 40) * 0.012
        temp_nucleo -= resfriamento_agua
        
        temp_nucleo = max(30, min(temp_nucleo, 1200))
        fluxo_animacao += 2 + (temp_nucleo / 150)

        if temp_nucleo >= PONTO_EBULICAO:
            energia_termica_disponivel = (temp_nucleo - PONTO_EBULICAO) * 10.0 
            eficiencia_termica = 0.34 
            potencia_eletrica_mw = energia_termica_disponivel * eficiencia_termica
            velocidade_rotacao = (temp_nucleo - PONTO_EBULICAO) / 8
            rotacao_eixo += velocidade_rotacao
        else:
            potencia_eletrica_mw = 0.0
            rotacao_eixo = 0.0

    tela.fill((230, 235, 240))

    r_nuc = min(255, max(50, int((temp_nucleo - 30) / 700 * 205 + 50)))
    b_nuc = min(255, max(50, int(255 - (temp_nucleo - 30) / 700 * 205)))
    cor_nucleo = (r_nuc, 50, b_nuc)

    if temp_nucleo >= PONTO_EBULICAO:
        cor_fluido_saida = (220, 220, 230) 
    else:
        cor_fluido_saida = (100, 150, 255)

    # Tubulações (Ciclo Único)
    # Saída do Núcleo para a Turbina (Vapor)
    desenhar_tubo_animado(tela, cor_fluido_saida, (320, 240), (600, 240), fluxo_animacao * 1.5)
    
    # NOVO CANO: Da Turbina descendo para o Condensador (Vapor esfriando)
    desenhar_tubo_animado(tela, cor_fluido_saida, (635, 310), (635, 340), fluxo_animacao * 1.5)
    
    # Saída do Condensador (Água líquida fria) para a bomba de retorno
    desenhar_tubo_animado(tela, (50, 180, 255), (635, 410), (635, 440), fluxo_animacao)
    # Retorno para o Núcleo
    desenhar_tubo_animado(tela, (50, 180, 255), (635, 440), (320, 440), fluxo_animacao)

    # 1. Núcleo
    pygame.draw.rect(tela, cor_nucleo, (200, 190, 120, 300), border_radius=25)
    pygame.draw.rect(tela, (80, 80, 80), (200, 190, 120, 300), 4, border_radius=25)
    tela.blit(fonte_texto.render("NÚCLEO DO REATOR", True, (50, 50, 50)), (190, 500))
    
    if temp_nucleo >= PONTO_EBULICAO:
        for i in range(8):
            bx = 210 + (i * 12) 
            by = 470 - ((fluxo_animacao * 3 + i * 40) % 260)
            pygame.draw.circle(tela, (220, 220, 240), (int(bx), int(by)), 5)
    
    altura_haste = (insercao_hastes / 100.0) * 260
    pygame.draw.rect(tela, (50, 50, 50), (225, 190, 10, altura_haste))
    pygame.draw.rect(tela, (50, 50, 50), (255, 190, 10, altura_haste))
    pygame.draw.rect(tela, (50, 50, 50), (285, 190, 10, altura_haste))

    # 2. Estruturas de Geração Mecânica
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
    
    # 4. Condensador
    pygame.draw.rect(tela, (100, 150, 200), (590, 340, 90, 70), border_radius=8)
    tela.blit(fonte_texto.render("CONDENSADOR", True, (50, 50, 50)), (580, 420))

    # --- C. PAINEL DE INFORMAÇÕES (HUD) ---
    pygame.draw.rect(tela, (255, 255, 255), (20, 20, 960, 110), border_radius=10)
    pygame.draw.rect(tela, (180, 180, 180), (20, 20, 960, 110), 2, border_radius=10)

    tela.blit(fonte_titulo.render("1. CIRCUITO ÚNICO (Núcleo BWR)", True, (180, 50, 50)), (40, 20))
    tela.blit(fonte_info.render(f"Temperatura da Água: {temp_nucleo:.1f} °C (Operação normal: ~290°C)", True, (30, 30, 30)), (40, 45))
    
    estado = "ATIVA" if fissao_ativa else "PARADA"
    tela.blit(fonte_info.render(f"Fissão: {estado} (Hastes: {insercao_hastes:.0f}%)", True, (30, 30, 30)), (40, 65))
    
    if temp_nucleo >= PONTO_EBULICAO:
        texto_fase = "FERVENDO (Gerando Vapor no Núcleo)"
        cor_fase = (200, 100, 0)
    else:
        texto_fase = "LÍQUIDO (Aquecendo)"
        cor_fase = (50, 120, 180)
    tela.blit(fonte_info.render(f"Fase: {texto_fase}", True, cor_fase), (40, 85))

    tela.blit(fonte_titulo.render("2. ESPECIFICAÇÕES BWR", True, (50, 120, 180)), (380, 20))
    # ADICIONADO O COMBUSTÍVEL AQUI
    tela.blit(fonte_info.render(f"Combustível: Urânio Enriquecido (U-235)", True, (30, 30, 30)), (380, 45)) 
    tela.blit(fonte_info.render(f"Pressão Operacional: 75 atm (Menor que PWR)", True, (30, 30, 30)), (380, 65))
    tela.blit(fonte_info.render(f"Ebulição Ocorre a: {PONTO_EBULICAO} °C", True, (30, 30, 30)), (380, 85))
    
    tela.blit(fonte_titulo.render("3. REDE ELÉTRICA", True, (200, 150, 50)), (700, 20))
    tela.blit(fonte_energia.render(f"{potencia_eletrica_mw:.1f} MW", True, cor_energia), (700, 50))
    if potencia_eletrica_mw > 0:
        tela.blit(fonte_info.render(f"Eficiência Térmica: 34%", True, (30, 150, 30)), (700, 85))
    else:
        tela.blit(fonte_info.render(f"Sem geração (Aguardando vapor)", True, (150, 30, 30)), (700, 85))

    if temp_nucleo > 800:
        tela.blit(fonte_alerta.render("ALERTA: RISCO DE DERRETIMENTO DO NÚCLEO (MELTDOWN)!", True, (255, 0, 0)), (280, 140))

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