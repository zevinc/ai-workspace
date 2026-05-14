---
title: HTTP 协议面试题型完整归类与详解
tags:
  - http
  - https
  - interview
  - network
  - protocol
  - cache
  - cookie
  - session
  - token
  - jwt
  - tls
  - cors
  - http2
  - http3
  - quic
summary: HTTP 协议面试题型系统归类，覆盖 8 大类：基础概念、版本演进(0.9→3)、方法(GET/POST/PUT/PATCH...)、状态码(1xx~5xx)、头部、HTTPS/TLS、认证(Cookie/Session/JWT)、缓存(强缓存/协商缓存)，每类配有经典追问与标准答案，按初/中/高级标注重点。
created: 2026-05-14
---

# 背景

HTTP（HyperText Transfer Protocol）是后端开发面试中出现频率最高的网络协议考点。从校招到架构师级别，考察深度从"背状态码"延伸到"HTTP/3 QUIC 的 0-RTT 握手原理"。本文按 8 大类系统归并所有高频题型与标准答案。

# 分类总览

| 类别 | 子考点数 | 适用级别 |
|------|----------|----------|
| 基础概念 | 5 | 初级+ |
| 版本演进 | HTTP/0.9 → HTTP/3 | 中高级+ |
| HTTP 方法 | 9 种方法 | 初级+ |
| 状态码 | 1xx~5xx | 初级+ |
| HTTP 头部 | 20+ 头部 | 中级+ |
| HTTPS / TLS | 加密原理、握手、证书 | 中高级+ |
| 认证机制 | Cookie / Session / JWT | 中级+ |
| 缓存策略 | 强缓存 / 协商缓存 | 高级+ |

---

# 一、基础概念

## 1.1 HTTP 是什么？

超文本传输协议（HyperText Transfer Protocol），应用层协议，工作在 TCP/IP 协议栈之上。基于**请求-响应模型**：客户端发送请求，服务端返回响应。

## 1.2 HTTP 的特点

| 特性 | 说明 |
|------|------|
| **无状态** | 协议本身不记录历史请求。解决方案：Cookie、Session、Token |
| **无连接**（HTTP/1.0） | 每次请求都建新 TCP 连接。HTTP/1.1 引入 Keep-Alive 持久连接 |
| **明文传输** | HTTP 报文不加密，中间人可窃听/篡改。HTTPS 解决此问题 |
| **灵活可扩展** | Header 字段可自由添加，天然支持内容协商 |
| **简单快速** | 请求方法 + URI + 协议版本，结构简单 |

## 1.3 URL / URI / URN 区别

```
┌───────────────── URI (统一资源标识符) ─────────────────┐
│                                                        │
│  URL (统一资源定位符)              URN (统一资源名称)      │
│  https://example.com/users/1     urn:isbn:0451450523   │
│  "资源在哪 + 怎么访问"            "资源叫什么"             │
└────────────────────────────────────────────────────────┘
```

- **URI** = Uniform Resource Identifier，统称
- **URL** = Uniform Resource Locator，含访问方式（协议+地址+路径）
- **URN** = Uniform Resource Name，纯名称标识，不关心在哪

**经典追问**："Java 中 `java.net.URI` 和 `java.net.URL` 的区别？" → URI 是纯标识，不保证可解析；URL 需要能定位到资源并打开连接。

## 1.4 HTTP 报文结构

```
┌──────────────────────────┐
│  起始行 (请求行/状态行)     │  GET /api/users HTTP/1.1
│                          │  HTTP/1.1 200 OK
├──────────────────────────┤
│  头部字段 (Headers)       │  Host: example.com
│                          │  Content-Type: application/json
├──────────────────────────┤
│  空行 (CRLF)              │  ← 分隔符
├──────────────────────────┤
│  消息体 (Body)            │  {"name":"zevin"}
└──────────────────────────┘
```

## 1.5 OSI / TCP/IP 模型中的位置

```
OSI 七层              TCP/IP 四层
═══════════          ═══════════
应用层    ─┐
表示层     ├─→        应用层 (HTTP, DNS, FTP)
会话层    ─┘
传输层    ───→        传输层 (TCP, UDP)
网络层    ───→        网络层 (IP, ICMP)
链路层    ─┐
物理层     ├─→        网络接口层
```

---

# 二、HTTP 版本演进

## 2.1 各版本对比表

