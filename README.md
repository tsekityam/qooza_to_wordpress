# Qooza backup file to WordPress format converter

[Qooza](http://www.qooza.hk) was a popular blogger platform in Hong Kong. The backup of the file provide by the site is in a HTML file, which cannot be imported to [WordPress](https://www.wordpress.org), one of the most famous blogging platform in the world.

This is a python platform that can convert the HTML backup file to XML file, which can be imported to WordPress.

## Dependencies

* bs4 v4.8.2
* pytz v2019.3

## Instruction

1. `$ cd {project_directory}`
2. `$ python main.py -i {path_to_backup_file}`

`output.xml` file will be created in `{project_directory}`, which can be imported to WordPress.

The output is in backup of Xanga format. Please follow [this instruction](https://en.support.wordpress.com/import/import-from-xanga/) to import the file to WordPress

## Known issue
There are two minor issues of the program, however, the root cause of the issues are mostly related to Qooza, not the program. There is no plan to fix the issues.

### Invalid HTML syntax handling
There is a chance that the Qooza backup file contains invalid HTML syntax. We need to fix the syntax manually before processing it, or the program may crash

e.g. `<s{{comment}}></s>` can be found in my backup file. I need to correct it as `<s>{{comment}}</s>` before the run.

### Incorrect comment count
The backup file contains the total number of the comments in the file.

```html
<font size="2" face="Arial" color="#333333">
  日誌名稱： {{blog_name}}
  <br />
  日誌網址：
  <a href="http://blog.qooza.hk/{{username}}" target="_blank">
    http://blog.qooza.hk/{{username}}
  </a>
  <br />
  用戶名稱： {{username}}
  <br />
  備份時間： {{backup_at}}
  <br />
  日誌數目： {{blog_count}} 篇
  <br />
  留言數目： {{comment_count}} 個 &nbsp;( {{reply_count}} 個回覆 )
</font>
```

`comment_count` is the number of comments post by the visitors of the blog. `reply_count` is the number of the comments that the author replied to comments. The total number of comments in the backup file should be `comment_count` + `reply_count`.

However, I found that the number of comments in my backup file doesn't match the sum of the numbers. There are missing comments in the backup file. The program will give you a warning if it happens

### Duplicated comments
There are two duplicated comments in my backup file. WordPress may deduplicated it during import.