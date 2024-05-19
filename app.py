from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging

logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")


@app.route("/review", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        try:
            searchString = request.form["content"].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "cPHDOP col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a["href"]
            prodRes = requests.get(productLink)
            prodRes.encoding = "utf-8"
            prod_html = bs(prodRes.text, "html.parser")
            # print(prod_html)
            commentboxes = prod_html.find_all("div", {"class": "col pPAw9M"})
            comment = commentboxes[0]
            comment_url = "https://www.flipkart.com" + comment.a["href"]
            uClient = uReq(comment_url)
            comment_page = uClient.read()
            comment_html = bs(comment_page, "html.parser")
            comment_boxes = comment_html.find_all("div", {"class": "cPHDOP col-12-12"})
            overall_comment_url = "https://www.flipkart.com" + comment_boxes[2].div.div.a['href']
            uClient = uReq(overall_comment_url)
            overall_comment_pages = uClient.read()
            comment_html = bs(overall_comment_pages, "html.parser")
            comment_box = comment_html.find_all("div", {"class": "EKFha-"})
            # comment_review = []
            # for comment in comment_box:
            #     comment_review.append(comment.div.div.find_all("div", {"class": "row"})[1].text)

            # filename = searchString + ".csv"
            # fw = open(filename, "w")
            # headers = "Product, Customer Name, Rating, Heading, Comment \n"
            # fw.write(headers)
            reviews = []
            for commentbox in comment_box:
                try:
                    # name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('div', {'class': 'row gHqwa8'})[0].p.text

                except:
                    logging.info("name")

                try:
                    # rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.find_all('div', {'class': 'row'})[0].div.text

                except:
                    rating = "No Rating"
                    logging.info("rating")

                try:
                    # commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = "No Comment Heading"
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all("div", {"class": ""})
                    # custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {
                    "Product": request.form["content"].title(),
                    "Name": name,
                    "Rating": rating,
                    "CommentHead": commentHead,
                    "Comment": custComment,
                }
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))
            return render_template(
                "result.html", reviews=reviews[0 : (len(reviews) - 1)]
            )
        except Exception as e:
            logging.info(e)
            return "something is wrong"
    # return render_template('results.html')

    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
