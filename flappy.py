import pygame
from pygame.locals import *
import random
import os
# pygame'e ait genel ve ses icin baslatma fonksiyonlari(Alperen cevik)
pygame.init()
pygame.mixer.init()
# Oyunun kare hizinin ayarlanmasi(Alperen Cevik)
clock = pygame.time.Clock()
fps = 60
#
screen_width = 864
screen_height = 936
#
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird by Alperen,Yagmur, Emre')

# Yazi tiplerinin ve boyutlarinin ayarlanmasi(Alperen Cevik)
font = pygame.font.SysFont('Impact', 60)
text_font = pygame.font.SysFont('Impact', 42)
menu_font = pygame.font.SysFont('Impact', 32)

#define colours
white = (255, 255, 255)
black = (0, 0, 0)
coral = (255, 105, 105)
orange = (255, 105, 30)
gray = (119, 136, 153)

#// oyun degiskenlerini tanimlama(Alperen Cevik)
flying = False
game_over = False
score = 0
death_count = 0
death_count_text = "Death Count:"
score_text = "Score :"
best_text = "Best :"
start_text = "Click Anywhere to Start"
scroll_speed = 4
pipe_gap = 250
pipe_frequency = 1500 #milliseconds
ground_scroll = 0
last_pipe = pygame.time.get_ticks() - pipe_frequency
pass_pipe = False

# En yuksek skorumuzun kaydedilen kayit dosyasindan okunmasi(Alperen Cevik)
savefile = open('saves/data.txt','r')
high_score = int(savefile.read())
savefile.close()

# Ses klasorunu ve icerdigi ses dosyalarini tanimlama(Alperen Cevik)
s = 'sound'

rst_snd = pygame.mixer.Sound(os.path.join(s, 'reset.wav'))
jmp_snd = pygame.mixer.Sound(os.path.join(s, 'jump.wav'))
hscore_snd = pygame.mixer.Sound(os.path.join(s, 'highscore.mp3'))
death_snd = pygame.mixer.Sound(os.path.join(s, 'death.wav'))


#Resimlerin yuklenmesi(Alperen Cevik)
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')
gameover_img = pygame.image.load('img/gameover.png')
high_score_img = pygame.image.load('img/highscore.png')
menu_img = pygame.image.load('img/menu.png')
leftclick = pygame.image.load('img/left2.png')

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))
# Oyunu bastan baslatmak icin gereken sifirlama komutlari(Alperen Cevik)
def reset_game():
	pipe_group.empty()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0
	return score

# Kus sinifinin tanimi, ozelliklerin ve animasyonlarin olusturulmasi(Alperen cevik)
class Bird(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		self.counter = 0
		for num in range (1, 4):
			img = pygame.image.load(f"img/bird{num}.png")
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.vel = 0
		self.clicked = False
	#Eger Kus ucuyorsa vel degerini 0.5 artirarak asagi dusmesini yani yercekimini saglar(Alperen cevik)
	def update(self):

		if flying == True:
			#apply gravity
			self.vel += 0.5
			if self.vel > 8:
				self.vel = 8
			if self.rect.bottom < 768:
				self.rect.y += int(self.vel)

		if game_over == False:
			#jump
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				pygame.mixer.Sound.play(jmp_snd)
				self.vel = -10
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

			#Gorsellerin belirli zaman araliklariyla listeye eklenip cikarilmasiyla animasyonun olusmasi(Alperen cevik)

			flap_cooldown = 5
			self.counter += 1
			
			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
				self.image = self.images[self.index]


			#kusun kafasinin yukari asagi bakmasini saglar(Alperen Cevik)
			self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
		else:
			#eger yandiysak kusun kafasinin yere bakmasini saglar
			self.image = pygame.transform.rotate(self.images[self.index], -90)


# Borularin cok sayida spawn edilmesi icin sinif olarak olusturulmasi ve ayarlari(Alperen Cevik)
class Pipe(pygame.sprite.Sprite):

	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/pipe.png")
		self.rect = self.image.get_rect()
		
		#pozisyon 1 ise boruyu yukaridan -1 ise asagidan spawn eder(Alperen Cevik)
		if position == 1:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
		elif position == -1:
			self.rect.topleft = [x, y + int(pipe_gap / 2)]

	#update konksiyonu ile ekran hizina gore yeni boru eklenir ve gecilenler silinir(Alperen Cevik)
	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill()


# Kullanilacak butonun sinif ayarlari ve ozellikleri(Alperen Cevik)
class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):
		action = False

		#pos degiskeni ile mousenin lokasyonunun atanmasi(Alperen Cevik)
		pos = pygame.mouse.get_pos()

		#Collidepoint fonksiyonu ile mouse butonun uzerinde mi kontrol edilir(Alperen Cevik)
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True

		#Butonu cizdirir(Alperen Cevik)
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action


# Olusturdugumuz siniflar turunden yeni objeler olusturma ozellik verme ve gruplandirma(Alperen Cevik)
pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

