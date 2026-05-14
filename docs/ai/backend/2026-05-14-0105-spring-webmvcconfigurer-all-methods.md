---
title: Spring MVC WebMvcConfigurer 全部 18 个方法详解与实战示例
tags:
  - spring-mvc
  - spring-boot
  - webmvcconfigurer
  - java-config
  - extension-point
  - interceptor
  - cors
  - message-converter
  - argument-resolver
summary: WebMvcConfigurer 接口全部 18 个 default 方法的中文详解，每个方法配有完整代码示例、注释和最佳实践。覆盖路径匹配、内容协商、拦截器、CORS、消息转换器、参数解析器、视图解析等全部扩展点。
created: 2026-05-14
---

# 背景

`WebMvcConfigurer` 是 Spring MVC Java Config 时代的核心扩展接口。从 Spring 5 开始所有方法都有 `default` 实现，开发者只需实现接口并覆写需要定制的方法。Spring 6（Spring Boot 3.x）移除了已废弃的 `WebMvcConfigurerAdapter` 抽象类。

# 本文覆盖

- 全部 18 个方法的逐一详解
- 每个方法配有可运行的代码示例和中文注释
- 重点标注"替换 vs 扩展"的坑（configure / extend / add 的区别）
- 最佳实践建议

# 分类总览

| 分类 | 方法数 | 方法 |
|------|--------|------|
| 路径匹配 | 1 | `configurePathMatch` |
| 内容协商 | 1 | `configureContentNegotiation` |
| 异步支持 | 1 | `configureAsyncSupport` |
| 格式化 | 1 | `addFormatters` |
| 拦截器 | 1 | `addInterceptors` |
| 静态资源 | 1 | `addResourceHandlers` |
| 跨域 CORS | 1 | `addCorsMappings` |
| 视图控制器 | 1 | `addViewControllers` |
| 视图解析器 | 1 | `configureViewResolvers` |
| 参数解析器 | 1 | `addArgumentResolvers` |
| 返回值处理器 | 1 | `addReturnValueHandlers` |
| 消息转换器 | 2 | `configureMessageConverters` / `extendMessageConverters` |
| 异常解析器 | 2 | `configureHandlerExceptionResolvers` / `extendHandlerExceptionResolvers` |
| 默认 Servlet | 1 | `configureDefaultServletHandling` |
| 验证器 | 1 | `getValidator` |
| 消息编码 | 1 | `getMessageCodesResolver` |

---

# 一、路径匹配 — configurePathMatch

**作用**：定制 URL 路径匹配行为 —— 添加前缀、路径匹配策略、后缀匹配等。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.config.annotation.PathMatchConfigurer;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class PathMatchConfig implements WebMvcConfigurer {

    @Override
    public void configurePathMatch(PathMatchConfigurer configurer) {
        // 1. 给标注 @RestController 的 controller 统一加 /api 前缀
        configurer.addPathPrefix(
            "/api",
            c -> c.isAnnotationPresent(RestController.class)
        );

        // 2. 禁止尾斜杠匹配（/users 和 /users/ 视为不同路径）
        //    Spring Boot 3.x 默认已是 false
        configurer.setUseTrailingSlashMatch(false);

        // 3. 后缀模式匹配（如 /users.json 被当作 .json 后缀）
        //    Spring Boot 3.x 默认 false，一般不建议开启
        configurer.setUseSuffixPatternMatch(false);
    }
}
```

**最佳实践**：
- 前缀匹配常用于版本化 API：`/api/v1`、`/api/v2`
- Spring Boot 3.x 底层已默认使用 `PathPatternParser`（比 `AntPathMatcher` 性能更好）

---

# 二、内容协商 — configureContentNegotiation

**作用**：决定返回 JSON、XML 还是其他格式，依据请求的 `Accept` 头、URL 后缀、请求参数等。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.http.MediaType;
import org.springframework.web.servlet.config.annotation.ContentNegotiationConfigurer;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class ContentNegotiationConfig implements WebMvcConfigurer {

    @Override
    public void configureContentNegotiation(ContentNegotiationConfigurer configurer) {
        configurer
            // 1. 根据 URL 参数切换格式：/users?format=xml
            .favorParameter(true)
            .parameterName("format")              // 参数名
            .mediaType("json", MediaType.APPLICATION_JSON)
            .mediaType("xml", MediaType.APPLICATION_XML)
            // 2. 忽略 URL 后缀（如 /users.json → 不建议使用）
            .ignoreAcceptHeader(false)
            // 3. 默认返回 JSON
            .defaultContentType(MediaType.APPLICATION_JSON);
    }
}
```

