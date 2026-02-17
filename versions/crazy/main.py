"""
Crazy Mode -- Accelerating chaos mode with shrinking paddles/ball and increasing speed.
Everything gets faster and smaller over time!
"""
import sys
import os
import asyncio
import pygame
import math

# Add the project root to sys.path so "pong" can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import *
from pong.paddle import Paddle
from pong.ball import BallClassic as Ball
from pong.utilities import draw as draw_game, reset, handle_ball_collision
from pong.helpers import handle_paddle_movement
from pong.ai import ai_move_paddle, DIFFICULTY_NAMES
from pong.touch import TouchHandler, draw_touch_buttons, draw_touch_zones
from pong.powerups import PowerUpManager
from pong import audio
from pong.juice import JuiceManager
from pong.game_flow import countdown, PauseMenu, WinScreen, confirm_exit


class CrazyModeManager:
    """Manages the accelerating chaos effects in Crazy Mode."""
    
    def __init__(self):
        self.rally_count = 0  # Number of paddle hits in current rally
        self.total_time = 0  # Total frames elapsed
        self.round_number = 0  # Which round we're on (for increasing win score)
        self.base_ball_speed = BALL_DEFAULT_VEL[0]
        self.base_paddle_speed = PADDLE_DEFAULT_VEL
        self.base_paddle_height = PADDLE_HEIGHT
        self.base_ball_radius = BALL_RADIUS
        
    def update(self, dt=1.0/60.0):
        """Update acceleration over time."""
        self.total_time += dt
        
    def get_ball_speed_multiplier(self):
        """Ball speed increases over time."""
        # Start at 1.0, increase by 0.1 every 10 seconds
        return 1.0 + (self.total_time / 10.0) * 0.1
    
    def get_paddle_speed_multiplier(self):
        """Paddle speed increases over time."""
        # Start at 1.0, increase by 0.15 every 10 seconds
        return 1.0 + (self.total_time / 10.0) * 0.15
    
    def get_size_multiplier(self):
        """Paddles and ball shrink over time."""
        # Start at 1.0, shrink by 0.02 every 10 seconds, minimum 0.3
        shrink_factor = max(0.3, 1.0 - (self.total_time / 10.0) * 0.02)
        return shrink_factor
    
    def get_win_score(self):
        """Win score increases each round: 3, 5, 7, 9..."""
        return 3 + self.round_number * 2
    
    def on_rally_hit(self):
        """Called when ball hits a paddle (increases rally count)."""
        self.rally_count += 1
    
    def on_score(self):
        """Called when someone scores (resets rally)."""
        self.rally_count = 0
    
    def get_screen_shake_intensity(self):
        """Screen shake intensity based on rally count."""
        # More intense shake with longer rallies
        return min(15.0, 3.0 + self.rally_count * 0.5)
    
    def get_trail_length(self):
        """Trail length increases over time."""
        base_trail = 10
        return int(base_trail + self.total_time / 2.0)
    
    def get_color_shift(self):
        """Color shifts toward red over time."""
        # Returns a value 0-1 indicating how much to shift toward red
        return min(1.0, self.total_time / 60.0)  # Full red shift after 60 seconds