## Restart butonunun olusturulmasi(Alperen Cevik)
button = Button(screen_width // 2 - 60, screen_height // 2 - 21, button_img)

# Oyun calisir vaziyette iken calisacak olan sonsuz dongu(Alperen Cevik)

run = True
while run:

	clock.tick(fps)

	#draw background
	screen.blit(bg, (0,0))

	pipe_group.draw(screen)
	bird_group.draw(screen)
	bird_group.update()

	#draw and scroll the ground
	screen.blit(ground_img, (ground_scroll, 768))

	#check the score
	if len(pipe_group) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and pass_pipe == False:
			pass_pipe = True
		if pass_pipe == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				score += 1
				pass_pipe = False
	draw_text(str(score), font, white, int(screen_width / 2), 20)

	draw_text(str(death_count_text), text_font, white, 20, int(screen_height) - 60)
	draw_text(str(death_count), font, coral, 240, int(screen_height) - 75)

	#click here to start
	if pygame.mouse.get_pressed()[0] == 0 and flying == False and game_over == False:
		draw_text(str(start_text), font, white, 150, 300)
		screen.blit(leftclick, ( (screen_width / 2) + 50 , (screen_height / 2) - 80 ))



	#Zorluk ayari()
	if score == 7:
		scroll_speed = 4.5
		pipe_gap = 240
	if score == 17:
		pipe_gap = 230
		pipe_frequency = 1450
	if score == 27:
		scroll_speed = 5
		pipe_gap = 220
		pipe_frequency = 1400
	if score == 37:
		scroll_speed = 5.5
		pipe_gap = 200
		pipe_frequency = 1350
	if score == 47:
		scroll_speed = 6
		pipe_gap = 190
		pipe_frequency = 1200
	if score == 57:
		pipe_gap = 180
		pipe_frequency = 1200
	if score == 67:
		pipe_gap = 170
		pipe_frequency = 1100
	if score == 77:
		scroll_speed = 6.5
		pipe_gap = 170
		pipe_frequency = 1050
	if score == 87:
		scroll_speed = 7
		pipe_gap = 160
		pipe_frequency = 1000
	if score == 97:
		pipe_gap = 150
		pipe_frequency = 1000
	if score == 107:
		pipe_gap = 150
		pipe_frequency = 900
	if score == 117:
		scroll_speed = 7
		pipe_gap = 150
		pipe_frequency = 800
		
	
	#Carpma kontrolunun yapilmasi(Alperen Cevik)
	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
		game_over = True
	#kus yere degdiginde gameover yapan satir(Alperen)
	if flappy.rect.bottom >= 768:
		game_over = True
		flying = False
		if high_score >= score:
			pygame.mixer.Sound.play(death_snd)


	if flying == True and game_over == False:
		#yeni borular olusturan satir(Alperen Cevik)
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-100, 100)
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
			pipe_group.add(btm_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now
	#Update ile guncellenmesini saglar(bu komut olmadigi zaman hareket olmuyor)(Alperen Cevik)
		pipe_group.update()

		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0
	

	# oyunun bitip bitmedigini kontrol eden eger yandiysak menu cikaran (Alperen Cevik)
	# ve degerleri(skoru) hesaplayan ve sonra reset atmamizi saglayan komutlar
	if game_over == True:

		#highest score check
		if high_score >= score:
			screen.blit(gameover_img, ( (screen_width / 2) - (426 / 2) , (screen_height / 2) - 250 ))
		else:
			screen.blit(high_score_img, ( (screen_width / 2) - (679 / 2) , (screen_height / 2) - 250 ))
			pygame.mixer.Sound.play(hscore_snd)
		
		screen.blit(menu_img, ( (screen_width / 2) - 100 , (screen_height / 2) - 50 ))
		draw_text(str(score_text), menu_font, white, (screen_width / 2)-62 , (screen_height / 2)+ 50 )
		draw_text(str(score), menu_font, gray, (screen_width / 2)+34 , (screen_height / 2) + 52)
		draw_text(str(best_text), menu_font, white, (screen_width / 2)-44, (screen_height / 2)+ 115)
		draw_text(str(high_score), menu_font, gray, (screen_width / 2)+34, (screen_height / 2) + 117)

		#reset button click event
		if button.draw():
			death_count += 1
			game_over = False

			pygame.mixer.Sound.play(rst_snd)

			#highest score assignment
			if high_score < score:
				savefile = open('saves/data.txt','r+')
				high_score = score
				savefile.write(str(high_score))
				savefile.close()

			#difficulty reset
			scroll_speed = 4
			pipe_gap = 250
			pipe_frequency = 1500

			score = reset_game()


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
			flying = True

	pygame.display.update()

pygame.quit()

#yuksek skoru ani elektrik kesintisi, hata durumlarinda kayit altina alinmasini saglayan satir(Alperen Cevik)
if high_score < score:
	savefile = open('saves/data.txt','r+')
	high_score = score
	savefile.write(str(high_score))
	savefile.close()
