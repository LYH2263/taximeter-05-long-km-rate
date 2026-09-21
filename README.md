# 14-taximeter（打车计价）

Taximeter — 起步价 + 里程价 + 低速时长费（夜间加价系数）

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4300 |
| API | http://localhost:9300 |

## 主链

录行程里程与低速时长 → 拆解车费 → 行程单

## 远程里程单价（modules/long_km_rate）

- 规则含「远程起算公里」与「远程每公里单价」；单价必须为正，远程起算必须大于现行含公里。
- 同一时间只允许一条规则启用，冲突时拒绝并点名两条规则标识；可创建/更新/停用。
- 计费分段：含公里内走起步，含公里～远程起算走现行每公里，超出远程起算改走远程单价；低速费仍按现行低速单价。停用后全程恢复单一每公里、远程里程费为零。
- 打表结果拆为 `mileage`（普通里程费）与 `long_mileage`（远程里程费），应付 = 起步 + 两段里程 + 低速。已落库记录保留当时两段，事后改价不改写历史；只读试算（persist=false）不写记录。
- 规则接口：`GET/POST /api/long-km-rates`、`PUT /api/long-km-rates/{id}`、`POST /api/long-km-rates/{id}/deactivate`。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
