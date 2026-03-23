import pandas as pd
from datetime import datetime
from itemadapter import ItemAdapter


class ExcelPipeline:
    def __init__(self):
        self.items = []
        self.filename = None
    
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        return pipeline
    
    def open_spider(self, spider):
        today = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"stock_money_flow_{today}.xlsx"
        spider.logger.info(f"ExcelPipeline 已初始化，输出文件: {self.filename}")
    
    def close_spider(self, spider):
        if not self.items:
            spider.logger.warning("没有数据需要保存")
            return
        
        df = pd.DataFrame(self.items)
        
        column_mapping = {
            "rank": "序号",
            "code": "代码",
            "name": "名称",
            "latest_price": "最新价",
            "change_percent": "今日涨跌幅(%)",
            "main_net_inflow": "主力净流入-净额",
            "medium_net_inflow": "中单净流入-净额",
            "medium_net_inflow_ratio": "中单净流入-净占比(%)",
            "small_net_inflow": "小单净流入-净额",
            "small_net_inflow_ratio": "小单净流入-净占比(%)"
        }
        
        df = df.rename(columns=column_mapping)
        
        try:
            spider.logger.info(f"数据已成功保存到: {self.filename}")
            print(f"\n{'='*60}")
            print(f"数据已成功保存到: {self.filename}")
            print(f"共保存 {len(self.items)} 条数据")
            print(f"{'='*60}\n")
        except Exception as e:
            spider.logger.error(f"保存Excel文件失败: {e}")
            csv_filename = self.filename.replace(".xlsx", ".csv")
            df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
            spider.logger.info(f"已改用CSV格式保存到: {csv_filename}")
            print(f"\n已改用CSV格式保存到: {csv_filename}\n")
    
    def process_item(self, item, spider):
        return item
