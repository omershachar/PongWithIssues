"""
cursed_combat.py -- Sword-fighting combat system for Cursed Mode.

Features:
- Ball grab: catch a slow ball, carry it, then launch it at insane speed
- Paddle grab: grab the enemy paddle and throw it across the board
- Directional sword: controlled by movement keys, swings where you point
- Sword has physics mass — fast swings deal damage and deflect the ball
- 3-hit health system with visual damage states
- Permanent death (paddle stays dead until game restart)
- Little hands on paddle holding the sword
- Blood particle system with dripping, splattering, pooling
- Paddle-to-paddle collision (ramming)
"""

import math
import random
import time
import pygame
import numpy as np
from pong.constants import *


# ---- Blood colors ----
BLOOD_RED = (180, 0, 0)
BLOOD_DARK = (100, 0, 0)
BLOOD_BRIGHT = (220, 20, 20)
BLOOD_DRIP = (140, 0, 0)

# ---- Skin color for hands ----
SKIN_COLOR = (255, 220, 185)
SKIN_SHADOW = (220, 185, 150)

# ---- Sword constants ----
SWORD_LENGTH = 100  # longer reach for combat
SWORD_WIDTH = 4
SWORD_MASS = 3.0  # mass for momentum calculation
MIN_DAMAGE_ANGULAR_VEL = 3.0  # radians/sec minimum to deal damage
SWORD_LERP_SPEED = 0.25  # how fast sword tracks input direction
BALL_SWORD_IMPULSE = 12.0  # impulse applied to ball on sword hit
MAX_HEALTH = 3


# -----------------------------------------------------------------------
# Blood Particle System
# -----------------------------------------------------------------------

