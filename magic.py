import pygame
from settings import *
from boomerang import Boomerang

class MagicPlayer:
	def __init__(self,animation_player):
		self.next_attack = True
		self.animation_player = animation_player
		self.sounds = {
		'heal': pygame.mixer.Sound('./audio/heal.wav'),
		'flame':pygame.mixer.Sound('./audio/Fire.wav')
		}
		self.direction = pygame.math.Vector2(1,0)
		self.offset_x = (self.direction.x * 1) * TILESIZE
		self.offset_y = (self.direction.y * 1) * TILESIZE
	
	def attack(self,index,player,groups,type):
		self.player = player
		self.sounds['flame'].play()
		if player.dir == [2,0]: self.direction = pygame.math.Vector2(1,0) # right
		elif player.dir == [2,1]: self.direction = pygame.math.Vector2(-1,0) # left
		elif player.dir == [0,2]: self.direction = pygame.math.Vector2(0,-1) # up
		elif player.dir == [0,0]: self.direction = pygame.math.Vector2(1,-1) # up right
		elif player.dir == [0,1]: self.direction = pygame.math.Vector2(-1,-1) # up left
		elif player.dir == [1,0]: self.direction = pygame.math.Vector2(1,1) # down right
		elif player.dir == [1,1]: self.direction = pygame.math.Vector2(-1,1) # down left
		elif player.dir == [1,2]: self.direction = pygame.math.Vector2(0,1) # down
		self.offset_x = (self.direction.x * 1) * TILESIZE
		self.offset_y = (self.direction.y * 1) * TILESIZE
		
		x = player.rect.centerx + self.offset_x #+ randint(-TILESIZE // 3, TILESIZE // 3)
		y = player.rect.centery + self.offset_y #+ randint(-TILESIZE // 3, TILESIZE // 3)
		self.boom = Boomerang(x,y,groups,groups[1],self.direction,player,type,index)
   
	def dump_to_network(self):
		return {
			'next_attack': self.next_attack,
			'direction': self.direction,
			'offset_x': self.offset_x,
			'offset_y': self.offset_y,
			'boom': self.boom.dump_to_network() if self.boom else None
		}
	
	def load_from_network(self, data):
		self.next_attack = data['next_attack']
		self.direction = data['direction']
		self.offset_x = data['offset_x']
		self.offset_y = data['offset_y']
		if data['boom'] is not None:
			self.boom = Boomerang(0,0,None,None,None,None,None,None)
		self.boom.load_from_network(data['boom'])
				
