BOT_NAME = "eastmoney_spider"

SPIDER_MODULES = ["eastmoney_spider.spiders"]
NEWSPIDER_MODULE = "eastmoney_spider.spiders"

ROBOTSTXT_OBEY = False

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 1

DEFAULT_REQUEST_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://data.eastmoney.com/zjlx/detail.html"
}

ITEM_PIPELINES = {
    "eastmoney_spider.pipelines.ExcelPipeline": 300,
}

LOG_LEVEL = "INFO"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
