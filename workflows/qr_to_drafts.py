import qrcode
import os.path
import subprocess

def_path = '~/Desktop/'
def_filename = 'qr'
path = os.path.expanduser(def_path)

drafts_url = "drafts://x-callback-url/create?text={0}&action=Inbox&x-success=scan:"


def qr_create(text, filename=def_filename):
    img = qrcode.make(
        drafts_url.format(
            text.replace(' ', '%20')
        )
    )
    if not filename.endswith('.png'):
        filename += '.png'
    img.save(path + filename)
    subprocess.call('open "' + path + filename + '"', shell=True)

if __name__ == '__main__':
    import sys
    if len(sys.argv) <= 1:
        print 'text to qr'
        sys.exit(0)
    qr_create(' '.join(sys.argv[1:]))
