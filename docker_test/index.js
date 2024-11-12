const express = require("express");
const PORT = 8080;

const app = express();

app.get("/", (req, res) => {
    res.json("hello world");
});

app.listen(PORT, () => {
    console.log("서버 가동");
});