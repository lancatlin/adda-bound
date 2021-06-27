# 💬AddaBound 阿達棒
AddaBound 是一個可連結不同聊天室的機器人，可以透過 AddaBound 與其他聊天室建立配對，讓你可以傳訊息給對方，而不須與對方建立好友關係或是在同一群組。

## 回饋表單

希望你幫我們填寫回饋表單，告訴我們你的寶貴想法喔！ https://forms.gle/gXniCwRNfBTb5aHz7

## 📌使用說明：
* 使用前需要先與使用者進行配對
* 輸入「/create 」或按選單中「建立配對」，系統建立一組配對碼（ex: /join 000000)
* 請希望配對的對象在有 AddaBound 的聊天室裡輸入配對碼（ex: /join 000000)
* 系統顯示「成功與 XXX bound 在一起！」後，代表AddaBound 已在兩個聊天室之間建立連結！
* 接下來只要打「 /send 」或按選單中「傳送訊息」就可以與對方聯繫了！

## 📌指令列表：

[ ] 代表參數

* /create 建立配對碼  
* /join [配對碼] 建立配對  
* /send 傳送訊息  
* /send [收件者] [訊息內容] 指令模式  
* /manage 管理配對  
* /delete 刪除我的帳號  
* /help 使用說明  

## 安裝

### Requirements

請先安裝 Docker 與 docker-compose。

請先註冊一個 [LINE Bot](https://developers.line.biz/)，取得 API TOKEN 及 SECRET，建立一個 .env 文件，填入以下內容

```
LINE_TOKEN=yourtoken
LINE_SECRET=yoursecret
```

Build container
```
docker-compose build
```

執行
```
docker-compose up -d
```

開發過程可用 [Ngrok](https://ngrok.com) 來建立 webhook，將 `https://yourhostname.com/api/line` 註冊到 LINE 的 Webhook URL。

接下來打開你的 LINE 找到 bot，應該就可以使用囉！
