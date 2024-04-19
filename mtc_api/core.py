"""Core business logic for mtc-api"""

import logging
import re

from random import randint

from fastilybot.core import XQuery
from pwiki.dwrap import ImageInfo
from pwiki.mquery import MQuery
from pwiki.ns import NS
from pwiki.wiki import Wiki
from pwiki.wparser import WikiTemplate, WParser

log = logging.getLogger(__name__)

_MTC = "Wikipedia:MTC!"
_USER_AT_PROJECT = "{{{{User at project|{}|w|en}}}}"

WIKI = Wiki()
COM = Wiki("commons.wikimedia.org")
BLACKLIST = set(WIKI.links_on_page(f"{_MTC}/Blacklist"))
WHITELIST = set(WIKI.links_on_page(f"{_MTC}/Whitelist"))


def _fuzz_for_param(target_key: str, t: WikiTemplate, default: str = "") -> str:
    """Fuzzy match template parameters to a given `target_key` and return the result.

    Args:
        target_key (str): The target key to fetch.  Will try ignore-case & underscore/space permutations
        t (WikiTemplate): The WikiTemplate to check
        default (str, optional): The default return value if nothing matching `target_key` was found. Defaults to "".

    Returns:
        str: The value associated with `target_key`, or the empty `str` if no match was found.
    """
    if not t:
        return default

    rgx = re.compile(r"(?i)" + re.sub(r"[ _]", "[ _]", target_key) + "")
    return str(next((t[k] for k in t if rgx.match(k)), default)).strip()


def _generate_commons_title(titles: list[str]) -> dict:
    """Generates a title for a file on enwp in preparation for transfer to Commons.  If the name of the enwp file is not on Commons, then try various permutations of the title.

    Args:
        titles (list[str]): The enwp titles to generate Commons titles for 

    Returns:
        dict: A dict such that each key is the local file name and the value is the generated title for Commons.
    """
    out = {s: s for s in titles}

    for s in XQuery.exists_filter(COM, titles):
        base, ext = s.rsplit(".", 1)
        out[s] = result.pop() if (result := XQuery.exists_filter(COM, [f"{base} {i}.{ext}" for i in range(1, 11)] + [f"{base} {randint(1000,1000000)}.{ext}"], False)) else None

    return out