| 版本 | 年份 | 传输层 | 核心特性 | 关键问题 |
|------|------|--------|----------|----------|
| HTTP/0.9 | 1991 | TCP | 仅 GET，无 Header 无状态码 | 功能单一 |
| HTTP/1.0 | 1996 | TCP | HEAD/POST、状态码、Content-Type | 短连接，每次 TCP 三次握手 |
| HTTP/1.1 | 1997 | TCP | 持久连接、管道化、Host、范围请求 | **队头阻塞** |
| HTTP/2 | 2015 | TCP | 二进制分帧、多路复用、HPACK、Server Push | **TCP 层队头阻塞仍存在** |
| HTTP/3 | 2022 | QUIC(UDP) | 0-RTT 握手、连接迁移、无队头阻塞 | 部署复杂，UDP 可能被防火墙拦截 |

## 2.2 HTTP/1.1 队头阻塞 (Head-of-Line Blocking)

**定义**：同一 TCP 连接上，上一个请求的响应未返回前，后续请求必须排队等待。

**原因**：HTTP/1.1 基于串行请求-响应模型，即使开启管道化（Pipelining），响应也必须按发送顺序返回。

**解决方案**：浏览器开启了 6-8 个并行 TCP 连接（域名分片），但治标不治本。

## 2.3 HTTP/2 多路复用

**原理**：在单条 TCP 连接上建立多个**双向流（Stream）**，每个流拆分为**帧（Frame）**，不同流的帧可以交错传输，接收方根据帧头的 Stream ID 重组。

```
连接 ─→ Stream 1 (请求 A): [HEADERS] [DATA] [DATA]
        Stream 3 (请求 B): [HEADERS] [DATA]
        Stream 5 (请求 C): [HEADERS] [DATA] [DATA] [DATA]

实际传输 (交错): [1:HEADERS] [3:HEADERS] [1:DATA] [5:HEADERS] [3:DATA] [1:DATA] [5:DATA]...
```

**未解决的问题**：TCP 丢包时，丢失的报文段会导致该 TCP 连接上的**所有 Stream 都阻塞**（TCP 层队头阻塞）。

## 2.4 HTTP/3 与 QUIC

**核心变革**：HTTP/3 抛弃 TCP，基于 QUIC（Quick UDP Internet Connections）协议。

| 特性 | TCP | QUIC (UDP) |
|------|-----|------------|
| 握手延迟 | 1-RTT (TCP) + 1-RTT (TLS) = 2-RTT | 0-RTT（恢复连接）或 1-RTT（首次） |
| 队头阻塞 | TCP 丢包阻塞整条连接 | 只阻塞丢包的 Stream，其他不受影响 |
| 连接迁移 | 不支持（IP:Port 变则断连） | **支持**（Connection ID，WiFi↔4G 无缝） |
| 部署 | 无阻碍 | UDP 可能被某些防火墙/负载均衡器拦截 |

**经典追问**："QUIC 在 UDP 上如何保证可靠？" → QUIC 在应用层自建了类似 TCP 的 ACK、重传、拥塞控制，不依赖底层 TCP。

---

# 三、HTTP 请求方法

## 3.1 9 种方法速查

| 方法 | 语义 | 幂等 | 安全 | 请求体 | 响应体 |
|------|------|------|------|--------|--------|
| **GET** | 获取资源 | ✅ | ✅ | 无 | 有 |
| **HEAD** | 获取响应头 | ✅ | ✅ | 无 | 无 |
| **POST** | 创建资源 | ❌ | ❌ | 有 | 有 |
| **PUT** | 全量替换 | ✅ | ❌ | 有 | 有 |
| **PATCH** | 部分更新 | ❌* | ❌ | 有 | 有 |
| **DELETE** | 删除资源 | ✅ | ❌ | 可有 | 可有 |
| **OPTIONS** | 探测方法 | ✅ | ✅ | 无 | 有 |
| **TRACE** | 回显请求 | ✅ | ✅ | 无 | 有 |
| **CONNECT** | 建立隧道 | ❌ | ❌ | 无 | 有 |

> 幂等：执行 N 次效果相同。安全：不改变服务端状态。
> *PATCH 通常不幂等，取决于实现（如 `{"$inc": {"age": 1}}` 不幂等）

## 3.2 高频追问

**"POST 和 PUT 的区别？"**

| 维度 | POST | PUT |
|------|------|-----|
| 语义 | 创建子资源 | 替换指定资源 |
| URL | `/users` (集合) | `/users/1` (具体资源) |
| 幂等性 | 否（重复 POST 创建多条） | 是（重复 PUT 结果一样） |
| REST 用法 | CREATE | UPDATE (全量) |

