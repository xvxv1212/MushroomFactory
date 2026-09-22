const express = require("express");

const app = express();
const PORT = 3000;

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Backend server 정상 실행!");
});

app.listen(PORT, () => {
  console.log(`Backend server running at http://localhost:${PORT}`);
});