**最佳实践**：
- RESTful API 推荐只依赖 `Accept` 头做内容协商，关闭参数和路径后缀模式
- 只在需要同时支持 JSON 和 XML 时才配置此方法

---

# 三、异步支持 — configureAsyncSupport

**作用**：配置异步请求（`DeferredResult` / `Callable`）的超时时间和线程池。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.web.servlet.config.annotation.AsyncSupportConfigurer;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class AsyncConfig implements WebMvcConfigurer {

    @Override
    public void configureAsyncSupport(AsyncSupportConfigurer configurer) {
        // 1. 异步请求超时时间（毫秒），默认 30 秒
        configurer.setDefaultTimeout(60_000L);

        // 2. 自定义异步任务线程池（推荐，避免用默认的 SimpleAsyncTaskExecutor）
        //    Callable 类型的异步请求会用这个线程池
        configurer.setTaskExecutor(asyncTaskExecutor());

        // 3. 注册 DeferredResult 拦截器（含 Callable 处理拦截器）
        //    configurer.registerDeferredResultInterceptors(...);
        //    configurer.registerCallableInterceptors(...);
    }

    /**
     * 自定义线程池：避免新线程无限制创建导致 OOM
     */
    public ThreadPoolTaskExecutor asyncTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(200);
        executor.setThreadNamePrefix("mvc-async-");
        executor.initialize();
        return executor;
    }
}
```

**Controller 示例**：

```java
@GetMapping("/async/users")
public Callable<List<User>> asyncUsers() {
    // Spring MVC 会在 asyncTaskExecutor 线程池中执行
    return () -> userService.findAll();
}

@GetMapping("/async/orders")
public DeferredResult<List<Order>> asyncOrders() {
    DeferredResult<List<Order>> result = new DeferredResult<>(60_000L);
    // 异步回调设置结果
    orderService.findAsync().whenComplete((orders, ex) -> {
        if (ex != null) result.setErrorResult(ex);
        else result.setResult(orders);
    });
    return result;
}
```

---

# 四、格式化器 — addFormatters

**作用**：注册自定义 `Formatter`（字符串 ↔ 对象转换）和 `Converter`（对象 ↔ 对象转换）。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.format.Formatter;
import org.springframework.format.FormatterRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.text.ParseException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

@Configuration
public class FormatterConfig implements WebMvcConfigurer {

    @Override
    public void addFormatters(FormatterRegistry registry) {
        // 1. 注册自定义 Formatter：将字符串 "yyyy-MM-dd" 转换为 LocalDate
        registry.addFormatter(new LocalDateFormatter());

        // 2. 注册通用 Converter：String → 枚举大写转换
        registry.addConverter(String.class, StatusEnum.class,
            source -> StatusEnum.valueOf(source.toUpperCase()));
    }

    /**
     * 自定义日期格式化器
     */
    static class LocalDateFormatter implements Formatter<LocalDate> {

        private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd");

        @Override
        public LocalDate parse(String text, Locale locale) throws ParseException {
            return LocalDate.parse(text, DF);
        }

        @Override
        public String print(LocalDate object, Locale locale) {
            return object.format(DF);
        }
    }
}
```

**使用效果**：

```java
// Controller 中可直接接收 LocalDate：
@GetMapping("/report")
public Report getReport(@RequestParam("date") LocalDate date) {
    // ?date=2026-05-14 → 自动解析为 LocalDate
    return reportService.findByDate(date);
}
```

---

# 五、拦截器 — addInterceptors

**作用**：注册 `HandlerInterceptor`，在 Controller 方法执行前后插入逻辑（认证、日志、性能统计等）。

