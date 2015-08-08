# -*- coding: utf-8 -*-
# CREATED ON DATE: 27.07.15
__author__ = 'mail@pythonic.ninja'

import re
import os
import sys
import json
import aiohttp
import asyncio


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
        print('Images to collect: ', len(images_links))
        self.download_parallel(links=images_links)

    @classmethod
    @asyncio.coroutine
    def download(cls, future, url):
        response = yield from aiohttp.request('GET', url)
        if response.status == 200:
            print("data fetched successfully for: %s" % url)
        else:
            print("data fetch failed for: %s" % url)
            print(response.content, response.status)

        content = yield from response.read()
        future.set_result(content)

    def download_image(self, link, name, view_box=1200):
        future = asyncio.Future()
        yield from self.download(future, link+'?viewBox='+str(view_box))
        image = future.result()

        for process in self.process_images:
            image = process(image, name)

        return image

    def download_image_list(self, api_url):
        links = []
        page = 0
        loop = asyncio.get_event_loop()
        while True:
            future = asyncio.Future()
            loop.run_until_complete(asyncio.wait([AmazonDownloader.download(future=future, url=api_url + '&offset=' + str(page))]))
            api_data = json.loads(future.result().decode('utf-8'))
            count = api_data['count']
            for data in api_data['data']:
                links.append((data['tempLink'], data['name']))
            print('images already found:', len(links))
            if len(links) != count:
                page += 200
            else:
                break
        return links

    @classmethod
    def optimize_save(cls, image, name, directory='downloaded'):
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, name), 'wb') as file_img:
            file_img.write(image)

    def transform_url(self, share_link):
        m = re.match(self.re_url_share, share_link)
        groups = m.groupdict()
        return self.url_api % groups

    def download_parallel(self, links, download_function=None):
        loop = asyncio.get_event_loop()

        if not download_function:
            download_function = self.download_image

        def download():
            yield from asyncio.gather(*[
                asyncio.Task(download_function(link[0], link[1]))
                for link in links
            ])

        loop.run_until_complete(download())


if __name__ == '__main__':
    amazon_downloader = AmazonDownloader(share_link=sys.argv[1])
