<div align="center">
<pre>
      ___                       ___     
     /\  \          ___        /\__\    
    /::\  \        /\  \      /::|  |   
   /:/\ \  \       \:\  \    /:|:|  |   
  _\:\~\ \  \      /::\__\  /:/|:|  |__ 
 /\ \:\ \ \__\  __/:/\/__/ /:/ |:| /\__\
 \:\ \:\ \/__/ /\/:/  /    \/__|:|/:/  /
  \:\ \:\__\   \::/__/         |:/:/  / 
   \:\/:/  /    \:\__\         |::/  /  
    \::/  /      \/__/         /:/  /   
     \/__/                     \/__/    
</pre>

**Android runtime modding · Xposed · desktop tinkering**

<a href="mailto:mrxsin@gmail.com"><img src="https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
<a href="https://github.com/MrxSiN?tab=repositories"><img src="https://img.shields.io/badge/Modules-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Modules" /></a>
<img src="https://komarev.com/ghpvc/?username=MrxSiN&style=for-the-badge&color=orange&label=VISITORS" alt="Visitors" />

</div>

## About me

Most of what I write are Xposed modules. It started with Gmail putting ads in my inbox — I didn't want them hidden behind
a subscription, so I wrote [GmailHideAds](https://github.com/MrxSiN/GmailHideAds). X did the same thing later, then
Threads, and now there are three: [TwitterHideAds](https://github.com/MrxSiN/TwitterHideAds) and
[ThreadsHideAds](https://github.com/MrxSiN/ThreadsHideAds). They all hook the render path and drop the sponsored item
before it reaches the screen. No DNS filtering, no blank placeholder where the ad used to be.

The slow part isn't the hook, it's finding what to hook. These apps ship obfuscated and rename everything every few
releases, so most of my time goes into smali, reflection, and figuring out which method still means something after the
update. I try to make modules fail quietly instead of crashing the host app when that changes — a dead feature is
annoying, an app that won't open is worse.

Away from Android I mess with my desktop more than I should: Windhawk mods, GShade presets, a
[Hyprland shell](https://github.com/MrxSiN/HyprM3E) I archived once it started feeling like a second job, and
[modern_inverted_mouse](https://github.com/MrxSiN/modern_inverted_mouse), which redraws the old inverted Windows cursors
so they stop looking like 2009. There's Dota 2 stuff here too —
[SmartCast](https://github.com/MrxSiN/DoTA2-SmartCast) and a
[compact keybind layout](https://github.com/MrxSiN/super-compact-dota2-keybinds) I keep tweaking instead of playing.

Currently poking at Pixel Launcher and SystemUI internals, and moving things over to modern libxposed.

## How I build

- **Put it where the app already keeps it.** A toggle belongs in the app's own settings screen, not in a separate launcher icon.
- **Assume the internals move.** Version checks and graceful failure are part of the feature, not cleanup work for later.
- **Keep it reversible.** One module, one job, no surprise changes to things I never advertised.
- **Source or it didn't happen.** Everything here builds from what you can read. GPL or MIT.

## Toolbox

<div align="center">

<img src="https://skillicons.dev/icons?i=kotlin,java,androidstudio,gradle,git,github,linux,windows,cpp,neovim&perline=10" alt="Kotlin, Java, Android Studio, Gradle, Git, GitHub, Linux, Windows, C++, Neovim" />

</div>

## Stats

<div align="center">

<img height="165em" src="https://github-readme-stats.vercel.app/api?username=MrxSiN&show_icons=true&theme=onedark&include_all_commits=true&count_private=true&hide_border=true" alt="GitHub stats" />
<img height="165em" src="https://github-readme-stats.vercel.app/api/top-langs/?username=MrxSiN&langs_count=6&layout=compact&theme=onedark&hide_border=true" alt="Top languages" />

<img width="85%" src="https://streak-stats.demolab.com/?user=MrxSiN&theme=onedark&hide_border=true" alt="Streak" />

<img width="95%" src="https://github-readme-activity-graph.vercel.app/graph?username=MrxSiN&bg_color=282c34&color=FDFD96&line=FDFD96&point=FFFFFF&area=true&area_color=79FE96&hide_border=true&title_color=FDFD96" alt="Activity graph" />

<sub>Malaysia 🇲🇾 · Bug report? Open an issue with your app version — that's usually the whole answer.</sub>

</div>
