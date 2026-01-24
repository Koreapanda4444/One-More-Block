from __future__ import annotations
from typing import Optional
import pygame
from models import GameState

def handle_events(
	state: GameState,
	key_toggle_window_mode: int,
	key_drop: int,
	key_quit: int,
) -> Optional[str]:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			state.running = False
			return None

		if event.type == pygame.KEYDOWN:
			if event.key == key_quit:
				state.running = False
				return None

			if event.key == key_toggle_window_mode:
				return "toggle_window_mode"

			if state.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
				return "restart"

			if (not state.game_over) and event.key == key_drop:
				if state.current and state.current.phase == "move":
					state.current._orig_x = state.current.x
					state.current._orig_w = state.current.w
					state.current.phase = "drop"
				return None

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				if state.game_over:
					return "restart"
				if state.current and state.current.phase == "move":
					state.current._orig_x = state.current.x
					state.current._orig_w = state.current.w
					state.current.phase = "drop"
				return None

	return None

# input_handler.py 내용이 잘못되어 전체 삭제 또는 재작성 필요
