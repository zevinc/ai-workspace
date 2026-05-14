---
title: jakarta.servlet.DispatcherType 枚举类详解
tags:
  - servlet
  - jakarta
  - dispatchertype
  - filter
  - enum
  - tomcat
  - spring-boot
  - spring-security
summary: 详解 jakarta.servlet.DispatcherType 枚举的 6 个值（REQUEST/FORWARD/INCLUDE/ASYNC/ERROR/WEBSOCKET），每个值的触发条件、Filter 作用机制、安全漏洞案例（forward 绕过）、Spring Boot / Spring Security 配置方式、Tomcat 源码级执行流程。
created: 2026-05-14
---

# 背景

在 Jakarta Servlet 规范中，同一个 URL 可以通过多种途径到达：

- 浏览器地址栏直接访问
- 服务端内部 `forward` 转发
- JSP `include` 嵌入
- 异步 `dispatch`
- 错误页面映射
- WebSocket 升级

`DispatcherType` 枚举的精确定义了这些**请求分发类型**，控制 Filter 在哪些类型下生效，是实现精细化过滤控制的关键。

# 枚举定义

```java
package jakarta.servlet;

/**
 * @since Servlet 3.0
 */
public enum DispatcherType {

    /** 客户端直接发起的请求 */
    REQUEST,

    /** RequestDispatcher.forward() 服务端内部转发 */
    FORWARD,

    /** RequestDispatcher.include() 服务端包含 */
    INCLUDE,

    /** 异步 dispatch：AsyncContext.dispatch() */
    ASYNC,

    /** 错误页面转发：web.xml <error-page> 或 @WebServlet 错误映射 */
    ERROR,

    /** WebSocket HTTP Upgrade 请求（Servlet 6.1 新增） */
    WEBSOCKET
}
```

---

# 六大枚举值详解

## 1. REQUEST — 客户端请求

**触发条件**：客户端（浏览器/AJAX/curl）发起 HTTP 请求到达 Servlet 容器。

```java
// 容器收到请求后：
//   1. 解析 HTTP 报文
//   2. 创建 DispatcherType.REQUEST 的请求上下文
//   3. 匹配 URL → 选择合适的 Filter
//   4. 调用 service() → doGet()/doPost()

// 请求示例：
//   GET http://example.com/users
//   POST http://example.com/api/login
```

**Filter 默认行为**：当 Filter 配置中**未声明** `dispatcherTypes` 时，默认只对 `REQUEST` 生效。

```xml
<!-- web.xml 中不写 <dispatcher> → 默认等同于 REQUEST -->
<filter-mapping>
    <filter-name>authFilter</filter-name>
    <url-pattern>/admin/*</url-pattern>
    <!-- 缺少 <dispatcher>REQUEST</dispatcher> → 仅 REQUEST 下执行 -->
</filter-mapping>
```

```java
// @WebFilter 注解中不写 dispatcherTypes → 默认只有 REQUEST
@WebFilter(urlPatterns = "/admin/*")
public class AuthFilter implements Filter { }
```

---

## 2. FORWARD — 服务端内部转发

**触发条件**：`request.getRequestDispatcher(path).forward(req, res)`。

```java
// Controller A 内部转发到 Controller B
@GetMapping("/checkout")
public String checkout(HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException {
    // 某些条件下转发到订单确认页
    request.getRequestDispatcher("/orders/confirm").forward(request, response);
    return null; // forward 后本方法不再继续
}
```

**关键特性**：
- URL 不变：浏览器地址栏仍是 `/checkout`
- 同一个请求对象（`request` / `response` 不重建）
- 只能转发到同 Web 应用的资源

**安全风险**：如果 `/orders/confirm` 路径有权限 Filter，但该 Filter 只配置了 `REQUEST` 类型，`forward` 过来的请求会**绕过**安全检查。

```
┌─────────────────────────────────────────────────────────┐
│ 场景：绕过 AdminFilter                                   │
│                                                         │
│ ① /public 路径有 PublicFilter (仅 REQUEST)                │
│ ② /admin  路径有 AdminFilter  (仅 REQUEST)               │
│                                                         │
│ 攻击路径：                                                │
│   GET /public → PublicFilter 放行 →                    │
│   Controller 内部 forward("/admin/secret")              │
│   → AdminFilter 不触发！（因为是 FORWARD 类型）            │
│                                                         │
│ 防御：AdminFilter 加 FORWARD 类型                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. INCLUDE — 服务端包含

**触发条件**：`request.getRequestDispatcher(path).include(req, res)`。

```java
// JSP 中：
//   <jsp:include page="/sidebar.jsp" />

