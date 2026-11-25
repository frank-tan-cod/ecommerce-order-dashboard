#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 GitHub Pages 静态站点：
- 从 project/exports/*.csv 汇总 data.json
- 复制 ECharts、matplotlib 图、架构图到 web/assets
- 页面本身是纯静态 HTML/CSS/JS，不需要 Flask
"""
import csv
import json
import shutil
from datetime import datetime
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
WEB = PROJECT / "web"
ASSETS = WEB / "assets"


def read_csv(name):
    path = PROJECT / "exports" / f"{name}.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def main():
    for sub in ("assets", "assets/figures", "assets/diagrams"):
        (WEB / sub).mkdir(parents=True, exist_ok=True)

    consistency = read_csv("consistency")
    category = read_csv("category_summary")
    daily = read_csv("daily_trend")
    hourly = read_csv("hourly")
    users = read_csv("user_top10")
    top3 = read_csv("daily_top3")
    status = read_csv("hbase_status")
    anomaly = read_csv("anomaly_types")
    hot = read_csv("product_hot")

    order_cnt = sum(num(r.get("order_cnt")) for r in category)
    gmv = sum(num(r.get("gmv")) for r in category)
    paid_gmv = sum(num(r.get("paid_gmv")) for r in category)
    paid_orders = sum(num(r.get("paid_orders")) for r in category)
    base = consistency[0] if consistency else {}
    summary = {
        "raw_rows": int(num(base.get("raw_rows"))),
        "distinct_order_ids": int(num(base.get("distinct_order_ids"))),
        "valid_rows_in_raw": int(num(base.get("valid_rows_in_raw"))),
        "invalid_rows": int(num(base.get("invalid_rows_in_raw"))),
        "duplicate_extra_rows": int(num(base.get("duplicate_extra_rows"))),
        "clean_rows": int(num(base.get("valid_rows_in_raw")) - num(base.get("duplicate_extra_rows"))),
        "order_cnt": int(order_cnt),
        "gmv": round(gmv, 2),
        "paid_gmv": round(paid_gmv, 2),
        "paid_orders": int(paid_orders),
        "pay_conversion": round(paid_orders / order_cnt, 4) if order_cnt else 0,
        "avg_order_value": round(gmv / order_cnt, 2) if order_cnt else 0,
        "hbase_rows": 0,
    }

    def clean_rows(rows, numeric=()):
        out = []
        for r in rows:
            d = dict(r)
            for k in numeric:
                if k in d:
                    d[k] = num(d[k])
            out.append(d)
        return out

    data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "period": "2026-11-17 至 2026-11-23",
        "summary": summary,
        "category": clean_rows(category, ("order_cnt", "gmv", "paid_gmv", "paid_orders",
                                          "avg_order_value", "pay_conversion")),
        "daily": clean_rows(daily, ("order_cnt", "gmv", "paid_gmv", "paid_orders")),
        "hourly": clean_rows(hourly, ("hr", "order_cnt", "gmv", "paid_gmv")),
        "users": clean_rows(users, ("paid_orders", "paid_amount")),
        "top3": clean_rows(top3, ("rn", "gmv")),
        "status": clean_rows(status, ("order_cnt",)),
        "anomaly": clean_rows(anomaly, ("cnt",)),
        "hot": clean_rows(hot, ("paid_orders", "total_quantity", "paid_sales")),
    }
    # HBase 行数 = 合法状态订单数 + 异常行数（异常行也写入 HBase）
    data["summary"]["hbase_rows"] = int(sum(num(r.get("order_cnt")) for r in status) + summary["invalid_rows"])
    (ASSETS / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ECharts 本地化
    src = PROJECT / "dashboard" / "static" / "echarts.min.js"
    if src.exists():
        shutil.copy2(src, ASSETS / "echarts.min.js")

    # 论文图与架构图
    for p in (PROJECT / "figures").glob("*"):
        if p.suffix.lower() in (".png", ".pdf"):
            shutil.copy2(p, ASSETS / "figures" / p.name)
    for name in ("architecture.png", "dataflow.png"):
        p = PROJECT / "diagrams" / name
        if p.exists():
            shutil.copy2(p, ASSETS / "diagrams" / name)

    print("data.json:", (ASSETS / "data.json"), "size", (ASSETS / "data.json").stat().st_size)
    print("figures:", len(list((ASSETS / "figures").glob("*"))))
    print("echarts:", (ASSETS / "echarts.min.js").exists())


if __name__ == "__main__":
    main()
