import os
import re
import sys

if __name__ == '__main__':
    file_to_transform = sys.argv[1]
    print("Tranforming the raw actorle file at {}".format(file_to_transform))

    with open(file_to_transform, "r") as raw_file:
        raw_content = raw_file.readlines()

    if len(raw_content) != 1:
        print("The raw content must be on a single line - not sure how to handle this file, exiting")
        sys.exit(1)
    raw_content = raw_content[0]
    preamble_html = '<table cellspacing="0" cellpadding="0"><thead><tr class="css-yww95x"><th align="left" class="css-yxjuuu"><div class="css-11d1x01"><button type="button" class="ant-btn ant-btn-circle ant-btn-primary ant-btn-sm"><span>?</span></button></div>Movie Title</th><th align="left" class="css-x4em2r">Genres</th><th align="left" class="css-hz967x">IMDB</th></tr></thead><tbody>'
    transformed_content = raw_content.replace(preamble_html, '')
    transformed_content = transformed_content.replace('<tr><td class="css-78tlv6"><div class="css-16gxh5a"><span class="css-mmvz9h">', '\n')
    transformed_content = transformed_content.replace('</span></div><div class="css-1fapvp5">', '|')
    transformed_content = transformed_content.replace('</div><div class="css-iyxy5d"></div></td><td class="css-wen7vf">', '|')
    transformed_content = transformed_content.replace('</span></td><td class="css-ptlbxk"><div class="css-zjik7"><div class="css-19ufyx7">', '|')
    transformed_content = transformed_content.replace('</div></div></td></tr>', '')
    transformed_content = re.sub('</span><span class="ant-tag css-[a-z0-9]{5,}">', ',', transformed_content)
    transformed_content = transformed_content.replace('</span></td><td class="css-1k81oxp"><div class="css-zjik7"><div class="css-1ntf0l5">', '|')
    transformed_content = re.sub('<span class="ant-tag css-[a-z0-9]{5,}">', '', transformed_content)
    transformed_content = transformed_content.replace('</tbody></table>', '')
    transformed_content = transformed_content.replace('&amp;', '&')
    # remove blank lines
    transformed_content = os.linesep.join([s for s in transformed_content.splitlines() if s])
    print("\nThe transformed content looks like:\n'{}'\n".format(transformed_content))

    with open(file_to_transform, "wt") as transformed_file:
        transformed_file.write(transformed_content)
    print("Transformed the raw actorle file at {}".format(file_to_transform))