// Servlet 中：
@GetMapping("/dashboard")
public void dashboard(HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException {
    // 拼装多个页面片段
    request.getRequestDispatcher("/fragments/header").include(request, response);
    response.getWriter().write("<div>Main Content</div>");
    request.getRequestDispatcher("/fragments/footer").include(request, response);
}
```

**与 FORWARD 的区别**：

| 维度 | FORWARD | INCLUDE |
|------|---------|---------|
| 响应输出 | 目标资源接管整个响应 | 目标资源输出被拼接到调用方响应中 |
| 响应头 | 目标资源可覆盖 | 不能设置响应头（会被忽略） |
| 请求参数 | 可修改 | 原请求参数保留 |
| 适用场景 | 完全跳转到另一页面 | 拼装页面片段（页头/侧栏/页脚） |

---

## 4. ASYNC — 异步分发

**触发条件**：`AsyncContext.dispatch(path)` 将异步处理结果分发到目标资源。

```java
@WebServlet(urlPatterns = "/async-task", asyncSupported = true)
public class AsyncTaskServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
        AsyncContext asyncCtx = req.startAsync();

        // 异步线程执行耗时操作
        asyncCtx.start(() -> {
            try {
                // 模拟耗时处理
                Thread.sleep(5000);
                req.setAttribute("result", "done");
            } catch (InterruptedException ignored) {}

            // 完成后分发到结果页面 —— 此时触发 ASYNC 类型的 Filter
            asyncCtx.dispatch("/task-result");
        });
    }
}
```

**执行时序**：

```
请求到达 → REQUEST Filter 链 → Servlet startAsync() → 返回
                                                      ↓
                                        异步线程干活 ...
                                                      ↓
                                   asyncCtx.dispatch() → ASYNC Filter 链 → 目标 Servlet

注意：REQUEST Filter 和 ASYNC Filter 是两次独立的调用
```

---

## 5. ERROR — 错误页面转发

**触发条件**：Servlet 抛出未捕获异常，或调用了 `response.sendError()`，容器根据错误映射转发到错误页面。

```xml
<!-- web.xml 错误页映射 -->
<error-page>
    <error-code>404</error-code>
    <location>/errors/404.html</location>
</error-page>

<error-page>
    <exception-type>java.lang.Exception</exception-type>
    <location>/errors/500.html</location>
</error-page>
```

```java
// Servlet 中手动触发
@GetMapping("/dangerous")
public void dangerous(HttpServletResponse response) throws IOException {
    // 触发 500 → 容器转发到 /errors/500.html
    // 此时 DispatcherType = ERROR
    throw new RuntimeException("Something went wrong");

    // 或显式调用
    // response.sendError(500, "Internal error");
}
```

**关键特性**：
- 容器自动创建错误请求属性：
  - `jakarta.servlet.error.status_code`
  - `jakarta.servlet.error.exception`
  - `jakarta.servlet.error.message`
  - `jakarta.servlet.error.request_uri`

```java
// 在错误页面中读取原始错误信息
Object status = request.getAttribute("jakarta.servlet.error.status_code");
Object ex = request.getAttribute("jakarta.servlet.error.exception");
Object uri = request.getAttribute("jakarta.servlet.error.request_uri");
```

---

## 6. WEBSOCKET — WebSocket 升级（Servlet 6.1）

**触发条件**：HTTP Upgrade 请求，协议从 HTTP 切换到 WebSocket。

```java
// 浏览器侧：
//   const ws = new WebSocket("ws://example.com/chat");

// 触发流程：
//   1. HTTP GET /chat   Headers: Upgrade: websocket, Connection: Upgrade
//   2. DispatcherType = WEBSOCKET
//   3. Filter 链执行
//   4. 握手成功 → 101 Switching Protocols → WebSocket 建立
```

**Servlet 6.1 之前**：WebSocket 升级请求会被 `REQUEST` 类型捕获，语义不准确。Servlet 6.1 专门拆分出 `WEBSOCKET`，便于独立控制。

---

# Filter 配置方式

## 方式 1：@WebFilter 注解（Jakarta Servlet 3.0+）

```java
// 在 REQUEST 和 FORWARD 下都生效
@WebFilter(
    urlPatterns = "/admin/*",
    dispatcherTypes = {DispatcherType.REQUEST, DispatcherType.FORWARD}
)
public class AdminFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;

        // 获取当前请求的 DispatcherType
        DispatcherType dispatcherType = request.getDispatcherType();

        System.out.println("AdminFilter 触发，类型: " + dispatcherType);

        // 权限检查
        chain.doFilter(req, res);
    }
}
```

## 方式 2：web.xml（Jakarta Servlet 2.5+）

```xml
<filter>
    <filter-name>authFilter</filter-name>
    <filter-class>com.example.AuthFilter</filter-class>
</filter>