```java
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class InterceptorConfig implements WebMvcConfigurer {

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry
            // 注册拦截器
            .addInterceptor(new AuthInterceptor())
            // 拦截路径
            .addPathPatterns("/api/**")
            // 排除路径（登录、健康检查不拦截）
            .excludePathPatterns("/api/public/**", "/api/health");

        // 可注册多个拦截器，按注册顺序依次执行
        registry
            .addInterceptor(new AccessLogInterceptor())
            .addPathPatterns("/**");
    }

    /**
     * 认证拦截器
     */
    static class AuthInterceptor implements HandlerInterceptor {

        @Override
        public boolean preHandle(HttpServletRequest request,
                                 HttpServletResponse response,
                                 Object handler) {
            String token = request.getHeader("Authorization");
            if (token == null || token.isBlank()) {
                response.setStatus(401);
                return false;   // 拒绝请求
            }
            // 校验 token...
            request.setAttribute("userId", extractUserId(token));
            return true;        // 放行
        }

        @Override
        public void afterCompletion(HttpServletRequest request,
                                    HttpServletResponse response,
                                    Object handler, Exception ex) {
            // 请求完成后清理线程变量（如 ThreadLocal）
            UserContext.clear();
        }

        private String extractUserId(String token) { /* ... */ return "1"; }
    }

    /**
     * 访问日志拦截器 —— 记录每个请求耗时
     */
    static class AccessLogInterceptor implements HandlerInterceptor {

        @Override
        public boolean preHandle(HttpServletRequest request,
                                 HttpServletResponse response,
                                 Object handler) {
            request.setAttribute("startTime", System.currentTimeMillis());
            return true;
        }

        @Override
        public void afterCompletion(HttpServletRequest request,
                                    HttpServletResponse response,
                                    Object handler, Exception ex) {
            long start = (long) request.getAttribute("startTime");
            long elapsed = System.currentTimeMillis() - start;
            System.out.printf("%s %s → %d (%dms)%n",
                request.getMethod(), request.getRequestURI(),
                response.getStatus(), elapsed);
        }
    }
}
```

**关键点**：
- `preHandle` 返回 `false` → 拦截后续处理
- `postHandle` 在视图渲染前执行
- `afterCompletion` 无论如何都会执行（适合清理资源）

---

# 六、静态资源 — addResourceHandlers

**作用**：将 URL 路径映射到静态文件目录，添加缓存策略。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class ResourceConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 1. classpath 静态资源
        registry.addResourceHandler("/static/**")
                .addResourceLocations("classpath:/static/")
                .setCachePeriod(3600);        // 浏览器缓存 1 小时（秒）

        // 2. 本地文件系统路径（如用户上传的文件）
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:/data/uploads/")
                .setCachePeriod(0);           // 不缓存

        // 3. 多个资源位置（优先级按添加顺序）
        registry.addResourceHandler("/assets/**")
                .addResourceLocations(
                    "classpath:/custom-assets/",
                    "classpath:/public/"
                );

        // 4. Swagger / Knife4j 文档资源
        registry.addResourceHandler("/doc.html")
                .addResourceLocations("classpath:/META-INF/resources/");
    }
}
```

---

# 七、跨域 CORS — addCorsMappings

**作用**：全局配置跨域资源共享（CORS），允许前端跨域访问 API。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry
            .addMapping("/api/**")                     // 匹配路径
            .allowedOrigins("https://example.com",
                            "https://admin.example.com") // 允许的前端域名
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowedHeaders("*")                        // 允许所有请求头
            .exposedHeaders("X-Total-Count",            // 暴露给前端的自定义头
                            "X-Request-Id")
            .allowCredentials(true)                     // 允许携带 Cookie
            .maxAge(3600L);                             // 预检请求缓存时间（秒）

        // 对不同路径可以有不同的 CORS 策略
        registry
            .addMapping("/public/**")
            .allowedOrigins("*")
            .allowedMethods("GET");
    }
}
```

**替代方式**：
- `@CrossOrigin` 注解在单个 Controller 或方法上
- Spring Security 中的 `cors()` 配置（配合 Spring Security 时优先使用）

---

# 八、视图控制器 — addViewControllers

