document.addEventListener("DOMContentLoaded", function () {
  var json_groups = JSON.parse(
    document.getElementById("json-groups").textContent
  );
  //   console.log("Loaded JSON groups:", json_groups);

  var send_url = JSON.parse(document.getElementById("send_url").textContent);
  //   console.log("Send_url:", send_url);

  document
    .querySelectorAll(".chats-container")
    .forEach(function (chatContainer) {
      chatContainer.addEventListener("click", function () {
        document
          .querySelectorAll(".chats-container")
          .forEach((el) => el.removeAttribute("id"));

        this.setAttribute("id", "active");
      });
    });

  const chatItems = document.querySelectorAll(".chats-container");
  const chatContents = document.querySelectorAll(".right-side");

  chatItems.forEach((chat) => {
    chat.addEventListener("click", function () {
      let index = this.getAttribute("data-id");

      chatContents.forEach((content) => (content.style.display = "none"));

      let selectedChat = document.querySelector(
        `.right-side[data-id='${index}']`
      );

      if (selectedChat) {
        selectedChat.style.display = "inline-flex";

        let chatContainer = selectedChat.querySelector(".message-display-area");

        if (chatContainer) {
          chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: "smooth",
          });
        }
      }
    });
  });

  var stream_url = JSON.parse(
    document.getElementById("stream_url").textContent
  );
  var user = JSON.parse(document.getElementById("user.id").textContent);

  const eventSource = new EventSource(stream_url);
  eventSource.onmessage = function (event) {
    let data = JSON.parse(event.data);

    let currentUser = user;

    let activeChatBox = document.querySelector(
      ".right-side:not([style*='display: none'])"
    );

    if (!activeChatBox) return;

    let activeUser = activeChatBox.getAttribute("data-id");

    if (data.from == activeUser || data.to == activeUser) {
      appendMessage(data, currentUser == data.from);

      const chatContainer = document.querySelector(
        `.chats-container[data-id='${activeUser}']`
      );
      const parent = chatContainer.parentElement;
      if (parent.firstChild !== chatContainer) {
        parent.insertBefore(chatContainer, parent.firstChild);
      }
    }
  };

  function moveMessage() {}

  function appendMessage(data, isSender) {
    let chatContainer = document.querySelector(
      ".right-side:not([style*='display: none']) .message-display-area"
    );

    if (!chatContainer) return;

    let messageDiv = document.createElement("div");
    messageDiv.classList.add("message", isSender ? "sent" : "received");

    let textDiv = document.createElement("div");
    textDiv.classList.add("message-text");
    textDiv.innerText = data.message;

    let timeDiv = document.createElement("div");
    timeDiv.classList.add("message-time");
    timeDiv.innerText = data.time;

    messageDiv.appendChild(textDiv);
    messageDiv.appendChild(timeDiv);
    chatContainer.appendChild(messageDiv);

    chatContainer.scrollTo({
      top: chatContainer.scrollHeight,
      behavior: "smooth",
    });
  }
});
