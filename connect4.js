const PLAYER1 = "pink";

const PLAYER2 = "green";

function createBoard(board) {
  // Inject stylesheet.
  const linkElement = document.createElement("link");
  linkElement.href = import.meta.url.replace(".js", ".css");
  linkElement.rel = "stylesheet";
  document.head.append(linkElement);
  // Generate board ...
  for (let column = 0; column < 7; column++) {
    const columnElement = document.createElement("div");
    columnElement.className = "column";
    columnElement.dataset.column = column;
    for (let row = 0; row < 6; row++) {
      const cellElement = document.createElement("div");
      cellElement.className = "cell empty";
      cellElement.dataset.column = column;
      columnElement.append(cellElement);
    }
    board.append(columnElement);
  }
}

function playMove(board, player, column, row, moves) {
  // Check values of arguments.
  if (player !== PLAYER1 && player !== PLAYER2) {
    throw new Error(`Player must be ${PLAYER1} or ${PLAYER2}.`);
  }
  const columnElement = board.querySelectorAll(".column")[column];
  if (columnElement === undefined) {
    throw new RangeError("Column must be between 0 and 6.");
  }
  const cellElement = columnElement.querySelectorAll(".cell")[row];
  if (cellElement === undefined) {
    throw new RangeError("Row must be between 0 and 5.");
  }
  // Place checker in cell.
  if (!cellElement.classList.replace("empty", player)) {
    throw new Error("Cell must be empty.");
  } else {
    let col = column + 1
    document.getElementById("txt1").textContent = `Last move ${moves} was in column ${col}`;
    document.getElementById("txt1").style.backgroundColor = `darkgray`;
    document.getElementById("txt1").style.color = player;
  }
}

export { PLAYER1, PLAYER2, createBoard, playMove };