**作用**：将 URL 直接映射到视图，无需写 Controller。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ViewControllerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class ViewControllerConfig implements WebMvcConfigurer {

    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        // 1. URL → 视图名称（Thymeleaf 会解析为 templates/index.html）
        registry.addViewController("/").setViewName("index");
        registry.addViewController("/login").setViewName("login");

        // 2. 重定向
        registry.addRedirectViewController("/old-home", "/");

        // 3. 直接设置 HTTP 状态码（如 404 页面）
        registry.addStatusController("/not-found", HttpStatus.NOT_FOUND)
                .setViewName("error/404");
    }
}
```

**适用场景**：
- 单页应用（SPA）的前端路由 fallback 到 `index.html`
- 纯展示页面（无后端逻辑）

---

# 九、视图解析器 — configureViewResolvers

**作用**：注册和配置视图解析器。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ViewResolverRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class ViewResolverConfig implements WebMvcConfigurer {

    @Override
    public void configureViewResolvers(ViewResolverRegistry registry) {
        // 1. 启用 ContentNegotiatingViewResolver（依据内容协商选择视图）
        //    配合 configureContentNegotiation 使用
        // registry.enableContentNegotiation(...);

        // 2. JSP 视图（需设置 prefix 和 suffix）
        registry.jsp("/WEB-INF/views/", ".jsp");

        // 3. 自定义 ViewResolver（极少需要；Thymeleaf 等自动配置已足够）
        // registry.viewResolver(new MyCustomViewResolver());
    }
}
```

**最佳实践**：
- Spring Boot 已自动配置 Thymeleaf / FreeMarker / Groovy 模板
- 一般**不推荐**覆写这个方法，除非你有非常特殊的视图层需求

---

# 十、参数解析器 — addArgumentResolvers

**作用**：自定义 Controller 方法参数的解析逻辑，如自定 `@CurrentUser` 注解。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.core.MethodParameter;
import org.springframework.web.bind.support.WebDataBinderFactory;
import org.springframework.web.context.request.NativeWebRequest;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.method.support.ModelAndViewContainer;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.List;

@Configuration
public class ArgumentResolverConfig implements WebMvcConfigurer {

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        resolvers.add(new CurrentUserArgumentResolver());
    }

    /**
     * 自定义参数解析器：自动注入当前登录用户
     *
     * 使用方式：
     *   @GetMapping("/me")
     *   public User me(@CurrentUser User user) { return user; }
     */
    static class CurrentUserArgumentResolver implements HandlerMethodArgumentResolver {

        @Override
        public boolean supportsParameter(MethodParameter parameter) {
            // 只处理带 @CurrentUser 注解的参数
            return parameter.hasParameterAnnotation(CurrentUser.class);
        }

        @Override
        public Object resolveArgument(MethodParameter parameter,
                                      ModelAndViewContainer mavContainer,
                                      NativeWebRequest webRequest,
                                      WebDataBinderFactory binderFactory) {
            // 从请求中提取 token → 查询用户 → 返回
            String authHeader = webRequest.getHeader("Authorization");
            // 实际项目中：解析 token，查询数据库或缓存
            return new User(1L, "zevin");
        }
    }
}

// 自定义注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.PARAMETER)
@interface CurrentUser {}
```

**常见场景**：
- `@CurrentUser` 注入登录用户
- `@RequestAttribute` 的增强版
- 分页参数自动封装 `Pageable`

---

# 十一、返回值处理器 — addReturnValueHandlers

**作用**：自定义 Controller 方法返回值的处理逻辑。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.core.MethodParameter;
import org.springframework.web.context.request.NativeWebRequest;
import org.springframework.web.method.support.HandlerMethodReturnValueHandler;
import org.springframework.web.method.support.ModelAndViewContainer;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.List;

@Configuration
public class ReturnValueHandlerConfig implements WebMvcConfigurer {

    @Override
    public void addReturnValueHandlers(List<HandlerMethodReturnValueHandler> handlers) {
        // 注册自定义返回值处理器（如统一包装返回值）
        handlers.add(new ApiResultReturnValueHandler());
    }

    /**
     * 自定义返回值处理器：自动将 Controller 返回值包装为 ApiResult
     *
     * 原理：Controller 返回 User → 自动包装为 ApiResult(0, "ok", user)
     */
    static class ApiResultReturnValueHandler implements HandlerMethodReturnValueHandler {

        @Override
        public boolean supportsReturnType(MethodParameter returnType) {
            // 排除已标注 @RawResponse 的方法
            return !returnType.hasMethodAnnotation(RawResponse.class);
        }

        @Override
        public void handleReturnValue(Object returnValue,
                                      MethodParameter returnType,
                                      ModelAndViewContainer mavContainer,
                                      NativeWebRequest webRequest) throws Exception {
            // 标记请求已处理（不继续走视图解析）
            mavContainer.setRequestHandled(true);

            // 包装返回值
            ApiResult<?> result = ApiResult.success(returnValue);

            // 获取 HttpServletResponse 写入
            jakarta.servlet.http.HttpServletResponse response =
                webRequest.getNativeResponse(jakarta.servlet.http.HttpServletResponse.class);
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write(new ObjectMapper().writeValueAsString(result));
        }
    }
}

// 标记不需要包装的注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface RawResponse {}

record ApiResult<T>(int code, String message, T data) {
    static <T> ApiResult<T> success(T data) {
        return new ApiResult<>(0, "ok", data);
    }
}
```

