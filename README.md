# mtc-api
[![Python 3.11+](https://upload.wikimedia.org/wikipedia/commons/6/62/Blue_Python_3.11%2B_Shield_Badge.svg)](https://www.python.org)
[![MediaWiki 1.35+](https://upload.wikimedia.org/wikipedia/commons/b/b3/Blue_MediaWiki_1.35%2B_Shield_Badge.svg)](https://www.mediawiki.org/wiki/MediaWiki)
[![License: GPL v3](https://upload.wikimedia.org/wikipedia/commons/8/86/GPL_v3_Blue_Badge.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)

mtc-api is an API that assists with file imports from Wikipedia to Commons.  It provides a simple interface web service API that can batch generate description pages and new titles for transfer candinates.

👉 This API does not perform the actual transfers, it is only able to generate description pages and new titles.

## Usage
### POST `/generate`
Takes a list of titles of files on enwp and attempts to generate file description pages and a title for each file for when the file is transferred to Commons.  This route by default also filters files which may not be appropriate for Commons.  This functionality can optionally be disabled by passing the key-value pair `force: true` at the top level of the payload JSON.


#### Basic Example
<details>
  <summary>Body</summary>

```json
{
    "titles": [
        "File:Diarmuid Lynch.jpg",
        "File:DFO dog stare.JPG"
    ]
}
```
</details>

<details>
  <summary>Response</summary>

```json
{
    "fails": [
        "File:Diarmuid Lynch.jpg"
    ],
    "generated_text": [
        {
            "com_title": "File:DFO dog stare.JPG",
            "desc": "== {{int:filedesc}} ==\n{{Information\n|description=for use in my user space.\n|date=\n|source=\n|author=\n|permission=\n|other versions=\n}}\n\n== {{int:license-header}} ==\n{{Cc-by-sa-4.0}}\n{{Own}}\n\n== {{Original upload log}} ==\n{{Original file page|en.wikipedia|DFO dog stare.JPG}}\n{| class=\"wikitable\"\n! {{int:filehist-datetime}} !! {{int:filehist-dimensions}} !! {{int:filehist-user}} !! {{int:filehist-comment}}\n|-\n| 2020-11-01 18:04:48 || 4000 × 6000 || [[w:User:Deepfriedokra|Deepfriedokra]] || ''<nowiki>{{own work}} for use in my user space.</nowiki>''\n|}",
            "enwp_title": "File:DFO dog stare.JPG"
        }
    ]
}
```
</details>

#### Filter Disabled Example
<details>
  <summary>Body</summary>

```json
{
    "titles": [
        "File:FleetwoodLeyland.jpg",
        "File:DFO dog stare.JPG"
    ],
    "force": true
}
```
</details>

<details>
  <summary>Response</summary>

```json
{
    "fails": [],
    "generated_text": [
        {
            "com_title": "File:FleetwoodLeyland.jpg",
            "desc": "== {{int:filedesc}} ==\n{{Information\n|description=Fleetwood-Smith (second from right) has England batsman [[w:Maurice Leyland]] caught at slip by [[w:Arthur Chipperfield]], one of his ten wickets in the fourth Test at [[w:Adelaide Oval]] - from the 1936-37 cricket series between Australia and England.\n|date=c. 1936-7\n|source=\n|author=\n|permission=Image is pre-1955 and therefore in the Public Domain.\n|other versions=\n}}\n\n== {{int:license-header}} ==\n{{PD-URAA|pdsource=yes}}\n{{PD-Australia|1=commons}}\n\n== {{Original upload log}} ==\n{{Original file page|en.wikipedia|FleetwoodLeyland.jpg}}\n{| class=\"wikitable\"\n! {{int:filehist-datetime}} !! {{int:filehist-dimensions}} !! {{int:filehist-user}} !! {{int:filehist-comment}}\n|-\n| 2007-12-17 07:14:40 || 252 × 472 || [[w:User:Phanto282|Phanto282]] || ''<nowiki>Pic fromt the 1936-37 cricket series between Australia and England. Image is pre-1955 and therefore in the Public Domain. {{Template:PD-Australia}}</nowiki>''\n|}",
            "enwp_title": "File:FleetwoodLeyland.jpg"
        },
        {
            "com_title": "File:DFO dog stare.JPG",
            "desc": "== {{int:filedesc}} ==\n{{Information\n|description=for use in my user space.\n|date=\n|source=\n|author=\n|permission=\n|other versions=\n}}\n\n== {{int:license-header}} ==\n{{Cc-by-sa-4.0}}\n{{Own}}\n\n== {{Original upload log}} ==\n{{Original file page|en.wikipedia|DFO dog stare.JPG}}\n{| class=\"wikitable\"\n! {{int:filehist-datetime}} !! {{int:filehist-dimensions}} !! {{int:filehist-user}} !! {{int:filehist-comment}}\n|-\n| 2020-11-01 18:04:48 || 4000 × 6000 || [[w:User:Deepfriedokra|Deepfriedokra]] || ''<nowiki>{{own work}} for use in my user space.</nowiki>''\n|}",
            "enwp_title": "File:DFO dog stare.JPG"
        }
    ]
}
```
</details>

## Useful commands
```bash
# start development server
python -m mtc_api

# use gunicorn to run in prod
gunicorn -w 2 -b "0.0.0.0:8000" mtc_api.__main__:app
```