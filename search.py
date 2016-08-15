#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import re
import urllib2
import json
import csv
import codecs
import os
import socket
from socket import AF_INET, SOCK_DGRAM
from contextlib import contextmanager


def load_credentials():
    with open('credentials.json') as fd:
        _ = json.load(fd)
        client_access_token = _.get('access_token')
        client_id     = _.get('client_id', 'fillinyourclientid-OPTIONAL')
        client_secret = _.get('client_secret', 'fillinyourclientsecret-OPTIONAL')
        return client_id, client_secret, client_access_token


@contextmanager
def setup(search_term):
    dst = 'output/'
    if not os.path.exists(dst):
        os.makedir('output')

    try:
        outputfilename = 'output/output-{}.csv'.format(
            re.sub(r'[^A-Za-z]+', '', search_term))

        with codecs.open(outputfilename, 'ab', encoding='utf8') as outputfile:
            outwriter = csv.writer(outputfile)
            if os.stat(outputfilename).st_size == 0:
                header = ['page', 'id', 'title',
                          'url', 'path', 'header_image_url',
                          'annotation_count', 'pyongs_count',
                          'primaryartist_id', 'primaryartist_name',
                          'primaryartist_url', 'primaryartist_imageurl']
                outwriter.writerow(header)
            yield outwriter
    finally:
        pass


def search(search_term,outputfilename, client_access_token):
    with setup(search_term) as outwriter:
        page=1
        while True:
            querystring = 'http://api.genius.com/search?q=' +\
                          urllib2.quote(search_term) +\
                          '&page=' +\
                          str(page)

            request = urllib2.Request(querystring)
            request.add_header('Authorization', 'Bearer ' + client_access_token)
            request.add_header('User-Agent', 'curl/7.9.8 (i686-pc-linux-gnu) '
                               'libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)')
            while True:
                try:
                    response = urllib2.urlopen(request, timeout=4)
                    raw      = response.read()
                except socket.timeout:
                    print('Timeout raised and caught')
                    continue
                break

            json_obj = json.loads(raw)
            body     = json_obj['response']['hits']
            num_hits = len(body)
            if num_hits == 0:
                if page == 1:
                    print('No results for: ' + search_term, file=sys.stderr)
                break
            print('page {0}; num hits {1}'.format(page, num_hits))

            for result in (x['result'] for x in body):
                print(json.dumps(result, sort_keys=True,
                                 indent=4, separators=(',', ': '))
                )
                exit(1)
                result_id = result['id']
                title = result['title']
                url   = result['url']
                path  = result['path']
                header_image_url = result['header_image_url']
                annotation_count = result['annotation_count']
                pyongs_count     = result['pyongs_count']
                primaryartist_id   = result['primary_artist']['id']
                primaryartist_name = result['primary_artist']['name']
                primaryartist_url  = result['primary_artist']['url']
                primaryartist_imageurl = result['primary_artist']['image_url']
                row  = [page, result_id, title,
                        url, path, header_image_url,
                        annotation_count, pyongs_count, primaryartist_id,
                        primaryartist_name, primaryartist_url, primaryartist_imageurl]
                outwriter.writerow(row) # write as CSV
            page += 1


def main():
    # so you can input searches from command line if you want
    arguments   = sys.argv[1:]
    search_term = arguments[0].translate(None, '\'\"')
    outputfilename = setup(search_term)
    client_id, client_secret, client_access_token = load_credentials()
    search(search_term,outputfilename,client_access_token)


if __name__ == '__main__':
    main()
