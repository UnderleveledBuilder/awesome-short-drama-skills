// 去写剧本的输入框（首页、实测页、几个编剧的项目页）：带着这句话去 write.shortdramaskills.com。
// 这句话放在网址 # 后面，不发给任何服务器；那边把它填进输入框，不自动开写。
// 没开脚本时，表单只带 from（和 lang）过去，框旁的「直接去写」链接也能点。
for (const form of document.querySelectorAll("form[data-write]")) {
  const box = form.querySelector("textarea");
  const go = () => {
    const text = box.value.trim();
    if (!text) {
      box.focus();
      return;
    }
    const query = new URLSearchParams(new FormData(form)).toString();
    window.location.href = `${form.action}?${query}#idea=${encodeURIComponent(text)}`;
  };
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    go();
  });
  // 回车就去；Shift+回车换行；中文输入法选字时的回车不算。
  box.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing && e.keyCode !== 229) {
      e.preventDefault();
      go();
    }
  });
}
