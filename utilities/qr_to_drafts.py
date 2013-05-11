import qrcode
import os.path

def_path = '~/Desktop/'
def_filename = 'qr'
path = os.path.expanduser(def_path)

drafts_url = "drafts://x-callback-url/create?text={0}&action=Inbox"


def qr_create(text, filename=def_filename):
    img = qrcode.make(
        drafts_url.format(
            text.replace(' ', '%20')
        )
    )
    if not filename.endswith('.png'):
        filename += '.png'
    img.save(path + filename)


if __name__ == '__main__':
    import sys
    qr_create(' '.join(sys.argv[1:]))
