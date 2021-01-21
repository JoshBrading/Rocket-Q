# Rocket-Q
## What is Rocket-Q

> Rocket-Q is a customizable 1v1 queue system that enables streamers to setup a queue against viewers using their chat bot.
I originally started this project for a fellow Rocket League streamer, shoutout to [TickleMeGains](https://www.twitch.tv/ticklemegains).

## Why does it exist
> For a mid to large streamer it can be challenging setting up a 1v1 queue against viewers. Some streamers use a "pay-to-play" system where either
they play against subscribers or use Twitch's built in channel point system to track players. This works well unless the streamer does not want
to charge viewers anything to play, introducing Rocket-Q. Rocket-Q is a web API that can communicate with any chat bots that support URL fetching.

## What can it do
 Rocket-Q can do a few simple actions
  
Commands | Description | Permission Level
------------ | ------------- | -------------
Start | Opens the queue | Mod
Stop | Closes the queue | Mod
Next | Moves the queue to the next player | Mod
Join | Adds the player to the queue | Viewer
Leave | Removes the player from the queue | Viewer
Queue | Displays the queue | Viewer

## How to use

> Feel free to download my code and self host or make modifications but if you prefer I currently host Rocket-Q myself for anyone to use
[here](https://rocket-q.tacki.xyz/). The actual setup with Twitch is extremely easy, just connect Rocket-Q with Twitch and then customize your commands. Currently I just display the commands for Nightbot but this may change soon.

## The code
> About 85% of the code for HTML and CSS was done with a generator. I wish I had the time to learn HTML and CSS but alas I wanted to finish the project before the semester started.
Enjoy the sweet Python code, considering this was my first time using Flask and completing the project in just a couple days I think it went well.

## Login and Customization Images
<img src="https://i.imgur.com/L2LLcch.png" width="75%">
<img src="https://i.imgur.com/2HeUho6.png" width="75%">
