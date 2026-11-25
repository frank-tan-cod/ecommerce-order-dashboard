#!/usr/bin/env bash
# 发布静态站到 GitHub Pages
# 前置：已安装 gh 并登录（frank-tan-cod），仓库不存在
set -e
cd "$(dirname "$0")"

REPO="frank-tan-cod/ecommerce-order-dashboard"
URL="https://frank-tan-cod.github.io/ecommerce-order-dashboard/"

if [ ! -d .git ]; then
  git init -b main
fi
git add .
git -c user.name="frank-tan-cod" -c user.email="frank-tan-cod@users.noreply.github.com" \
  commit -m "Update ecommerce dashboard" || true

if ! gh repo view "$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public --source=. --remote=origin --push \
    --description "基于 Hadoop 生态的电商订单数据分析系统可视化看板"
else
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$REPO.git"
  git push -u origin main
fi

# 启用 GitHub Pages：main 分支根目录
printf '{"source":{"branch":"main","path":"/"},"build_type":"legacy"}' \
  | gh api --method POST "repos/$REPO/pages" --input - >/dev/null 2>&1 || true

sleep 8
gh api "repos/$REPO/pages" 2>/dev/null | head -20 || true
echo
echo "站点地址：$URL"
echo "首次发布通常需要 1–2 分钟，构建完成后可访问。"
