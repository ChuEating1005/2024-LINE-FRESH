document.addEventListener("DOMContentLoaded", () => {
  const title = article.title;
  const author = article.author;
  const time = article.time;
  const markdown = article.content;
  const tags = article.tags;
  const images = article.images;

  const lines = markdown.split("\n");
  if (lines.length < 3)
    throw new Error("文章格式錯誤，至少需要標題、作者和時間");

  document.getElementById("article-title").innerText = title;
  document.getElementById(
    "article-author-time"
  ).innerText = `${author}\n${time}`;

  let contentMarkdown = "";
  let imgIndex = 1;

  for (let i = 3; i < lines.length; i++) {
    if (lines[i].trim() === "") {
      // 遇到空行插入對應圖片
      const imgPath = images[imgIndex - 1];
      contentMarkdown += `\n\n![Image ${imgIndex}](${imgPath})\n\n`;
      imgIndex++;
    } else {
      // 添加段落文字
      contentMarkdown += `${lines[i]}\n`;
    }
  }

  // 使用 marked.js 解析 Markdown 為 HTML
  document.getElementById("article-content").innerHTML =
    marked.parse(contentMarkdown);

  // 載入文章標籤
  const tagContainer = document.createElement("div");
  tagContainer.className = "tag-container";

  tags.forEach((tag) => {
    const tagElement = document.createElement("span");
    tagElement.className = "tag";
    tagElement.innerText = tag;
    tagContainer.appendChild(tagElement);
  });

  const authorTimeElement = document.getElementById("article-author-time");
  authorTimeElement.insertAdjacentElement("afterend", tagContainer);
});
