document.addEventListener("DOMContentLoaded", () => {
    const trapezoids = document.querySelectorAll(".trapezoid");
  
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible"); // 添加浮現類
            observer.unobserve(entry.target); // 元素可見後停止監聽
          }
        });
      },
      { threshold: 0.1 } // 當元素可見 10% 時觸發
    );
  
    trapezoids.forEach((trapezoid) => observer.observe(trapezoid));

    const leftArrows = document.querySelectorAll(".left-arrow");
  const rightArrows = document.querySelectorAll(".right-arrow");
  const articleLists = document.querySelectorAll(".article-list");

  const currentIndices = {}; // 用於存儲每個主題的當前索引
  const articlesData = {}; // 用於存儲每個主題的文章數據

  // 初始化每個主題
  articleLists.forEach((articleList) => {
    const topic = articleList.dataset.topic;
    const dataFile = articleList.dataset.file; // 獲取對應的文件名
    currentIndices[topic] = 0; // 初始化索引
    fetchArticles(topic, dataFile); // 加載對應主題的文章數據
  });

  // 加載文章數據
  function fetchArticles(topic, file) {
    fetch(file)
      .then((response) => response.text())
      .then((data) => {
        articlesData[topic] = data
          .trim()
          .split("\n")
          .map((line) => {
            const [image, title, author] = line.split(" ");
            return { image, title, author };
          });
        updateArticles(topic); // 初始化顯示文章
      })
      .catch((error) => console.error(`Error loading ${file}:`, error));
  }

  // 更新指定主題的文章列表
  function updateArticles(topic) {
    const articleList = document.querySelector(`.article-list[data-topic="${topic}"]`);
    const articles = articlesData[topic];
    const currentIndex = currentIndices[topic];

    articleList.innerHTML = ""; // 清空列表

    if (articles && articles.length > 0) {
      const visibleArticles = [
        articles[currentIndex],
        articles[(currentIndex + 1) % articles.length],
      ];

      visibleArticles.forEach((article) => {
        const articleItem = document.createElement("div");
        articleItem.classList.add("article-item");
        articleItem.innerHTML = `
          <img src="./img_list/${article.image}" alt="${article.title}" />
          <h3 class="article-title">${article.title}</h3>
          <p class="article-author">${article.author}</p>
        `;
        articleList.appendChild(articleItem);
      });
    }
  }

  // 左箭頭事件
  leftArrows.forEach((arrow) => {
    arrow.addEventListener("click", () => {
      const topic = arrow.dataset.topic;
      const articles = articlesData[topic];
      if (articles && articles.length > 0) {
        currentIndices[topic] =
          (currentIndices[topic] - 1 + articles.length) % articles.length;
        updateArticles(topic);
      }
    });
  });

  // 右箭頭事件
  rightArrows.forEach((arrow) => {
    arrow.addEventListener("click", () => {
      const topic = arrow.dataset.topic;
      const articles = articlesData[topic];
      if (articles && articles.length > 0) {
        currentIndices[topic] = (currentIndices[topic] + 1) % articles.length;
        updateArticles(topic);
      }
    });
  });

});
  