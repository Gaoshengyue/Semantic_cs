### 主题

文本分词提取，默认为按行读文本提取。主要用于csv文本分析。类似于趋势词查询、高热度词频分析。

### 使用方法

#### 环境

python3

#### 安装包

```
pip3 install -r requirements.txt
```

#### 启动

主目录下，直接运行命令

```
uvicorn main:app --reload --port 8091 --host 0.0.0.0
```

#### 接口文档及测试用例

访问 http://127.0.0.1:8091/docs

目前暂时有两个接口

**词频排名**

POST   http://127.0.0.1:8091/file_c/word_frequency/      Content-Type:multipart/form-data

参数：{"file":文件名.csv}

返回结果为词频前百名及顺序排名

**关键词匹配切分**

POST  http://127.0.0.1:8091/file_c/files/              Content-Type: multipart/form-data

参数：{"keyword":关键词,"threshold":相似度阈值,"file":文件名.csv}

返回结果为设定阈值以上的数据返回及匹配结果

GET  http://127.0.0.1:8091/file_c/          

简单页面返回，匹配的是关键词时间组合命名的数据结果，分为result.txt  result_er.txt两个文件，分别是匹配结果文本与非匹配结果文本

