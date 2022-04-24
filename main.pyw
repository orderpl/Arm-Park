import pygame, sys, random
from pygame.math import Vector2

pygame.init()
clock = pygame.time.Clock()

res = (1920, 1080)
screen = pygame.display.set_mode(res)
pygame.display.set_caption("Arm Park 1.4.1")
pygame.mixer.init()

def setpvp():
	global mode, bullets, loser, tick, wait_tick
	mode = 'pvp'
	setPlayers()
	bullets = []
	loser = ''
	tick = 0
	wait_tick = -301

def setmenu():
	global mode, bullets, loser, tick, c
	mode = 'menu'
	bullets = []
	loser = ''
	tick = 0
	c = (0, 0, 0)


def setPlayers():
	global p1, p2
	ammo = 300
	missles = 10
	p1 = Player(res[0]/8, res[1]/2, (160, 255, 160), "green", [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d], [ammo, 0, 0], missles)
	p2 = Player(res[0] - res[0]/8, res[1]/2, (160, 160, 255), "blue", [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT], [ammo, res[0]-30, 0], missles)

def getLoser(players):
	for p in players:
		if p.getshot() != None:
			if p.getshot()[1] == 'green':
				return 'green'
			elif p.getshot()[1] == 'blue':
				return 'blue'

def reset():
	global p1, p2, loser, tick, bullets, wait_tick
	bullets = []
	setPlayers()
	loser = ''
	tick = 0
	wait_tick = -301

def writeText(text, x, y, size, color=(200, 200, 120)):
	font = pygame.font.SysFont("Consolas", size)
	render = font.render(text, True, color)
	screen.blit(render, (x, y))

def getText(text, size, color=(200, 200, 120)):
	font = pygame.font.SysFont("Consolas", size)
	return font.render(text, True, color)

class RectButton(object):
	def __init__(self, action, look, colors, text='', actiont=None):
		self.look = look
		self.text = text
		self.action = action
		self.actiont = actiont
		self.color_n = colors[0]
		self.color_t = colors[1]
		self.color_p = colors[2]

	def getTarget(self):
		if self.look.collidepoint(pygame.mouse.get_pos()):
			return True
		return False

	def getPressed(self):
		if pygame.mouse.get_pressed()[0] and self.getTarget():
			return True
		else:
			return False

	def tick(self):
		self.render()
		if self.getPressed():
			self.action()
		if self.getTarget() and self.actiont != None:

	def render(self):
		if self.getPressed():
			pygame.draw.rect(screen, self.color_p, self.look)
		elif self.getTarget():
			pygame.draw.rect(screen, self.color_t, self.look)
		else:
			pygame.draw.rect(screen, self.color_n, self.look)
		font = pygame.font.SysFont("Calibri", 45)
		render = font.render(self.text, True, (0, 0, 0))
		lcx = self.look.x + self.look.w/2
		lcy = self.look.y + self.look.h/2
		rcx = render.get_rect().w/2
		rcy = render.get_rect().h/2
		screen.blit(render, (lcx-rcx, lcy-rcy))
	

class Bullet(object):
	def __init__(self, x, y, direction, color, team):
		self.direction = direction
		self.team = team
		power = 13
		# 1 = up, 2 = right, 3 = down, 4 = left
		self.position = Vector2(x, y)
		if self.direction == 1:
			self.acc = Vector2(0, -power)
		elif self.direction == 2:
			self.acc = Vector2(power, 0)
		elif self.direction == 3:
			self.acc = Vector2(0, power)
		elif self.direction == 4:
			self.acc = Vector2(-power, 0)
		self.vel = Vector2(0, 0)
		self.size = 5
		self.color = color

	def tick(self):
		self.render()
		self.vel += self.acc
		self.position += self.vel
		self.acc *= 0
		self.vel *= 0.9995

	def render(self):
		self.rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
		pygame.draw.rect(screen, self.color, self.rect)

class Missle(object):
	def __init__(self, x, y, color, team):
		self.position = Vector2(x, y)
		self.vel = Vector2(0, 0)
		self.acc = Vector2(0, 0)
		self.team = team
		self.color = (color[0]+30, color[1]+30, color[2]+30)
		self.size = 10
		self.rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
		self.speed = 0.4
		self.tickno = 0

	def tick(self):
		self.vel += self.acc
		self.position += self.vel
		self.acc *= 0
		self.vel *= 0.975
		self.tickno += 1
		if self.tickno > 180:
			self.speed = 0.005
		self.render()
		self.move()
			

	def move(self):
		global p1, p2
		if p1.team != self.team:
			self.emmypos = p1.position
		if p2.team != self.team:
			self.emmypos = p2.position

		if self.emmypos.x > self.position.x:
			self.addForce(Vector2(self.speed, 0))
		elif self.emmypos.x < self.position.x:
			self.addForce(Vector2(-self.speed, 0))
		else:
			pass

		if self.emmypos.y > self.position.y:
			self.addForce(Vector2(0, self.speed))
		elif self.emmypos.y < self.position.y:
			self.addForce(Vector2(0, -self.speed))
		else:
			pass

	def render(self):
		pygame.draw.rect(screen, self.color, self.rect)
		self.rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)

	def addForce(self, force):
		self.acc += force


