from bs4 import BeautifulSoup
from datetime import datetime
import pytz

comment_template = """
      <wp:comment>
        <wp:comment_content><![CDATA[{comment_content}]]></wp:comment_content>
        <wp:comment_approved>1</wp:comment_approved>
        <wp:comment_date>{comment_date}</wp:comment_date>
        <wp:comment_date_gmt>{comment_date_gmt}</wp:comment_date_gmt>
        <wp:comment_author>{comment_author}</wp:comment_author>
        <wp:comment_author_url>{comment_author_url}</wp:comment_author_url>
        <wp:comment_user_id>0</wp:comment_user_id>
        <wp:comment_parent>{comment_parent}</wp:comment_parent>
        <wp:comment_type></wp:comment_type>
        <wp:comment_id>{comment_id}</wp:comment_id>
      </wp:comment>
"""


def get_comment(dom, blog_author):
    new_dom = str(dom).replace("</br>", "<br/>").replace("<br>", "<br/>")
    soup = BeautifulSoup(new_dom, "html.parser")

    comment_dom_strings = []

    for comment_dom in soup.find_all("table", id="comment"):
        prev_comment_id = "0"
        for visitor_dom in comment_dom.find_all("td", text=["網主回覆：", "訪客名稱："]):
            current_dom = visitor_dom
            next_dom = current_dom.find_next("td")

            comment_author_url = ""
            comment_content = ""
            date = ""
            comment_parent = "0"

            if current_dom.text == "網主回覆：":
                comment_author = blog_author
                comment_content = ""
                comment_parent = prev_comment_id
                for sub_element in next_dom.contents:
                    if isinstance(sub_element, str):
                        continue
                    elif sub_element.text.startswith("Posted at "):
                        date = sub_element.text[len("Posted at "):]
                    else:
                        comment_content += str(sub_element)
            else:
                a_dom = next_dom.find_next("a", title="會員資料")
                if a_dom is not None:
                    comment_author_url = a_dom.attrs["href"]
                    comment_author = a_dom.string
                else:
                    comment_author = next_dom.string

                comment_dom = next_dom.find_next('td', text="留言內容：").find_next("td")
                for sub_element in comment_dom.contents:
                    comment_content += str(sub_element)

                date_dom = comment_dom \
                    .find_next("td", {"width": "92%", "height": "28", "valign": "bottom"}) \
                    .find_next("span")
                date = date_dom.text[len("Posted at "):]

            if date == "":
                print("something")
            d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %p')

            comment_date = d.strftime("%Y-%m-%d %H:%M:%S")
            comment_date_gmt = d.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            comment_id = int(datetime.timestamp(d))
            prev_comment_id = comment_id
            comment_dom_strings.append(comment_template.format(comment_author=comment_author,
                                                               comment_author_url=comment_author_url,
                                                               comment_content=comment_content,
                                                               comment_date=comment_date,
                                                               comment_date_gmt=comment_date_gmt,
                                                               comment_id=comment_id,
                                                               comment_parent=comment_parent))

    # remove duplicated comment
    comment_dom_strings = list(dict.fromkeys(comment_dom_strings))

    result_dom = ""
    comment_count = 0
    for comment_dom_string in comment_dom_strings:
        result_dom += comment_dom_string
        comment_count += 1

    return result_dom, comment_count
