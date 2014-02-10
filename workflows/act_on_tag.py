import todoflow
import subprocess

from todoflow.src.utils import remove_tags
# Actions

def open_action(tag, item):
    path = item.get_tag_param(tag)
    subprocess.check_output('open "{0}"'.format(path), shell=True)
    return True


def alfred_search_action(prefix):
    def f(tag, item):
        query = ' '.join([prefix, remove_tags(item.text)])
        subprocess.call(
            'osascript -e "tell application \\"Alfred 2\\" to search \\"{0}\\""'.format(query),
            shell=True
        )
    return f


def open_website_action(url):
    def f(tag, item):
        full_url = url.format(query=remove_tags(item.text))
        subprocess.call('open "{0}"'.format(full_url), shell=True)
        return True
    return f


def put_to_clipboard_action(tag, item):
    subprocess.call('echo ' + item.text + ' | pbcopy', shell=True)

# Config

tag_to_action = {
    'mail': open_action,
    'web': open_action,
    'file': open_action,
    'search': open_website_action('http://google.com/search?q={query}'),
    'research': open_website_action('http://google.com/search?q={query}'),
    'imgsearch': open_website_action('http://google.com/search?q={query}&source=lnms&tbm=isch'),
    'download': alfred_search_action('pb'),
    'tvseries': alfred_search_action('pb'),
    'comics': alfred_search_action('pb'),
}

# Act on tag

def act_on_tag_id(item_id):
    item = todoflow.get_item(item_id)
    act_on_tag(item)


def act_on_tag(item):
    for tag in tag_to_action:
        if item.has_tag(tag):
            should_continue = tag_to_action[tag](tag, item)
            if not should_continue:
                return
    