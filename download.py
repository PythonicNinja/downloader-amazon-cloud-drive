# -*- coding: utf-8 -*-
# CREATED ON DATE: 27.07.15
__author__ = 'mail@pythonic.ninja'

import re
import os
import sys
import json
import urllib2
from threading import Thread


class AmazonDownloader(object):
    re_url_share = r'https://www.amazon.com/clouddrive/share/(?P<share_id>[^\/]+)/folder/(?P<folder>[^\/]+)'
    url_api = 'https://www.amazon.com/drive/v1/nodes/%(folder)s/children?tempLink=true&shareId=%(share_id)s'

    def __init__(self, share_link, process_images=()):
        api_url = self.transform_url(share_link)
        images_links = self.download_image_list(api_url)
        if not process_images:
            self.process_images = (
                AmazonDownloader.optimize_save,
            )
        print 'Images to collect: ', len(images_links)
        self.download_parallel(links=images_links)

    def download(self, url):
        response = urllib2.urlopen(url)
        print 'downloading:', url
        return response.read()

    def download_image(self, link, name, view_box=1200):
        image = self.download(link+'?viewBox='+str(view_box))

        for process in self.process_images:
            image = process(image, name)

        return image

    def download_image_list(self, api_url):
        links = []
        page = 0
        while True:
            api_data = json.loads(self.download(api_url + '&offset=' + str(page)))
            count = api_data['count']
            for data in api_data['data']:
                links.append((data['tempLink'], data['name']))
            print 'images already found:', len(links)
            if len(links) != count:
                page += 200
            else:
                break
        return links

    @classmethod
    def optimize_save(cls, image, name, directory='downloaded'):
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, name), 'w') as file_img:
            file_img.write(image)

    def transform_url(self, share_link):
        m = re.match(self.re_url_share, share_link)
        groups = m.groupdict()
        return self.url_api % groups

    def download_parallel(self, links, download_function=None):
        if not download_function:
            download_function = self.download_image

        for i, link in enumerate(links):
            print str(i)+'/'+str(len(links))
            Thread(target=download_function, args=(link[0], link[1])).start()


if __name__ == '__main__':
    amazon_downloader = AmazonDownloader(share_link=sys.argv[1])