**最佳实践**：
- 更推荐用 `ResponseBodyAdvice<Object>` 做响应包装（侵入性更低）
- 自定义返回值处理器适合极端定制场景

---

# 十二、消息转换器（一）— configureMessageConverters（替换）

**作用**：**完全替换** Spring MVC 默认的消息转换器列表。

> ⚠️ 调用此方法会丢弃 Jackson、String 等内置转换器，导致 JSON 序列化失效！

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.List;

@Configuration
public class ReplaceConvertersConfig implements WebMvcConfigurer {

    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        // ⚠️ 危险操作：清空默认列表后重新设置
        // 此时你必须手动添加所有需要的转换器，否则 JSON 序列化都会挂掉

        // 手动添加 Jackson JSON 转换器
        converters.add(new MappingJackson2HttpMessageConverter());

        // 手动添加 String 转换器
        converters.add(new StringHttpMessageConverter(StandardCharsets.UTF_8));

        // 添加 Protobuf 转换器
        converters.add(new ProtobufHttpMessageConverter());
    }
}
```

**极少数适用场景**：需要完全掌控转换器列表和顺序。

---

# 十二、消息转换器（二）— extendMessageConverters（扩展）★推荐

**作用**：在默认转换器列表**基础上追加**自定义转换器。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.charset.StandardCharsets;
import java.util.List;

@Configuration
public class ExtendConvertersConfig implements WebMvcConfigurer {

    @Override
    public void extendMessageConverters(List<HttpMessageConverter<?>> converters) {
        // ✅ 推荐方式：保留默认，在顶部插入自定义转换器

        // 示例1：将 UTF-8 String 转换器插入最前面
        converters.add(0, new StringHttpMessageConverter(StandardCharsets.UTF_8));

        // 示例2：自定义 Jackson 配置（日期格式、时区等）
        converters.stream()
            .filter(c -> c instanceof MappingJackson2HttpMessageConverter)
            .map(c -> (MappingJackson2HttpMessageConverter) c)
            .forEach(jackson -> {
                jackson.getObjectMapper()
                    .setDateFormat(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss"))
                    .setTimeZone(TimeZone.getTimeZone("Asia/Shanghai"));
            });

        // 示例3：在末尾追加 Protobuf 转换器
        converters.add(new ProtobufHttpMessageConverter());
    }
}
```

**最佳实践**：
- 永远优先用 `extendMessageConverters`
- `add(0, ...)` 插入到列表头部，使自定义转换器优先级最高
- Jackson 配置更推荐通过定义一个 `Jackson2ObjectMapperBuilderCustomizer` Bean 来实现

```java
// Jackson 配置的更好方式（不在 WebMvcConfigurer 里改）
@Bean
public Jackson2ObjectMapperBuilderCustomizer jacksonCustomizer() {
    return builder -> builder
        .simpleDateFormat("yyyy-MM-dd HH:mm:ss")
        .timeZone("Asia/Shanghai");
}
```

---

# 十三、异常解析器（一）— configureHandlerExceptionResolvers（替换）

> ⚠️ 会**替换**全部异常解析器，极少使用。绝大多数场景用 `@ControllerAdvice`。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.HandlerExceptionResolver;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.List;

@Configuration
public class ReplaceExceptionResolversConfig implements WebMvcConfigurer {

