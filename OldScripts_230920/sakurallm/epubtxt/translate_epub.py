import json
import time
import os, re
import fnmatch
import glob
import shutil
import zipfile
from tqdm import tqdm

TEXT_LEN = 512

def find_all_htmls(root_dir):
    html_files = []
    for foldername, subfolders, filenames in os.walk(root_dir):
        for extension in ['*.html', '*.xhtml', '*.htm']:
            for filename in fnmatch.filter(filenames, extension):
                file_path = os.path.join(foldername, filename)
                html_files.append(file_path)
    return html_files

def get_html_text_list(epub_path, text_length):
    data_list = []

    def clean_text(text):
        text=re.sub(r'<rt[^>]*?>.*?</rt>', '', text)
        text=re.sub(r'<[^>]*>|\n', '', text)
        return text

    with open(epub_path, 'r', encoding='utf-8') as f:
        file_text = f.read()
        matches = re.finditer(r'<(h[1-6]|p|a|title).*?>(.+?)</\1>', file_text, flags=re.DOTALL)
        if not matches:
            print("perhaps this file is a struct file")
            return data_list, file_text
        groups = []
        text = ''
        pre_end = 0
        for match in matches:
            match_text = clean_text(match.group(2))
            # 第一次强制走if分支，确保一定有至少一条文本。
            if len(text + match_text) <= text_length or text == '':
                new_text = match_text
                if new_text:
                    groups.append(match)
                    text += '\n' + new_text
            else:
                data_list.append((text, groups, pre_end))
                pre_end = groups[-1].end()
                new_text = match_text
                if new_text:
                    groups = [match]
                    text = match_text
                else:
                    groups = []
                    text = ''

        if text:
            data_list.append((text, groups, pre_end))
    # TEST:
    # for d in data_list:
    #     print(f"{len(d[0])}", end=" ")
    return data_list, file_text


f = open('msg_tr.json', encoding='utf8')
msg_dict = json.load(f)

def get_msg_tr(text):
    if text in msg_dict:
        return msg_dict[text]
    else:
        print("W: untranslated \"message\": " + text)
        return text


def main():

    import coloredlogs
    coloredlogs.install(level="INFO")

    print("Start translating...")
    start = time.time()

    epub_list = ["1.epub",
                 "2.epub"]
    save_list = ["1.epub",
                 "2.epub"]
    for i in range(len(save_list)):
        save_list[i] = "cn/" + save_list[i]

    for epub_path, save_path in zip(epub_list, save_list):
        print(f"translating {epub_path}...")
        start_epub = time.time()

        if os.path.exists('./temp'):
            shutil.rmtree('./temp')
        with zipfile.ZipFile(epub_path, 'r') as f:
            f.extractall('./temp')

        with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as f:
            for html_path in find_all_htmls('./temp'):
                print(f"\ttranslating {html_path}...")
                start_html = time.time()

                translated = ''
                data_list, file_text = get_html_text_list(html_path, TEXT_LEN)
                if len(data_list) == 0:
                        continue
                for text, groups, pre_end in tqdm(data_list):
                    output = get_msg_tr(text)
                    texts = output.strip().split('\n')
                    if len(texts) < len(groups):
                        texts += [''] * (len(groups) - len(texts))
                    else:
                        texts = texts[:len(groups)-1] + ['<br/>'.join(texts[len(groups)-1:])]
                    for t, match in zip(texts, groups):
                        t = match.group(0).replace(match.group(2), t)
                        translated += file_text[pre_end:match.start()] + t
                        pre_end = match.end()

                translated += file_text[data_list[-1][1][-1].end():]
                with open(html_path, 'w', encoding='utf-8') as fout:
                    fout.write(translated)

                end_html = time.time()
                print(f"\t{html_path} translated, used time: ", end_html-start_html)

            for file_path in glob.glob(f'./temp/**', recursive=True):
                if not os.path.isdir(file_path):
                    relative_path = os.path.relpath(file_path, './temp')
                    f.write(file_path, relative_path)

        shutil.rmtree('./temp')

        end_epub = time.time()
        print(f"{epub_path} translated, used time: ", end_epub-start_epub)

    end = time.time()
    print("translation completed, used time: ", end-start)


if __name__ == "__main__":
    main()
