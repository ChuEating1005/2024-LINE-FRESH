document.addEventListener("DOMContentLoaded", () => {
  const articleMdPath = "article.md"; // 主文章的路徑 -> should change to the database
  const imgDir = "./img"; // 主文章圖片資料夾 -> should change to the database
  const relatedDirPath = "./related"; // 相關文章資料夾 -> should change to the database

  // load the main article
  fetch(articleMdPath)
    .then((response) => {
      if (!response.ok) throw new Error(`載入文章失敗: ${response.status}`);
      return response.text();
    })
    .then((markdown) => {
      const lines = markdown.split("\n");
      if (lines.length < 3) throw new Error("文章格式錯誤，至少需要標題、作者和時間");

      const title = lines[0].replace("# ", "").trim();
      const author = lines[1].trim();
      const time = lines[2].trim();

      document.getElementById("article-title").innerText = title;
      document.getElementById("article-author-time").innerText = `${author}\n${time}`;

      let contentMarkdown = "";
      let imgIndex = 1;

      for (let i = 3; i < lines.length; i++) {
        if (lines[i].trim() === "") {
          // 遇到空行插入對應圖片
          const imgPath = `${imgDir}/${imgIndex}.png`;
          contentMarkdown += `\n\n![Image ${imgIndex}](${imgPath})\n\n`;
          imgIndex++;
        } else {
          // 添加段落文字
          contentMarkdown += `${lines[i]}\n`;
        }
      }

      // 使用 marked.js 解析 Markdown 為 HTML
      document.getElementById("article-content").innerHTML = marked.parse(contentMarkdown);
    })
    .catch((error) => {
      console.error(error.message);
      document.getElementById("article-content").innerHTML = `<p>無法載入文章內容，請稍後再試。</p>`;
    });

  // 載入相關文章
  const relatedFolders = ["related1", "related2"]; // 手動列出相關文章目錄
  const relatedContent = document.getElementById("related-content");

  relatedFolders.forEach((folder) => {
    const imgPath = `${relatedDirPath}/${folder}/img/cover.png`;
    const relatedMdPath = `${relatedDirPath}/${folder}/related.md`;

    fetch(relatedMdPath)
      .then((response) => {
        if (!response.ok) throw new Error(`無法載入相關文章 ${folder}: ${response.status}`);
        return response.text();
      })
      .then((relatedMarkdown) => {
        const lines = relatedMarkdown.split("\n");
        const title = lines[0].replace("# ", "").trim();
        const author = lines[1].trim();

        relatedContent.innerHTML += `
          <div class="related-item">
            <img src="${imgPath}" alt="${title}" onerror="this.style.display='none';">
            <p>${title}</p>
            <p>${author}</p>
          </div>`;
      })
      .catch((error) => {
        console.error(error.message);
        relatedContent.innerHTML += `<p>無法載入相關文章資料。</p>`;
      });
  });
});