**"PUT 和 PATCH 的区别？"**

| 维度 | PUT | PATCH |
|------|-----|-------|
| 更新方式 | 全量替换 | 部分修改 |
| 传参 | 完整对象 | 只传变更字段 |
| 幂等性 | 幂等 | 取决于实现（`{op: "replace"}` 幂等，`{op: "increment"}` 不幂等） |

**"GET 请求可以带 Body 吗？"** → RFC 规范没有禁止，但大多数服务端和中间件（Nginx、Tomcat 默认）会忽略或丢弃。不要这样做。

**"OPTIONS 请求是什么？什么时候发？"** → CORS 预检请求（Preflight），检查跨域请求是否被允许。触发条件：非简单请求（如 Content-Type 为 `application/json`、自定义 Header、PUT/DELETE 等方法）。

---

# 四、HTTP 状态码

## 4.1 五大类速记

```
1xx  信息      100 Continue        客户端继续发送请求体
               101 Switching       切换协议（WebSocket 升级）

2xx  成功      200 OK              请求成功
               201 Created         资源创建成功（POST 返回）
               204 No Content      请求成功但无响应体（DELETE 后常用）
               206 Partial         部分内容（断点续传、分片下载）

3xx  重定向    301 Moved           永久重定向（浏览器缓存、SEO 权重转移）
               302 Found           临时重定向（可能改变请求方法 POST→GET）
               304 Not Modified    资源未修改，用缓存
               307 Temporary       临时重定向，严格保留请求方法
               308 Permanent       永久重定向，严格保留请求方法

4xx  客户端    400 Bad Request     请求格式错误
               401 Unauthorized    未认证（没登录/Token 无效）
               403 Forbidden       无权限（已登录但不配）
               404 Not Found       资源不存在
               405 Method Not      请求方法不允许
               409 Conflict        资源冲突（并发修改）
               429 Too Many        请求频率超限

5xx  服务端    500 Internal        服务器内部错误
               502 Bad Gateway     网关收到无效上游响应
               503 Service         服务暂不可用（维护/过载）
               504 Gateway         网关等待上游超时
```

## 4.2 高频追问

**"301 和 302 区别？"**
- 301：永久重定向。浏览器会缓存，下次直接走目标地址。搜索引擎将权重转移给新 URL。
- 302：临时重定向。浏览器不缓存。通常用于未登录跳转登录页。

**"302 和 307 区别？"**
- 302：重定向时浏览器可能把 POST 改成 GET（历史兼容行为）。
- 307：严格保留原 HTTP 方法和 Body。

**"401 和 403 区别？"**
- 401 Unauthorized：你是谁？—— 没登录或 Token 过期，提示需要认证。
- 403 Forbidden：你不配 —— 已登录但权限不足（普通用户访问管理员页面）。

**"502 和 504 区别？"**

| 状态码 | 场景 | 比喻 |
|--------|------|------|
| 502 Bad Gateway | 上游返回了格式错误或连接被拒 | 打电话给前台，前台说"经理不在" |
| 504 Gateway Timeout | 上游响应超时 | 打电话给前台，前台转接经理一直没人接 |

**"304 Not Modified 发生了什么？"**
→ 协商缓存命中。浏览器发请求带 `If-None-Match`（ETag）或 `If-Modified-Since`（Last-Modified），服务端判断资源未变，返回 304 + 空 Body。浏览器直接用本地缓存。请求确实发出了，只是没传输 Body。

---

# 五、HTTP 头部

## 5.1 关键头部速查

### 请求头

| 头部 | 说明 |
|------|------|
| `Host` | **HTTP/1.1 唯一必填**，多虚拟主机共用 IP 时区分站点 |
| `User-Agent` | 客户端信息（浏览器/操作系统） |
| `Accept` | 期望的响应 Content-Type（如 `application/json`） |
| `Accept-Encoding` | 期望的压缩算法（`gzip`, `br`） |
| `Accept-Language` | 期望的语言（`zh-CN`） |
| `Authorization` | 认证凭证（`Basic xxx` / `Bearer xxx`） |
| `Origin` | 请求来源（scheme+host+port，不含路径） |
| `Referer` | 请求来源（完整 URL，可能被裁剪） |
| `Cookie` | 携带客户端存储的 Cookie |
| `If-None-Match` | 缓存验证（ETag 值） |
| `If-Modified-Since` | 缓存验证（时间戳） |
| `Range` | 范围请求（`bytes=0-1023`） |

