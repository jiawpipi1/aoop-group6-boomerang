import pygame, sys
from settings import *
from level import Level
import argparse
from client import GameClient
import asyncio
import ast

from debug import debug, debug_init

class Game:
	def __init__(self, props=None):
		self.menu = True
		# general setup
		pygame.init()
		# self.screen = pygame.display.set_mode(RESOLUTION)
		# pygame.display.set_caption('Zelda')
		self.screen = pygame.Surface((2048, 1152)) # 32 * 18
		# self.screen = pygame.Surface((1024, 576))

		self.transport = None
		if props is not None:
			self.transport = props['transport']
		self.props = props
		self.online = self.transport is not None
   
		self.resolution = RESOLUTION
		self.window = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN if FULLSCREEN else 0)
		
		self.start_image = pygame.image.load('./graphics/button/start.png').convert_alpha()
		self.start_rect = self.start_image.get_rect(topleft = (600,200))

		self.exit_image = pygame.image.load('./graphics/button/exit.png').convert_alpha()
		self.exit_rect = self.exit_image.get_rect(topleft = (680,800))

		pygame.display.set_caption(TITLE)
		self.clock = pygame.time.Clock()

		self.level = Level(screen=self.screen, props=self.props)

		icon = pygame.image.load('./graphics/monsters/bamboo/attack/0.png')
		pygame.display.set_icon(icon)

		# sound 
		main_sound = pygame.mixer.Sound('./audio/main.ogg')
		main_sound.set_volume(0)
		main_sound.play(loops = -1)

		debug_init(self.screen)

		pygame.display.update()
	
	def get_self_player(self):
		return self.level.player[self.level.index]

	def get_all_player(self):
		return self.level.player
	
	def run_local(self):
		while True:
			while self.menu:
				resized_screen = pygame.transform.scale(self.screen, self.resolution) 
			#while menu:
				self.screen.fill(WATER_COLOR)
			#create button
				self.screen.blit(self.start_image, self.start_rect.topleft)
				self.screen.blit(self.exit_image, self.exit_rect.topleft)
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						pygame.quit()
						sys.exit()
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_m:
							self.level.toggle_menu()
					if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
						if(event.pos[0] >= 500 and event.pos[0] <= 1075 and event.pos[1] >= 190 and event.pos[1] <= 340):
							self.menu = False
						elif(event.pos[0] >= 640 and event.pos[0] <= 830 and event.pos[1] >= 570 and event.pos[1] <= 950):
							pygame.quit()
							sys.exit()
				self.window.blit(resized_screen, (0, 0))
				pygame.display.update()
				self.clock.tick(FPS)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_m:
						self.level.toggle_menu()

			self.screen.fill(WATER_COLOR)
   
			self.level.run()
			# debug(f'{self.resolution}')
			resized_screen = pygame.transform.scale(self.screen, self.resolution) 
			self.window.blit(resized_screen, (0, 0))
			pygame.display.update()
			self.clock.tick(FPS)
   
async def send_player_state(player, transport):
	while True:
		transport.send_status(player.dump_to_network())
		await asyncio.sleep(1 / 60)	

def update_player_state(message, level, players, uuids):
	# print(message)
	message = ast.literal_eval(message)
	if message['action'] == 'status':
		index = uuids.index(message['uuid'])
		if message['event'] == 'update':
			players[index].update_from_network(message)
		elif message['event'] == 'create_attack':
			print('create_attack')
			level.create_attack(index)
		elif message['event'] == 'create_magic':
			print('create_magic')
			level.create_magic(message['style'], message['strength'], index, True)
		elif message['event'] == 'destroy_attack':
			print('destroy_attack')
			level.destroy_attack(index)
  
async def game_client(args):
	props = await GameClient.join_game(args.host, args.port)
	print(props['uuids'])
	game = Game(props)
	game.menu = False
	all_players = game.get_all_player()
	player = game.get_self_player()
	level = game.level
	props['transport'].datagram_received_cb = lambda message: update_player_state(message, level, all_players, props['uuids'])
	
	asyncio.create_task(send_player_state(player, props['transport']))
	
	while True:
		await asyncio.sleep(0.01)  # Add a small sleep to yield to other tasks
		# resized_screen = pygame.transform.scale(game.screen, game.resolution)
		
		for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_m:
						game.level.toggle_menu()

		game.screen.fill(WATER_COLOR)

		game.level.run()
		# debug(f'{game.resolution}')
		resized_screen = pygame.transform.scale(game.screen, game.resolution) 
		game.window.blit(resized_screen, (0, 0))
		pygame.display.update()
		game.clock.tick(FPS)
	
	# 保持伺服器運行
	try:
		await asyncio.Future()
	finally:
		...
		
	# 關閉伺服器
	transport = props['transport']
	transport.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	# parse resolution arguments
	parser.add_argument('--resolution', type=str, default='1280x720')
	parser.add_argument('--fullscreen', type=bool, default=False)
	
	# parse multiplayer arguments
	parser.add_argument('-m', '--multiplayer', action='store_true')
	parser.add_argument('--host', type=str, default='127.0.0.1')
	parser.add_argument('--port', type=int, default=12345)
 
	parser.add_argument('-debug', '--debug', action='store_true')

	args = parser.parse_args()
 
	resolution = tuple(map(int, args.resolution.split('x')))
	fullscreen = args.fullscreen
	# debug = args.debug
	if args.multiplayer:
		print(f'Server IP: {args.host}:{args.port}')
		asyncio.run(game_client(args))
	else:
		game = Game()
		game.run_local()

