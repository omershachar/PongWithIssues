export interface Vector2 {
  x: number;
  y: number;
}

export function add(a: Vector2, b: Vector2): Vector2 {
  return { x: a.x + b.x, y: a.y + b.y };
}

export function scale(vec: Vector2, scalar: number): Vector2 {
  return { x: vec.x * scalar, y: vec.y * scalar };
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function magnitude(vec: Vector2): number {
  return Math.sqrt(vec.x * vec.x + vec.y * vec.y);
}

export function normalize(vec: Vector2): Vector2 {
  const mag = magnitude(vec);
  if (mag === 0) {
    return { x: 0, y: 0 };
  }
  return { x: vec.x / mag, y: vec.y / mag };
}
