from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods.taxonomies import GetTerms
from wordpress_xmlrpc.methods.posts import GetPosts, GetPost
from bs4 import BeautifulSoup
import openai
import requests
import datetime
today = datetime.date.today()
tt = str(today.month)+"."+str(today.day)


# openai.api_key = "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"  # wave-function
# openai.api_key = "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"    #emily8833
# openai.api_key = "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"  # jack95zz
openai.api_key = "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"   # wavefunction61
client = Client('http://www.wavefunction.info/xmlrpc.php', 'qupunk', 'UIJEhTWHuLH1FuUQhZ')
categories = client.call(GetTerms('category'))
# 查找或创建电影分类
economy_category = None
for category in categories:
    if category.name == 'Economy':
        economy_category = category
        break
def ask_question_gpt3(question):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        max_tokens=3996,
        messages=[
            {"role": "system", "content": question}
        ]
    ).choices[0].message.content
    return response
def ask_question_gpt4(question):
    response = openai.ChatCompletion.create(
        model='gpt-4',
        max_tokens=7996,
        messages=[
            {"role": "system", "content": question}
        ]
    ).choices[0].message.content
    return response
def get_yahoo_finance_news():
    url = "https://finance.yahoo.com/news/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = []
    links = []
    for article in soup.find_all("li", {"class": "js-stream-content"}):
        title = article.find("h3").text
        link = article.find("a")["href"]
        titles.append(title)
        links.append(link)
    return titles, links
n = 3
titles, links = get_yahoo_finance_news()
# print(titles)
for i in range(len(titles)):
     head = "Generate an attractive and topical title about " + titles[i+n] +", less than 20 words."
     title = ask_question_gpt3(head)
     # print('title:', title)
     contents = "It is reported that ("+ links[i+n] +") and Do not mention the year, \
     In addition, Analyze similar events in history from an economist's point of view.Don't call yourself an AI language model \
     Finally, summarize the relationship between the above contents with a historian's perspective and look forward to the future. No more than 5000 words" #in a professional but humorous way, No less than 3000 words"
     try:  #长度超过跳出循环
         content = ask_question_gpt3(contents)
     except openai.error.InvalidRequestError:
             # 如果出现错误，跳过当前循环
             continue
     print('i:', i)
     print('title:', title)
     # 根据标题创作一张图片
     # picture1 = title + ', Describe this sentence in as much detail as possible to generate a prompt picture. Limit the description to 101 words and apply to DALL-E-2'
     # picture2 = ask_question_gpt3(picture1)
     prompt = title + 'Unreal Engine;digital art；Exquisite Detail every detail；'  # 3D ; a little bit more pink' # cyberpunk
     try:   #触发openai的安全就跳出循环
         response = openai.Image.create(prompt=prompt, n=1, size='512x512')
     except openai.error.InvalidRequestError:
         # 如果出现错误，跳过当前循环
         continue
     image_url = response['data'][0]['url']
     # 保存图片
     with open("pic/{i}{i}.jpg".format(prompt=prompt, i=i), "wb") as f:
         f.write(requests.get(image_url).content)
         f.close()
     print('save image success')
     # Upload the picture
     with open('pic/{i}{i}.jpg'.format(prompt=prompt, i=i), 'rb') as img:
         data = {
             'name': 'my-image.jpg',
             'type': 'image/jpeg',
             # 'size': '256*256',
             'bits': img.read(),
             'overwrite': True
         }
         response = client.call(UploadFile(data))
     print('upload image success')
     # Create a new post
     post = WordPressPost()
     post.title = title
     post.content = content
     post.post_status = 'publish'
     post.post_author = '0'
     post.comment_status = 'open'  # 开启评论
     post.terms_names = {'category': [economy_category.name]}
     # Set the featured image ID
     if response:
         attachment_id = response['id']
         post.thumbnail = attachment_id

     # Publish the post
     client.call(NewPost(post))
     title = ""
     content = ""
     print(response['id'])

