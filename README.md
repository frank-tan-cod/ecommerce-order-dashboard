# 电商订单数据分析系统 · 公网看板

基于 Hadoop 生态的电商订单数据分析系统静态展示页，数据来自 Kafka → HDFS/HBase → Hive 的实际查询结果。

**公网地址：<https://frank-tan-cod.github.io/ecommerce-order-dashboard/>**

- 有效订单：5000（清洗去重后）
- 原始消息：5120（含 100 条异常、20 条重复）
- HBase 唯一 RowKey：5100
- 统计区间：2026-11-17 至 2026-11-23（模拟订单数据）
- 技术栈：Hadoop 3.3.2、Hive 3.1.3、HBase 2.4.18、Kafka 2.8.2、ZooKeeper 3.5.9、Python 3.10、matplotlib、ECharts

## 页面内容

- 核心指标 KPI：订单量、GMV、已支付 GMV、支付转化率、HBase 行数
- ECharts 交互图：类别占比、类别已支付 GMV、每日趋势、小时分布、高价值用户、订单状态
- 热销商品与异常数据类型表
- matplotlib 学术风格静态图（PNG + PDF 矢量版）
- 系统架构图与数据流程图
- 数据质量与一致性对账

## 本地预览

```bash
python -m http.server 8090
# 打开 http://localhost:8090/
```

## 数据生成

`build_site.py` 从 `../exports/*.csv` 汇总 `assets/data.json`，并把 `../figures`、`../diagrams` 复制到 `assets/`。重新生成：

```bash
python build_site.py
```

## 部署

本仓库通过 GitHub Pages 发布，`main` 分支根目录即站点根目录。`assets/echarts.min.js` 已本地化，无外部 CDN 依赖。
