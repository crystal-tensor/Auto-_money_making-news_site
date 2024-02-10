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


openai.api_key = "sk-******"   # openai.api_key
client = Client('http://www.******.com/xmlrpc.php', 'name', 'password')
# www.******.com is your webstation url
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
        max_tokens=7996,  # The maximum support is 16k
        messages=[
            {"role": "system", "content": question}
        ]
    ).choices[0].message.content
    return response
def get_yahoo_finance_news():
    url = "https://finance.yahoo.com/news/"
    # url = "https://finance.yahoo.com/"
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
n = 5
titles, links = get_yahoo_finance_news()
# print(titles)
for i in range(len(titles)):
     head = "Generate an attractive and topical title about " + titles[i+n] +", less than 20 words."
     print(titles[i+n])
     title = ask_question_gpt4(head)
     # print('title:', title)
     contents1 = "It is reported that ("+ links[i+n] +") and Do not mention the year, \
      In addition,Analyze similar events in history from the perspective of economists in a dialogue tone.No less than 12000 words"
     # In addition,Give a detailed list of similar events in history, and use an economist's perspective to analyze the similarities and differences between these similar events and the current event, and provide constructive analysis. \
     # Don't call yourself an AI language model，No less than 12000 words are required"
     #Finally, summarize the relationship between the above contents with a historian's perspective and look forward to the future. No more than 5000 words" #in a professional but humorous way, No less than 3000 words"
     content1 = ask_question_gpt4(contents1)
     contents2 = "In short,summarize the above(" + links[i+n] + ") form the perspective of a historian of economic thought in a dialogue tone, \
          and raises questions about the possible future implications of the events mentioned above and invites readers to share their thoughts and opinions. \
        , No less than 10000 words are required"  # in a professional but humorous way, No less than 3000 words"
     content2 = ask_question_gpt4(contents2)
     # print('content1:', content1)
     # print('content2:', content2)
     print('i:', i)
     print('title:', title)
     # 根据标题创作一张图片
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
     post.content = content1+content2
     # print('post.content:', post.content)
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
