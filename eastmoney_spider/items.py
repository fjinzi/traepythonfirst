from scrapy.item import Item, Field


class StockMoneyFlowItem(Item):
    rank = Field()
    code = Field()
    name = Field()
    latest_price = Field()
    change_percent = Field()
    main_net_inflow = Field()
    main_net_inflow_ratio = Field()
    super_large_net_inflow = Field()
    super_large_net_inflow_ratio = Field()
    large_net_inflow = Field()
    large_net_inflow_ratio = Field()
    medium_net_inflow = Field()
    medium_net_inflow_ratio = Field()
    small_net_inflow = Field()
    small_net_inflow_ratio = Field()