class BloodParticle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'max_life',
                 'size', 'splat', 'splat_size')

    def __init__(self, x, y, vx, vy, color, life, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.splat = False
        self.splat_size = 0


class BloodSystem:
    """Gore particle system. Blood droplets fly, drip, and splat on surfaces."""

    MAX_PARTICLES = 500
    GRAVITY = 200  # heavier than normal particles

    def __init__(self):
        self._particles = []
        self._splats = []  # permanent blood pools on surfaces
        self._last_time = time.monotonic()

    def emit_slash(self, x, y, direction_x, count=40):
        """Emit blood from a sword slash. direction_x: 1 or -1."""
        colors = [BLOOD_RED, BLOOD_DARK, BLOOD_BRIGHT, BLOOD_DRIP,
                  (200, 0, 0), (160, 10, 10)]
        for _ in range(count):
            angle = random.uniform(-1.2, 1.2)
            spd = random.uniform(80, 350)
            vx = math.cos(angle) * spd * direction_x
            vy = math.sin(angle) * spd - random.uniform(50, 200)
            color = random.choice(colors)
            life = random.uniform(0.8, 2.5)
            size = random.randint(2, 6)
            self._particles.append(
                BloodParticle(x, y, vx, vy, color, life, size))

    def emit_drip(self, x, y, count=5):
        """Continuous drip from a bleeding paddle."""
        for _ in range(count):
            vx = random.uniform(-15, 15)
            vy = random.uniform(20, 80)
            color = random.choice([BLOOD_RED, BLOOD_DARK, BLOOD_DRIP])
            life = random.uniform(1.0, 3.0)
            size = random.randint(1, 3)
            self._particles.append(
                BloodParticle(x + random.uniform(-5, 5), y, vx, vy,
                              color, life, size))

    def emit_impact(self, x, y, count=20):
        """Blood burst from a high-speed paddle ram."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(40, 200)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            color = random.choice([BLOOD_RED, BLOOD_BRIGHT, (200, 30, 30)])
            life = random.uniform(0.5, 1.5)
            size = random.randint(2, 5)
            self._particles.append(
                BloodParticle(x, y, vx, vy, color, life, size))

    def emit_hit(self, x, y, count=15):
        """Medium blood burst for a sword hit (not kill)."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(30, 150)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd - random.uniform(20, 80)
            color = random.choice([BLOOD_RED, BLOOD_DARK, BLOOD_BRIGHT])
            life = random.uniform(0.5, 1.8)
            size = random.randint(1, 4)
            self._particles.append(
                BloodParticle(x, y, vx, vy, color, life, size))

    def update(self):
        now = time.monotonic()
        dt = now - self._last_time
        self._last_time = now
        if dt <= 0:
            return

        grav = self.GRAVITY * dt
        alive = []
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                # Convert to permanent splat
                if p.y >= HEIGHT - 20 and not p.splat:
                    self._splats.append(
                        (int(p.x), int(p.y), p.color, random.randint(2, 5)))
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += grav

            # Floor collision — splat and slow
            if p.y >= HEIGHT - 5:
                p.y = HEIGHT - 5
                p.vy = -abs(p.vy) * 0.2
                p.vx *= 0.5
                if not p.splat:
                    p.splat = True
                    p.splat_size = random.randint(3, 7)
                    self._splats.append(
                        (int(p.x), int(p.y), p.color, p.splat_size))

            alive.append(p)

        # Budget
        overflow = len(alive) - self.MAX_PARTICLES
        if overflow > 0:
            del alive[:overflow]
        self._particles = alive

        # Limit permanent splats
        if len(self._splats) > 300:
            self._splats = self._splats[-200:]

    def draw(self, surface):
        # Draw permanent blood pools first (underneath)
        for sx, sy, color, size in self._splats:
            pygame.draw.circle(surface, color, (sx, sy), size)

        # Draw active blood particles
        for p in self._particles:
            ratio = max(p.life / p.max_life, 0.0)
            cur_size = max(int(p.size * ratio), 1)
            # Elongate fast-moving particles (blood streaks)
            speed = math.sqrt(p.vx * p.vx + p.vy * p.vy)
            if speed > 100 and cur_size >= 2:
                dx = p.vx / speed * cur_size * 2
                dy = p.vy / speed * cur_size * 2
                pygame.draw.line(surface, p.color,
                                 (int(p.x - dx), int(p.y - dy)),
                                 (int(p.x + dx), int(p.y + dy)),
                                 max(cur_size - 1, 1))
            else:
                pygame.draw.circle(surface, p.color,
                                   (int(p.x), int(p.y)), cur_size)

    def reset(self):
        self._particles.clear()
        self._splats.clear()


# -----------------------------------------------------------------------
# Sword (directional, physics-based)
# -----------------------------------------------------------------------

class Sword:
    """A sword attached to a paddle. Controlled by movement keys direction."""

    def __init__(self, is_left):
        self.is_left = is_left
        self.angle = 0.0  # current sword angle in radians relative to base
        self.prev_angle = 0.0  # previous frame angle for angular velocity
        self.angular_velocity = 0.0  # rad/s for damage calculation
        self.visible = False  # only visible when player presses movement keys
        self._target_angle = 0.0
        self._hit_cooldown = 0.0  # brief per-hit cooldown to avoid double hits

    def _base_angle(self):
        """Left paddle sword points RIGHT (0), right paddle points LEFT (pi)."""
        return 0.0 if self.is_left else math.pi

    def set_direction(self, dx, dy):
        """Set sword direction from input vector. (0,0) = sheathe."""
        if abs(dx) < 0.01 and abs(dy) < 0.01:
            self.visible = False
            return
        self.visible = True
        # Target angle relative to base
        input_angle = math.atan2(dy, dx)
        # For right paddle, mirror the input
        if not self.is_left:
            input_angle = math.pi - input_angle
        self._target_angle = input_angle

    def update(self, dt=1/60):
        """Update sword angle with smooth lerp toward target."""
        self._hit_cooldown = max(0, self._hit_cooldown - dt)
        self.prev_angle = self.angle

        if not self.visible:
            # Lerp back to neutral when hidden
            self.angle += (0 - self.angle) * 0.2
            self.angular_velocity = 0
            return

        # Smooth rotation toward target
        diff = self._target_angle - self.angle
        # Normalize angle difference to [-pi, pi]
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi

        self.angle += diff * SWORD_LERP_SPEED
        self.angular_velocity = (self.angle - self.prev_angle) / dt

    def get_tip_pos(self, paddle):
        """Get sword tip world position."""
        cx = paddle.pos[0] + paddle.width / 2
        cy = paddle.pos[1] + paddle.height / 2
        final_angle = self._base_angle() + self.angle
        tip_x = cx + math.cos(final_angle) * SWORD_LENGTH
        tip_y = cy + math.sin(final_angle) * SWORD_LENGTH
        return tip_x, tip_y

    def get_hitbox(self, paddle):
        """Get sword line segment for collision detection."""
        cx = paddle.pos[0] + paddle.width / 2
        cy = paddle.pos[1] + paddle.height / 2
        final_angle = self._base_angle() + self.angle
        tip_x = cx + math.cos(final_angle) * SWORD_LENGTH
        tip_y = cy + math.sin(final_angle) * SWORD_LENGTH
        return (cx, cy), (tip_x, tip_y)

    def can_hit(self):
        """Whether this sword can deal damage right now."""
        return (self.visible and
                abs(self.angular_velocity) > MIN_DAMAGE_ANGULAR_VEL and
                self._hit_cooldown <= 0)

    def register_hit(self):
        """Mark that a hit just happened (brief cooldown)."""
        self._hit_cooldown = 0.25  # 250ms between hits

    def draw(self, surface, paddle):
        if not self.visible:
            return

        cx = int(paddle.pos[0] + paddle.width / 2)
        cy = int(paddle.pos[1] + paddle.height / 2)
        final_angle = self._base_angle() + self.angle

        tip_x = cx + math.cos(final_angle) * SWORD_LENGTH
        tip_y = cy + math.sin(final_angle) * SWORD_LENGTH

        # Blade color varies with swing speed
        speed_ratio = min(abs(self.angular_velocity) / 10.0, 1.0)
        r = int(255 * (1 - speed_ratio * 0.3))
        g = int(255 * (1 - speed_ratio * 0.5))
        b = int(255 * (1 - speed_ratio * 0.2))
        blade_color = (r, g, b)

        # Blade
        pygame.draw.line(surface, blade_color,
                         (cx, cy), (int(tip_x), int(tip_y)),
                         SWORD_WIDTH)

        # Shiny edge (last 30% of blade)
        edge_start = 0.7
        edge_x1 = cx + math.cos(final_angle) * (SWORD_LENGTH * edge_start)
        edge_y1 = cy + math.sin(final_angle) * (SWORD_LENGTH * edge_start)
        pygame.draw.line(surface, (200, 200, 255),
                         (int(edge_x1), int(edge_y1)),
                         (int(tip_x), int(tip_y)), 2)

        # Guard (small cross at base)
        perp_angle = final_angle + math.pi / 2
        g1x = cx + math.cos(perp_angle) * 8
        g1y = cy + math.sin(perp_angle) * 8
        g2x = cx - math.cos(perp_angle) * 8
        g2y = cy - math.sin(perp_angle) * 8
        pygame.draw.line(surface, GREY, (int(g1x), int(g1y)),
                         (int(g2x), int(g2y)), 3)

    def draw_hands(self, surface, paddle):
        """Draw little hands on the paddle holding the sword."""
        cx = paddle.pos[0] + paddle.width / 2
        cy = paddle.pos[1] + paddle.height / 2
        final_angle = self._base_angle() + self.angle

        # Hand positions: two hands near the guard, offset perpendicular
        perp = final_angle + math.pi / 2
        hand_dist = 5  # distance along blade from center
        hand_spread = 6  # perpendicular spread

        for sign in (-1, 1):
            hx = cx + math.cos(final_angle) * hand_dist + math.cos(perp) * hand_spread * sign
            hy = cy + math.sin(final_angle) * hand_dist + math.sin(perp) * hand_spread * sign
            # Shadow
            pygame.draw.circle(surface, SKIN_SHADOW, (int(hx) + 1, int(hy) + 1), 5)
            # Hand
            pygame.draw.circle(surface, SKIN_COLOR, (int(hx), int(hy)), 4)

        # When sword is sheathed, draw hands at paddle sides instead
        if not self.visible:
            side_x = paddle.pos[0] + (paddle.width + 3 if self.is_left else -3)
            for offset_y in (-10, 10):
                hy = cy + offset_y
                pygame.draw.circle(surface, SKIN_SHADOW, (int(side_x) + 1, int(hy) + 1), 5)
                pygame.draw.circle(surface, SKIN_COLOR, (int(side_x), int(hy)), 4)


# -----------------------------------------------------------------------
# CursedCombatManager
# -----------------------------------------------------------------------

class CursedCombatManager:
    """
    Manages all insane cursed mode combat mechanics:
    - Ball grab & launch
    - Paddle grab & throw
    - Directional sword combat with momentum-based damage
    - 3-hit health system with visual damage
    - Permanent paddle death
    - Sword-ball interaction
    - Paddle ramming
    """

    GRAB_SPEED_THRESHOLD = 12.0  # Ball must be slower than this to grab
    GRAB_RANGE = 50.0
    LAUNCH_SPEED_MULT = 2.5  # Launch speed = paddle speed * this
    PADDLE_GRAB_RANGE = 50.0
    THROW_SPEED = 15.0
    RAM_DAMAGE_THRESHOLD = 4.0  # Min paddle speed for ram damage

    def __init__(self):
        self.blood = BloodSystem()
        self.left_sword = Sword(is_left=True)
        self.right_sword = Sword(is_left=False)

        # Grab state
        self.ball_grabbed_by = None  # 'left' or 'right' or None
        self.paddle_grabbed = None  # 'left_grabs_right', 'right_grabs_left', None
        self._grab_offset = np.zeros(2)

        # Health system: 3 hits to kill
        self.health = {'left': MAX_HEALTH, 'right': MAX_HEALTH}

        # Cut state: paddle halves (when health reaches 0)
        self.left_cut = False
        self.right_cut = False
        self.left_cut_halves = None
        self.right_cut_halves = None
        self._left_bleed_timer = 0
        self._right_bleed_timer = 0

        # Damage flash timers
        self._damage_flash = {'left': 0, 'right': 0}

    def set_sword_direction(self, side, dx, dy):
        """Set sword direction from input keys. Called each frame."""
        sword = self.left_sword if side == 'left' else self.right_sword
        sword.set_direction(dx, dy)

    def try_grab_ball(self, side, paddle, ball):
        """Try to grab the ball. Returns True if grabbed."""
        if self.ball_grabbed_by is not None:
            return False
        if self.paddle_grabbed is not None:
            return False

        dist = np.linalg.norm(ball.pos - paddle.pos -
                              np.array([paddle.width / 2, paddle.height / 2]))
        ball_speed = np.linalg.norm(ball.vel)

        if dist < self.GRAB_RANGE and ball_speed < self.GRAB_SPEED_THRESHOLD:
            self.ball_grabbed_by = side
            self._grab_offset = ball.pos.copy() - paddle.pos.copy()
            ball.vel[:] = 0
            ball.spin = 0
            return True
        return False

    def release_ball(self, paddle, ball):
        """Release a grabbed ball, launching it with the paddle's velocity."""
        if self.ball_grabbed_by is None:
            return
        paddle_speed = np.linalg.norm(paddle.vel)
        if paddle_speed > 0.5:
            direction = paddle.vel / paddle_speed
            launch_speed = max(8.0, paddle_speed * self.LAUNCH_SPEED_MULT)
            ball.vel[:] = direction * launch_speed
        else:
            # Default launch forward
            is_left = self.ball_grabbed_by == 'left'
            ball.vel[:] = [8.0 if is_left else -8.0, 0]
        ball.spin = paddle.vel[1] * 0.3
        self.ball_grabbed_by = None

    def update_grabbed_ball(self, paddle, ball):
        """Keep grabbed ball attached to paddle."""
        if self.ball_grabbed_by is None:
            return
        ball.pos[:] = paddle.pos + self._grab_offset
        ball.vel[:] = 0

    def try_grab_paddle(self, grabber_side, grabber, target):
        """Try to grab the enemy paddle."""
        if self.paddle_grabbed is not None:
            return False
        if self.ball_grabbed_by is not None:
            return False

        gc = grabber.pos + np.array([grabber.width / 2, grabber.height / 2])
        tc = target.pos + np.array([target.width / 2, target.height / 2])
        dist = np.linalg.norm(gc - tc)

        if dist < self.PADDLE_GRAB_RANGE:
            self.paddle_grabbed = f'{grabber_side}_grabs_{"right" if grabber_side == "left" else "left"}'
            self._grab_offset = target.pos.copy() - grabber.pos.copy()
            target.vel[:] = 0
            return True
        return False

    def throw_paddle(self, grabber, target):
        """Throw the grabbed paddle."""
        if self.paddle_grabbed is None:
            return
        grabber_speed = np.linalg.norm(grabber.vel)
        if grabber_speed > 0.5:
            direction = grabber.vel / grabber_speed
            target.vel[:] = direction * max(self.THROW_SPEED, grabber_speed * 2)
        else:
            is_left = 'left_grabs' in self.paddle_grabbed
            target.vel[:] = [self.THROW_SPEED if is_left else -self.THROW_SPEED, 0]
        self.paddle_grabbed = None

    def update_grabbed_paddle(self, grabber, target):
        """Keep grabbed paddle attached to grabber."""
        if self.paddle_grabbed is None:
            return
        target.pos[:] = grabber.pos + self._grab_offset
        target.vel[:] = 0

    def check_sword_hit(self, left_paddle, right_paddle):
        """Check if a sword hits the enemy paddle. Apply damage if so."""
        for sword, attacker, target, target_side in [
            (self.left_sword, left_paddle, right_paddle, 'right'),
            (self.right_sword, right_paddle, left_paddle, 'left'),
        ]:
            if not sword.can_hit():
                continue
            if self.is_cut(target_side):
                continue
            # Get sword line
            (sx, sy), (tx, ty) = sword.get_hitbox(attacker)
            # Check intersection with target paddle rect
            pr = pygame.Rect(int(target.pos[0]), int(target.pos[1]),
                             int(target.width), int(target.height))
            if pr.clipline(sx, sy, tx, ty):
                sword.register_hit()
                self._apply_damage(target, target_side, attacker)

    def check_sword_ball_hit(self, ball):
        """Check if a sword blade intersects the ball. Apply impulse if so."""
        for sword, paddle_attr in [
            (self.left_sword, 'left'),
            (self.right_sword, 'right'),
        ]:
            if not sword.visible:
                continue
            if sword._hit_cooldown > 0:
                continue

        # We need the paddle to compute hitbox — this is called from update()
        # with paddles available, so we use a different approach below
        pass

    def _check_sword_ball(self, sword, paddle, ball):
        """Check if sword blade hits ball and deflect it."""
        if not sword.visible:
            return False
        if sword._hit_cooldown > 0:
            return False

        (sx, sy), (tx, ty) = sword.get_hitbox(paddle)

        # Point-to-line-segment distance for ball center
        bx, by = ball.pos[0], ball.pos[1]
        dx, dy = tx - sx, ty - sy
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq < 1:
            return False

        t = max(0, min(1, ((bx - sx) * dx + (by - sy) * dy) / seg_len_sq))
        closest_x = sx + t * dx
        closest_y = sy + t * dy
        dist = math.sqrt((bx - closest_x) ** 2 + (by - closest_y) ** 2)

        if dist < ball.radius + SWORD_WIDTH:
            # Deflect ball in sword direction with impulse
            final_angle = sword._base_angle() + sword.angle
            impulse_strength = min(BALL_SWORD_IMPULSE,
                                   abs(sword.angular_velocity) * SWORD_MASS * 0.5 + 4)
            ball.vel[0] = math.cos(final_angle) * impulse_strength
            ball.vel[1] = math.sin(final_angle) * impulse_strength
            sword.register_hit()
            return True
        return False

    def _apply_damage(self, target, target_side, attacker):
        """Deal 1 damage to a paddle. Cut in half at 0 HP."""
        self.health[target_side] -= 1
        hp = self.health[target_side]
        self._damage_flash[target_side] = 15  # flash frames

        cx = target.pos[0] + target.width / 2
        mid_y = target.pos[1] + target.height / 2
        direction = 1.0 if attacker.pos[0] < target.pos[0] else -1.0

        if hp <= 0:
            # Kill — cut in half!
            self._apply_cut(target, target_side, attacker)
        else:
            # Damage hit — blood splash scaled by remaining HP
            blood_count = 10 + (MAX_HEALTH - hp) * 10
            self.blood.emit_hit(cx, mid_y, count=blood_count)

    def _apply_cut(self, target, target_side, attacker):
        """Cut a paddle in half! Gore time."""
        mid_y = target.pos[1] + target.height / 2

        if target_side == 'left':
            self.left_cut = True
            self.left_cut_halves = (target.pos[1], mid_y + 8,
                                    target.height)
        else:
            self.right_cut = True
            self.right_cut_halves = (target.pos[1], mid_y + 8,
                                     target.height)

        # Blood explosion at cut point
        cx = target.pos[0] + target.width / 2
        direction = 1.0 if attacker.pos[0] < target.pos[0] else -1.0
        self.blood.emit_slash(cx, mid_y, direction, count=60)

        # Target paddle is now "dead" — halved and can't move
        target.vel[:] = 0

    def is_cut(self, side):
        """Check if a paddle is cut in half (dead)."""
        return self.left_cut if side == 'left' else self.right_cut

    def check_paddle_collision(self, left_paddle, right_paddle):
        """Check if paddles are colliding (ramming)."""
        lr = pygame.Rect(int(left_paddle.pos[0]), int(left_paddle.pos[1]),
                         int(left_paddle.width), int(left_paddle.height))
        rr = pygame.Rect(int(right_paddle.pos[0]), int(right_paddle.pos[1]),
                         int(right_paddle.width), int(right_paddle.height))

        if lr.colliderect(rr):
            rel_vel = left_paddle.vel - right_paddle.vel
            rel_speed = np.linalg.norm(rel_vel)

            if rel_speed > 0.5:
                # Separate paddles
                overlap_x = (lr.right - rr.left)
                if overlap_x > 0:
                    left_paddle.pos[0] -= overlap_x / 2
                    right_paddle.pos[0] += overlap_x / 2

                # Exchange momentum
                temp_vel = left_paddle.vel.copy()
                left_paddle.vel[:] = right_paddle.vel * 0.8
                right_paddle.vel[:] = temp_vel * 0.8

                # Ram blood effect if fast enough
                if rel_speed > self.RAM_DAMAGE_THRESHOLD:
                    impact_x = (lr.right + rr.left) / 2
                    impact_y = (lr.centery + rr.centery) / 2
                    self.blood.emit_impact(impact_x, impact_y,
                                           count=int(rel_speed * 3))

    def update(self, left_paddle, right_paddle, ball):
        """Per-frame update."""
        dt = 1 / 60  # fixed timestep

        self.left_sword.update(dt)
        self.right_sword.update(dt)

        # Decay damage flash
        for side in ('left', 'right'):
            if self._damage_flash[side] > 0:
                self._damage_flash[side] -= 1

        self.check_sword_hit(left_paddle, right_paddle)
        self.check_paddle_collision(left_paddle, right_paddle)

        # Sword-ball interaction
        if self.ball_grabbed_by is None:
            if self._check_sword_ball(self.left_sword, left_paddle, ball):
                pass  # hit handled
            elif self._check_sword_ball(self.right_sword, right_paddle, ball):
                pass

        # Bleed from damaged/cut paddles
        if self.left_cut:
            self._left_bleed_timer += 1
            if self._left_bleed_timer % 4 == 0:
                mid_y = left_paddle.pos[1] + left_paddle.height / 2
                self.blood.emit_drip(
                    left_paddle.pos[0] + left_paddle.width / 2,
                    mid_y, count=2)
        elif self.health['left'] < MAX_HEALTH:
            self._left_bleed_timer += 1
            if self._left_bleed_timer % 12 == 0:
                mid_y = left_paddle.pos[1] + left_paddle.height / 2
                self.blood.emit_drip(
                    left_paddle.pos[0] + left_paddle.width / 2,
                    mid_y, count=1)

        if self.right_cut:
            self._right_bleed_timer += 1
            if self._right_bleed_timer % 4 == 0:
                mid_y = right_paddle.pos[1] + right_paddle.height / 2
                self.blood.emit_drip(
                    right_paddle.pos[0] + right_paddle.width / 2,
                    mid_y, count=2)
        elif self.health['right'] < MAX_HEALTH:
            self._right_bleed_timer += 1
            if self._right_bleed_timer % 12 == 0:
                mid_y = right_paddle.pos[1] + right_paddle.height / 2
                self.blood.emit_drip(
                    right_paddle.pos[0] + right_paddle.width / 2,
                    mid_y, count=1)

        self.blood.update()

    def draw(self, surface, left_paddle, right_paddle):
        """Draw all combat visuals."""
        # Blood (under everything)
        self.blood.draw(surface)

        # Hands and swords for alive paddles
        if not self.left_cut:
            self.left_sword.draw_hands(surface, left_paddle)
            self.left_sword.draw(surface, left_paddle)
            self._draw_health_bar(surface, left_paddle, 'left')
            self._draw_damage_state(surface, left_paddle, 'left')
        if not self.right_cut:
            self.right_sword.draw_hands(surface, right_paddle)
            self.right_sword.draw(surface, right_paddle)
            self._draw_health_bar(surface, right_paddle, 'right')
            self._draw_damage_state(surface, right_paddle, 'right')

        # Cut paddle halves with blood gap
        if self.left_cut and self.left_cut_halves:
            self._draw_cut_paddle(surface, left_paddle, self.left_cut_halves)
        if self.right_cut and self.right_cut_halves:
            self._draw_cut_paddle(surface, right_paddle, self.right_cut_halves)

        # Grab indicators
        if self.ball_grabbed_by:
            self._draw_grab_indicator(surface, "BALL GRABBED!", (255, 200, 0))
        if self.paddle_grabbed:
            self._draw_grab_indicator(surface, "PADDLE GRABBED!", (255, 100, 100))

    def _draw_health_bar(self, surface, paddle, side):
        """Draw HP pips above paddle."""
        hp = self.health[side]
        bar_y = int(paddle.pos[1]) - 12
        bar_x = int(paddle.pos[0])

        for i in range(MAX_HEALTH):
            px = bar_x + i * 7
            if i < hp:
                color = (0, 220, 0) if hp == 3 else (255, 200, 0) if hp == 2 else (255, 50, 50)
            else:
                color = (60, 60, 60)
            pygame.draw.rect(surface, color, (px, bar_y, 5, 5))

    def _draw_damage_state(self, surface, paddle, side):
        """Draw visual damage on paddle (cracks, flicker)."""
        hp = self.health[side]
        if hp >= MAX_HEALTH:
            return

        px = int(paddle.pos[0])
        py = int(paddle.pos[1])
        pw = int(paddle.width)
        ph = int(paddle.height)

        # Damage flash (white flash on hit)
        if self._damage_flash[side] > 0:
            flash_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            alpha = int(200 * (self._damage_flash[side] / 15))
            flash_surf.fill((255, 255, 255, alpha))
            surface.blit(flash_surf, (px, py))

        # Crack lines
        if hp <= 2:
            # First crack
            pygame.draw.line(surface, BLOOD_DARK,
                             (px + 2, py + ph // 3),
                             (px + pw - 2, py + ph // 3 + 5), 1)
        if hp <= 1:
            # Second crack + red pulse
            pygame.draw.line(surface, BLOOD_DARK,
                             (px + 1, py + ph * 2 // 3),
                             (px + pw - 1, py + ph * 2 // 3 - 4), 1)
            pygame.draw.line(surface, BLOOD_RED,
                             (px + pw // 2 - 3, py + ph // 4),
                             (px + pw // 2 + 3, py + ph * 3 // 4), 1)

            # Pulse red overlay
            pulse = abs(math.sin(time.monotonic() * 8)) * 0.4
            pulse_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pulse_surf.fill((255, 0, 0, int(pulse * 100)))
            surface.blit(pulse_surf, (px, py))

    def _draw_cut_paddle(self, surface, paddle, halves):
        """Draw a paddle that's been cut in half with a bleeding gap."""
        top_y, bottom_y, orig_height = halves
        half_h = orig_height / 2 - 4

        # Top half (slides up slightly)
        top_rect = pygame.Rect(int(paddle.pos[0]),
                               int(paddle.pos[1] - 3),
                               int(paddle.width), int(half_h))
        pygame.draw.rect(surface, paddle.color, top_rect)

        # Bottom half (slides down slightly)
        bottom_rect = pygame.Rect(int(paddle.pos[0]),
                                  int(paddle.pos[1] + orig_height / 2 + 3),
                                  int(paddle.width), int(half_h))
        pygame.draw.rect(surface, paddle.color, bottom_rect)

        # Blood in the gap
        gap_y = int(paddle.pos[1] + orig_height / 2)
        for i in range(-3, 4):
            bx = int(paddle.pos[0]) + random.randint(0, int(paddle.width))
            pygame.draw.circle(surface, BLOOD_RED,
                               (bx, gap_y + i), random.randint(1, 3))

    def _draw_grab_indicator(self, surface, text, color):
        """Draw grab state text."""
        font = FONT_TINY_DIGITAL
        rendered = font.render(text, True, color)
        surface.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, 75))

    def reset(self):
        """Reset all combat state (full game restart)."""
        self.ball_grabbed_by = None
        self.paddle_grabbed = None
        self.health = {'left': MAX_HEALTH, 'right': MAX_HEALTH}
        self.left_cut = False
        self.right_cut = False
        self.left_cut_halves = None
        self.right_cut_halves = None
        self._left_bleed_timer = 0
        self._right_bleed_timer = 0
        self._damage_flash = {'left': 0, 'right': 0}
        self.left_sword = Sword(is_left=True)
        self.right_sword = Sword(is_left=False)
        self.blood.reset()
