import pygame 
from settings import *
from support import import_folder
from entity import Entity

class Player(Entity):
	def __init__(self,index,pos,groups,obstacle_sprites,create_attack,destroy_attack,create_magic,keybinds,transport):
		super().__init__(groups)
		self.sprite_type = 'player'
		self.death_sound = pygame.mixer.Sound('./audio/death.wav')
		self.hit_sound = pygame.mixer.Sound('./audio/hit.wav')
		self.index = index
		
		self.transport = transport
		self.keybinds = keybinds
   
		self.image = pygame.image.load('./graphics/test/player.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-6,HITBOX_OFFSET['player'])
		self.groups = groups
		# graphics setup
		self.import_player_assets()
		self.status = 'down'
		self.dir = [2,2]

		# movement 
		self.attacking = False
		self.attack_cooldown = 100
		self.attack_time = None
		self.obstacle_sprites = obstacle_sprites

		self.attack_interval = 500
		self.can_attack_time = None
		self.can_attack = True
  
		# weapon
		self.create_attack = create_attack
		self.destroy_attack = destroy_attack
		self.weapon_index = 0
		self.weapon = list(weapon_data.keys())[self.weapon_index]
		self.can_switch_weapon = True
		self.weapon_switch_time = None
		self.switch_duration_cooldown = 200

		# magic 
		self.create_magic = create_magic
		self.magic_index = 0
		self.magic = list(magic_data.keys())[self.magic_index]
		self.can_switch_magic = True
		self.magic_switch_time = None

		# stats
		self.stats = {'health': 100,'energy':60,'attack': 10,'magic': 4,'speed': 5}
		# self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic' : 10, 'speed': 10}
		# self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic' : 100, 'speed': 100}
		self.health = self.stats['health'] * 0.5
		self.energy = self.stats['energy'] * 0.8
		# self.exp = 5000
		self.speed = self.stats['speed']
		self.projectile_cooldown = True
		# damage timer
		self.vulnerable = True
		self.hurt_time = None
		self.invulnerability_duration = 500

		# import a sound
		self.weapon_attack_sound = pygame.mixer.Sound('./audio/sword.wav')
		self.weapon_attack_sound.set_volume(0.4)

	def import_player_assets(self):
		character_path = './graphics/player/'
		self.animations = {'up': [],'down': [],'left': [],'right': [],
			'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
			'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)

	def input(self):
		if not self.attacking:
			keys = pygame.key.get_pressed()

			# movement input
			if keys[self.keybinds['up']]:
				self.direction.y = -1
				self.status = 'up'
				self.dir[0] = 0
				
			elif keys[self.keybinds['down']]:
				self.direction.y = 1
				self.status = 'down'
				self.dir[0] = 1
			else:
				self.direction.y = 0
				self.dir[0] = 2
			

			if keys[self.keybinds['right']]:
				self.direction.x = 1
				self.status = 'right'
				self.dir[1] = 0
			elif keys[self.keybinds['left']]:
				self.direction.x = -1
				self.status = 'left'
				self.dir[1] = 1
			else:
				self.direction.x = 0
				self.dir[1] = 2
    
			if keys[self.keybinds['run']]:
				self.stats['speed'] = self.speed * 1.5
				if self.can_attack:
					self.can_attack_time = pygame.time.get_ticks()
					self.can_attack = False
			else:
				self.stats['speed'] = self.speed

			# attack input 
			if keys[self.keybinds['attack']] and self.can_attack:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				self.create_attack(self.index)
				self.weapon_attack_sound.play()
				
				self.can_attack = False
				self.can_attack_time = pygame.time.get_ticks()

			# projectile input 
			if keys[self.keybinds['projectile']] and self.can_attack:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				style = list(magic_data.keys())[self.magic_index]
				strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
				cost = list(magic_data.values())[self.magic_index]['cost']
				self.create_magic(style,strength,self.index,self.projectile_cooldown)
				self.can_attack = False
				self.can_attack_time = pygame.time.get_ticks()
        

			if keys[self.keybinds['switch_weapon']] and self.can_switch_weapon:
				self.can_switch_weapon = False
				self.weapon_switch_time = pygame.time.get_ticks()
				
				if self.weapon_index < len(list(weapon_data.keys())) - 1:
					self.weapon_index += 1
				else:
					self.weapon_index = 0
					
				self.weapon = list(weapon_data.keys())[self.weapon_index]

			if keys[self.keybinds['switch_projectile']] and self.can_switch_magic:
				self.can_switch_magic = False
				self.magic_switch_time = pygame.time.get_ticks()
				
				if self.magic_index < len(list(magic_data.keys())) - 1:
					self.magic_index += 1
				else:
					self.magic_index = 0

				self.magic = list(magic_data.keys())[self.magic_index]
				
	def get_damage(self,player,attack_type):
		if self.vulnerable:
			if attack_type == 'weapon':
				self.health -= player.get_full_weapon_damage()
				self.hit_sound.play()
				self.vulnerable = False
			else:
				if player.get_projectile_damage() != 0:
					self.health -= player.get_projectile_damage()
					self.vulnerable = False
					self.hit_sound.play()
			self.hit_time = pygame.time.get_ticks()

	def get_status(self):

		# idle status
		if self.direction.x == 0 and self.direction.y == 0:
			if not 'idle' in self.status and not 'attack' in self.status:
				self.status = self.status + '_idle'

		if self.attacking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle','_attack')
				else:
					self.status = self.status + '_attack'
		else:
			if 'attack' in self.status:
				self.status = self.status.replace('_attack','')

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
  
		if not self.can_attack:
			if current_time - self.can_attack_time >= self.attack_interval:
				self.can_attack = True

		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
				self.attacking = False
				self.destroy_attack(self.index)

		if not self.can_switch_weapon:
			if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
				self.can_switch_weapon = True

		if not self.can_switch_magic:
			if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
				self.can_switch_magic = True

		if not self.vulnerable:
			if current_time - self.hurt_time >= self.invulnerability_duration:
				self.vulnerable = True

	def animate(self):
		animation = self.animations[self.status]

		# loop over the frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# set the image
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)

		# flicker 
		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def get_full_weapon_damage(self):
		base_damage = self.stats['attack']
		weapon_damage = weapon_data[self.weapon]['damage']
		return base_damage + weapon_damage

	def get_full_magic_damage(self):
		base_damage = self.stats['magic']
		spell_damage = magic_data[self.magic]['strength']
		return base_damage + spell_damage
	
	def get_projectile_damage(self):
		if self.magic == 'flame':
			return 999999
		else:
			if pygame.time.get_ticks() - self.attack_time > 300:
				return 0
			else:
				return 999999

	def get_value_by_index(self,index):
		return list(self.stats.values())[index]

	# def get_cost_by_index(self,index):
	# 	return list(self.upgrade_cost.values())[index]

	def energy_recovery(self):
		if self.energy < self.stats['energy']:
			self.energy += 0.01 * self.stats['magic']
		else:
			self.energy = self.stats['energy']

	def update(self):
		if self.keybinds:
			self.input()
			self.cooldowns()
			self.get_status()
			self.move(self.stats['speed'])
			self.energy_recovery()
			self.animate()
			# if self.transport is not None:
			# 	print(self.dump_to_network())
			# 	self.transport.send_status(self.dump_to_network())	
	
		# print(self.dump_to_network())
  
	def dump_to_network(self):
		return {
				'event': 'update',
				# 'hitbox': self.hitbox,
      			'x': self.rect.x,
				'y': self.rect.y,
				'dir': self.dir,
				'vulnerable': self.vulnerable,
				'direction_x': self.direction.x,
				'direction_y': self.direction.y,
				'status': self.status,
				'health': self.health,
				'energy': self.energy,
				'weapon': self.weapon,
				'magic': self.magic,
				# 'speed': self.stats['speed'],
				# 'attack': self.stats['attack'],
				# 'magic': self.stats['magic'],
				# 'health': self.stats['health'],
				# 'energy': self.stats['energy']
		}
  
	def update_from_network(self, player_data):
		self.animate()
		# self.hitbox = player_data['hitbox']
		self.rect.x = player_data['x']
		self.rect.y = player_data['y']
		self.dir = player_data['dir']	
		self.vulnerable = player_data['vulnerable']
		self.direction.x = player_data['direction_x']
		self.direction.y = player_data['direction_y']
		self.status = player_data['status']
		self.health = player_data['health']
		self.energy = player_data['energy']
		self.weapon = player_data['weapon']
		self.magic = player_data['magic']
  
		# self.stats['speed'] = player_data['speed']
		# self.stats['attack'] = player_data['attack']
		# self.stats['magic'] = player_data['magic']
		# self.stats['health'] = player_data['health']
		# self.stats['energy'] = player_data['energy']
		