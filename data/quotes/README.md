# 每日一句

`daily.sqlite3` 的 `daily_quotes` 表按 `publish_date`（本机日历的 YYYY-MM-DD）安排每日一句。首批从 2026-11-25 至 2029-08-20，共 1000 条，含 16 条原创与 984 条节选。底部显示语句和作者，悬停可查看日期、出处和思考问题。程序启动时只读载入，每分钟检查日期，仅空闲时更新。

英文节选来自以下公版译本。每条记录有作者、作品、译者、章节或条目编号及来源网址。多数节选由程序筛选，思考问题按主题共用；开头几条经过人工挑选并配有专属问题。

- [La Rochefoucauld, Reflections; or Sentences and Moral Maxims](https://www.gutenberg.org/ebooks/9105)
- [Nietzsche, Human, All Too Human, Part I](https://www.gutenberg.org/ebooks/51935) 与 [Part II](https://www.gutenberg.org/ebooks/37841)
- [Pascal, Pensées](https://www.gutenberg.org/ebooks/18269)
- [Marcus Aurelius, Thoughts of Marcus Aurelius](https://www.gutenberg.org/ebooks/6920)
- [Epictetus, The Golden Sayings of Epictetus](https://www.gutenberg.org/ebooks/871)

维护者可检查或延长日期表，修改后重启生效。

```sql
SELECT publish_date, quote, author FROM daily_quotes ORDER BY publish_date;
```

### 未排期日期的后备词库

数据库不可读或当天没有排期时，按本机日期轮换使用 `daily.json` 中的 16 条语句（12 条中文、4 条英文）。

语句取自公版古籍《论语·为政》《荀子·劝学》《老子》第六十四章，文字按简体与现代标点整理，部分为原文节选。参考网页为Chinese Text Project：

- https://ctext.org/analects/wei-zheng/ens
- https://ctext.org/xunzi/quan-xue
- https://ctext.org/text.pl?if=en&node=11655&remap=gb&show=parallel

本轮核对使用网站搜索索引摘录；直接抓取部分页面受403访问限制，不声称做过版本学全文校勘。应用显示时不访问这些网站。

维护者可增加或替换条目，保留非空字符串`text`、`source`、`url`。修改后重启；条目数改变会改变日期与名句的对应关系。文件缺失或格式错误时使用内置《老子》语句后备，不影响启动。


2026-11-11：采纳 wikidog 于2026-11-10提出的建议，每3条中文后穿插1条英文原句。新增英文来自 Emerson《Self-Reliance》（3条）与 Shakespeare《Hamlet》第一幕第三场（1条），已核对以下全文来源：

- https://www.gutenberg.org/cache/epub/2944/pg2944-images.html
- https://shakespeare.folger.edu/downloads/pdf/hamlet_PDF_FolgerShakespeare.pdf

`language` 可选为 `zh` 或 `en`，英文显示作者/作品，中文保留书名号；旧条目不带该字段时仍兼容。英文为公版原文短句，不是中文语句的翻译。新词库会改变日期与语句的对应关系，程序运行时仍完全离线。
