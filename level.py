import pygame 
from settings import *
from tile import Tile
from player import Player
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from particles import AnimationPlayer
from magic import MagicPlayer

class Level:
	def __init__(self, screen, props):
		self.transport = None
		if props is not None:
			self.transport = props['transport']
			self.index = props['uuids'].index(self.transport.uuid)
			self.player_count = props['player_count']
		self.online = self.transport is not None

		self.local_attack_replay = []

		# self.locations = props['locations']
		self.locations = [(128, 128), (128, 1000), (1000, 128), (1000, 1000)]

		if self.online:
			self.player = [None] * self.player_count
			# get the display surface 
			self.display_surface = screen
			self.game_paused = False

			# sprite group setup
			self.visible_sprites = YSortGroup(screen=screen)
			self.obstacle_sprites = pygame.sprite.Group()

			# attack sprites
			self.current_attack = [None] * self.player_count
			self.attack_sprites = pygame.sprite.Group()
			self.attackable_sprites = pygame.sprite.Group()

			# sprite setup
			self.create_map()

			# user interface 
			self.ui = UI(screen=screen)
			# self.upgrade = Upgrade(self.player, screen)
	
			# particles
			self.animation_player = AnimationPlayer()
			self.magic_player = [MagicPlayer(self.animation_player)] * self.player_count
			self.projectile = [True] * self.player_count

		else:
			self.player = [None,None]
			# get the display surface 
			self.display_surface = screen
			self.game_paused = False

			# sprite group setup
			self.visible_sprites = YSortGroup(screen=screen)
			self.obstacle_sprites = pygame.sprite.Group()

			# attack sprites
			self.current_attack = [None,None]
			self.attack_sprites = pygame.sprite.Group()
			self.attackable_sprites = pygame.sprite.Group()

			# sprite setup
			self.create_map()

			# user interface 
			self.ui = UI(screen=screen)
			# self.upgrade = Upgrade(self.player, screen)
	
			# particles
			self.animation_player = AnimationPlayer()
			self.magic_player = [MagicPlayer(self.animation_player),MagicPlayer(self.animation_player)]
			self.projectile = [True,True]

	def create_map(self):
		layouts = {
			'boundary': import_csv_layout('./map/map_FloorBlocks.csv'),
			'grass': import_csv_layout('./map/map_Grass.csv'),
			'object': import_csv_layout('./map/map_Objects.csv'),
			'entities': import_csv_layout('./map/map_Entities.csv')
		}
		graphics = {
			'grass': import_folder('./graphics/Grass'),
			'objects': import_folder('./graphics/objects')
		}
  
		if self.online:
			for i in range(self.player_count):
				# if i == self.index:
				self.player[i] = Player(
					i,
					self.locations[i],
					[self.visible_sprites,self.attackable_sprites],
					self.obstacle_sprites,
					self.create_attack,
					self.destroy_attack,
					self.create_magic,
					P1_KEY_BINDINGS if i == self.index else None,
					self.transport
					)
				# else:
				# 	self.player[i] = Player(
				# 		i,
				# 		self.locations[i],
				# 		[self.visible_sprites,self.attackable_sprites],
				# 		self.obstacle_sprites,
				# 		self.create_attack,
				# 		self.destroy_attack,
				# 		self.create_magic,
				# 		None,
				# 		self.transport
				# 		)
   
		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x,y),[self.obstacle_sprites],'invisible')
						if style == 'grass':
							random_grass_image = choice(graphics['grass'])
							Tile(
								(x,y),
								[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites],
								'grass',
								random_grass_image)

						if style == 'object':
							surf = graphics['objects'][int(col)]
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)

						if style == 'entities' and (not self.online):
							if col == '394':
								self.player[0] = Player(
									0,
									(128,128),
									# (x,y),
									[self.visible_sprites,self.attackable_sprites],
									self.obstacle_sprites,
									self.create_attack,
									self.destroy_attack,
									self.create_magic,
									P1_KEY_BINDINGS,
									None
									)
							elif col == '395':
								self.player[1] = Player(
									1,
									(1000,1000),
									# (x,y),
									[self.visible_sprites,self.attackable_sprites],
									self.obstacle_sprites,
									self.create_attack,
									self.destroy_attack,
									self.create_magic,
									P2_KEY_BINDINGS,
									None
									)
							#else:
							#	if col == '390': monster_name = 'bamboo'
							#	elif col == '391': monster_name = 'spirit'
							#	elif col == '392': monster_name ='raccoon'
							#	else: monster_name = 'squid'
								
							#	Enemy(
							#		monster_name,
							#		(x,y),
							#		[self.visible_sprites,self.attackable_sprites],
							#		self.obstacle_sprites,
							#		self.damage_player,
							#		self.trigger_death_particles,
									# self.add_exp
         					#		)

	def create_attack(self,index):
		self.current_attack[index] = Weapon(index,self.player[index],[self.visible_sprites,self.attack_sprites])
		print(index)
		if self.online and index == self.index:
			print(index == self.index)
			self.transport.send_status({
				'event': 'create_attack'
			})
			print('sending create_attack')
		print(f'create attack {index}')

	def create_magic(self,style,strength,index,cooldown=True,magic_player=None):
		if cooldown:
			self.player[index].projectile_cooldown = False
			weapon_name = "axe" if style == "flame" else "sai"
			# if magic_player is not None:
			# 	self.magic_player[index].load_from_network(magic_player)
			# 	print(magic_player)	
			self.magic_player[index].attack(index,self.player[index],[self.visible_sprites,self.attack_sprites], weapon_name)
			if self.online and index == self.index:
				data = {
					'event': 'create_magic',
					# 'magic_player': self.magic_player[index].dump_to_network(),
					'style': style,
					'strength': strength,
					'index': index
				}
				self.transport.send_status(data)
				print(data)
			print(f'create magic {index}')

	def destroy_attack(self,index):
		if self.current_attack[index]:
			self.current_attack[index].kill()
		self.current_attack[index] = None
		if self.online and index == self.index:
			self.transport.send_status({
				'event': 'destroy_attack'
			})
		print(f'destroy attack {index}')
  
	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if target_sprite.sprite_type == 'grass':
							pos = target_sprite.rect.center
							offset = pygame.math.Vector2(0,75)
							for leaf in range(randint(3,6)):
								self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
							target_sprite.kill()
						elif target_sprite.sprite_type == 'player':
							player_index, enemy_index = target_sprite.index, attack_sprite.index
							if player_index != enemy_index:
								target_sprite.hurt_time = pygame.time.get_ticks()
								target_sprite.get_damage(self.player[enemy_index],attack_sprite.sprite_type)
							print(f'player {player_index} get damage from player {enemy_index}')

	def damage_player(self,amount,attack_type,index):
		if self.player[index].vulnerable:
			self.player[index].health -= amount
			self.player[index].vulnerable = False
			self.player[index].hurt_time = pygame.time.get_ticks()
			self.animation_player.create_particles(attack_type,self.player[index].rect.center,[self.visible_sprites])

	def trigger_death_particles(self,pos,particle_type):
		self.animation_player.create_particles(particle_type,pos,self.visible_sprites)

	def toggle_menu(self):
		self.game_paused = not self.game_paused 

	def run(self):
		self.visible_sprites.custom_draw()
		if self.online:
			self.ui.display(self.player[self.index])
		else:
			self.ui.display(self.player[0],0)
			self.ui.display(self.player[1],1)

		# debug(f'{self.player[0].rect.centerx}, {self.player[0].rect.centery}, {self.player[0].can_attack}')
		# debug(f'{self.player[1].rect.centerx}, {self.player[1].rect.centery}, {self.player[1].can_attack}')
		
		if self.game_paused:
			# self.upgrade.display()
			...
		else:
			self.visible_sprites.update()
			self.visible_sprites.boomerang_update()
			self.player_attack_logic()
			#self.visible_sprites.enemy_update(self.player[0])
			#self.visible_sprites.enemy_update(self.player[1])
		

