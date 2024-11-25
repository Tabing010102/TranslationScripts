import json
import time

import requests

import utils
from sakurallm.sakura import translate_rpg
from sakurallm.sakura.v010 import translate as translate_v010, translate_rpg as translate_rpg_v010

# print(translate_rpg("""
# エロは変身ヒロイン・サクラ(プリセシール)を操作してのボス敗北による凌辱がメインであり、ENDによっては男主人公(=プレイヤー)は幼なじみである彼女をNTRれてしまう。いずれのシーンでもテキスト・差分の量ともに多く、演出も凝っている。
#
# まず敗北凌辱では、敵に捕まっても諦めないヒロインが、徹底して犯されることとなる。触手や電撃をはじめとして、身体を酷使するものが多く、スチルでも傷痕が身体を彩ることとなる。それでも「まだ負けていない」とヒロインらしい強さを見せるも、最後には屈服する。キラキラと意志を宿した瞳が、絶望に曇るのが最高だ。
# 特に、本作では変身解除が多く取り入れられており、その際にハートが粉砕される演出は否が応でも「完全敗北」を印象づけ、効果を発揮している。処女喪失のショック、失禁による辱め、以前倒した敵に大好き宣言するなど、精神的痛みや屈辱を倍増させたシチュも機能しており、1シーンごとがオススメである。
#
# NTRシーンは絶望的な描写でプレイヤーを叩きのめす。サクラが相手の男の虜になるのも納得がいくよう、丁寧に彼女の心の隙を描いており、そこから加速度的に離れてゆく展開のどうしようもなさが良い。サクラ自身も心から相手を愛してしまうことに加え、ここにプレイヤーはサクラに理解されない孤立まで追い打ちをかけられるので、極上の味わいとなっている。
#
# ゲームは探索要素が抱負であり、発見が面白い。「ここはあそこにつながっていたのか」「こんな所にも行けるのか」と驚きと達成感が心地よい。雑魚敵は復活しない使用だが、クリアには十分すぎるほど配置されており、一度倒せば探索に集中できる新設設計がありがたい。
#
# ストーリーは王道的で、とっつきやすい。途中で挿入される悪側のそれぞれの思惑、関係が進展する主人公組と、要領よくまとまった話運びは読んでいて楽しい。総じて、傑作と呼んで間違い無しの一大傑作である。"""))
# print(translate_rpg("下層のマフィアを通じて国外で売買して、隠し財産を築いていたの"))
# print(translate_rpg("魔法"))
# print(translate_rpg("ヤバ井沢"))
# while True:
#     print(translate_rpg("""「待ってろドラゴン、ステーキにしてやる！」
#
#     ダンジョンの奥深くでドラゴンに襲われ、金と食料を失ってしまった冒険者・ライオス一行。
#     再びダンジョンに挑もうにも、このまま行けば、途中で飢え死にしてしまう。
#     そこでライオスは決意する。「そうだ、モンスターを食べよう！」
#     スライム、バジリスク、ミミック、そしてドラゴン！
#     襲い来る凶暴なモンスターを食べながら、ダンジョンの踏破を目指せ！冒険者よ！
#     """, endpoint='http://127.0.0.1:5000/'))

for i in range(5):
    # print(translate_v010("フランソワ", api_url="http://192.168.7.119:40053/"))
    # print(translate_v010("先祖から受け継いだ孤島で謎の少女「つらら」にアドバイスをもらいながら", api_url="http://192.168.7.119:40053/"))
    print(translate_v010("身分を隠した少女・パステルや森の少女・サシュ、幽霊のミーネを中心にさまざまな魅力的なキャラクターが登場します。"))

while True:
    print(translate_v010("「ううん、嬉しかったよ。いなばさん、明るくて　一緒にいると楽しいし、色々教えてくれるから」",
                         gpt_dict=[{"src": "いなば", "dst": "因幡", "info": "女"}],
                         api_url="http://127.0.0.1:11434"))
    print(translate_v010("「ううん、嬉しかったよ。いなばさん、明るくて　一緒にいると楽しいし、色々教えてくれるから」",
                         gpt_dict=None,
                         api_url="http://127.0.0.1:11434"))

while True:
    print(translate_v010("「ううん、嬉しかったよ。いなばさん、明るくて　一緒にいると楽しいし、色々教えてくれるから」",
                         gpt_dict=[{"src": "いなば", "dst": "因幡", "info": "女"}],
                         api_url="http://192.168.5.19:5000"))
    print(translate_v010("「ううん、嬉しかったよ。いなばさん、明るくて　一緒にいると楽しいし、色々教えてくれるから」",
                         gpt_dict=None,
                         api_url="http://192.168.5.19:5000"))

# print(translate_v010("エレナ"))
print(translate_v010("裏筋を張りのある秘唇に挟まれると、思わず腰を突きあげたくなってしまう。",
                     gpt_dict=None, api_url="http://192.168.5.19:40050"))
for i in range(5):
    print(translate_v010("「ううん、嬉しかったよ。いなばさん、明るくて　一緒にいると楽しいし、色々教えてくれるから」",
                         gpt_dict=[{"src": "いなば", "dst": "因幡"}]))
for i in range(5):
    print(translate_v010("「ううん、嬉しかったよ。いなばさん、明るくて　一緒にいると楽しいし、色々教えてくれるから」",
                         gpt_dict=[{"src": "いなば", "dst": "因幡", "info": "女"}]))

while True:
    print(translate_v010("田舎のコミュニティは狭いんだぞ、七ちゃんのことが誤解されたらどうする。",
                         api_url="http://192.168.5.19:40050/"))

# print(translate_v010("週末に七ちゃんから言われたことを考えていたら、あっという間に夜明け間近になっていた。"))
print(translate_v010("田舎のコミュニティは狭いんだぞ、七ちゃんのことが誤解されたらどうする。"))
print(translate_v010("田舎のコミュニティは狭いんだぞ、七ちゃんのことが誤解されたらどうする。", gpt_dict=[
    {"src": "七", "dst": "七"}
]))
print(translate_v010("田舎のコミュニティは狭いんだぞ、七ちゃんのことが誤解されたらどうする。", gpt_dict=[
    {"src": "七", "dst": "七", "info": "主角义妹名字"}
]))

input()

f = open('ManualTransFile.json', encoding='utf8')
ori_data = json.load(f)
total_lines = len(ori_data) + 2

result = {}

i = 2
for key in ori_data:
    # if i > 30:
    #     break
    if not utils.is_cjk_str(key):
        print("L[" + str(i) + "/" + str(total_lines) + "]: " + key + " -> skipped")
        i = i + 1
        continue
    cnt_result = ""
    while True:
        try:
            cnt_result = translate_rpg(key)
            break
        except Exception as e:
            sleep_secs = 2
            print("Error: " + str(e))
            print("Sleeping for " + str(sleep_secs) + " secs")
            time.sleep(sleep_secs)
            continue
    print("L[" + str(i) + "/" + str(total_lines) + "]: " + key + " -> " + cnt_result)
    result[key] = cnt_result
    i = i + 1

with open('a/r/sr.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False))
with open('a/r/sp.json', 'w', encoding='utf8') as f3:
    f3.writelines(json.dumps(result, ensure_ascii=False, indent=4))
