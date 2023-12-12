from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin

application = Flask(__name__)
app = application

@app.route('/',methods=['GET'])
@cross_origin()
def homePage():
    return render_template('index.html')

@app.route('/details',methods = ['GET', 'POST'])
@cross_origin()
def detailsPage():
    if request.method != 'POST':
        return render_template('index.html')
    else:
        try:
            print("Hello")
            query = request.form['content']
            driver = webdriver.Chrome()
            name = query.split('/')[3]
            name = name[1:]
            name
            driver.get(query)
            last_height = driver.execute_script("return document.documentElement.scrollHeight")
            while True:
                driver.execute_script(f"scrollTo(0,{last_height})")
                time.sleep(3)
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height != last_height:
                    last_height = new_height
                else:
                    break
            response = driver.page_source
            soup = bs(response,'html.parser')
            images = soup.find_all('img',{'class': "yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded"})
            thumbnail_url = []
            for img in images:
                thumbnail_url.append(img['src'])
            titles_html = soup.find_all(id = "video-title")
            video_title = []
            for title in titles_html:
                video_title.append(title.text)
            views_duration = soup.find_all('span',{'class': "inline-metadata-item style-scope ytd-video-meta-block"})
            views_duration_list = list(views_duration)
            views = []
            for i in range(0,len(views_duration_list),2):
                views.append(views_duration_list[i].text)
            duration = []
            for i in range(1,len(views_duration_list),2):
                duration.append(views_duration_list[i].text)
            driver.quit()
            data = {"Video Thumbnail":thumbnail_url, "Title":video_title, "Views":views, "Time of Posting": duration}
            df = pd.DataFrame(data)
            df.to_csv(f"{name}.csv",index=False)
            data = pd.read_csv(f"{name}.csv").to_dict('records')
            return render_template("details.html",name=f"{name}.csv",data=data)
        except Exception as e:
            print("The exception Message is ",e)
            return "Something went wrong"
if __name__ == "__main__":
    app.run(host='127.0.0.1',port=4000,debug=False)
