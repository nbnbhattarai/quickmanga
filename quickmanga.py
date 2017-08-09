#!/usr/bin/env python
import requests
from lxml import html
import os
from tqdm import tqdm
import pydoc
import string
from urllib.request import urlretrieve
import sys
import getopt

url_mangalist = 'http://www.mangapanda.com/alphabetical'
url_root = 'http://www.mangapanda.com'
base_dir = os.path.abspath(__file__)


def read_mana_name():
    return input('Enter Manga Name: ')


def get_manga_by_url(manga_url):
    tmp_url = url_root+manga_url
    page = requests.get(tmp_url)
    tree = html.fromstring(page.content)
    manga_name = tree.xpath('//div[@id="mangaproperties"]/table/tr/td/h2[@class="aname"]/text()')
    return (manga_name[0], manga_url)


def search_manga(manga_name, show_selection=True):
    print('Searching %s . \r' % (manga_name), end='')
    page = requests.get(url_mangalist)
    # print(page)
    tree = html.fromstring(page.content)
    manga_list = tree.xpath(
        '//div[@class="series_alpha" and ./h2/a/text()="%c"]/ul/li/a/text()'
        % (manga_name[0].upper()))
    result = []
    if len(manga_list) == 0:
        print("No result found !")
        return None
    manga_urls = tree.xpath(
        '//div[@class="series_alpha" and ./h2/a/text()="%c"]/ul/li/a/@href'
        % (manga_name[0].upper()))
    # print(manga_urls)
    mangas = dict(zip(manga_list, manga_urls))
    for manga in mangas:
        if manga_name.lower() in manga.lower():
            result.append((manga, mangas[manga]))
    if not show_selection:
        return result
    print("Results:")
    # print(result)
    for i, r in enumerate(result):
        print("#%i\t%s" % (i, r[0]))
    manga_result = None
    while True:
        index = int(input('Select One :'))
        if index >= 0 and index < len(result):
            manga_result = (result[index])
            break
        else:
            print("Invalid Selection")
            continue
    return manga_result


def get_episode_count(manga_url):
    url = url_root + manga_url
    page = requests.get(url)
    tree = html.fromstring(page.content)
    latest_episode = tree.xpath('//div[@id="latestchapters"]/ul/li[1]/a/@href')
    # print(latest_episode)
    return latest_episode[0].split('/')[-1]


def get_episodes_list(manga):
    url_tmp = url_root+manga[1]
    page = requests.get(url_tmp)
    tree = html.fromstring(page.content)
    episodes_n = tree.xpath(
        '//div[@id="chapterlist"]/table[@id="listing"]/tr/td[a]/text()'
    )
    episodes_c = tree.xpath(
        '//div[@id="chapterlist"]/table[@id="listing"]/tr/td/a/text()'
    )
    episodes_name = [e.split(':')[-1].strip() for e in episodes_n if ':' in e]
    episodes_count = [ec.split()[-1].strip() for ec in episodes_c]
    episodes_all = dict(zip(episodes_count, episodes_name))
    return episodes_all


def download_episode(manga, episodes):
    try:
        os.mkdir(manga[0])
    except:
        pass
    os.chdir(manga[0])
    print("Downloading in dir ./%s" % (manga[0]))
    episodes_count = get_episode_count(manga[1])
    episodes_all = get_episodes_list(manga)
    if '*' in episodes:
        episodes = [str(x) for x in range(1, int(episodes_count)+1)]
    for episode in episodes:
        if str(episode) not in episodes_all:
            print('Episode %i not available!' % (int(episode)))
            continue
        episode_url = url_root+manga[1]+'/'+str(episode)
        try:
            os.mkdir('Chapter ' + episode + ' ' + episodes_all[episode])
        except:
            pass
        os.chdir('Chapter ' + episode + ' ' + episodes_all[episode])
        page = requests.get(episode_url)
        tree = html.fromstring(page.content)
        page_count = len(tree.xpath('//select[@id="pageMenu"]/option/text()'))
        for p in range(1, page_count):
            episode_page_url = episode_url + '/' + str(p)
            # print('Episode %i : %s' % (p, episode_page_url))
            page = requests.get(episode_page_url)
            tree = html.fromstring(page.content)
            image_url = tree.xpath('//img[@name="img"]/@src')[0]
            filename = str(p) + '.' + image_url.split('.')[-1]
            print('Downloading Episode #%s %s (%i/%i) ...\r' % (episode, episodes_all[episode], p, page_count), end='')
            response = requests.get(image_url, stream=True)
            with open(filename, "wb") as handle:
                for data in response.iter_content():
                    handle.write(data)
        print('Downloaded  Episode #%s %s (%i/%i) ...\r' % (episode, episodes_all[episode], page_count, page_count))
        os.chdir('..')


def get_user_action():
    while True:
        manga_name = read_mana_name()
        manga_result = search_manga(manga_name)

        while True:
            print(
                "Actions:\n1. Download\n2. List Episode\n0. Back\n"
            )
            i = input('> ')
            if i == '1':
                print("\nEnter comma seperated episode number like 1,2,3,60 \nEnter * to download all episodes like *")
                episodes = input('> ')
                episodes = episodes.split(',')
                if '*' in episodes:
                    download_episode(manga_result, ['*'])
                else:
                    download_episode(manga_result, episodes)
            elif i == '2':
                episode_list = get_episodes_list(manga_result)
                sorted_list = sorted(
                    episode_list,
                    key=lambda x: int(x.lower().rstrip(
                        string.ascii_lowercase)))
                text = '{:25s} {:25s}\n'.format('Episode #', 'Episode Name')
                for i in sorted_list:
                    text += '{:25s} {:25s}\n'.format(str(i), episode_list[i])
                pydoc.pager(text)
            elif i == '0':
                break
            else:
                continue


def print_usage():
    print("Usage: ./quickmanga.py -S <> -D <> -R <> -L <>")


def print_help():
    print_usage()
    print('''
    Options
    -------------
    -h      --help          print this help message
    -S      --search        search Manga
    -D      --download      Download Manga, provide url
    -R      --read          Read Manga, provide url
    -L      --latest        Read Latest Manga, provide url
    -E      --episode       Specify Episode
    ''')


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hS:D:L:E:", ["help", "search=", "download=", "read=", "episode="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    episodes_t = []
    for opt, arg in opts:
        if opt in ('-E', '--episode'):
            episodes_t = arg.split(',')

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-S", "--search"):
            manga_name = arg
            result = search_manga(manga_name, show_selection=False)
            print('{:10s} {:25s} {:25s} '.format('#', 'Manga Name', 'Manga URL'))
            for i, r in enumerate(result, 1):
                print('{:10s} {:25s} {:25s}'.format(str(i), r[0], r[1]))

        # Download this manga
        elif opt in ("-D", "--download"):
            manga_url = arg
            if manga_url[0] != '/':
                manga_url = '/'+manga_url
            manga = get_manga_by_url(manga_url)
            download_episode(manga, episodes_t)

        # Read This manga
        elif opt in ("-R", "--read"):
            manga_url = arg
            if manga_url[0] != '/':
                manga_url = '/'+manga_url
            print('To Read %s' % (manga_url))


if __name__ == '__main__':
    # name = read_mana_name()  
    # manga_result = search_manga(name)
    # episode_count = get_episode_count(manga_result[1])
    # manga = ('One Piece', '/one-piece')
    # episodes = ['10', '12']
    # download_episode(manga, episodes)
    # action = get_u
    main(sys.argv[1:])
    # get_user_action()
