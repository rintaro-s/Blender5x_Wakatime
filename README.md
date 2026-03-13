**WakatimeBlender** is a simple plugin for the [Blender](https://www.blender.org/) 3D graphics software that sends time-tracking statistics to the [Wakatime](https://wakatime.com) online service using official wakatime client.

**Supports Blender 5.0 and later versions.**

(At least it worked in 5.0.1.)

#### Features (English)
- Tracks editing + save/write activity for the currently opened *.blend* file and sends heartbeats via the official `wakatime-cli`.
- Auto-loads `~/.wakatime.cfg` (API key, API URL, heartbeat rate limit, custom project name) and surfaces the state directly inside Blender preferences.
- Offers a project-name builder (folder/file based, trim chars, prefix/postfix) plus optional global override flags.
- Bundles a downloader to keep `wakatime-cli` updated from GitHub releases with status logs in Blender.
- Provides a reload button + rich debug logs to help diagnose configuration problems instantly.

#### Quick Usage (English)
- Install the ZIP via *Edit → Preferences → Add-ons → Install...* and enable **Wakatime**.
- Save your `.blend` file so WakaTime receives a valid path.
- Open *Blender → System → Wakatime Preferences* (or search “wakatime”) to enter the API key / custom settings.
- Optionally edit the project-name rules, heartbeat frequency, and custom project override to fit your workflow.
- Use the **Reload Config** button if you edit `~/.wakatime.cfg` outside Blender.

#### 機能 (日本語)
- 現在開いている *.blend* ファイルでの編集・保存アクティビティを検知し、公式 `wakatime-cli` を通じてハートビートを送信します。
- `~/.wakatime.cfg`（APIキー／API URL／ハートビート間隔／カスタムプロジェクト名）を自動読み込みし、Blender内の設定画面に反映します。
- フォルダー／ファイル名・接尾文字削除・プレフィックス／ポストフィックスなど柔軟なプロジェクト名生成機能を搭載、グローバル上書きも設定可能。
- GitHubの最新リリースから `wakatime-cli` を取得・更新するダウンローダーを同梱し、進捗をBlenderログに表示します。
- 設定リロードボタンと詳細なデバッグログで、設定ミスを即座に特定できます。

#### 使い方 (日本語)
- *編集 → 設定 → アドオン → Install...* からZIPを導入し、**Wakatime** を有効化します。
- `.blend` ファイルを保存して、WakaTimeに有効なパスを渡します。
- *Blender → システム → Wakatime Preferences*（または検索で「wakatime」）を開き、APIキーや各種設定を入力します。
- プロジェクト名ルール、ハートビート間隔、カスタムプロジェクト名を必要に応じて調整します。
- Blender外で `~/.wakatime.cfg` を編集した場合は **Reload Config** ボタンで即反映します。

### Installation

To install the plugin you need to download the source code [zip archive](https://github.com/wakatime/blender-wakatime/archive/refs/heads/master.zip).

Save it somewhere, open the Blender, go to *Edit->Preferences...->Add-ons->Install...*

![Install](https://imgur.com/5FtTClK.png)

Select the downloaded `.zip` and click `Install Addon`.

![Installation2](https://imgur.com/rhlzNPe.png)

Then check the check-box near the plugin name in the list to enable it.

![Installation1](https://imgur.com/2ve0YJ9.png)

After that a dialog prompting to enter the Wakatime API key may appear. Enter your key here and push "OK". If the key is incorrect and an attempt to send statistics fails the dialog will show up again.

![WakatimePreferences](https://imgur.com/vmYBiPx.png)

If wish to change the key or other settings, press Space to summon the floating search menu, then start type "wakatime" until corresponding actions are shown. Select "Wakatime Preferences" to summon the dialog again.

![WakatimeActions](https://imgur.com/OPo290V.png)

Another way to get to this dialog is through the _Blender->System->_ menu

![WakatimeMenu](https://imgur.com/HhUoVxf.png)

When setup is finished, the plugin should start sending the time you've spent on the currently loaded .blend file automatically in the background. **Note**, that unless you save a newly created file no stats are gathered, because Wakatime needs a filepath.

If you need to re-download wakatime client, use the menu/search action "Download wakatime client". The progress will be reported in the "Info" window as well as on the status bar.

![DownloadWakatime](https://imgur.com/HQiQ6ne.png)

### Configuration
Wakatime will try to detect the projects name, e.g. from the git-repo.
If you do not work with git, the project's name would be "Unknown Project" within Wakatime.
<br/>
So this Add-On can _construct_ the project name from the current `.blend` file name or from the name of its parent folder.

To fine-tune the project's name there are some options available under _Blender->System->Wakatime Preferences_ (or through the global search menu).

![WakatimePreferences](https://imgur.com/vmYBiPx.png)

The first two check-boxes allow you to decide whether to **always** use the guessed name from this Add-On, effectively overwriting WakaTime discovered name (i.e. the git-repo).

- _Overwrite project-discovery by default_ - sets the global default (stored in .wakatime.cfg), which **applies to new files**
- _Overwrite project-discovery with the name from below_ - enables project descovery override **for the current `.blend` file**

The following options only work when the _Overwrite project-discovery with the name from below_ is enabled.

The _Use folder-name as projectname_ check-box enables the use of .blend file parent folder name as the base of the Wakatime-project-name:
* if not checked (the default) - the file name (without the `.blend` extension) is used
* if checked - the name of the folder containing the `.blend` file is used

With the project-name extracted, further processing takes place:
1. If there are specific (default: numbers, underscores and dots) **trailing** characters, those will be removed too.
2. Optional: add a prefix to the project's title.
3. Optional: add a postfix to the project's title.

The _Heartbeat Frequency_ option allows to change the interval (in minutes) of sending _idle_ activity reports to wakatime server.

#### Examples
1. To give the project-name a ".blend"-extension, add ".blend" in the postfix-text-field.
2. To only remove trailing numbers (e.g. versions), enter "1234567890" in the trailing character-text-field and press enter.
3. To remove numbers, underscores and dots, enter "1234567890.\_" in the trailing character-text-field and press enter. (This is the default.)
4. To turn "captain_afterburner.blend" into the project-name "\[blender\] captain_afterburner", set the prefix to "\[blender\] ", the postfix to "" (nothing).
5. To turn "captain_afterburner_05.blend" into the project-name "\[blender\] captain_afterburner", apply steps #3 and #4 together.
6. If you want to use the directory's name, check "Use folder-name as project-name". All steps from #1 to #5 can still be used to adjust the name.
7. To prevent any adjusting of the projects-name, remove all the characters from all three text-fields and press enter.

### Contribution

When working on issues and/or new features, please, use the latest stable Blender _and the python it bundles_.

Before submitting a PR, always format the code with [`black`](https://github.com/psf/black). _I don't particularly like
its style myself, but it's the easiest-to-set-up common ground._
