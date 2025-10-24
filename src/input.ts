export type Direction = -1 | 0 | 1;

export class InputManager {
  private upKeys = new Set(["ArrowUp", "w", "W"]);
  private downKeys = new Set(["ArrowDown", "s", "S"]);
  private direction: Direction = 0;

  constructor(private target: Window = window) {}

  public bind(): void {
    this.target.addEventListener("keydown", this.handleKeyDown);
    this.target.addEventListener("keyup", this.handleKeyUp);
  }

  public unbind(): void {
    this.target.removeEventListener("keydown", this.handleKeyDown);
    this.target.removeEventListener("keyup", this.handleKeyUp);
  }

  public getDirection(): Direction {
    return this.direction;
  }

  private handleKeyDown = (event: KeyboardEvent): void => {
    if (this.upKeys.has(event.key)) {
      this.direction = -1;
    } else if (this.downKeys.has(event.key)) {
      this.direction = 1;
    }
  };

  private handleKeyUp = (event: KeyboardEvent): void => {
    if (this.upKeys.has(event.key) && this.direction === -1) {
      this.direction = 0;
    } else if (this.downKeys.has(event.key) && this.direction === 1) {
      this.direction = 0;
    }
  };
}