<filter-mapping>
    <filter-name>authFilter</filter-name>
    <url-pattern>/admin/*</url-pattern>
    <dispatcher>REQUEST</dispatcher>
    <dispatcher>FORWARD</dispatcher>
    <dispatcher>ASYNC</dispatcher>
    <!-- 不写 ERROR / INCLUDE / WEBSOCKET -->
</filter-mapping>
```

## 方式 3：Spring Boot FilterRegistrationBean

```java
import jakarta.servlet.DispatcherType;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class FilterConfig {

    @Bean
    public FilterRegistrationBean<AuthFilter> authFilterRegistration() {
        FilterRegistrationBean<AuthFilter> reg = new FilterRegistrationBean<>(new AuthFilter());

        reg.addUrlPatterns("/admin/*");
        reg.setDispatcherTypes(
            DispatcherType.REQUEST,
            DispatcherType.FORWARD,
            DispatcherType.ASYNC
        );

        // 拦截所有：reg.setDispatcherTypes(DispatcherType.values());
        return reg;
    }
}
```

---

# 获取当前请求的 DispatcherType

```java
@GetMapping("/info")
public String info(HttpServletRequest request) {
    DispatcherType type = request.getDispatcherType();

    switch (type) {
        case REQUEST:  return "来自客户端请求";
        case FORWARD:  return "来自 forward 转发";
        case INCLUDE:  return "来自 include 包含";
        case ASYNC:    return "来自异步分发";
        case ERROR:    return "来自错误转发";
        case WEBSOCKET: return "来自 WebSocket 升级";
        default:       return "未知";
    }
}
```

---

# Spring Security 的 DispatcherType 策略

Spring Security 默认将 `springSecurityFilterChain` 注册为**全部类型**：

```java
// Spring Security 内部源码（SecurityFilterAutoConfiguration 简化）
@Bean
public DelegatingFilterProxyRegistrationBean securityFilterChainRegistration() {
    DelegatingFilterProxyRegistrationBean reg = new DelegatingFilterProxyRegistrationBean("springSecurityFilterChain");
    reg.addUrlPatterns("/*");
    // 覆盖所有 DispatcherType —— 安全最大化
    reg.setDispatcherTypes(
        DispatcherType.REQUEST,
        DispatcherType.ASYNC,
        DispatcherType.ERROR,
        DispatcherType.FORWARD,
        DispatcherType.INCLUDE
    );
    // WEBSOCKET 在低版本 Servlet 中没有，高版本自动追加
    return reg;
}
```

**设计理由**：安全过滤器链必须覆盖所有请求路径，无论以何种方式到达。如果漏掉 `FORWARD`，就会出现本章开头描述的绕过漏洞。

---

# Tomcat 源码：Filter 执行判定流程

Tomcat 的 `ApplicationFilterFactory` 根据当前请求的 `DispatcherType` 匹配 Filter：

```java
// Tomcat ApplicationFilterFactory.createFilterChain() 简化伪代码
public static ApplicationFilterChain createFilterChain(
        ServletRequest request,
        Wrapper wrapper,
        Servlet servlet) {

    // 获取当前请求的分发类型
    DispatcherType dispatcher = request.getDispatcherType();

    ApplicationFilterChain filterChain = new ApplicationFilterChain();

    // 遍历所有已注册的 Filter
    for (FilterMap filterMap : context.findFilterMaps()) {

        // 只有 dispatcher 匹配的 Filter 才加入链
        if (!filterMap.getDispatcherTypes().contains(dispatcher)) {
            continue; // ← 不匹配则跳过
        }

        // URL 模式匹配
        if (!matchFiltersURL(filterMap, requestPath)) {
            continue;
        }

        // 加入执行链
        filterChain.addFilter(
            context.findFilterConfig(filterMap.getFilterName())
        );
    }

    return filterChain;
}
```

**关键**：Filter 是否执行，取决于两个条件同时满足：
1. 当前请求的 `DispatcherType` 在 Filter 的 `dispatcherTypes` 集合中
2. 请求 URL 匹配 Filter 的 `urlPatterns`

---

# 最佳实践

| 场景 | 推荐 DispatcherType | 理由 |
|------|---------------------|------|
| **安全/认证 Filter** | REQUEST + FORWARD + ASYNC + ERROR | 防止 forward 绕过、异步分发绕过、错误页泄露信息 |
| **访问日志 Filter** | REQUEST (仅) | 避免 forward/include 重复记录 |
| **XSS 防护 Filter** | ALL | 所有输出路径都需要转义，包括错误页面和 include |
| **性能监控 Filter** | REQUEST + FORWARD | forward 也产生耗时，需计入；include 通常忽略 |
| **字符编码 Filter** | REQUEST + FORWARD + INCLUDE | 拼装页面也可能需要编码设置 |
| **CORS Filter** | REQUEST + ASYNC | OPTIONS 预检只需在入口处理 |

---

# 常见踩坑

1. **Spring Boot 的 `@WebFilter` 不生效** → 需要在启动类上加 `@ServletComponentScan`
2. **`sendRedirect` vs `forward`** → `sendRedirect` 返回 302 让浏览器重新请求（触发 REQUEST），不会触发 FORWARD
3. **Filter 执行顺序** → 多个 Filter 的 `dispatcherTypes` 配置不同，可能导致同一请求只有部分 Filter 执行。排查顺序问题的第一件事就是打印 `request.getDispatcherType()`

---

# 一句话总结

`DispatcherType` 是 Jakarta Servlet 规范中定义请求"入口身份"的枚举。Filter 默认只拦截 `REQUEST` 类型的请求，只有当显式声明 `FORWARD` / `INCLUDE` / `ASYNC` / `ERROR` / `WEBSOCKET` 后，才会对相应的内部转发路径生效。理解它，是写出安全、无遗漏的过滤器链的前提。
