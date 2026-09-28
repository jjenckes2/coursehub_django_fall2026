const button = document.querySelector("#tip-button");
const tip = document.querySelector("#study-tip");

if (button && tip) {
  button.addEventListener("click", () => {
    tip.hidden = !tip.hidden;
    button.setAttribute("aria-expanded", String(!tip.hidden));
    button.textContent = tip.hidden ? "Show study tip" : "Hide study tip";
  });
}