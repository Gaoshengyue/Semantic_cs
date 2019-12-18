import os,time,datetime
from fastapi import APIRouter, File, UploadFile
from jieba import lcut
import jieba.posseg as pseg
from collections import Counter
from gensim.similarities import SparseMatrixSimilarity
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from tqdm import tqdm
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from tinydb import TinyDB,Query

router = APIRouter()

#TinyDB读取
db=TinyDB("demo.json")
templates = Jinja2Templates(directory="templates")

def takeSecond(elem):
    return elem[1]
@router.get("/",)
async def read_users(request:Request):
    rs_list=[]
    obj=Query()
    dir_name=db.search(obj.type=="dir")
    for item in dir_name:
        data=db.search(obj.dir==item.get("name"))
        item["child"]=data
        rs_list.append(item)
    return templates.TemplateResponse("model.html", {"request":request,"result":rs_list})

@router.post("/word_frequency/")
async def get_words(file:UploadFile=File(...)):
    contents = file.file.read()
    now = time.time()
    with open("./cache_file/" + str(now) + file.filename, "w+") as f:
        f.write(contents.decode("utf-8"))

    with open("./cache_file/" + str(now) + file.filename, "r") as f_read:
        data = f_read.readlines()

    texts = [lcut(text.strip("\n")) for text in tqdm(data)]
    all_txt=[]
    for item in texts:
        for st in item:
            if "/" not in st and " " not in st and st and "[" not in st and "]" not in st and "【" not in st and "】" not in st and len(st)>=2:
                all_txt.append(st)

    c = Counter(all_txt).most_common(100)  # 取最多的10组
    print(c)
    os.remove("./cache_file/"+str(now)+file.filename)
    return {"rs":c}

def seg_sentence(sentence, stop_words):
    # stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']#过滤数字m
    stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'f', 'r']
    sentence_seged = pseg.cut(sentence)
    # sentence_seged = set(sentence_seged)
    outstr = []
    for word, flag in sentence_seged:
        # if word not in stop_words:
        if word not in stop_words and flag not in stop_flag:
            outstr.append(word)
    return outstr

def StopWordsList(filepath):
    wlst = [w.strip() for w in open(filepath, 'r', encoding='utf8').readlines()]
    return wlst

@router.post("/files/")
async def create_file(keyword:str,threshold:float,file:UploadFile=File(...)):
    contents = file.file.read()
    now=time.time()
    with open("./cache_file/"+str(now)+file.filename,"w+") as f:
        f.write(contents.decode("utf-8"))
    with open("./cache_file/"+str(now)+file.filename,"r") as f_read:
        data=f_read.readlines()
    # 1、将【文本集】生成【分词列表】
    texts = [lcut(text.strip("\n")) for text in tqdm(data)]
    # 2、基于文本集建立【词典】，并获得词典特征数
    dictionary = Dictionary(texts)
    num_features = len(dictionary.token2id)
    # 3.1、基于词典，将【分词列表集】转换成【稀疏向量集】，称作【语料库】
    corpus = [dictionary.doc2bow(text) for text in tqdm(texts)]
    # 3.2、同理，用【词典】把【搜索词】也转换为【稀疏向量】
    kw_vector = dictionary.doc2bow(lcut(keyword))
    # 4、创建【TF-IDF模型】，传入【语料库】来训练
    tfidf = TfidfModel(corpus)
    # 5、用训练好的【TF-IDF模型】处理【被检索文本】和【搜索词】
    tf_texts = tfidf[corpus]  # 此处将【语料库】用作【被检索文本】
    tf_kw = tfidf[kw_vector]
    # 6、相似度计算
    sparse_matrix = SparseMatrixSimilarity(tf_texts, num_features)
    similarities = sparse_matrix.get_similarities(tf_kw)
    # print(similarities)
    new_now=datetime.datetime.now()
    #文件目录简单管理
    os.makedirs("./static/"+keyword+str(new_now))
    db.insert({"name":keyword+str(new_now),"type":"dir"})
    f = open("./static/"+keyword+str(new_now)+"/result.txt", "w")
    db.insert({"name": keyword+str(new_now) + "/result.txt", "type": "file","dir":keyword+str(new_now)})
    f1 = open("./static/"+keyword+str(new_now)+"/result_er.txt", "w")
    db.insert({"name": keyword+str(new_now) + "/result_er.txt", "type": "file","dir":keyword+str(new_now)})
    #end
    Semantic_list=[]

    for e, s in enumerate(similarities, 1):
        su=(e,s)
        Semantic_list.append(su)
        try:
            if s >= threshold:
                f.write(data[e - 1].strip("\n")+str(s)+"\n")
            else:
                f1.write(data[e - 1].strip("\n")+str(s)+"\n")
        except Exception as e:
            pass
    Semantic_list.sort(key=takeSecond,reverse=True)
    rs_list=[]
    for item in Semantic_list[0:101]:
        rs_dic={"msg":data[item[0]-1],"Similaritydegree":str(item[1])}
        rs_list.append(rs_dic)
    # Semantic_list

    os.remove("./cache_file/"+str(now)+file.filename)
    return {"semantic":rs_list}
