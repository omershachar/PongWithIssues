export function add(a, b) {
    return { x: a.x + b.x, y: a.y + b.y };
}
export function scale(vec, scalar) {
    return { x: vec.x * scalar, y: vec.y * scalar };
}
export function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}
export function magnitude(vec) {
    return Math.sqrt(vec.x * vec.x + vec.y * vec.y);
}
export function normalize(vec) {
    const mag = magnitude(vec);
    if (mag === 0) {
        return { x: 0, y: 0 };
    }
    return { x: vec.x / mag, y: vec.y / mag };
}
