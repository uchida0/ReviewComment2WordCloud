from PIL import Image
#import numpy as np
from matplotlib import pyplot as plt
from wordcloud import WordCloud
import requests
import MeCab
from bs4 import BeautifulSoup
import urllib
#from gensim.models import KeyedVectors

#ストップワード辞書のslothlibを使用
slothlib_path = 'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt'
slothlib_file = urllib.request.urlopen(slothlib_path)
slothlib_stopwords = [line.decode("utf-8").strip() for line in slothlib_file]
slothlib_stopwords = [ss for ss in slothlib_stopwords if not ss==u'']

StopWordJa = ["もの", "こと", "とき", "そう", "たち", "これ", "よう", "これら", "それ", "すべて"]

StopWordJa += slothlib_stopwords

StopWordJa = list(set(StopWordJa))

#日本語用
def  create_word_cloud_ja(word_list):

    fontpath = "C:\Windows\Fonts\源暎ゴシックN\GenEiGothicN-Heavy.otf"

    # ワードクラウド
    # 1つのコメントにつき単語のカウントは1回にする（同様の語が繰り返し使われることを避けるため）
    # 基本形にして収集する
    # 類似語については1つの語として扱いたい(未実装)

    word_chain = " ".join(word_list)
    wordcloud = WordCloud(
        background_color="white",
        font_path=fontpath,
        width=900,
        height=500,
        stopwords=set(StopWordJa)
    ).generate(word_chain)

    # 描画
    plt.figure(figsize=(15,20))
    plt.imshow(wordcloud)
    plt.axis("off")
    #plt.show()
    wordcloud.to_file("word_cloud.png")



# レビューコメントをmorphにする
# 重複なしの単語リストを返す
# return: 重複なしの単語list
def morph_comment(comment):
    tagger = MeCab.Tagger()
    tagger.parse("")
    node = tagger.parseToNode(comment)

    word_list = []

    while node:
        word_type = node.feature.split(",")[0]
        word_surf = node.surface.split(",")[0]

        #["名詞", "形容詞", "動詞"] => 形容詞、動詞についてはtf-idfなどで除去する必要があるかもしれない

        if word_type in ["名詞"] and word_surf not in StopWordJa:
            word_base = node.feature.split(",")[6]
            
            #print(word_base)
            if len(word_base) > 1:
                word_list.append(word_base)

        node = node.next
    
    #重複なしにする
    word_list = list(set(word_list))

    return word_list


# linkを元にコメントを平文で取得
# return: レビューコメントのlist
def collect_comment(link):
    
    try:
        html = requests.get(link)
        soup = BeautifulSoup(html.content, "html.parser")

        #レビュー項目抽出
        review_head = soup.findAll("td", {"class": "revHead"})
        head_list = []

        for rh in review_head:
            head = rh.text.split("\n")[0]
            head_list.append("【" +  head + "】")
        

        #レビューコメント抽出部分
        print("レビューコメント抽出開始...")
        review_comments = soup.findAll("p", {"class": "revEntryCont"})
        comment_list = []

        for rc in review_comments:
            comment = rc.text
            #項目のテンプレートを用いて書かれているレビューコメントに対しての処理
            for h in head_list:
                comment = comment.replace(h, "\n")
            comment_list.append(comment)

        print("レビューコメント抽出完了!!")
        
        return comment_list
    
    except Exception as e:
        print("リンクが間違っているかもしれません")
        exit(0)






#実行部分
def analyze(link):

    #collect_comment()でレビューコメント取得
    comment_list = collect_comment(link)

    
    #morph_comment()で各形態素解析語に得られる単語リストを取得
    #全レビューコメントの単語リストと連結
    print("レビューコメントから単語抽出開始...")
    word_list = []

    for comment in comment_list:
        morph_list = morph_comment(comment)
        word_list += morph_list

    print("レビューコメントから単語抽出終了!!")

    #create_word_cloud()でワードクラウド作成
    print("ワードクラウド作成開始...")
    create_word_cloud_ja(word_list)
    print("ワードクラウド作成完了!!")


if __name__ == "__main__":
    description = ("価格.comの商品レビューのリンクを貼ってください。\nレビューコメントについてワードクラウドを生成します。")
    print(description)

    link = input("商品レビューリンク：")

    analyze(link)