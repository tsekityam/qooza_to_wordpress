import getopt
import html
import sys
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import comment_helper

prefix = """
    <rss version="2.0" xmlns:excerpt="http://wordpress.org/export/1.1/excerpt/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:wfw="http://wellformedweb.org/CommentAPI/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:wp="http://wordpress.org/export/1.1/">
      <channel>
        <title>{title}</title>
        <wp:wxr_version>1.1</wp:wxr_version>
        <wp:multisite>
          <wp:xanga_user_id>{username}</wp:xanga_user_id>
          <wp:site_title>{title}</wp:site_title>
        </wp:multisite>
        <wp:author>
          <wp:author_login>{username}</wp:author_login>
          <wp:author_display_name>{username}</wp:author_display_name>
        </wp:author>
    """

blog_template = """
    <item>
      <title>{title}</title>
      <dc:creator>{creator}</dc:creator>
      <pubDate>{post_date}</pubDate>
      <content:encoded><![CDATA[{content}]]></content:encoded>
      <wp:post_date>{post_date}</wp:post_date>
      <wp:post_date_gmt>{post_date_gmt}</wp:post_date_gmt>
      <wp:comment_status>open</wp:comment_status>
      <wp:status>Publish</wp:status>
      <wp:post_type>post</wp:post_type>
      <wp:original_xanga_id>{original_xanga_id}</wp:original_xanga_id>
      {comment}
    </item>
"""

suffix = """
  </channel>
</rss>
"""


def main(argv):
    input_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:")
    except getopt.GetoptError:
        print('test.py -i <input_file>')
        exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <input_file>')
            exit()
        elif opt == "-i":
            input_file = arg

    dom = open(input_file, 'r').read()

    soup = BeautifulSoup(dom, "html.parser")

    post_dates = []
    titles = []
    contents = []
    publish_dates = []
    original_xanga_ids = []

    comments = {}

    username = ""
    title = ""
    actual_blog_count = 0
    expected_comment_count = 0

    body_dom = soup.find("body")
    blog_info_dom = body_dom.find()
    for i in blog_info_dom.contents:
        if isinstance(i, str):
            i = i.strip()
            if i.startswith("日誌名稱： "):
                title = i[len("日誌名稱： "):]
            elif i.startswith("用戶名稱： "):
                username = i[len("用戶名稱： "):]
            elif i.startswith("日誌數目： "):
                actual_blog_count = int((i[len("日誌數目： "):])[:-len(" 篇")])
            elif i.startswith("留言數目： "):
                regex = r"留言數目： ([0-9]*) 個\W*([0-9]*)"
                matches = re.finditer(regex, i)

                for matchNum, match in enumerate(matches, start=1):
                    expected_comment_count = (int(match.groups()[0]) + int(match.groups()[1]))

    for element in soup.find_all("table", class_="date"):
        post_dates.append(element.text.strip())

    for element in soup.find_all("td", class_="blogtopic"):
        titles.append(element.text)

    for element in soup.find_all("td", class_="blogcontent"):
        content = ""
        for sub_element in element.contents:
            content += str(sub_element)
        contents.append(content)

    for element in soup.find_all("td", class_="contentfooter"):
        date_string = element.text[len("發表時間："):len("2010-06-27 01:07:32") + len("發表時間：")]
        publish_dates.append(datetime.fromisoformat(date_string + "+08:00"))

    actual_comment_count = 0
    for element in soup.find_all("a", {"name": True}):
        id_ = element.attrs['name']
        original_xanga_ids.append(element.attrs['name'])
        comments[id_] = ""

        comment_dom = soup.find("div", id="comment" + id_)
        if comment_dom is not None:
            comment_dom_string, comment_count = comment_helper.get_comment(comment_dom, username)
            comments[id_] = comment_dom_string
            actual_comment_count += comment_count

    if len(post_dates) != actual_blog_count or \
            len(titles) != actual_blog_count or \
            len(contents) != actual_blog_count or \
            len(publish_dates) != actual_blog_count or \
            len(original_xanga_ids) != actual_blog_count:
        print("Error: failed to extract all blog")
        exit(1)

    if actual_comment_count != expected_comment_count:
        print("Warning: comment count in the output file is different from expected: " +
              "{expected} expected but only found {actual}.".format(
                  expected=expected_comment_count, actual=actual_comment_count))

    result = ""
    for x in range(0, actual_blog_count):
        result += blog_template.format(title=html.escape(titles[x]),
                                       creator=username,
                                       content="<p>" + post_dates[x] + "</p>\n" + contents[x],
                                       pubDate=publish_dates[x].strftime("%a, %d %b %Y %H:%M:%S +08:00"),
                                       post_date=publish_dates[x].strftime("%Y-%m-%d %H:%M:%S"),
                                       post_date_gmt=publish_dates[x].astimezone(pytz.utc).strftime(
                                           "%Y-%m-%d %H:%M:%S"),
                                       original_xanga_id=original_xanga_ids[x],
                                       comment=comments[original_xanga_ids[x]], )

    text_file = open("output.xml", "w")
    text_file.write(prefix.format(username=username, title=title) + result + suffix)
    text_file.close()


if __name__ == "__main__":
    main(sys.argv[1:])