class Player(object):
	def __init__(self, x, y, color, team, controls, ammo, missles):
		self.position = Vector2(x, y)
		self.vel = Vector2(0, 0)
		self.acc = Vector2(0, 0)
		self.size = res[0]/48
		self.color = color
		self.speed = 1
		self.shown = True
		self.team = team
		self.controls = controls
		self.missles = missles

		self.ammorectmaxh = 150
		self.ammo = ammo[0]
		self._1ammoh = self.ammorectmaxh / self.ammo
		self.ammorect = pygame.Rect(ammo[1], ammo[2], 30, self.ammo * self._1ammoh)

	def __help__(self):
		print("team is string for team identification")
		print("controls is list of controls")
		print("[up, down, left, right]")

	def hide(self):
		self.shown = False

	def tick(self):
		self.render()
		self.move()
		self.vel += self.acc
		self.position += self.vel
		self.acc *= 0
		self.vel *= 0.90
		
	def render(self):
		if self.shown:
			self.rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
			pygame.draw.rect(screen, self.color, self.rect)
		self.ammorect.h = self.ammo * self._1ammoh
		pygame.draw.rect(screen, self.color, self.ammorect)
		ty = 10
		for l in "AMMO":
			writeText(l, self.ammorect.x+7, ty, 30, (90, 90, 90))
			ty += 30

	def addForce(self, force):
		self.acc += force

	def move(self):
		inputs = pygame.key.get_pressed()
		if inputs[self.controls[0]]:
			self.addForce(Vector2(0, -self.speed))
		if inputs[self.controls[1]]:
			self.addForce(Vector2(0, self.speed))
		if inputs[self.controls[2]]:
			self.addForce(Vector2(-self.speed, 0))
		if inputs[self.controls[3]]:
			self.addForce(Vector2(self.speed, 0))

	def shoot(self):
		if self.ammo > 0 and loser == '':
			x = self.position.x + self.size / 2
			y = self.position.y + self.size / 2
			c = (self.color[0] - 30, self.color[1] - 30, self.color[2] - 30)
			t = self.team

			s = pygame.mixer.Sound('pew.ogg')
			s.play()

			for i in range(4): bullets.append(Bullet(x, y, i+1, c, t))
			self.ammo -= 1

	def missle(self):
		if self.missles > 0 and loser == '':
			x = self.position.x + self.size / 2
			y = self.position.y + self.size / 2
			c = (self.color[0] - 30, self.color[1] - 30, self.color[2] - 30)
			t = self.team

			s = pygame.mixer.Sound('missile.ogg')
			s.play()

			bullets.append(Missle(x, y, c, t))
			self.missles -= 1


	def getshot(self):
		for b in bullets:
			if self.rect.collidepoint(b.position) and b.team != self.team:
				return b.team, self.team


if __name__ == "__main__":
	setmenu()
	btns = []
	qrect = pygame.Rect(res[0]/2-200, res[1]/2+100, 400, 80)
	prect = pygame.Rect(res[0]/2-200, res[1]/2-50, 400, 80)
	btns.append(RectButton(sys.exit, qrect, ((255, 255, 255), (200, 200, 200), (100, 100, 100)), 'QUIT'))
	btns.append(RectButton(setpvp, prect, ((255, 255, 255), (200, 200, 200), (100, 100, 100)), 'PLAY'))

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: sys.exit(0)
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: setmenu()
			if mode == 'pvp': 
				if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: p1.shoot()
				if event.type == pygame.KEYDOWN and event.key == pygame.K_RSHIFT: p2.shoot()
				if event.type == pygame.KEYDOWN and event.key == pygame.K_LALT: p1.missle()
				if event.type == pygame.KEYDOWN and event.key == pygame.K_RCTRL: p2.missle()
		if mode == 'pvp':
			for b in bullets:
				b.tick()

			if getLoser([p1, p2]) == 'green':
				p1.hide()
				if loser == '': pygame.mixer.Sound('explosion.ogg').play()
				if loser == "" or loser == "Blue": loser += "Green"
				wait_tick = tick
				bullets = []
			elif getLoser([p1, p2]) == 'blue':
				p2.hide()
				if loser == '': pygame.mixer.Sound('explosion.ogg').play()
				if loser == "" or loser == "Green": loser += "Blue"
				wait_tick = tick
				bullets = []
			if p1.ammo == 0 and p2.ammo == 0:
				loser = "No one"
				wait_tick = tick
				bullets = []

			if loser != '':
				writeText(loser + " lost!", 50, 30, 40)
			if wait_tick + 300 == tick:
				reset()

			p1.tick()
			p2.tick()
			tick += 1
		elif mode == 'menu':
			for b in btns: b.tick()
			if tick % 10 == 0: 
				c = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
			r = getText("Arm Park", 100, c)
			screen.blit(r, (res[0]/2-r.get_rect().w/2, res[1]/2-250))
			tick += 1

		writeText("Game by 0RD3R | v1.4.1 Python edition", res[0]-520, res[1]-25, 25)
		clock.tick(60)
		pygame.display.update()
		screen.fill((40, 40, 40))