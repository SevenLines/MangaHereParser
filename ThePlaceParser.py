#!/usr/bin/python
import argparse
import os
from time import sleep

import urllib2
import re
import bs4
import socket
from Parser import Parser
from Parser import tr

class ThePlace(Parser):
    baseUrl = "http://www.theplace.ru/"
    chaptersPage = "photos/gallery.php"
    encoding = "cp1251"
    chapterItemSelector = ".listalka a"
    chapterItemAttr = "href"
    chapterNameSelector = "h1"
    chapterNameAttr = ""
    pageItemSelector = ".gallery-pics-list .pic_box a"
    pageItemSelectorAttr = "href"
    imageItemSelector = ".pic-big-box img"
    imageItemSelectorAttr = "src"

    def chapterUrl(self, id):
        return  str.format("{0}?id={1}", self.chaptersPage, id )

    def getReferer(self):
        return self.baseUrl;

    def getChapters(self, id):
        pageUrl = self.chapterUrl(id)
        s = self.getPage(pageUrl)

        soup = bs4.BeautifulSoup(s)
        li = soup.select(self.chapterItemSelector)

        hrefs = list(item[self.chapterItemAttr] for item in li)
        prog = re.compile('page=(\d+)')
        maxPage =  max(int(prog.search(href).group(1)) for href in hrefs)

        hrefs = list( str.format('{0}?id={1}&page={2}', self.chaptersPage, id, num+1) for num in xrange(maxPage))
        return hrefs

    def getImagesList(self, imagesPage):
        imageList = list( self.getPath(item) for item in Parser.getImagesList(self, imagesPage) )
        return  imageList

    def getChapterName(self, id):
        pageUrl = self.chapterUrl(id)
        s = self.getPage(pageUrl)
        soup = bs4.BeautifulSoup(s)
        li = soup.select(self.chapterNameSelector)[0]
        if not self.chapterNameAttr:
            return li.text
        else:
            return li[self.chapterNameAttr]

    def getPagesList(self, chapterPage):
        pages = list(item for item in Parser.getPagesList(self, chapterPage) if item[:3]!='/ar')
        return pages


def exists_rec(path, fileName):
    for root, subFolders, files in os.walk(path):
        if fileName in files:
            return 1
    return 0

def main():

    # create site parser
    the_place = ThePlace()

    # parse command line args
    parser = argparse.ArgumentParser()

    parser.add_argument('--personId', '-i', help="person id, for example 2275 for Megan Fox", default=-1, type=str)
    parser.add_argument('--outputDir', '-o', metavar="", help='output dir, by default: .', default='.', type=str)
    parser.add_argument('--firstChapter', '-f', metavar="",
                        help='the first chapter for download in the order as it appears on site', default=1, type=int)
    parser.add_argument('--lastChapter', '-l', metavar="", help='the last chapter for download', default=-1, type=int)
    parser.add_argument('--overwrite', '-w', metavar="", help='reload picture if it exists', default=0, type=bool)
    parser.add_argument('--makeDirs', '-d', help='set if u want to create folder for each set', default=0, type=bool)

    args = parser.parse_args()

    if args.personId == -1:
        value = ""
        while not value.isdigit():
            value = raw_input("enter person id:")
        args.personId = value;

    # assign args
    firstChapter = args.firstChapter
    lastChapter = args.lastChapter
    savePath = args.outputDir


    #get chapters list
    chapters = the_place.getChapters(args.personId)

    # recalculate chapter list
    if lastChapter != -1:
        lastChapter = min(lastChapter, len(chapters))
    else:
        lastChapter = len(chapters)

    # assign chapter counter
    counter = 1

    saveDir = savePath + '/' + the_place.getChapterName(args.personId)

    # create dirs
    if not os.path.exists(saveDir):
        os.makedirs( saveDir )


    pCounter = 1
    # itterate over chapters
    for chapter in chapters:

        if  counter > lastChapter:
            break

        # skipping some chapters if nessacery
        if counter >= firstChapter:

            pages = the_place.getPagesList(chapter)

            pCounter = 1
            for page in pages:
                # inform user
                print(str.format("[{0}/{1}] - [{2}/{3}]",
                                 counter,
                                 lastChapter,
                                 pCounter,
                                 len(pages)))

                # get image url
                imageUrl = the_place.getImagesList(page)[0]
                saveName = the_place.getImageName(imageUrl)

                savePath = os.path.abspath(saveDir + '/' + saveName)

                # check for existance
                if not os.path.exists(savePath) or args.overwrite:
                    # get image data
                    imageData = the_place.getPageBytes(imageUrl, 0);

                    # write file to disk
                    file = open(savePath, 'wb')
                    file.write(imageData)
                    file.close()

                    # inform user
                    print( unicode.format(tr(u'{0} -> "{1}"'), saveName, savePath) )

                    # sleep a bit
                    print(tr('sleep 1 sec'))
                    sleep(1)
                else:
                    print( unicode.format(u'skip "{0}"', saveName))

                pCounter+=1
        counter += 1

    print tr("parsing ended! ^_^")


if __name__ == '__main__':
    main()