### 响应头

| 头部 | 说明 |
|------|------|
| `Set-Cookie` | 服务端设置 Cookie |
| `Location` | 重定向目标 URL（配合 301/302） |
| `ETag` | 资源版本标识（协商缓存） |
| `Last-Modified` | 资源最后修改时间 |
| `Access-Control-Allow-Origin` | CORS 允许的来源 |
| `Content-Range` | 范围请求的返回范围 |
| `Content-Encoding` | 实际压缩方式 |
| `Content-Length` | Body 字节数 |

### 通用头 / 实体头

| 头部 | 说明 |
|------|------|
| `Content-Type` | 请求/响应体的 MIME 类型 |
| `Cache-Control` | 缓存策略（核心） |
| `Connection` | 连接管理（`keep-alive` / `close`） |
| `Transfer-Encoding` | 传输编码（`chunked` 分块传输） |

## 5.2 高频追问

**"Content-Length 和 Transfer-Encoding: chunked 能共存吗？"**
→ 不能。分块传输时 Body 长度在传输时才动态确定，预先不知道 `Content-Length`。如果同时出现，`Transfer-Encoding` 优先级更高，浏览器以它为准。

**"Referer 和 Origin 的区别？"**

| 维度 | Referer | Origin |
|------|---------|--------|
| 内容 | 完整 URL 路径（含 query string） | 仅 scheme + host + port |
| 可否省略 | 可（隐私策略、HTTPS→HTTP 不传） | CORS 请求必带 |
| 用途 | 防盗链、来源分析 | CORS 安全校验 |
| 安全 | 可能泄露敏感 query 参数 | 更安全（无路径信息） |

**"Content-Type 的常见值？"**
```
application/json                      RESTful API
application/x-www-form-urlencoded     普通 HTML 表单
multipart/form-data                   文件上传表单
text/html                             HTML 页面
application/octet-stream              二进制流
application/xml                       XML 数据
```

---

# 六、HTTPS / TLS

## 6.1 为什么需要 HTTPS？

HTTP 明文传输的三重风险：

| 风险 | 说明 | 例子 |
|------|------|------|
| **窃听** | 中间人可截获通信内容 | 咖啡馆 WiFi，抓到密码明文 |
| **篡改** | 中间人可修改请求/响应 | 运营商劫持，插入广告脚本 |
| **冒充** | 攻击者伪装成目标服务器 | DNS 劫持，虚假银行页面 |

HTTPS = HTTP + TLS/SSL，通过加密解决以上三大问题。

## 6.2 HTTPS 加密原理

**混合加密方案**：

```
握手阶段（非对称加密）：
  客户端 ←→ 服务端，用 RSA 或 ECDHE 安全交换对称密钥
  特点：安全，但计算量大

数据传输阶段（对称加密）：
  双方用协商好的对称密钥（AES 等）加解密
  特点：高效，速度快
```

**为什么不用纯非对称加密？** → 太慢了。RSA 加解密比 AES 慢 100-1000 倍，纯非对称加密会压垮服务器。

## 6.3 TLS 握手流程

### TLS 1.2（2-RTT）

```
Client                          Server
  |                                |
  |--- ClientHello --------------->|  ① 客户端：支持的加密套件 + 随机数1
  |                                |
  |<-- ServerHello ----------------|  ② 服务端：选定加密套件 + 随机数2
  |<-- Certificate ---------------|  ③ 证书（含公钥）
  |<-- ServerHelloDone ----------|  ④ 完成
  |                                |
  |--- ClientKeyExchange -------->|  ⑤ 客户端：用公钥加密 PreMasterSecret
  |--- ChangeCipherSpec --------->|  ⑥ 通知：接下来加密
  |--- Finished ----------------->|  ⑦ 加密的握手结束消息
  |                                |
  |<-- ChangeCipherSpec ----------|  ⑧ 服务端：切换到加密
  |<-- Finished ------------------|  ⑨ 加密的握手结束消息
  |                                |
  |<==== 对称加密传输数据 ========>|
```

### TLS 1.3（1-RTT）

TLS 1.3 大幅精简：
- 去掉 RSA 密钥交换，强制 ECDHE（前向安全）
- 砍掉 ChangeCipherSpec 等冗余步骤
- 合并 ClientHello + KeyShare，服务端可选 0-RTT

## 6.4 证书与 PKI

