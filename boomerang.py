import pygame
from settings import *
from entity import Entity
from support import *
from math import sin

class Boomerang(Entity):
	def __init__(self,x,y,groups,attack_sprites,direc,player,type,index):
		# general setup
		super().__init__(groups)
		self.index = index
		self.time = pygame.time.get_ticks()
		self.player = player
		self.sprite_type = 'projectile'
		self.direc = direc
		self.type = type
		# graphics setup
		if self.type == 'axe':
			self.full_path = f'./graphics/projectiles/axe/1.png'
		else:
			self.full_path = f'./graphics/projectiles/sai/1.png'

		
		self.image = pygame.image.load(self.full_path).convert_alpha()
		self.rect = self.image.get_rect(topleft = (x,y))
		self.hitbox = self.rect.inflate(0,-10)
		self.attack_sprites = attack_sprites
		# stats
		self.speed = 20
		self.attack_damage = 99999999
		self.next_attack = False

		# player interaction
		self.can_attack = True
		self.attack_time = None
		self.attack_cooldown = 400

		# animation
		self.frame_index = 1

		# sounds
		self.hit_sound = pygame.mixer.Sound('./audio/hit.wav')
		self.hit_sound.set_volume(0.6)
	def move(self,x,y):
		self.hitbox.x = self.hitbox.x + x
		self.hitbox.y = self.hitbox.y + y
		self.rect.center = self.hitbox.center
	
	def getspeed(self):
		if self.type == 'axe':
			self.speed = self.speed-0.35
		else:
			if pygame.time.get_ticks() - self.time > 300:
				self.speed = 0
				self.attack_damage = 0
			else:
				self.speed  = 30
	
	def actions(self,speed):
			if((self.direc.x!=0.0 )&(self.direc.y!=0.0)):
				self.direction.x = speed*0.7*self.direc.x
				self.direction.y = speed*0.7*self.direc.y
			else:
				self.direction.x = speed*self.direc.x
				self.direction.y = speed*self.direc.y
	
	def check_death(self):
		if abs(self.rect.centerx-self.player.rect.centerx)<60 and abs(self.rect.centery-self.player.rect.centery)<60 and self.speed <= 0:
			self.player.projectile_cooldown = True
			self.kill()
		elif self.rect.centerx > 1960 or self.rect.centerx < 0 or self.rect.centery >  1060 or self.rect.centery < 0:
			self.player.projectile_cooldown = True
			self.kill()
		elif pygame.time.get_ticks() - self.time > 6000:
			self.player.projectile_cooldown = True
			self.kill()

	def animate(self):
		self.frame_index += self.animation_speed
		if self.frame_index >= 5:
			self.frame_index = 1
		self.full_path = f'./graphics/projectiles/{self.type}/{int(self.frame_index)}.png'
		self.image = pygame.image.load(self.full_path).convert_alpha()

	def update(self):
		self.check_death()
		self.move(self.direction.x,self.direction.y)
		if(self.speed!=0):
			self.animate()

		# dump = self.dump_to_network()
		# print(dump)	

	def boomerang_update(self):
		self.getspeed()
		self.actions(self.speed)
  
	def dump_to_network(self):
		return {
			'index': self.index,
			'x': self.rect.x,
			'y': self.rect.y,
			'frame_index': self.frame_index,
			'speed': self.speed,
			'direction': self.direction,
			'attack_damage': self.attack_damage,
			'attack_cooldown': self.attack_cooldown,
			'attack_time': self.attack_time,
			'can_attack': self.can_attack,
			'next_attack': self.next_attack,
			'sprite_type': self.sprite_type,
			'type': self.type,
			'hitbox': self.hitbox,
			'player': self.player,
			'time': self.time,
			'full_path': self.full_path
		}
	
	def update_from_network(self, data):
		self.index = data['index']
		self.rect.x = data['x']
		self.rect.y = data['y']
		self.frame_index = data['frame_index']
		self.speed = data['speed']
		self.direction = data['direction']
		self.attack_damage = data['attack_damage']
		self.attack_cooldown = data['attack_cooldown']
		self.attack_time = data['attack_time']
		self.can_attack = data['can_attack']
		self.next_attack = data['next_attack']
		self.sprite_type = data['sprite_type']
		self.type = data['type']
		self.hitbox = data['hitbox']
		self.player = data['player']
		self.time = data['time']
		self.full_path = data['full_path']
		# self.image = pygame.image.load(self.full_path).convert_alpha()
		# self.rect = self.image.get_rect(topleft = (self.rect.x,self.rect.y))
		# self.hitbox = self.rect.inflate(0,-10)
		# self.attack_sprites = data['attack_sprites']
		# self.hit_sound = pygame.mixer.Sound('./audio/hit.wav')
		# self.hit_sound.set_volume(0.6)
