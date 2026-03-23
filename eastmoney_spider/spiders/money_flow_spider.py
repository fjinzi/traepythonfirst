import scrapy
import json
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from datetime import datetime
from eastmoney_spider.items import StockMoneyFlowItem


class MoneyFlowSpider(scrapy.Spider):

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
            
        }
        
        yield scrapy.Request(
            url=api_url,
            method="GET",
            callback=self.parse_api_response
        )
    
    def parse_api_response(self, response):
        self.logger.info(f"响应状态码: {response.status}")
        self.logger.info(f"响应内容: {response.text[:500]}")
        
        try:
            json_data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("JSON解析失败")
            return
        
        if not json_data or json_data.get("data") is None:
            self.logger.error(f"未获取到有效数据, json_data: {json_data}")
            return
        
        diff_data = json_data["data"].get("diff", [])
        if not diff_data:
            self.logger.error("数据列表为空")
            return
        
        xml_content = self._build_xml_from_data(diff_data)
        
        items = self.parse_with_beautifulsoup(xml_content)
        
        for item in items:
            yield item
    
    def _build_xml_from_data(self, data_list):
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append("<stocks>")
        
        for idx, item in enumerate(data_list, 1):
            xml_parts.append("<stock>")
            xml_parts.append(f"<rank>{idx}</rank>")
            xml_parts.append(f"<code>{item.get('f12', '')}</code>")
            xml_parts.append(f"<name><![CDATA[{item.get('f14', '')}]]></name>")
            xml_parts.append(f"<latest_price>{item.get('f2', 0)}</latest_price>")
            xml_parts.append(f"<change_percent>{item.get('f3', 0)}</change_percent>")
            xml_parts.append(f"<large_net_inflow>{item.get('f72', 0)}</large_net_inflow>")
            xml_parts.append(f"<small_net_inflow>{item.get('f84', 0)}</small_net_inflow>")
            xml_parts.append(f"<small_net_inflow_ratio>{item.get('f87', 0)}</small_net_inflow_ratio>")
            xml_parts.append("</stock>")
        
        xml_parts.append("</stocks>")
        return "\n".join(xml_parts)
    
    def parse_with_beautifulsoup(self, xml_content):
        soup = BeautifulSoup(xml_content, "xml")
        
        items = []
        
        stocks = soup.find_all("stock")
        
        for stock in stocks:
            item = StockMoneyFlowItem()
            
            item["rank"] = self._get_text(stock, "rank")
            item["code"] = self._get_text(stock, "code")
            item["name"] = self._get_text(stock, "name")
            item["latest_price"] = self._get_text(stock, "latest_price")
            item["change_percent"] = self._get_text(stock, "change_percent")
            item["main_net_inflow"] = self._format_amount(self._get_text(stock, "main_net_inflow"))
            item["main_net_inflow_ratio"] = self._get_text(stock, "main_net_inflow_ratio")
            item["super_large_net_inflow"] = self._format_amount(self._get_text(stock, "super_large_net_inflow"))
            item["medium_net_inflow_ratio"] = self._get_text(stock, "medium_net_inflow_ratio")
            item["small_net_inflow"] = self._format_amount(self._get_text(stock, "small_net_inflow"))
            item["small_net_inflow_ratio"] = self._get_text(stock, "small_net_inflow_ratio")
            
            items.append(item)
        
        self.logger.info(f"BeautifulSoup成功解析 {len(items)} 条数据")
        return items
    
    def _get_text(self, parent, tag_name):
        tag = parent.find(tag_name)
        if tag:
            return tag.get_text()
        return "-"
    
    def _format_amount(self, value):
        try:
            amount = float(value)
            if abs(amount) >= 100000000:
                return f"{amount/100000000:.2f}亿"
            elif abs(amount) >= 10000:
                return f"{amount/10000:.2f}万"
            else:
                return f"{amount:.2f}"
        except (ValueError, TypeError):
            return "-"
