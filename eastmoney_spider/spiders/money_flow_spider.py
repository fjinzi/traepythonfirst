import scrapy
import json
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from datetime import datetime
from eastmoney_spider.items import StockMoneyFlowItem


class MoneyFlowSpider(scrapy.Spider):
    name = "money_flow"
    allowed_domains = ["eastmoney.com", "push2.eastmoney.com"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 1,
    }

    def start_requests(self):
        base_url = "https://push2.eastmoney.com/api/qt/clist/get"

        params = {
            "fid": "f62",
            "po": "1",
            "pz": 50,
            "pn": "1",
            "np": "1",
            "fltt": "2",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
            "fields": "f1,f2,f3,f12,f13,f14,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13"
        }

        api_url = f"{base_url}?{urlencode(params)}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://data.eastmoney.com/zjlx/detail.html",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }

        yield scrapy.Request(
            url=api_url,
            method="GET",
            headers=headers,
            callback=self.parse_api_response
        )

    def parse_api_response(self, response):
        self.logger.info(f"响应状态码: {response.status}")
        self.logger.info(f"响应内容前500字符: {response.text[:500]}")

        try:
            json_data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            return

        if not json_data or json_data.get("data") is None:
            self.logger.error(f"未获取到有效数据, json_data: {json_data}")
            return

        diff_data = json_data["data"].get("diff", [])
        if not diff_data:
            self.logger.error("数据列表为空")
            return

        self.logger.info(f"获取到 {len(diff_data)} 条原始数据")

        for idx, item in enumerate(diff_data, 1):
            stock_item = self._parse_stock_item(idx, item)
            if stock_item:
                yield stock_item

    def _parse_stock_item(self, rank, item):
        try:
            stock_item = StockMoneyFlowItem()

            stock_item["rank"] = rank
            stock_item["code"] = item.get("f12", "")
            stock_item["name"] = item.get("f14", "")
            stock_item["latest_price"] = self._format_value(item.get("f2", 0))
            stock_item["change_percent"] = self._format_value(item.get("f3", 0))

            stock_item["main_net_inflow"] = self._format_amount(item.get("f62", 0))
            stock_item["main_net_inflow_ratio"] = self._format_value(item.get("f184", 0))

            stock_item["super_large_net_inflow"] = self._format_amount(item.get("f66", 0))
            stock_item["super_large_net_inflow_ratio"] = self._format_value(item.get("f69", 0))

            stock_item["large_net_inflow"] = self._format_amount(item.get("f72", 0))
            stock_item["large_net_inflow_ratio"] = self._format_value(item.get("f75", 0))

            stock_item["medium_net_inflow"] = self._format_amount(item.get("f78", 0))
            stock_item["medium_net_inflow_ratio"] = self._format_value(item.get("f81", 0))

            stock_item["small_net_inflow"] = self._format_amount(item.get("f84", 0))
            stock_item["small_net_inflow_ratio"] = self._format_value(item.get("f87", 0))

            return stock_item
        except Exception as e:
            self.logger.error(f"解析第{rank}条数据时出错: {e}")
            return None

    def _format_value(self, val):
        if val == "-" or val is None:
            return "-"
        try:
            return float(val)
        except (ValueError, TypeError):
            return "-"

    def _format_amount(self, val):
        if val == "-" or val is None:
            return "-"
        try:
            amount = float(val)
            if abs(amount) >= 100000000:
                return f"{amount/100000000:.2f}亿"
            elif abs(amount) >= 10000:
                return f"{amount/10000:.2f}万"
            else:
                return f"{amount:.2f}"
        except (ValueError, TypeError):
            return "-"
