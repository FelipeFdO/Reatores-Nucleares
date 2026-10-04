# ⚛️ Simuladores Didáticos de Reatores Nucleares e Fusão

Projeto voltado para o ensino de **Física Moderna**, **Termodinâmica** e **Engenharia Nuclear**. 
Contém simuladores interativos com respostas térmicas, fluídicas, elétricas e mecanismos de controle em tempo real.

---

## 🚀 Acesse a Versão Web Interativa
Os simuladores podem ser executados diretamente no navegador através do GitHub Pages:
> **[Acessar Simulador Online](https://felipefdo.github.io/Reatores-Nucleares/)**

---

## 🧪 Modelos Incluídos

1. **PWR (Pressurized Water Reactor - Água Pressurizada)**
   * Circuito primário sob alta pressão (~155 atm) para evitar ebulição.
   * Gerador de vapor secundário com eficiência térmica de ~33%.
   * Controle por hastes absorvedoras de nêutrons.

2. **BWR (Boiling Water Reactor - Água Fervente / Ciclo Direto)**
   * Ebulição direta no interior da cuba do reator a ~285°C.
   * Vapor produzido no núcleo alimenta diretamente a turbina a vapor.
   * Hastes de controle inseridas pela base do reator.

3. **CANDU (Canada Deuterium Uranium - Calandria e D₂O)**
   * Utiliza urânio natural não enriquecido (0.7% U-235).
   * Moderação e transporte de calor primário por Água Pesada (Óxido de Deutério - $\text{D}_2\text{O}$).
   * Tubos de pressão horizontais e circuito secundário de água leve.

4. **RBMK (Reator Moderado a Grafite / Chernobyl)**
   * Coeficiente de vazio positivo característico dos reatores RBMK-1000 soviéticos.
   * Simulação do pico de reatividade induzido pelo botão de emergência **AZ-5** (pontas de grafite).
   * Efeitos de instabilidade térmica e explosão do núcleo com opção de reinício didático.

5. **Tokamak (Fusão Nuclear por Confinamento Magnético)**
   * Confinamento toroidal de plasma de Deutério-Trítio em temperaturas de dezenas de milhões de °C.
   * Controle da estabilidade do plasma pelo campo magnético das bobinas.
   * Simulação de disrupção de plasma (perda de confinamento com resfriamento de segurança).

---

## ⌨️ Controles
* **Espaço:** Iniciar / Parar a Fissão ou Injeção de Plasma.
* **W:** Puxar hastes de controle / Aumentar intensidade do campo magnético.
* **S:** Descer hastes de controle / Reduzir intensidade do campo magnético.
* **P:** Pausar / Retomar a simulação.
* **R:** Reiniciar o reator.
* **Clique do Mouse:** Todos os botões na tela são totalmente interativos.

---

## 🐍 Execução Local via Python (Pygame)
Caso prefira rodar os simuladores em janela nativa Python:
```bash
pip install pygame
python simulador_pwr.py
python simulador_bwr.py
python simulador_candu.py
python simulador_rbmk.py
python simulador_tokamak.py
```