    @Override
    public void configureHandlerExceptionResolvers(List<HandlerExceptionResolver> resolvers) {
        // ⚠️ 替换所有异常解析器
        resolvers.clear();
        resolvers.add(new MyGlobalExceptionResolver());
    }
}
```

---

# 十三、异常解析器（二）— extendHandlerExceptionResolvers（扩展）

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.HandlerExceptionResolver;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.List;

@Configuration
public class ExtendExceptionResolversConfig implements WebMvcConfigurer {

    @Override
    public void extendHandlerExceptionResolvers(List<HandlerExceptionResolver> resolvers) {
        // 在默认解析器基础上追加自定义的
        resolvers.add(new CustomBusinessExceptionResolver());
    }

    /**
     * 自定义异常解析器：将业务异常映射为具体 HTTP 状态码和 JSON 体
     *
     * 注意：HandlerExceptionResolver 的优先级低于 @ExceptionHandler
     *       如果你的 @ControllerAdvice 已经捕获了异常，这里不会执行
     */
    static class CustomBusinessExceptionResolver implements HandlerExceptionResolver {

        @Override
        public ModelAndView resolveException(
                HttpServletRequest request,
                HttpServletResponse response,
                Object handler, Exception ex) {

            // 只处理特定异常
            if (ex instanceof BusinessException bizEx) {
                response.setStatus(bizEx.getHttpStatus());
                response.setContentType("application/json;charset=UTF-8");
                try {
                    response.getWriter().write(
                        "{\"code\":" + bizEx.getCode() +
                        ",\"message\":\"" + bizEx.getMessage() + "\"}"
                    );
                } catch (Exception ignored) {}
                return new ModelAndView();  // 空 ModelAndView 表示已处理
            }
            // 返回 null → 交给下一个异常解析器处理
            return null;
        }
    }
}
```

**实际开发建议**：99% 的情况用 `@ControllerAdvice`，别碰这两个方法。

```java
// 绝大多数情况下用这个就行了：
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResult<?> handleBusinessException(BusinessException ex) {
        return new ApiResult<>(ex.getCode(), ex.getMessage(), null);
    }
}
```

---

# 十四、默认 Servlet — configureDefaultServletHandling

**作用**：让 `DispatcherServlet` 把未匹配到的请求转发给 Servlet 容器的默认 Servlet（处理静态文件）。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.DefaultServletHandlerConfigurer;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class DefaultServletConfig implements WebMvcConfigurer {

    @Override
    public void configureDefaultServletHandling(DefaultServletHandlerConfigurer configurer) {
        // 启用默认 Servlet 转发
        // 场景：DispatcherServlet 映射到 /，静态资源配置未覆盖时，
        //       请求会被转发给 Tomcat 的 DefaultServlet 处理
        configurer.enable();

        // 也可指定默认 Servlet 名称（通常不需要）
        // configurer.enable("default");
    }
}
```

**Spring Boot 默认行为**：已通过 `addResourceHandlers` 处理好静态资源，一般不需要这个。

---

# 十五、验证器 — getValidator

**作用**：提供自定义的 Spring `Validator` 实例，替代 Bean Validation。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.validation.Errors;
import org.springframework.validation.Validator;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class ValidatorConfig implements WebMvcConfigurer {

    @Override
    public Validator getValidator() {
        return new CustomValidator();
    }

    /**
     * 自定义验证器：不用 @Valid / @NotNull，改为编程式校验
     */
    static class CustomValidator implements Validator {

        @Override
        public boolean supports(Class<?> clazz) {
            // 表示这个 Validator 可以校验哪些类型
            return UserCreateDto.class.isAssignableFrom(clazz);
        }

        @Override
        public void validate(Object target, Errors errors) {
            UserCreateDto dto = (UserCreateDto) target;

            // 编程式校验逻辑
            if (dto.getUsername() == null || dto.getUsername().length() < 3) {
                errors.rejectValue("username", "too.short",
                    "用户名至少 3 个字符");
            }

            if (dto.getEmail() != null && !dto.getEmail().contains("@")) {
                errors.rejectValue("email", "invalid",
                    "邮箱格式不正确");
            }
        }
    }
}
```

