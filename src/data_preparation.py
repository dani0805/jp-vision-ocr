import json
import os
import random
import re
import sys
from math import ceil


def prepare_data(
        fonts=('ヒラギノ明朝 ProN.ttc', ),
        stop_after=1000000,
        min_occurrences=0.00001,
        size=(2048, 2048),
        line_length=60):

    global main_dir, r, strip_xml, log_progress, create_image, draw_text, draw_vertical_text, get_v_size, draw_background
    # make sure you have the fonts locally in a fonts/ directory
    # W, H = (1280, 720) # image size
    main_dir = os.getcwd()
    r = random.Random()

    def strip_xml():
        writing = False
        count = 0
        with open(main_dir + '/corpus/jawiki-20181001-corpus.xml') as f:
            with open(main_dir + '/corpus/jawiki-20181001-corpus.txt', mode="w") as o:
                for line in f:
                    if line.startswith("<content>"):
                        writing = True
                    if line.startswith("</content>"):
                        writing = False
                    if writing:
                        new_line = [re.sub('&[^;]*;', '', re.sub('<[^>]*>', '', line.replace("&quot;", "\""))).lstrip()]
                        if len(new_line[0]) > line_length:
                            new_array = []
                            tot_len = len(new_line[0])
                            cut = 0
                            while cut + line_length < tot_len:
                                new_array.append(new_line[0][cut: cut + line_length] + "\n")
                                cut += line_length
                            new_array.append(new_line[0][cut: tot_len])
                            new_line = new_array

                        for l in new_line:
                            o.write(l)
                    if count == stop_after:
                        return
                    count = log_progress(count)

    def log_progress(count, char=".", new_line=100000, step=1000):
        if count % new_line == 0:
            print()
        if count % step == 0:
            sys.stdout.write(char)
        count += 1
        return count

    def prepare_corpus():
        print()
        strip_xml()
        counts_dict = {}
        charcount = 0
        count = 0
        with open(main_dir + '/corpus/jawiki-20181001-corpus.txt') as f:
            for line in f:
                for c in list(line):
                    if c not in counts_dict:
                        counts_dict[c] = 0
                    counts_dict[c] += 1
                    charcount += 1
                count = log_progress(count, "#")

        p_0001 = ceil(charcount / 1000000)
        p_001 = ceil(charcount / 100000)
        p_01 = ceil(charcount / 10000)
        p_1 = ceil(charcount / 1000)
        p_cut = ceil(charcount * min_occurrences)
        print("\nnumber of characters:" + str(len(counts_dict)))
        print("more than 0.0001% (" + str(p_0001) + ") occurrence:" + str(
            len({k: v for k, v in counts_dict.items() if v > p_0001})))
        print("more than 0.001% (" + str(p_001) + ") occurrence:" + str(
            len({k: v for k, v in counts_dict.items() if v > p_001})))
        print("more than 0.01% (" + str(p_01) + ")  occurrence:" + str(
            len({k: v for k, v in counts_dict.items() if v > p_01})))
        print("more than 0.1% (" + str(p_1) + ")  occurrence:" + str(
            len({k: v for k, v in counts_dict.items() if v > p_1})))
        final_dict = {k: v for k, v in counts_dict.items() if v > p_cut}
        print("ignoring characters appearing less then " + str(min_occurrences * 100) + "% times. Found " + str(
            len(final_dict)) + " characters")
        with open(main_dir + '/corpus/jawiki-20181001-corpus.stat', mode="w") as stat:
            json.dump(final_dict, stat, indent=2)

    def create_image(text: str, font: str, name: str, fontsize: int = 35, direction='ttb'):
        W, H = size  # image size
        txt = text  # text to render
        background = (255, 255, 255)  # white

        image = Image.new('RGBA', (W, H), background)
        image = draw_background(H, W, image)
        image, x, y, w, h = draw_text(image, txt, direction, font, fontsize, W, H)
        if not os.path.exists(main_dir + '/data'):
            os.makedirs(main_dir + '/data')
        if not os.path.exists(main_dir + '/data'):
            os.makedirs(main_dir + '/data/img')
        if not os.path.exists(main_dir + '/data'):
            os.makedirs(main_dir + '/data/label')

        image = draw_background(H, W, image, poly_count=3, min_alpha=10, max_alpha=40)
        image.save(main_dir + '/data/' + name)


    def draw_text(image, txt, direction, font, fontsize, W, H):
        font = ImageFont.truetype(font, fontsize)
        w, h = font.getsize_multiline(txt, direction=direction)
        red = random.randrange(0, 255)
        blue = random.randrange(0, 255)
        green = random.randrange(0, 255)
        x = r.randint(5, W - w - ceil(h / 3) - 5)
        y = r.randint(5, H - h - ceil(w / 3) - 5)
        if direction == 'ltr':
            tmp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            tdraw = ImageDraw.Draw(tmp)
            tdraw.multiline_text((0, 0), txt, fill=(red, green, blue), font=font,
                direction=direction)
        else:
            # positioning in TTB is buggy need to do it by hand
            w, h, lines = get_v_size(fontsize, txt)
            tmp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            tdraw = ImageDraw.Draw(tmp)
            y = r.randint(5, H - h - ceil(w / 3) - 5)
            x = r.randint(W - w - 5 - ceil(h / 3), W - 5 - fontsize)
            draw_vertical_text(tdraw, txt, font, fontsize, blue, red, green, W, H, w, h, w, 0, lines)
            x = x - w + ceil(fontsize * 1.4)
        tmp = tmp.rotate(r.randint(-15, 16), expand=1)
        image.paste(tmp, (x, y), tmp)
        sx, sy = tmp.size
        tdraw = ImageDraw.Draw(image)
        tdraw.rectangle([(x, y), (x + sx, y + sy)])
        return image, x, y, sx, sy

    def draw_vertical_text(draw, txt, font, fontsize, blue, red, green, W, H, w, h, x, y, lines):
        assert H > h + 10
        start = x
        for line in lines:
            draw.text((start, y), line, fill=(red, green, blue), font=font, direction='ttb')
            start -= ceil(fontsize * 1.4)

    def get_v_size(fontsize, txt):
        lines = txt.split("\n")
        max_len = max(*[len(l) for l in lines])
        w = ceil(fontsize * 1.4 * len(lines))
        h = ceil(max_len * 1 * fontsize)
        return w, h, lines

    def draw_background(H, W, image, min_alpha=255, max_alpha=256, poly_count=20):
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(tmp)
        for i in range(poly_count):
            path = []
            for i in range(r.randint(3, 6)):
                x = r.randint(ceil(-W * .5), ceil(W * 1.5))
                y = r.randint(ceil(-H * .5), ceil(H * 1.5))
                path.append((x, y))
            red = random.randrange(0, 255)
            blue = random.randrange(0, 255)
            green = random.randrange(0, 255)
            alpha = random.randrange(min_alpha, max_alpha)
            tdraw.polygon(path, fill=(red, green, blue, alpha))
        comp = Image.alpha_composite(image, tmp)
        return comp

    def prepare_images():
        with open(main_dir + '/corpus/jawiki-20181001-corpus.txt') as f:
            g_count = 0
            count = 0
            n_lines = r.randint(1, 10)
            txt = ""
            for line in f:
                txt += line
                count += 1

                if count == n_lines:
                    create_image(
                        text=txt,
                        font=fonts[0],
                        name="sample_" + str(g_count) + ".png",
                        fontsize=r.randint(15, 25),
                        direction=r.choice(['ltr', 'ttb'])
                    )
                    g_count += 1
                    count = 0
                    n_lines = r.randint(1, 10)
                    txt = ""
                    log_progress(g_count, char="/", step=1, new_line=100)
                if g_count == 40:
                    return

    # prepare_corpus()
    prepare_images()