**CA（Certificate Authority）**：数字证书颁发机构。

**信任链验证流程**：
```
根 CA (预置在系统/浏览器)
  ├── 签名 → 中间 CA
  │           ├── 签名 → 站点证书 (example.com)
  │           └── 中间 CA 是否有权签发？
  └── 根 CA 是否受信任？
```

**中间人攻击 (MITM) 防御**：攻击者无法伪造由受信任 CA 签名的证书，浏览器会在 TLS 握手中验证证书链，发现伪造后提示不安全。

**证书固定 (Certificate Pinning)**：App 内置目标服务证书或公钥哈希，即使系统信任了新的 CA，也不放行，防止被企业代理或恶意 CA 窥探数据。

## 6.5 前向安全 (Forward Secrecy)

**定义**：即使服务器长期私钥未来泄露，过去的历史通信密文也无法被解密。

**实现**：临时密钥交换（ECDHE）。每次会话生成一对临时密钥，用完即丢弃。私钥只用于签名认证，不参与会话密钥生成。

**对比**：RSA 密钥交换不提供前向安全，因为攻击者保存了加密的 `PreMasterSecret`，私钥泄露后就能解密。这也是 TLS 1.3 淘汰 RSA 密钥交换的原因。

---

# 七、Cookie / Session / Token 认证

## 7.1 三者对比

| 维度 | Cookie | Session | JWT Token |
|------|--------|---------|-----------|
| 存储位置 | 浏览器 | 服务端内存/Redis | 客户端 (浏览器/App) |
| 安全性 | 可被窃取 (HttpOnly 缓解) | 较安全 | 不可篡改但可被窃取 |
| 跨域支持 | 默认不支持 | 依赖 Cookie | **天然支持** |
| 扩展性 | 单机 | 需 Session 共享 | **天然分布式** |
| 服务端状态 | — | 有状态 | **无状态** |
| 注销 | 删除 Cookie | 删除 Session | 被动过期，主动需黑名单 |
| 数据承载 | 少 (4KB) | 存 Session ID 即可 | 可存用户信息(避免频繁查库) |

## 7.2 JWT 深入

**结构**：`Header.Payload.Signature`

```
Header:   {"alg":"HS256","typ":"JWT"}   → Base64URL
Payload:  {"sub":"123","exp":1700000000} → Base64URL
Signature: HMAC-SHA256(Header.Payload, secret)
```

**经典追问**：

"JWT 存在哪里？"
- `localStorage`：方便但 XSS 攻击可直接读取
- `HttpOnly Cookie`：防 XSS，但需要处理 CSRF（用 `SameSite=Strict/Lax`）
- 内存变量（SPA）：最安全，但刷新页面就丢失

"JWT 如何主动注销？"
→ JWT 是无状态的，无法服务端主动失效。解决方案：
- 维护 Token 黑名单（Redis），每次请求查黑名单——回归有状态
- 双 Token 机制：短期 Access Token (15min) + 长期 Refresh Token (7day)，维护 Refresh Token 列表

"双 Token 机制怎么用？"
```
1. 用户登录 → 返回 Access Token (15min) + Refresh Token (7day)
2. 每次请求带 Access Token
3. Access Token 过期 → 用 Refresh Token 换新的 Access Token
4. Refresh Token 也过期 → 重新登录
5. 注销 → 删除 Refresh Token
```

---

# 八、HTTP 缓存

## 8.1 缓存决策流程

```
┌─────────────────────────────┐
│        浏览器请求资源          │
└─────────────┬───────────────┘
              │
    ┌─────────▼──────────┐
    │  强缓存是否命中？     │
    │  Cache-Control      │
    │  Expires            │
    └────┬──────────┬─────┘
         │命中       │未命中
         ▼           ▼
  200 (from cache)  ┌──────────────────┐
                    │ 发送请求（带验证头）  │
                    │ If-None-Match     │
                    │ If-Modified-Since │
                    └────┬──────────┬───┘
                         │未变       │已变
                         ▼           ▼
                    304 Not      200 OK
                    Modified     (返回新内容)
```

## 8.2 强缓存 (无需发请求)

| 响应头 | 示例 | 说明 |
|--------|------|------|
| `Cache-Control: max-age=3600` | 缓存 3600 秒 | HTTP/1.1，主流 |
| `Expires: Thu, 01 Dec 2026 16:00:00 GMT` | 到期时间 | HTTP/1.0，被 Cache-Control 覆盖 |