**对比 JSR-380（Bean Validation）**：
- JSR-380 用注解 `@NotNull` `@Size` `@Email`，简单直观，**推荐**
- `Validator` 接口用于复杂对象级校验、跨字段校验（如"密码和确认密码一致"）

---

# 十六、消息编码解析器 — getMessageCodesResolver

**作用**：自定义数据绑定和校验错误信息的编码规则。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.validation.DefaultMessageCodesResolver;
import org.springframework.validation.MessageCodesResolver;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class MessageCodesConfig implements WebMvcConfigurer {

    @Override
    public MessageCodesResolver getMessageCodesResolver() {
        DefaultMessageCodesResolver resolver = new DefaultMessageCodesResolver();

        // 设置错误码格式：PREFIX_ERROR_CODE
        // 默认格式：
        //   errorCode.objectName.field        → "Size.userCreateDto.username"
        //   errorCode.field                   → "Size.username"
        //   errorCode.fieldType               → "Size.java.lang.String"
        //   errorCode                         → "Size"
        resolver.setMessageCodeFormatter(
            DefaultMessageCodesResolver.Format.POSTFIX_ERROR_CODE
        );

        return resolver;
    }
}
```

**一般不需要修改**，Spring 默认的错误码生成策略已经足够匹配 `messages.properties` 里的国际化文案了。

---

# 完整示例：生产级配置类

以下是一个综合性的生产级配置示例，按实际使用频率排列：

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    // ==================== 高频使用 ====================

    // 1. CORS（前后端分离必配）
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("https://frontend.example.com")
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowCredentials(true);
    }

    // 2. 拦截器（认证 / 日志）
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new AuthInterceptor())
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/public/**");
    }

    // 3. 消息转换器扩展
    @Override
    public void extendMessageConverters(List<HttpMessageConverter<?>> converters) {
        // 修改 Jackson 配置等
    }

    // 4. 自定义参数解析器
    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        resolvers.add(new CurrentUserArgumentResolver());
    }

    // 5. 静态资源缓存
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/static/**")
                .addResourceLocations("classpath:/static/")
                .setCachePeriod(3600);
    }

    // ==================== 中频使用 ====================

    // 6. 格式化器
    @Override
    public void addFormatters(FormatterRegistry registry) {
        registry.addFormatter(new LocalDateFormatter());
    }

    // 7. 视图控制器（SPA fallback）
    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        registry.addViewController("/{spring:[^.]+}")
                .setViewName("forward:/");
    }

    // 8. 路径前缀
    @Override
    public void configurePathMatch(PathMatchConfigurer configurer) {
        configurer.addPathPrefix("/api/v1",
            c -> c.isAnnotationPresent(RestController.class));
    }

    // ==================== 低频使用 ====================

    // 9. 内容协商
    // 10. 异步支持
    // 11. 视图解析器
    // 12. 返回值处理器
    // 13~14. 异常解析器（用 @ControllerAdvice 代替）
    // 15. 默认 Servlet
    // 16. 验证器
    // 17. 消息编码解析器

    // ⚠️ 慎用（替换模式）：
    // configureMessageConverters()
    // configureHandlerExceptionResolvers()
}
```

---

# 核心原则总结

| 方法前缀 | 语义 | 最佳实践 |
|----------|------|----------|
| `configure*` | **替换**全部默认配置 | ​**几乎不用**。一旦覆写，Spring Boot 自动配置的会被丢弃 |
| `extend*` | **扩展**，保留默认 + 追加自定义 | `extendMessageConverters`、`extendHandlerExceptionResolvers` |
| `add*` | **追加**，不影响已有配置 | 最常用的模式：`addInterceptors`、`addCorsMappings`、`addResourceHandlers` |
| `get*` | 提供自定义实例 | `getValidator`、`getMessageCodesResolver` |

# 不要做的事

1. **不要**在 `@Configuration` 上加 `@EnableWebMvc` —— 会禁用 Spring Boot 的 MVC 自动配置
2. **不要**用 `configureMessageConverters` 除非你清楚知道自己在干什么 —— 用 `extendMessageConverters`
3. **不要**在 `addInterceptors` 中放耗时逻辑 —— `preHandle` 阻塞请求线程
4. **不要**同时配置 `@CrossOrigin` 和全局 CORS —— 可能导致重复 `Access-Control-Allow-Origin` 头
