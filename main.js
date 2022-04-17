import { createBoard, playMove } from "./connect4.js";

function getWebSocketServer() {
  if (window.location.host === "tplocher.github.io") {
    return "wss://tpconnect4.herokuapp.com/";
  } else if (window.location.host === "localhost:8000") {
    return "ws://localhost:8001/";
  } else {
    throw new Error(`Unsupported host: ${window.location.host}`);
  }
}

function initGame(websocket) {
  websocket.addEventListener("open", () => {
    // Send an "init" event according to who is connecting.
    const params = new URLSearchParams(window.location.search);
    let event = { type: "init" };
    if (params.has("join")) {
      // Second player joins an existing game.
      document.getElementById("txt0").textContent = `Player 2`;
      document.getElementById("txt1").textContent = `Player ${event.start} starts!`;
      event.join = params.get("join");
    } else if (params.has("watch")) {
      // Spectator watches an existing game.
      document.getElementById("txt0").textContent = `Spectator`;
      document.getElementById("txt1").textContent = `Player ${event.start} starts!`;
      event.watch = params.get("watch");
    } else {
      // First player starts a new game.
      if (params.has("joinID")) {
        // First Player wants to set a specific join-ID
        event.joinID = params.get("joinID");
        document.getElementById("txt0").textContent = `Player 1 (join=${event.joinID})`;
      } else {
        event.joinID = params.get("none");
      }
    }
    websocket.send(JSON.stringify(event));
  });
}

function showMessage(message) {
  window.setTimeout(() => window.alert(message), 50);
}

function receiveMoves(board, websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "init":
        // Create links for inviting the second player and spectators.
        document.querySelector(".join").href = "?join=" + event.join;
        document.querySelector(".watch").href = "?watch=" + event.watch;
        document.getElementById("txt1").textContent = `Player ${event.start} starts!`;
        break;
      case "play":
        // Update the UI with the move.
        playMove(board, event.player, event.column, event.row);
        break;
      case "win":
        showMessage(`Player ${event.player} wins!`);
        document.getElementById("txt1").textContent = `Player ${event.player} wins!`;
        // No further messages are expected; close the WebSocket connection.
        websocket.close(1000);
        break;
      case "error":
        showMessage(event.message);
        break;
      default:
        throw new Error(`Unsupported event type: ${event.type}.`);
    }
  });
}

function sendMoves(board, websocket) {
  // Don't send moves for a spectator watching a game.
  const params = new URLSearchParams(window.location.search);
  if (params.has("watch")) {
    return;
  }
  // When clicking a column, send a "play" event for a move in that column.
  board.addEventListener("click", ({ target }) => {
    document.getElementById("txt1").textContent = ``
    const column = target.dataset.column;
    // Ignore clicks outside a column.
    if (column === undefined) {
      return;
    }
    const event = {
      type: "play",
      column: parseInt(column, 10),
    };
    document.getElementById("txt1").textContent = `Last column played: ${event.column}`
    websocket.send(JSON.stringify(event));
  });
  document.getElementById("txt1").textContent = `Determining who starts.`
}

window.addEventListener("DOMContentLoaded", () => {
  // Initialize the UI.
  const board = document.querySelector(".board");
  createBoard(board);
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket(getWebSocketServer());
  initGame(websocket);
  receiveMoves(board, websocket);
  sendMoves(board, websocket);
});