**状态码**：200 (from disk cache) 或 200 (from memory cache)

## 8.3 协商缓存 (需要发请求验证)

| 请求头 | 响应头 | 校验方式 |
|--------|--------|----------|
| `If-None-Match: "abc123"` | `ETag: "abc123"` | 内容指纹（hash），精确 |
| `If-Modified-Since: Wed, 13 May 2026...` | `Last-Modified: Wed, ...` | 时间戳，精度到秒 |

**状态码**：304 Not Modified（资源未变）/ 200 OK（资源已变，返回新内容）

## 8.4 Cache-Control 指令详解

| 指令 | 效果 |
|------|------|
| `max-age=3600` | 缓存 3600 秒后过期 |
| `no-cache` | **可以缓存**，但每次使用前必须验证（走协商缓存，可能返回 304） |
| `no-store` | **绝对不缓存**（银行/支付页面） |
| `public` | 允许 CDN 等中间节点缓存 |
| `private` | 仅浏览器缓存（默认） |
| `must-revalidate` | 过期后必须重新验证，不能用过期缓存 |
| `immutable` | 资源绝不改变（带 hash 的静态资源如 `app.1a2b3c.js`） |

**经典追问**："`no-cache` 和 `no-store` 的区别？"
→ `no-cache` 缓存了但每次验证（有协商缓存语义，可能有 304）；`no-store` 根本不存（无缓存语义）。

## 8.5 ETag vs Last-Modified

| 维度 | ETag | Last-Modified |
|------|------|---------------|
| 粒度 | 内容摘要 (hash)，变化即更新 | 修改时间，精度秒级 |
| 缺点 | 计算 hash 有开销（大文件） | 1 秒内多次修改检测不到；周期性重写但内容不变也会触发 |
| 优先级 | **高**（两者同时存在优先用 ETag） | 低 |

## 8.6 缓存最佳实践

```
HTML (入口文件)       → Cache-Control: no-cache        (频繁验证)
CSS/JS (带 hash)      → Cache-Control: max-age=31536000, immutable  (永久强缓存)
图片/字体 (不太变)     → Cache-Control: max-age=2592000  (强缓存 30 天)
API 数据              → Cache-Control: no-store, private (不缓存)
CDN                   → Cache-Control: public + max-age + ETag
```

---

# 题型分布（按面试级别）

| 级别 | 核心考察范围 |
|------|-------------|
| **初级**（0-2年） | 基础概念、常用方法(GET/POST/PUT/DELETE)、常见状态码(200/301/404/500)、HTTP vs HTTPS 区别 |
| **中级**（3-5年） | Cookie/Session/Token 原理、缓存策略（强缓存/协商缓存）、TLS 握手流程（简版）、HTTP/1.1 vs 2 差异、CORS 预检 |
| **高级**（5年+） | HTTP/2 多路复用帧与流细节、HTTP/3 QUIC 0-RTT 及连接迁移、TLS 1.3 完整握手与前向安全、TCP 层队头阻塞 vs HTTP 层队头阻塞、代理/CDN 原理、CSRF/XSS 攻击与防御 |

---

# 高频一句话总结

| 问题 | 一句话答案 |
|------|-----------|
| HTTP 是什么 | 超文本传输协议，基于请求-响应的无状态应用层协议 |
| HTTPS 加密原理 | 握手阶段非对称加密交换会话密钥，数据传输阶段对称加密 |
| HTTP/2 最大改进 | 多路复用，单 TCP 连接上多个流交错传输 |
| HTTP/3 为什么用 UDP | QUIC 在 UDP 上实现可靠传输，解决 TCP 队头阻塞，支持连接迁移 |
| GET vs POST | GET 幂等安全参数在 URL，POST 不幂等不安全参数在 Body |
| PUT vs PATCH | PUT 全量替换(幂等)，PATCH 部分更新(通常不幂等) |
| 301 vs 302 | 301 永久重定向(缓存)，302 临时重定向(不缓存) |
| 401 vs 403 | 401 没登录(Unauthorized)，403 没权限(Forbidden) |
| 502 vs 504 | 502 上游坏响应，504 上游超时 |
| no-cache vs no-store | no-cache 缓存但每次验证(304)，no-store 根本不存 |
| Cookie vs JWT | Cookie 由服务端通过 Set-Cookie 控制，JWT 在客户端自包含、天然跨域 |
| CORS 预检 | 非简单请求(Custom Header / JSON Content-Type)触发 OPTIONS 预检 |
