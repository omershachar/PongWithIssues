import { GAME_HEIGHT, GAME_WIDTH } from "./constants.js";
import { InputManager } from "./input.js";
import { Game } from "./game.js";

const canvasElement = document.getElementById("game");
const startButtonElement = document.getElementById("start");
const statusElement = document.getElementById("status");
const playerScoreElement = document.getElementById("player-score");
const cpuScoreElement = document.getElementById("cpu-score");

if (
  !(canvasElement instanceof HTMLCanvasElement) ||
  !(startButtonElement instanceof HTMLButtonElement) ||
  !(statusElement instanceof HTMLElement) ||
  !(playerScoreElement instanceof HTMLElement) ||
  !(cpuScoreElement instanceof HTMLElement)
) {
  throw new Error("Unable to locate UI elements");
}

const canvas = canvasElement;
const startButton = startButtonElement;
const statusLabel = statusElement;
const playerScoreLabel = playerScoreElement;
const cpuScoreLabel = cpuScoreElement;

canvas.width = GAME_WIDTH;
canvas.height = GAME_HEIGHT;

const input = new InputManager();
input.bind();

const updateStatus = (message: string): void => {
  statusLabel.textContent = message;
};

const game = new Game(canvas, input, updateStatus);

function updateScoreboard(): void {
  const { player, cpu } = game.getScores();
  playerScoreLabel.textContent = `Player: ${player}`;
  cpuScoreLabel.textContent = `CPU: ${cpu}`;
}

function tick(): void {
  updateScoreboard();
  requestAnimationFrame(tick);
}

requestAnimationFrame(tick);

startButton.addEventListener("click", () => {
  startButton.disabled = true;
  updateStatus("Launching game...");
  setTimeout(() => {
    game.start();
    startButton.disabled = false;
    startButton.textContent = "Restart";
  }, 150);
});

window.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && game.getState() !== "running") {
    updateStatus("Game paused. Click start to resume.");
  }
});

updateStatus("Press Start to begin.");
