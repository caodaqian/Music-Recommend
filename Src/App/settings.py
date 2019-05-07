import os

# 数据库配置
DB_SETTING = {
    'host': 'localhost',
    'user': 'cdq',
    'passwd': '970808',
    'charset': 'utf8',
    'port': 3306
}

# 日志存放目录
LOG_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "\\Log\\"

# 打分文件保存的目录
RATE_PATH = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))) + "\\Data\\rate.txt"

# chromedriver的应用程序目录
CHROMEDRIVER_PATH = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'

# 音乐存放路径
MUSIC_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))) + "\\Data\\music\\{}.mp3"

# Scrapy爬虫数据
SCRAPY_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))) + "\\Data\\"

# spuer用户上传文件的格式
FILEEXT = set(['json', 'txt'])

# 评分标准
# 喜欢 4分
# 不喜欢 - 8分
# 标签类似 2 分
# 标签存在但是不同 -2 分
# 评论数 / 700000 * 4 （以1万评论数为基数，4分满分，当前数据集当中最大的评论数量为 671727）
# 试听 1分
# 下载 3分
# 因此 最低为 -10 分， 最高为 4 + 2 + 4 + 1 + 3 = 14 分
SCORE = {
    'like': 4,
    'unlike': -8,
    'similarTags': 2,
    'comments': 4,
    'comment_base': 700000,
    'audition': 1,
    'download': 3
}
