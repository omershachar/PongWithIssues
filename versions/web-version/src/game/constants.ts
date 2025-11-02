/**
 * constants.ts -- All game-wide settings and fixed values for PongWithIssues.
 */

// -------------------- Colors (RGB) --------------------
export const COLORS = {
    BLACK: [0, 0, 0] as const,
    DARK_GREY: [64, 64, 64] as const,
    GREY: [128, 128, 128] as const,
    LIGHT_GREY: [224, 224, 224] as const,
    WHITE: [255, 255, 255] as const,
    PURPLE: [122, 118, 229] as const,
    LIGHT_PURPLE: [185, 183, 232] as const,
    LIGHT_RED: [255, 204, 203] as const,
    RED: [255, 0, 0] as const,
    DARK_RED: [139, 0, 0] as const,
    YELLOW: [255, 255, 0] as const,
    
    // Fire Colors
    DARK_ORANGE: [170, 65, 0] as const,
    ORANGE: [255, 140, 0] as const,
    LIGHT_ORANGE: [255, 180, 50] as const,
    GOLD: [255, 215, 0] as const,
    DARK_YELLOW: [200, 180, 20] as const,
    BRIGHT_YELLOW: [255, 255, 100] as const,
    FIERY_RED: [255, 40, 0] as const,
    SCARLET: [255, 36, 0] as const,
    CRIMSON: [220, 20, 60] as const,
    CHERRY: [255, 70, 70] as const,
    AMBER: [255, 191, 0] as const,
    FLAME: [255, 87, 34] as const,
    TANGERINE: [255, 120, 0] as const,
    
    // Transition colors for smoother fire gradients
    ORANGE_RED: [255, 69, 0] as const,
    TOMATO: [255, 99, 71] as const,
    DARK_GOLD: [218, 165, 32] as const,
    MELLOW_YELLOW: [255, 239, 120] as const,
    PEACH: [255, 229, 180] as const,
} as const;

// -------------------- Screen & Coordinates --------------------
export const WIDTH = 800;
export const HEIGHT = 800;
export const GAME_MARGIN_X = 10;
export const GAME_FOOTER = [WIDTH / 2, HEIGHT - 30] as const;
export const MIDDLE_BOARD = [WIDTH / 2, HEIGHT / 2] as const;

export const MENU_MARGIN_Y = 45;
export const MENU_SUBTITLES_Y = MENU_MARGIN_Y + 300;
export const MENU_FOOTER = HEIGHT - MENU_MARGIN_Y;

// -------------------- Paddle Settings --------------------
export const PADDLE_WIDTH = 15;
export const PADDLE_HEIGHT = 85;
export const PADDLE_SIZE = [PADDLE_WIDTH, PADDLE_HEIGHT] as const;

export const ORIGINAL_LEFT_PADDLE_POS = [GAME_MARGIN_X, HEIGHT / 2 - PADDLE_HEIGHT / 2] as const;
export const ORIGINAL_RIGHT_PADDLE_POS = [WIDTH - GAME_MARGIN_X - PADDLE_WIDTH, HEIGHT / 2 - PADDLE_HEIGHT / 2] as const;

export const PADDLE_DEFAULT_VEL = 4.5;
export const PADDLE_MAX_VEL = 9;
export const PADDLE_DEFAULT_ACC = [0, 3] as const;

// -------------------- Ball Settings --------------------
export const BALL_RADIUS = 7;
export const BALL_DEFAULT_VEL = [6, 0] as const;

// -------------------- Physics Constants --------------------
export const GRAVITY = 9.81;
export const SPIN_FACTOR = 0.5;                // Multiplier for paddle spin effect
export const MAX_DEFLECTION_SPEED = 7;         // Max vertical speed after deflection
export const FRICTION_COEFFICIENT = 0.4;       // Not currently used, placeholder

// -------------------- Game Settings --------------------
export const FPS = 60;
export const WINNING_SCORE = 3;

// Game states
export const GAME_STATES = {
    MENU: 0,
    PLAYING: 1,
} as const;

// -------------------- ASCII Title --------------------
export const PONG_ASCII_3D = `
██████╗   ██████╗  ███╗   ██╗  ██████╗   ██╗
██╔══██╗ ██╔═══██╗ ████╗  ██║ ██╔════╝   ██║
██████╔╝ ██║   ██║ ██╔██╗ ██║ ██║  ███╗  ██║
██╔═══╝  ██║   ██║ ██║╚██╗██║ ██║   ██║  ╚═╝
██║      ╚██████╔╝ ██║ ╚████║ ╚██████╔╝  ██╗
╚═╝       ╚═════╝  ╚═╝  ╚═══╝  ╚═════╝   ╚═╝
`;

// -------------------- Font Settings --------------------
export const FONT_SIZES = {
    SMALL: 20,
    MEDIUM: 30,
    DEFAULT: 35,
    LARGE: 45,
    BIG: 65,
    TITLE: 80,
} as const;

export type Color = readonly [number, number, number];
export type Position = readonly [number, number];
export type Velocity = readonly [number, number];
export type GameState = typeof GAME_STATES[keyof typeof GAME_STATES];
