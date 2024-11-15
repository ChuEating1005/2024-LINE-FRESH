LINEBOT/db_utils/裡面有把資料庫crud包成handler可以直接call 不過沒有很完整 只有一些新增刪除查找
資料庫原本是用mongoDB的atlas 但免費的一下子就滿了 後來改先用local 把uri = "mongodb://localhost:27017/"  改成自己的localhost
跑db_handler.py可以存基本的資料庫欄位做測試
還沒處理嵌入圖片的方法

LINEBOT/web/裡面的前端是我簡單測試用的 有兩個畫面 一個是條列文章title 還有按鈕可以點入各個文章 第二個就是顯示文章的頁面 
只要看templates/和views.py 其他沒改

不過目前把markdown傳到html不太會正確排版 好像還要下載markdown的css 或是用其他方法存 這邊還沒做

跑manage.py runserver可以跑local網頁