async def main(vs_ai=False, settings=None):
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Crazy Pong!")
    clock = pygame.time.Clock()

    # Initialize audio
    audio.init()

    paused = False
    show_instructions = False
    game_started = False

    # Apply settings or use defaults
    p_w = settings.paddle_width if settings else PADDLE_SIZE[0]
    p_h = settings.paddle_height if settings else PADDLE_SIZE[1]
    p_speed = settings.paddle_speed if settings else PADDLE_DEFAULT_VEL
    b_radius = settings.ball_radius if settings else BALL_RADIUS
    b_speed = settings.ball_speed if settings else BALL_DEFAULT_VEL[0]
    l_color = settings.left_paddle_color if settings else LIGHT_PURPLE
    r_color = settings.right_paddle_color if settings else LIGHT_PURPLE
    bg_color = settings.background_color if settings else BLACK

    ai_diff = settings.ai_difficulty if settings else 5

    # Store original values
    orig_p_h = p_h
    orig_b_radius = b_radius
    orig_b_speed = b_speed
    orig_p_speed = p_speed

    # Create paddles and ball with original sizes
    left_paddle = Paddle(ORIGINAL_LEFT_PADDLE_POS[0], ORIGINAL_LEFT_PADDLE_POS[1],
                         p_w, p_h, color=l_color, mode='classic', fixed_vel=p_speed)
    right_paddle = Paddle(ORIGINAL_RIGHT_PADDLE_POS[0], ORIGINAL_RIGHT_PADDLE_POS[1],
                          p_w, p_h, color=r_color, mode='classic', fixed_vel=p_speed)
    ball = Ball(*MIDDLE_BOARD, b_radius, RED, b_speed, 0)  # Start with red color

    touch = TouchHandler(single_player=vs_ai)
    left_score = 0
    right_score = 0

    # Power-ups (always on in crazy mode)
    pu_mgr = PowerUpManager(left_paddle, right_paddle)

    # Juice (visual effects) with higher shake intensity
    juice = JuiceManager(settings)

    # Crazy mode manager
    crazy = CrazyModeManager()

    # Pause menu & win screen
    pause_menu = PauseMenu()
    win_screen = WinScreen()

    # Mode label
    if vs_ai:
        diff_name = DIFFICULTY_NAMES.get(ai_diff, "")
        mode_label = f"MODE: CRAZY vs AI ({diff_name})"
    else:
        mode_label = "MODE: CRAZY"

    def draw_full_scene():
        """Draw the complete game scene."""
        # Calculate dynamic shake intensity
        shake_intensity = crazy.get_screen_shake_intensity()
        sx, sy = juice.shake.get_offset()
        # Amplify shake based on rally
        if crazy.rally_count > 0:
            sx *= (shake_intensity / 3.0)
            sy *= (shake_intensity / 3.0)
        
        # Color shift toward red
        color_shift = crazy.get_color_shift()
        ball_color = (
            int(RED[0] * color_shift + ball.color[0] * (1 - color_shift)),
            int(RED[1] * color_shift + ball.color[1] * (1 - color_shift)),
            int(RED[2] * color_shift + ball.color[2] * (1 - color_shift))
        )
        
        # Temporarily override ball color for drawing
        original_color = ball.color
        ball.color = ball_color
        
        draw_game(WIN, [left_paddle, right_paddle], ball, left_score, right_score, 
                  FONT_LARGE_DIGITAL, bg_color, offset=(sx, sy))
        
        # Restore original color
        ball.color = original_color
        
        if pu_mgr:
            pu_mgr.draw(WIN)
            pu_mgr.draw_extra_balls(WIN)
        
        mode_text = FONT_SMALL_DIGITAL.render(mode_label, True, RED)
        WIN.blit(mode_text, (10, 10))
        
        # Show acceleration stats
        speed_text = FONT_TINY_DIGITAL.render(
            f"Speed: {crazy.get_ball_speed_multiplier():.2f}x | Size: {crazy.get_size_multiplier():.2f}x | Rally: {crazy.rally_count}",
            True, GREY
        )
        WIN.blit(speed_text, (10, 35))
        
        juice.draw(WIN)

    # Initial countdown
    result = await countdown(WIN, draw_full_scene)
    if result == 'quit':
        return
    game_started = True

    while True:
        dt = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            touch.handle_event(event)
            if event.type == pygame.QUIT:
                return

            if paused:
                action = pause_menu.handle_event(event, touch)
                if action == 'resume':
                    paused = False
                elif action == 'restart':
                    crazy = CrazyModeManager()  # Reset crazy mode
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    if pu_mgr: pu_mgr.reset()
                    paused = False
                    result = await countdown(WIN, draw_full_scene)
                    if result == 'quit': return
                elif action == 'menu':
                    return
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    should_exit = await confirm_exit(WIN, draw_full_scene, touch)
                    if should_exit:
                        return
                if event.key == pygame.K_SPACE:
                    paused = True
                if event.key == pygame.K_r:
                    crazy = CrazyModeManager()  # Reset crazy mode
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    if pu_mgr: pu_mgr.reset()
                    result = await countdown(WIN, draw_full_scene)
                    if result == 'quit': return
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions

        # Touch button actions
        if not paused:
            if touch.tapped_menu_btn():
                should_exit = await confirm_exit(WIN, draw_full_scene, touch)
                touch.clear_taps()
                if should_exit:
                    return
            if touch.tapped_pause_btn():
                paused = True

        # Touch pause menu handling
        if paused:
            action = pause_menu.handle_touch(touch)
            if action == 'resume':
                paused = False
            elif action == 'restart':
                crazy = CrazyModeManager()  # Reset crazy mode
                left_score, right_score = reset(ball, left_paddle, right_paddle)
                if pu_mgr: pu_mgr.reset()
                paused = False
                touch.clear_taps()
                result = await countdown(WIN, draw_full_scene)
                if result == 'quit': return
            elif action == 'menu':
                return

        # Update crazy mode
        if not paused:
            crazy.update(dt)
            
            # Apply dynamic size changes
            size_mult = crazy.get_size_multiplier()
            new_p_h = int(orig_p_h * size_mult)
            new_b_radius = max(3, int(orig_b_radius * size_mult))  # Minimum radius of 3
            
            # Update paddle heights (keep width same)
            left_paddle.height = new_p_h
            right_paddle.height = new_p_h
            
            # Update ball radius
            ball.radius = new_b_radius
            
            # Apply dynamic speed changes
            speed_mult = crazy.get_ball_speed_multiplier()
            paddle_speed_mult = crazy.get_paddle_speed_multiplier()
            
            # Update ball speed (preserve direction, scale magnitude)
            ball_speed_mag = math.sqrt(ball.vel[0]**2 + ball.vel[1]**2)
            if ball_speed_mag > 0:
                new_speed = orig_b_speed * speed_mult
                ball.vel[0] = (ball.vel[0] / ball_speed_mag) * new_speed
                ball.vel[1] = (ball.vel[1] / ball_speed_mag) * new_speed
            
            # Update paddle speeds
            left_paddle.fixed_vel = orig_p_speed * paddle_speed_mult
            right_paddle.fixed_vel = orig_p_speed * paddle_speed_mult

        # Update juice effects
        juice.update()

        # Draw scene
        draw_full_scene()

        if paused:
            pause_menu.draw(WIN)

        # Bottom footer instructions
        if show_instructions:
            footer_text = "Press [SPACE] to pause | [R] to restart | [M] to return | [ESC] to quit | [H] to hide"
        else:
            footer_text = "Press [H] for help"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (GAME_MARGIN_X, GAME_FOOTER[1]))

        draw_touch_zones(WIN, touch)
        touch.update_ripples()
        touch.draw_ripples(WIN)
        draw_touch_buttons(WIN, paused)
        pygame.display.update()

        if not paused:
            # Freeze guard: save positions for frozen paddles
            if pu_mgr:
                frozen_l = pu_mgr.is_frozen(left_paddle)
                frozen_r = pu_mgr.is_frozen(right_paddle)
                if frozen_l: saved_l = left_paddle.pos.copy()
                if frozen_r: saved_r = right_paddle.pos.copy()
            else:
                frozen_l = frozen_r = False

            handle_paddle_movement(keys, left_paddle, right_paddle, ai_right=vs_ai, touch=touch)
            if vs_ai:
                ai_move_paddle(right_paddle, ball, difficulty=ai_diff)

            # Enforce freeze: restore position, zero velocity
            if frozen_l:
                left_paddle.pos[:] = saved_l
                left_paddle.vel[:] = 0
            if frozen_r:
                right_paddle.pos[:] = saved_r
                right_paddle.vel[:] = 0

            left_paddle.update()
            right_paddle.update()

            ball.move()

            old_vx = ball.vel[0]
            old_vy = ball.vel[1]
            handle_ball_collision(ball, left_paddle, right_paddle, HEIGHT)

            # Wall bounce detection — check if vy flipped sign
            if old_vy != 0 and (old_vy > 0) != (ball.vel[1] > 0):
                audio.play('wall_bounce')
                wall_y = ball.radius if ball.pos[1] <= HEIGHT // 2 else HEIGHT - ball.radius
                juice.on_wall_bounce(ball.pos[0], wall_y)

            # Detect paddle hit — check if vx flipped sign
            if old_vx < 0 and ball.vel[0] > 0:
                audio.play('paddle_hit')
                crazy.on_rally_hit()  # Increment rally count
                juice.on_paddle_hit(left_paddle.pos[0] + left_paddle.width, ball.pos[1], l_color)
                if pu_mgr: pu_mgr.set_last_hit('left')
            elif old_vx > 0 and ball.vel[0] < 0:
                audio.play('paddle_hit')
                crazy.on_rally_hit()  # Increment rally count
                juice.on_paddle_hit(right_paddle.pos[0], ball.pos[1], r_color)
                if pu_mgr: pu_mgr.set_last_hit('right')

            # Extra balls physics
            if pu_mgr:
                for eb in pu_mgr.extra_balls:
                    eb.move()
                    handle_ball_collision(eb, left_paddle, right_paddle, HEIGHT)
                pu_mgr.update(ball)
                pu_mgr.create_extra_balls(ball, mode='classic')

            # Scoring
            scored = False
            if pu_mgr and (pu_mgr.extra_balls or pu_mgr.main_ball_parked):
                # Multi-ball active
                if not pu_mgr.main_ball_parked:
                    if ball.pos[0] - ball.radius < 0:
                        pu_mgr.park_main_ball(ball, 'left')
                    elif ball.pos[0] + ball.radius > WIDTH:
                        pu_mgr.park_main_ball(ball, 'right')
                pu_mgr.extra_balls = [
                    eb for eb in pu_mgr.extra_balls
                    if -eb.radius <= eb.pos[0] <= WIDTH + eb.radius
                ]
                result = pu_mgr.check_multiball_done()
                if result == 'right_scores':
                    right_score += 1
                    scored = True
                    ball.reset()
                    pu_mgr.reset()
                elif result == 'left_scores':
                    left_score += 1
                    scored = True
                    ball.reset()
                    pu_mgr.reset()
            else:
                # Normal scoring
                if ball.pos[0] - ball.radius < 0:
                    right_score += 1
                    scored = True
                    ball.reset()
                    if pu_mgr: pu_mgr.reset()
                elif ball.pos[0] + ball.radius > WIDTH:
                    left_score += 1
                    scored = True
                    ball.reset()
                    if pu_mgr: pu_mgr.reset()

            if scored:
                audio.play('score')
                # Score pop on the side that scored
                if left_score > right_score or (left_score == right_score and ball.vel[0] > 0):
                    juice.on_score(WIDTH // 4, 20 + 25, str(left_score), FONT_LARGE_DIGITAL, RED)
                else:
                    juice.on_score(WIDTH * 3 // 4, 20 + 25, str(right_score), FONT_LARGE_DIGITAL, RED)
                # Reset rally count on score
                crazy.rally_count = 0

        # Win condition (dynamic based on round)
        win_score = crazy.get_win_score()
        if left_score >= win_score or right_score >= win_score:
            right_name = "AI" if vs_ai else "Right Player"
            winner = "Left Player Won!" if left_score > right_score else f"{right_name} Won!"

            if left_score > right_score:
                audio.play('win')
            else:
                audio.play('lose') if vs_ai else audio.play('win')

            # Interactive win screen — save final scores before potential reset
            final_left, final_right = left_score, right_score
            win_screen.selected = 0
            choosing = True
            while choosing:
                clock.tick(FPS)
                for event in pygame.event.get():
                    touch.handle_event(event)
                    if event.type == pygame.QUIT:
                        return
                    action = win_screen.handle_event(event)
                    if action == 'play_again':
                        crazy.round_number += 1  # Advance to next round
                        crazy.rally_count = 0  # Reset rally
                        left_score, right_score = reset(ball, left_paddle, right_paddle)
                        if pu_mgr: pu_mgr.reset()
                        choosing = False
                    elif action == 'menu':
                        return

                # Touch handling for win screen
                action = win_screen.handle_touch(touch)
                if action == 'play_again':
                    crazy.round_number += 1  # Advance to next round
                    crazy.rally_count = 0  # Reset rally
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    if pu_mgr: pu_mgr.reset()
                    choosing = False
                elif action == 'menu':
                    return

                draw_full_scene()
                win_screen.draw(WIN, winner, final_left, final_right)
                draw_touch_buttons(WIN, False)
                pygame.display.update()
                touch.clear_taps()
                await asyncio.sleep(0)

            # Countdown before next match
            result = await countdown(WIN, draw_full_scene)
            if result == 'quit': return

        touch.clear_taps()
        await asyncio.sleep(0)

if __name__ == '__main__':
    asyncio.run(main())
