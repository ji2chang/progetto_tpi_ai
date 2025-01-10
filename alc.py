import pygame
import cv2
import pose
import time

class Player:
    def __init__(self, life, energy, hp_color, mp_color, x, y):
        self.life = life
        self.energy = energy
        self.hp_color = hp_color
        self.mp_color = mp_color
        self.x = x
        self.y = y
        self.move=''
        self.cooldowns = {
            'atk': 2,       # 2 secondi di cooldown per 'atk'
            'atk_hig': 2,   # 2 secondi di cooldown per 'atk_hig'
            'def': 0.5,       # 1 secondo di cooldown per 'def'
            'def_hig': 0.5    # 1 secondo di cooldown per 'def_hig'
        }
        self.last_move_time = {
            'atk': -99999,
            'atk_hig': -99999,
            'def': -99999,
            'def_hig': -99999
        }
        self.atk_ready = False
        self.loading_start = None

    def draw_cooldown_bars(self, screen):
        font = pygame.font.SysFont(None, 16)
        for idx, move in enumerate(self.cooldowns.keys()):
            bar_width = 100
            bar_height = 20
            bar_x = self.x + 55
            bar_y = self.y + idx * (bar_height + 10) + 400
            text_surface = font.render(move, True, (255, 255, 255))
            screen.blit(text_surface, (bar_x - text_surface.get_width() - 10, bar_y))
            cooldown = self.cooldowns[move]
            last_time = self.last_move_time[move]
            current_time = time.time()
            time_since_last = current_time - last_time
            cooldown_ratio = max(0, min(1, time_since_last / cooldown))
            fill_width = bar_width * cooldown_ratio
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width,
                                                   bar_height))  # Red background
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height)) # Green fill

    def draw_status(self, screen, font):
        pygame.draw.rect(screen, self.hp_color, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, self.mp_color, (self.x, self.y + 30, 150, 20))

        life_text = font.render(f"Vita: {self.life}", True, (255, 255, 255))
        energy_text = font.render(f"Energia: {self.energy}", True, (255, 255, 255))

        screen.blit(life_text, (self.x + 5, self.y))
        screen.blit(energy_text, (self.x + 5, self.y + 30))
        self.draw_cooldown_bars(screen)
        self.draw_loading_bar(screen)

    def can_move(self, move):
        current_time = time.time()
        if current_time - self.last_move_time[move] >= self.cooldowns[move]:
            return True
        return False

    def start_loading(self): 
        self.loading_start = time.time() 
    
    def draw_loading_bar(self, screen): 
        if self.loading_start: 
            elapsed_time = time.time() - self.loading_start 
            loading_fraction = min(elapsed_time / 0.7, 1) 
            bar_width = 200 
            bar_height = 20 
            loading_width = int(bar_width * loading_fraction) 
            pygame.draw.rect(screen, (255, 255, 255), (self.x + (-20 if self.x > 400 else 20) , self.y + 60, bar_width, bar_height), 2) # Contorno
            pygame.draw.rect(screen, (0, 255, 0), (self.x + (-20 if self.x > 400 else 20), self.y + 60, loading_width, bar_height)) # Barra di caricamento
            if loading_fraction >= 1: 
                self.loading_start = None # Fine del caricamento
                self.atk_ready = True

    def move_by_pos(self, img, opponent):
        if self.move == 'wait_atk':
            if self.atk_ready:
                if opponent.move != 'def':
                    opponent.life -= 10  # Riduci la vita dell'avversario di 10
                self.atk_ready = False
                if opponent.life < 0:
                    opponent.life = 0
                self.move = ''
            return
        elif self.move == 'wait_atk_hig':
            if self.atk_ready:
                if opponent.move != 'def_hig':
                    opponent.life -= 15  # Riduci la vita dell'avversario di 10
                self.atk_ready = False
                if opponent.life < 0:
                    opponent.life = 0
                self.move = ''
            return

        move = pose.get_pos_img(img)
        if not move:
            self.move = ''
            return
        if self.can_move(move):
            self.move = move
            org_time = self.last_move_time[move]
            self.last_move_time[move] = time.time()
            if move == 'atk' and self.energy >= 20:
                if self.loading_start is None:
                    self.energy -= 20  # Tolgo la mia energia
                    self.loading_start = time.time()
                    self.move = 'wait_atk'
            elif move == 'atk_hig' and self.energy >= 30:
                if self.loading_start is None:
                    self.energy -= 30  # Tolgo la mia energia
                    self.loading_start = time.time()
                    self.move = 'wait_atk_hig'
            elif move == 'def' and self.energy >= 10:
                self.energy -= 12
            elif move == 'def_hig' and self.energy >= 10:
                self.energy -= 8
            else:
                self.last_move_time[move] = org_time
                self.move = ''

# Inizializza Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Riconoscimento dei Gesti - Gioco")

# Inizializza la videocamera con OpenCV
cap = cv2.VideoCapture(0)

# Crea i giocatori
player1 = Player(100, 100, (0, 255, 0),(0,0,255), 10, 10)
player2 = Player(100, 100, (0, 255, 0),(0,0,255), 640, 10)

font = pygame.font.Font(None, 36)  # Font per il testo
last_time = time.time()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Cattura un frame dalla videocamera
    ret, frame = cap.read()
    if not ret:
        continue

    # Converti l'immagine da BGR a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (800, 600))  # Ridimensiona il frame per adattarlo alla finestra

    # Dividi il frame in due parti
    frame_right = frame_rgb[:, :400]
    frame_left = frame_rgb[:, 400:]

    # Disegna le due superfici sullo schermo
    surf_left = pygame.surfarray.make_surface(frame_left)
    surf_right = pygame.surfarray.make_surface(frame_right)

    # Ruota e capovolgi le superfici per il giusto orientamento
    surf_left = pygame.transform.rotate(surf_left, -90)
    surf_left = pygame.transform.flip(surf_left, False, False)
    surf_right = pygame.transform.rotate(surf_right, -90)
    surf_right = pygame.transform.flip(surf_right, False, False)

    # Disegna le due superfici sullo schermo
    screen.blit(surf_left, (0, 0))
    screen.blit(surf_right, (400, 0))

    # Disegna una linea divisoria
    pygame.draw.line(screen, (0, 0, 0), (400, 0), (400, 600), 5)
    curr_t = time.time()
    if curr_t - last_time >= 2:
        player1.energy = min(player1.energy+5,100)
        player2.energy = min(player2.energy+5,100)
        last_time = curr_t
    # Disegna lo stato di ciascun giocatore
    player1.draw_status(screen, font)  # Giocatore 1
    player2.draw_status(screen, font)  # Giocatore 2
    player1.move_by_pos(frame_left,player2)
    player2.move_by_pos(frame_right,player1)
    if player1.life == 0:
        print('Ha vinto p2')
        break
    elif player2.life == 0:
        print('Ha vinto p1')
        break
    pygame.display.flip()

cap.release()
pygame.quit()