class YSortGroup(pygame.sprite.Group):
	def __init__(self, screen):

		# general setup 
		super().__init__()
		self.display_surface = screen
		# self.half_width = self.display_surface.get_size()[0] // 2
		# self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()

		# creating the floor
		#self.floor_surf = pygame.image.load('./graphics/tilemap/ground.png').convert()
		#self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def custom_draw(self):

		# getting the offset 
		#self.offset.x = 0 #player.rect.centerx - self.half_width
		#self.offset.y = 0 #player.rect.centery - self.half_height

		# drawing the floor
		# floor_offset_pos = self.floor_rect.topleft - self.offset
		# self.display_surface.blit(self.floor_surf,floor_offset_pos)


		# for sprite in self.sprites():
		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			#offset_pos = sprite.rect.topleft  - self.offset
			self.display_surface.blit(sprite.image, sprite.rect.topleft)#,offset_pos)
			if sprite.rect.left > 2048:
				continue
			if sprite.rect.top > 1152:
				break

	# def enemy_update(self,player):
	# 	enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
	# 	for enemy in enemy_sprites:
	# 		enemy.enemy_update(player)

	def boomerang_update(self):
		boomerang_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'projectile']
		for boomerang in boomerang_sprites:
			boomerang.boomerang_update()
			# print(boomerang)		
		