def _generate_text(title: str, is_own_work: bool, ii_l: list[ImageInfo]) -> str:
    """Generates Commons wikitext for the specified enwp file

    Args:
        title (str): The enwp title to make Commons wikitext for
        is_own_work (bool): Set `True` if this file is own work
        ii_l (list[ImageInfo]): The `ImageInfo` associated with `title`.

    Returns:
        str: The Commons wikitext generated for `title`.
    """
    if not (ii_l):
        log.error(f"No image info found for '{title}', please verify this exists on wiki.")
        return

    uploader = ii_l[-1].user

    # strip comments, categories, and wikitables (usually captions)
    txt = WIKI.page_text(title)
    for rgx in [r"(?s)<!--.*?-->", r"(?i)\n?\[\[Category:.+?\]\]", r"\n?==.*?==\n?", r'(?si)\{\|\s*?class\s*?=\s*?"wikitable.+?\|\}']:
        txt = re.sub(rgx, "", txt)

    # parse down text
    doc_root = WParser.parse(WIKI, title, txt)

    # drop templates we should not transfer (these exist on Commons)
    bl = {"Bots", "Copy to Wikimedia Commons"}
    for t in WikiTemplate.normalize(WIKI, *doc_root.all_templates(), bypass_redirects=True):
        if t.title in bl:
            t.drop()

    # drop templates which do not exist on Commons
    tl = doc_root.all_templates()
    drop_list = XQuery.exists_filter(COM, [(WIKI.convert_ns(t.title, NS.TEMPLATE) if WIKI.in_ns(t.title, NS.MAIN) else t.title) for t in tl], False)
    for t in tl:
        if (WIKI.convert_ns(t.title, NS.TEMPLATE) if WIKI.in_ns(t.title, NS.MAIN) else t.title) in drop_list:  # this is an uber dirty hack
            t.drop()

    # transform special templates
    info = None
    for t in doc_root.all_templates():
        if t.title == "Information":
            info = t
        elif t.title == "Self":
            if "author" not in t:
                t["author"] = _USER_AT_PROJECT.format(uploader)
        elif t.title == "GFDL-self":
            t.title = "GFDL-self-en"
            t["author"] = _USER_AT_PROJECT.format(uploader)
        elif t.title == "PD-self":
            t.title = "PD-user-en"
            t["1"] = uploader
        elif t.title == "GFDL-self-with-disclaimers":
            t.title = "GFDL-user-en-with-disclaimers"
            t["1"] = uploader

    if info:
        info.drop()

    # Add any Commons-compatible top-level templates to License section.
    lic_section = "== {{int:license-header}} =="
    for t in doc_root.all_templates():
        lic_section += f"\n{t}"
        t.drop()

    # fill out Information Template.  Don't use dedent, breaks on interpolated newlines
    desc = "== {{int:filedesc}} ==\n{{Information\n" + \
        f'|description={_fuzz_for_param("Description", info)}{str(doc_root).strip()}\n' + \
        f'|date={_fuzz_for_param("Date", info)}\n' + \
        f'|source={_fuzz_for_param("Source", info, "{{Own work by original uploader}}" if is_own_work else "")}\n' + \
        f'|author={_fuzz_for_param("Author", info, "[[User:{u}|{u}]]".format(u=uploader) if is_own_work else "")}\n' + \
        f'|permission={_fuzz_for_param("Permission", info)}\n' + \
        f'|other versions={_fuzz_for_param("Other_versions", info)}\n' + \
        "}}\n\n" + lic_section

    desc = re.sub(r"(?<=\[\[)(.+?\]\])", "w:\\1", desc)  # add enwp prefix to links
    desc = re.sub(r"(?i)\[\[w::", "[[w:", desc)  # Remove any double colons in interwiki links
    desc = re.sub(r"(?i)\[\[w:w:", "[[w:", desc)  # Remove duplicate interwiki prefixes
    desc = re.sub(r"\n{3,}", "\n", desc)  # Remove excessive spacing

    # Generate Upload Log Section
    desc += "\n\n== {{Original upload log}} ==\n" + f"{{{{Original file page|en.wikipedia|{WIKI.nss(title)}}}}}" + "\n{| class=\"wikitable\"\n! {{int:filehist-datetime}} !! {{int:filehist-dimensions}} !! {{int:filehist-user}} !! {{int:filehist-comment}}"
    for ii in ii_l:
        ii.summary = ii.summary.replace('\n', ' ').replace('  ', ' ') if ii.summary else ''
        desc += f"\n|-\n| {ii.timestamp:%Y-%m-%d %H:%M:%S} || {ii.height} \u00D7 {ii.width} || [[w:User:{ii.user}|{ii.user}]] || ''<nowiki>{ii.summary}</nowiki>''"

    return desc + "\n|}"


def generate_text_multi(titles: list[str], force: bool) -> dict:
    """Generates text for multiple files on enwp at a time.  Output can be used directly as the return json for the web service.

    Args:
        titles (list[str]): The list of enwp titles to generate titles/text for.  PRECONDITION: `titles` is non-empty and well-formed.

    Returns:
        dict: The output json
    """
    cat_map = MQuery.categories_on_page(WIKI, titles)

    if force:
        l = titles
        fails = []
    else:
        l = [title for title, cats in cat_map.items() if BLACKLIST.isdisjoint(cats) and not WHITELIST.isdisjoint(cats)]  # filter blacklist & whitelist
        l = [title for title, dupes in MQuery.duplicate_files(WIKI, l, False, True).items() if not dupes]  # don't transfer if already transferred
        fails = list(set(titles) - set(l))

    title_map = _generate_commons_title(l)
    image_infos = MQuery.image_info(WIKI, l)

    out = []
    for title in l:
        if (desc := _generate_text(title, "Category:Self-published work" in cat_map[title], image_infos[title])) and (com_title := title_map[title]):
            out.append({"enwp_title": title, "com_title": com_title, "desc": desc})
        else:
            log.warn("Could not generate title or wikitext for '%s', skipipng...", title)
            fails.append(title)

    return {"generated_text": out, "fails": fails}
