"""
Usage:
    client.py [--push --url=<url> --tag=<tag>] [--complete --url=<url>]

    client.py (-h | --help)
"""

from requests import put, get, post
import json
from docopt import docopt
import sys

if __name__ == '__main__':
    args = docopt(__doc__, version='umami client 1.0')

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    # Push a new task
    if args['--push']:
        url = args['--url']
        tag = args['--tag']

        if len(url) == 0 or len(url[0]) == 0:
            print 'url is not available'
            sys.exit()

        if len(tag) == 0 or len(url[0]) == 0:
            print 'tag is not available'
            sys.exit() 

        url = url[0]
        tag = tag[0]
        data =  {
                    'url': url, 
                    'tag': tag
                }
        api_url = "http://localhost:5000/pushTask"
        r = post(api_url, data=json.dumps(data), headers=headers)
        print r.text

    # Complete task
    if args['--complete']:
        url = args['--url']
        if len(url) == 0 or len(url[0]) == 0:
            print 'url is not available'
            sys.exit()
            
        data =  {'url': url}
        api_url = "http://localhost:5000/completeTask"
        r = post(api_url, data=json.dumps(data), headers=headers)
        print r.text

    # # Get pushed tasks
    # url = "http://localhost:5000/getPushedTasks"
    # r = get(url, headers=headers)
    # print r.text

    # # Get required tasks
    # url = "http://localhost:5000/getRequiredTasks"
    # r = get(url, headers=headers)
    # print r.text

