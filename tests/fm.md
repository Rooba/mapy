Free Market Integration
=======================

In the current version of MapleStory that we are working with, the free market is where all the items are sold by the players in the community amongst each other, and getting remotely close to viewing all listed items can take up to 4 hours within the game.

---

[Run Down](#run-down)
--------

*__Free Market Entrance__*     |  *__Free Market Room 1__*
--------------------------  |  ----------------------
![Free Market Entrance](https://maplelegends.com/static/images/lib/map/910000000.png) | ![Free Market Room 1](https://maplelegends.com/static/images/lib/map/910000001.png)

Viewing the map page below can give a better example
----------------------------------------------------

[Map View](https://maplelegends.com/lib/map?id=910000000#3)
-----------------------------------------------------------

> - 24 Total Rooms
>
> - About 20 Shop locations per room (The closest another player can get to opening a shop near another shop requires that none of the shops image is overlapping onto another, leaving very limited space)
>
> - Players will often fight for the closest rooms to the entrace, as well as the closest location near the entrace to the room portal
>
>   - All shops are closed and the rooms emptied once the server resets, so players will often plan for server resets in order to snipe the very best locations
>
>   - As to not completely cut out the premium of having a good spot, a sort of stamina can be added to viewing within the web, where market search queries for an item listing will consume the most, manually searching through rooms the least (Still faster speed than in game however)
>
>   - This also allows for the players that get the very last room [24] in channel 1 of the given world a fair chance to sell anything at all, as people can still find their listings within searches easily and be told their exact coords within the map
>
> - Knowing what the actual price of an item is can take weeks upon weeks of research, and prices often tend to fluctuate drastically, so having a listings page for past sales and statistics will hinder the market being 100% driven by players merchanting at 300% the normal cost

---

[Objectives](#objectives)
----------

[ ] Browseable Free market through mapy web
-----------------------------------------------

> *__Using in-game assets as well as character model, walking around from room to room and interacting with actual players in game__*
>
> *__Steering away from entirely allowing player to buy on mapy web offers benefits to both players and hosts__*
>
> - Promises to not entirely make getting optimal spots practically pointless for players who spend the time to plan for it
>
> - Doesn't entirely allow for players not have to worry at all about finding a competing location
>
> - Allowing for a couple purchases a day using [stamina](#stamina) could offer a way to allow players to still buy without spending multiple hours plus able to grab a deal if they are unable to get to their computer in time
>
> - Offer a way to further browse online using micro transactions to unlock features / usage time / allotted purchases
>
> - Allow players to still have access to social aspects of the game without having to have access to a computer, and allow full 24/7 access to the main entrance with no utilities if desired by players

[ ] Statistics View allowing searching of
-----------------------------------------

> - Average Quantity sold per day
>
> - Average price per x amount of a given item
>
> - Most Recently Sold quantity / price / time of the searched item
>
> - Daily / Weekly / Monthly change in price of an item

[ ] Cache all shops in an external redis service or something similar from within mapy
--------------------------------------------------------------------------

> - Quick access to all shops and sales
>
> - A safeguard to stop accidental closing of all shops due to an unforseen restart of the server which often times does not go over well
>
> - Easy Access for mapy web, however the option for a direct tcp connection to the server is still viable
