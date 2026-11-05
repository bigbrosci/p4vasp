# 每日一句

`daily.json`保存离线经典语句、篇名和参考网址。当前12条，按本机日历日期顺序轮换；同一天重复启动不随机更换，12天后循环。程序每分钟检查日期，仅空闲时更新，不覆盖任务或错误。

语句取自公版古籍《论语·为政》《荀子·劝学》《老子》第六十四章，文字按简体与现代标点整理，部分为原文节选。参考网页为Chinese Text Project：

- https://ctext.org/analects/wei-zheng/ens
- https://ctext.org/xunzi/quan-xue
- https://ctext.org/text.pl?if=en&node=11655&remap=gb&show=parallel

本轮核对使用网站搜索索引摘录；直接抓取部分页面受403访问限制，不声称做过版本学全文校勘。应用显示时不访问这些网站。

维护者可增加或替换条目，保留非空字符串`text`、`source`、`url`。修改后重启；条目数改变会改变日期与名句的对应关系。文件缺失或格式错误时使用内置《老子》语句后备，不影响启动。
