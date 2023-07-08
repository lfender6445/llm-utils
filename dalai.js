const Dalai = require("dalai")
new Dalai().request({
  url: "ws://localhost:3000",
  model: "7B",
  prompt: "The following is a conversation between a boy and a girl:",
}, (token) => {
  console.log("token", token)
})
