# tpconnect4
websocket and asyncio tutorial

1. Know how querystring works (Get, Post). This is a good doc:
https://www.w3schools.com/tags/ref_httpmethods.asp#:~:text=The%20two%20most%20common%20HTTP%20methods%20are%3A%20GET,data%20to%20a%20server%20to%20create%2Fupdate%20a%20resource.

2. know how Javascript query selector works (although it has been simplified by a lot of JS framework).
this is a good documents:
https://www.w3schools.com/tags/ref_httpmethods.asp#:~:text=The%20two%20most%20common%20HTTP%20methods%20are%3A%20GET,data%20to%20a%20server%20to%20create%2Fupdate%20a%20resource.

3. Know some basis of css. This is good documents:
https://www.tutorialstonight.com/css/css-introduction.php

The general logical of this tutorial is:
1. When the HTML is loaded the board is created. At the same time, because the .action[ref=""] is set to display:none,
you can only see the new button (because his ref="/)".
2. When you load the page , the app.python will decide you are init the game. Therefore it sends back the query string
of ?join=token and ?watch=token, the JS main.js use the query selector to find the <a> tag with attribute "action join"
and reset it's ref value with the query string returned by the server.If you click watch, then the main.js will set your
status to watch and the game will update the WS message in the flow.
3. when you share the link to your friend, you actually share the url and the join querystring
4. When you play, the message will be sent to the WS server backboned by app.py and it will send back to message
