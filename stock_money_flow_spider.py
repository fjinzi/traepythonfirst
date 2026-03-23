import requests
import pandas as pd
import time
from datetime import datetime


def get_stock_money_flow_data(page_size=50):
    api_url = "https://push2.eastmoney.com/api/qt/clist/get"
    
    params = {
        "fid": "f62",
        "po": "1",
        "pz": page_size,
        "pn": "1",
        "np": "1",
        "fltt": "2",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f1,f2,f3,f12,f13,f14,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://data.eastmoney.com/zjlx/detail.html",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def parse_data(json_data):
    if not json_data or json_data.get("data") is None:
        print("未获取到有效数据")
        return []
    
    diff_data = json_data["data"].get("diff", [])
    if not diff_data:
        print("数据列表为空")
        return []
    
    parsed_list = []
    
    for idx, item in enumerate(diff_data, 1):
        try:
            stock_code = item.get("f12", "")
            stock_name = item.get("f14", "")
            latest_price = item.get("f2", 0)
            change_percent = item.get("f3", 0)
            
            main_net_inflow = item.get("f62", 0)
            main_net_inflow_ratio = item.get("f184", 0)
            
            super_large_net_inflow = item.get("f66", 0)
            super_large_net_inflow_ratio = item.get("f69", 0)
            
            large_net_inflow = item.get("f72", 0)
            large_net_inflow_ratio = item.get("f75", 0)
            
            medium_net_inflow = item.get("f78", 0)
            medium_net_inflow_ratio = item.get("f81", 0)
            
            small_net_inflow = item.get("f84", 0)
            small_net_inflow_ratio = item.get("f87", 0)
            
            def format_value(val):
                if val == "-" or val is None:
                    return "-"
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return "-"
            
            def format_amount(val):
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
            
            parsed_list.append({
                "序号": idx,
                "代码": stock_code,
                "名称": stock_name,
                "最新价": format_value(latest_price),
                "今日涨跌幅(%)": format_value(change_percent),
                "主力净流入-净额": format_amount(main_net_inflow),
                "主力净流入-净占比(%)": format_value(main_net_inflow_ratio),
                "超大单净流入-净额": format_amount(super_large_net_inflow),
                "超大单净流入-净占比(%)": format_value(super_large_net_inflow_ratio),
                "大单净流入-净额": format_amount(large_net_inflow),
                "大单净流入-净占比(%)": format_value(large_net_inflow_ratio),
                "中单净流入-净额": format_amount(medium_net_inflow),
                "中单净流入-净占比(%)": format_value(medium_net_inflow_ratio),
                "小单净流入-净额": format_amount(small_net_inflow),
                "小单净流入-净占比(%)": format_value(small_net_inflow_ratio)
            })
        except Exception as e:
            print(f"解析第{idx}条数据时出错: {e}")
            continue
    
    return parsed_list


def save_to_excel(data, filename=None):
    if not data:
        print("没有数据可保存")
        return None
    
    if filename is None:
        today = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_money_flow_{today}.xlsx"
    
    df = pd.DataFrame(data)
    
    try:
        df.to_excel(filename, index=False, engine="openpyxl")
        print(f"数据已成功保存到: {filename}")
        return filename
    except Exception as e:
        print(f"保存Excel文件失败: {e}")
        csv_filename = filename.replace(".xlsx", ".csv")
        df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        print(f"已改用CSV格式保存到: {csv_filename}")
        return csv_filename


def main():
    print("=" * 60)
    print("东方财富网 - 个股资金流向数据爬虫")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    print("\n正在获取数据...")
    json_data = get_stock_money_flow_data(page_size=50)
    
    if json_data is None:
        print("获取数据失败，程序退出")
        return
    
    print("正在解析数据...")
    parsed_data = parse_data(json_data)
    
    if not parsed_data:
        print("解析数据失败，程序退出")
        return
    
    print(f"成功解析 {len(parsed_data)} 条数据")
    
    print("\n数据预览 (前5条):")
    print("-" * 60)
    for item in parsed_data[:5]:
        print(f"{item['序号']}. {item['代码']} {item['名称']} | "
              f"涨跌幅: {item['今日涨跌幅(%)']}% | "
              f"主力净流入: {item['主力净流入-净额']}")
    
    print("-" * 60)
    print("\n正在保存到Excel文件...")
    saved_file = save_to_excel(parsed_data)
    
    print("-" * 60)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
