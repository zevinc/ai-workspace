在保持 Spring Boot 所有默认 MVC 配置的前提下，通过实现 `WebMvcConfigurer` 接口，你可以获得以下 **22 个扩展点**。

我根据官方文档将它们分为核心配置、组件扩展、MVC 细节调优三大类，便于你按需使用。

### 核心配置扩展 (4项)

| 方法 | 用途说明 |
| :--- | :--- |
| **`addInterceptors`** | **注册拦截器**，用于在请求处理前后执行日志记录、权限校验等通用逻辑。 |
| **`addCorsMappings`** | **配置跨域资源共享 (CORS)**，解决浏览器跨域访问限制。 |
| **`addViewControllers`** | **配置视图控制器**，用于无需业务逻辑的页面跳转（如首页 `/` 映射到 `index.html`）。 |
| **`configureViewResolvers`** | **配置视图解析器**，当控制器返回字符串视图名（如 `"home"`）时，将其解析为具体的 JSP 或 Thymeleaf 视图。 |

### 组件与属性扩展 (10项)

| 方法 | 用途说明 |
| :--- | :--- |
| **`addFormatters`** | **注册自定义格式化器和转换器**，用于处理类型转换（如将字符串转换为 `Date` 或枚举）。 |
| **`addArgumentResolvers`** | **添加自定义参数解析器**，支持在 Controller 方法中使用更灵活的参数类型（如自动注入当前登录用户对象）。 |
| **`addReturnValueHandlers`** | **添加自定义返回值处理器**，定制 Controller 返回值的处理逻辑（如包装为统一 API 格式）。 |
| **`configureMessageConverters`** | **配置消息转换器**，用于请求/响应数据的序列化（如 JSON、XML）。**注意**：重写此方法会**覆盖**默认转换器列表。 |
| **`extendMessageConverters`** | **扩展消息转换器**，与上述不同，此方法**保留**默认转换器，仅添加自定义转换器。 |
| **`getValidator`** | **提供自定义校验器 (Validator)**，用于数据校验（如 `@Valid` 注解背后的实现）。 |
| **`addResourceHandlers`** | **配置静态资源处理器**，定义图片、JS、CSS 等静态文件的访问路径和存放位置。 |
| **`configureDefaultServletHandling`** | **配置默认 Servlet 处理**，当 DispatcherServlet 拦截所有请求（`/`）时，允许其将静态资源请求转发给容器的默认 Servlet。 |
| **`configureAsyncSupport`** | **配置异步请求处理**，设置异步请求的超时时间、任务执行器等。 |
| **`getMessageCodesResolver`** | **自定义消息编码解析器**，用于控制数据绑定和校验错误时的错误码生成规则。 |

### MVC 细节调优 (4项)

| 方法 | 用途说明 |
| :--- | :--- |
| **`configurePathMatch`** | **配置路径匹配规则**，如是否匹配末尾斜杠（`/user` 与 `/user/`）、是否使用后缀匹配等。 |
| **`configureContentNegotiation`** | **配置内容协商策略**，决定如何根据请求（如 URL 后缀 `.json` 或 `Accept` 头）返回不同格式的响应。 |
| **`configureHandlerExceptionResolvers`** | **配置异常解析器**，**覆盖**默认的 Spring MVC 异常处理机制。 |
| **`extendHandlerExceptionResolvers`** | **扩展异常解析器**，**保留**默认的异常处理机制，仅添加自定义的异常解析器。 |

### 关于 `@EnableWebMvc` 的重要提醒

再次强调：**在你当前的配置类上，千万不要添加 `@EnableWebMvc` 注解**。

一旦使用该注解，Spring Boot 的 `WebMvcAutoConfiguration` 自动配置将会失效。这会导致你失去 Spring Boot 提供的静态资源映射、默认消息转换器等一系列基础功能，需要你手动配置所有内容，与你的需求背道而驰。

### 示例：如何同时使用多个扩展点

下面是一个同时配置拦截器和视图控制器的简单例子。在这个配置类中，你可以根据需要，随时添加更多的方法。

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.ViewControllerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
// 关键：不要加 @EnableWebMvc 注解
public class MyWebMvcConfig implements WebMvcConfigurer {

    // 1. 添加自定义拦截器
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new MyCustomInterceptor())
                .addPathPatterns("/admin/**") // 拦截 /admin 下的所有请求
                .excludePathPatterns("/admin/login"); // 排除登录接口
    }

    // 2. 添加视图控制器：访问 / 直接跳转到 home 页面
    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        registry.addViewController("/").setViewName("home");
        registry.addViewController("/login").setViewName("login");
    }
    
    // 3. 你可以在这里继续添加其他重写方法，如 addCorsMappings、configurePathMatch 等
}
```

这 22 个扩展点覆盖了 Web 层配置的方方面面，你可以根据实际业务需求灵活选择、按需实现。
