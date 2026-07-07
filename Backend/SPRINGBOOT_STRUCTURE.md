# AGENT INSTRUCTIONS — Spring Boot (Java) Backend

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `SPRINGBOOT_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> This file is the single source of truth. No exceptions.

---

## YOUR IDENTITY

You are a senior Java backend engineer building production Spring Boot REST APIs.
Every file you generate MUST follow the exact structure, patterns, and rules in this document.
You have creative freedom only over business logic inside the defined boundaries.

---

## TECH STACK — USE EXACTLY THESE

```
Framework       : Spring Boot 3.x          (Jakarta EE, not javax)
Language        : Java 21                  (records, sealed classes, text blocks)
ORM             : Spring Data JPA          + Hibernate 6
Database        : PostgreSQL 16
Migrations      : Flyway
Validation      : Jakarta Bean Validation  (Hibernate Validator)
Security        : Spring Security 6        + JWT (jjwt 0.12.x)
Mapping         : MapStruct 1.6
Testing         : JUnit 5 + Mockito + Testcontainers
Build           : Maven (pom.xml)
Docs            : SpringDoc OpenAPI 2.x    (disabled in production)
```

---

## MANDATORY FOLDER STRUCTURE

```
src/
├── main/
│   ├── java/com/company/appname/
│   │   │
│   │   ├── AppNameApplication.java          # @SpringBootApplication entry point
│   │   │
│   │   ├── config/                          # Spring configuration classes
│   │   │   ├── SecurityConfig.java          # Spring Security + JWT filter
│   │   │   ├── JwtConfig.java               # JWT properties bean
│   │   │   ├── CorsConfig.java              # CORS configuration
│   │   │   └── OpenApiConfig.java           # Swagger/OpenAPI config
│   │   │
│   │   ├── domain/                          # JPA Entities — table definitions only
│   │   │   ├── common/
│   │   │   │   └── BaseEntity.java          # id, createdAt, updatedAt (abstract)
│   │   │   ├── User.java
│   │   │   └── Item.java
│   │   │
│   │   ├── dto/                             # Request + Response DTOs (Java records)
│   │   │   ├── common/
│   │   │   │   ├── PageResponse.java        # Generic paginated response wrapper
│   │   │   │   └── ApiError.java            # Standard error response
│   │   │   ├── user/
│   │   │   │   ├── UserCreateRequest.java
│   │   │   │   ├── UserUpdateRequest.java
│   │   │   │   └── UserResponse.java
│   │   │   ├── item/
│   │   │   │   ├── ItemCreateRequest.java
│   │   │   │   ├── ItemUpdateRequest.java
│   │   │   │   └── ItemResponse.java
│   │   │   └── auth/
│   │   │       ├── LoginRequest.java
│   │   │       └── TokenResponse.java
│   │   │
│   │   ├── repository/                      # Spring Data JPA interfaces
│   │   │   ├── UserRepository.java
│   │   │   └── ItemRepository.java
│   │   │
│   │   ├── service/                         # Business logic
│   │   │   ├── UserService.java
│   │   │   ├── ItemService.java
│   │   │   └── AuthService.java
│   │   │
│   │   ├── controller/                      # REST controllers
│   │   │   ├── UserController.java
│   │   │   ├── ItemController.java
│   │   │   └── AuthController.java
│   │   │
│   │   ├── security/                        # JWT + Spring Security internals
│   │   │   ├── JwtTokenProvider.java        # Create + validate JWT
│   │   │   ├── JwtAuthFilter.java           # OncePerRequestFilter
│   │   │   └── UserDetailsServiceImpl.java  # Loads user for auth
│   │   │
│   │   ├── exception/                       # Custom exceptions + global handler
│   │   │   ├── GlobalExceptionHandler.java  # @ControllerAdvice
│   │   │   ├── ResourceNotFoundException.java
│   │   │   ├── ConflictException.java
│   │   │   └── BadRequestException.java
│   │   │
│   │   └── mapper/                          # MapStruct entity ↔ DTO mappers
│   │       ├── UserMapper.java
│   │       └── ItemMapper.java
│   │
│   └── resources/
│       ├── application.yml                  # Base config
│       ├── application-dev.yml              # Dev overrides
│       ├── application-prod.yml             # Prod overrides
│       └── db/migration/                    # Flyway SQL migrations
│           └── V1__initial_schema.sql
│
├── test/
│   └── java/com/company/appname/
│       ├── controller/                      # MockMvc integration tests
│       ├── service/                         # Unit tests with Mockito
│       └── repository/                      # Testcontainers DB tests
│
└── pom.xml
```

---

## ARCHITECTURAL LAYERS — READ EVERY LINE

### LAYER RULES

```
domain/     → JPA entity definitions ONLY. No business logic. No queries in the entity.
dto/        → Java records for request/response. Validation annotations here.
repository/ → Spring Data JPA interfaces. Custom @Query here. Nothing else.
service/    → Business logic. Calls repository. Throws exceptions. No @Transactional on controller.
controller/ → HTTP routing. Calls service. Returns ResponseEntity. No logic.
mapper/     → MapStruct only. No manual field-by-field mapping.
security/   → JWT and Spring Security wiring. No business logic.
exception/  → Custom exception classes + @ControllerAdvice handler.
config/     → Spring beans and configuration. No logic.
```

---

## LAYER 1 — `domain/` — JPA Entities

```java
// domain/common/BaseEntity.java
package com.company.appname.domain.common;

import jakarta.persistence.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;
import java.time.Instant;
import java.util.UUID;

@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(updatable = false, nullable = false)
    private UUID id;

    @CreatedDate
    @Column(updatable = false, nullable = false)
    private Instant createdAt;

    @LastModifiedDate
    @Column(nullable = false)
    private Instant updatedAt;

    // getters only — no setters on id/createdAt/updatedAt
    public UUID getId()       { return id; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
}
```

```java
// domain/User.java
package com.company.appname.domain;

import com.company.appname.domain.common.BaseEntity;
import jakarta.persistence.*;
import java.util.List;

@Entity
@Table(name = "users",
       uniqueConstraints = @UniqueConstraint(columnNames = "email"))
public class User extends BaseEntity {

    @Column(nullable = false, length = 255)
    private String email;

    @Column(nullable = false, length = 255)
    private String hashedPassword;

    @Column(length = 255)
    private String fullName;

    @Column(nullable = false)
    private boolean isActive = true;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private Role role = Role.STAFF;

    @OneToMany(mappedBy = "owner", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Item> items;

    public enum Role { ADMIN, MANAGER, STAFF, VIEWER }

    // Getters and setters (or use Lombok @Getter @Setter — project standard)
    public String getEmail()          { return email; }
    public void setEmail(String e)    { this.email = e; }
    public String getHashedPassword() { return hashedPassword; }
    public void setHashedPassword(String h) { this.hashedPassword = h; }
    public String getFullName()       { return fullName; }
    public void setFullName(String n) { this.fullName = n; }
    public boolean isActive()         { return isActive; }
    public void setActive(boolean a)  { this.isActive = a; }
    public Role getRole()             { return role; }
    public void setRole(Role r)       { this.role = r; }
    public List<Item> getItems()      { return items; }
}
```

**Entity Rules:**
- ALWAYS extend `BaseEntity` — never define `id`/`createdAt`/`updatedAt` per-entity
- ALWAYS define `@Table(name = "...")` explicitly — no auto-naming
- NEVER put `@Transactional` on entity methods
- NEVER put queries, business logic, or service calls inside an entity
- Use `@Enumerated(EnumType.STRING)` — never `ORDINAL`

---

## LAYER 2 — `dto/` — Java Records

```java
// dto/user/UserCreateRequest.java
package com.company.appname.dto.user;

import jakarta.validation.constraints.*;

public record UserCreateRequest(
    @NotBlank @Email(message = "Invalid email")
    String email,

    @NotBlank @Size(min = 2, max = 100)
    String fullName,

    @NotBlank @Size(min = 8, max = 128)
    @Pattern(regexp = ".*[A-Z].*", message = "Must contain an uppercase letter")
    @Pattern(regexp = ".*[0-9].*", message = "Must contain a number")
    String password,

    @NotNull
    String role
) {}
```

```java
// dto/user/UserUpdateRequest.java
package com.company.appname.dto.user;

import jakarta.validation.constraints.*;

public record UserUpdateRequest(
    @Email String email,
    @Size(min = 2, max = 100) String fullName,
    @Size(min = 8, max = 128) String password,
    Boolean isActive
) {}
```

```java
// dto/user/UserResponse.java
package com.company.appname.dto.user;

import java.time.Instant;
import java.util.UUID;

public record UserResponse(
    UUID id,
    String email,
    String fullName,
    boolean isActive,
    String role,
    Instant createdAt,
    Instant updatedAt
) {
    // hashedPassword is NEVER included — not a field in this record
}
```

```java
// dto/common/PageResponse.java
package com.company.appname.dto.common;

import java.util.List;

public record PageResponse<T>(
    List<T> items,
    long total,
    int page,
    int size,
    int pages
) {
    public static <T> PageResponse<T> of(
        List<T> items, long total, int page, int size
    ) {
        return new PageResponse<>(items, total, page, size,
            (int) Math.ceil((double) total / size));
    }
}
```

**DTO Rules:**
- ALL DTOs are Java `record` types — never classes with getters/setters
- Validation annotations go on `Request` records only — never on entities
- `Response` records NEVER include `hashedPassword`, keys, or internal fields
- `Create/Update/Response` naming for every resource — no `Data`, `Payload`, `Model` suffixes

---

## LAYER 3 — `repository/` — Spring Data JPA

```java
// repository/UserRepository.java
package com.company.appname.repository;

import com.company.appname.domain.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface UserRepository extends JpaRepository<User, UUID> {

    Optional<User> findByEmail(String email);

    boolean existsByEmail(String email);

    Page<User> findByIsActiveTrue(Pageable pageable);

    @Query("SELECT u FROM User u WHERE u.role = :role AND u.isActive = true")
    Page<User> findActiveByRole(User.Role role, Pageable pageable);
}
```

**Repository Rules:**
- ALWAYS use Spring Data method naming — never write SQL for simple lookups
- Use `@Query` only for complex joins or aggregations
- NEVER inject repositories directly into controllers — always go through service
- NEVER put `@Transactional` on repository methods — Spring Data handles it

---

## LAYER 4 — `service/` — Business Logic

```java
// service/UserService.java
package com.company.appname.service;

import com.company.appname.domain.User;
import com.company.appname.dto.user.*;
import com.company.appname.dto.common.PageResponse;
import com.company.appname.exception.*;
import com.company.appname.mapper.UserMapper;
import com.company.appname.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final UserMapper     userMapper;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public UserResponse createUser(UserCreateRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new ConflictException("User with this email already exists.");
        }
        User user = userMapper.toEntity(request);
        user.setHashedPassword(passwordEncoder.encode(request.password()));
        return userMapper.toResponse(userRepository.save(user));
    }

    @Transactional(readOnly = true)
    public PageResponse<UserResponse> getUsers(int page, int size) {
        var pageResult = userRepository.findByIsActiveTrue(PageRequest.of(page, size));
        return PageResponse.of(
            pageResult.map(userMapper::toResponse).toList(),
            pageResult.getTotalElements(), page, size
        );
    }

    @Transactional(readOnly = true)
    public UserResponse getUserById(UUID id) {
        return userMapper.toResponse(findUserOrThrow(id));
    }

    @Transactional
    public UserResponse updateUser(UUID id, UserUpdateRequest request) {
        User user = findUserOrThrow(id);
        userMapper.updateEntityFromRequest(request, user);
        if (request.password() != null) {
            user.setHashedPassword(passwordEncoder.encode(request.password()));
        }
        return userMapper.toResponse(userRepository.save(user));
    }

    @Transactional
    public void deleteUser(UUID id) {
        User user = findUserOrThrow(id);
        userRepository.delete(user);
    }

    private User findUserOrThrow(UUID id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User", id));
    }
}
```

**Service Rules:**
- `@Transactional` on service methods — NEVER on controller methods
- Use `@Transactional(readOnly = true)` for all read operations (performance)
- ALWAYS hash passwords in service — NEVER in controller or repository
- Throw custom exceptions — never return `null` to indicate failure
- Use `@RequiredArgsConstructor` — inject via constructor, never `@Autowired` on fields

---

## LAYER 5 — `controller/` — REST Endpoints

```java
// controller/UserController.java
package com.company.appname.controller;

import com.company.appname.dto.user.*;
import com.company.appname.dto.common.PageResponse;
import com.company.appname.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @PreAuthorize("hasRole('ADMIN')")
    public UserResponse createUser(@Valid @RequestBody UserCreateRequest request) {
        return userService.createUser(request);
    }

    @GetMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    public PageResponse<UserResponse> getUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        return userService.getUsers(page, size);
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    public UserResponse getUserById(@PathVariable UUID id) {
        return userService.getUserById(id);
    }

    @PatchMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or #id == authentication.principal.id")
    public UserResponse updateUser(
        @PathVariable UUID id,
        @Valid @RequestBody UserUpdateRequest request
    ) {
        return userService.updateUser(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteUser(@PathVariable UUID id) {
        userService.deleteUser(id);
    }
}
```

**Controller Rules:**
- NEVER put business logic in controllers — call service only
- ALWAYS use `@Valid` on `@RequestBody` — validation is automatic
- ALWAYS use `@PreAuthorize` for role-based access control
- Return the DTO directly (Spring handles serialization) — no manual `ResponseEntity` wrapping unless you need custom headers
- Use `@RequestMapping("/api/v1/{resource}")` — versioned paths

---

## LAYER 6 — `mapper/` — MapStruct

```java
// mapper/UserMapper.java
package com.company.appname.mapper;

import com.company.appname.domain.User;
import com.company.appname.dto.user.*;
import org.mapstruct.*;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface UserMapper {

    @Mapping(target = "id",             ignore = true)
    @Mapping(target = "hashedPassword", ignore = true)   // hashed in service
    @Mapping(target = "createdAt",      ignore = true)
    @Mapping(target = "updatedAt",      ignore = true)
    @Mapping(source = "role", target = "role",
             qualifiedByName = "stringToRole")
    User toEntity(UserCreateRequest request);

    @Mapping(source = "role", target = "role",
             qualifiedByName = "roleToString")
    UserResponse toResponse(User user);

    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    @Mapping(target = "hashedPassword", ignore = true)
    void updateEntityFromRequest(UserUpdateRequest request, @MappingTarget User user);

    @Named("stringToRole")
    default User.Role stringToRole(String role) {
        return role == null ? User.Role.STAFF : User.Role.valueOf(role.toUpperCase());
    }

    @Named("roleToString")
    default String roleToString(User.Role role) {
        return role == null ? null : role.name();
    }
}
```

**Mapper Rules:**
- ALWAYS use MapStruct — never write manual `entity.setField(dto.getField())` loops
- ALWAYS ignore `id`, `hashedPassword`, `createdAt`, `updatedAt` when mapping from request
- `updateEntityFromRequest` MUST use `NullValuePropertyMappingStrategy.IGNORE` for PATCH semantics
- NEVER map sensitive fields (passwords) — handle in service

---

## LAYER 7 — `exception/` — Global Error Handling

```java
// exception/GlobalExceptionHandler.java
package com.company.appname.exception;

import com.company.appname.dto.common.ApiError;
import org.springframework.http.*;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
import java.time.Instant;
import java.util.stream.Collectors;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiError handleNotFound(ResourceNotFoundException ex) {
        return new ApiError(404, ex.getMessage(), Instant.now());
    }

    @ExceptionHandler(ConflictException.class)
    @ResponseStatus(HttpStatus.CONFLICT)
    public ApiError handleConflict(ConflictException ex) {
        return new ApiError(409, ex.getMessage(), Instant.now());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiError handleValidation(MethodArgumentNotValidException ex) {
        String message = ex.getBindingResult().getFieldErrors().stream()
            .map(FieldError::getDefaultMessage)
            .collect(Collectors.joining(", "));
        return new ApiError(400, message, Instant.now());
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiError handleGeneric(Exception ex) {
        // NEVER expose stack trace or message in production
        return new ApiError(500, "An internal error occurred.", Instant.now());
    }
}
```

```java
// exception/ResourceNotFoundException.java
package com.company.appname.exception;
import java.util.UUID;

public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String resource, UUID id) {
        super(resource + " not found with id: " + id);
    }
    public ResourceNotFoundException(String message) {
        super(message);
    }
}
```

```java
// dto/common/ApiError.java
package com.company.appname.dto.common;
import java.time.Instant;

public record ApiError(int status, String message, Instant timestamp) {}
```

---

## LAYER 8 — `security/` — JWT

```java
// security/JwtTokenProvider.java
package com.company.appname.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import javax.crypto.SecretKey;
import java.time.Instant;
import java.util.Date;

@Component
public class JwtTokenProvider {

    private final SecretKey key;
    private final long      expirationMs;

    public JwtTokenProvider(
        @Value("${app.jwt.secret}")      String  secret,
        @Value("${app.jwt.expiration-ms}") long  expirationMs
    ) {
        this.key          = Keys.hmacShaKeyFor(secret.getBytes());
        this.expirationMs = expirationMs;
    }

    public String generateToken(String userId, String role) {
        Instant now = Instant.now();
        return Jwts.builder()
            .subject(userId)
            .claim("role", role)
            .issuedAt(Date.from(now))
            .expiration(Date.from(now.plusMillis(expirationMs)))
            .signWith(key)
            .compact();
    }

    public Claims validateAndParseClaims(String token) {
        return Jwts.parser().verifyWith(key).build()
            .parseSignedClaims(token).getPayload();
    }

    public boolean isValid(String token) {
        try { validateAndParseClaims(token); return true; }
        catch (JwtException | IllegalArgumentException e) { return false; }
    }
}
```

---

## LAYER 9 — `application.yml`

```yaml
# src/main/resources/application.yml
spring:
  application:
    name: your-app-name
  datasource:
    url:               ${DB_URL}
    username:          ${DB_USERNAME}
    password:          ${DB_PASSWORD}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate      # NEVER create/update in production — Flyway handles schema
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: false
  flyway:
    enabled:  true
    locations: classpath:db/migration
    baseline-on-migrate: true

server:
  port: 8080
  error:
    include-message: never    # NEVER expose error messages in production
    include-stacktrace: never
    include-exception: false
  servlet:
    context-path: /

app:
  jwt:
    secret:        ${JWT_SECRET}
    expiration-ms: ${JWT_EXPIRATION_MS:1800000}   # 30 min default
  cors:
    allowed-origins: ${CORS_ALLOWED_ORIGINS}
```

```yaml
# src/main/resources/application-dev.yml
spring:
  jpa:
    show-sql: true
server:
  error:
    include-message: always
    include-stacktrace: on_param
```

```yaml
# src/main/resources/application-prod.yml
spring:
  jpa:
    show-sql: false
springdoc:
  api-docs:
    enabled: false     # hide API docs in production
  swagger-ui:
    enabled: false
```

---

## LAYER 10 — Flyway Migrations

```sql
-- src/main/resources/db/migration/V1__initial_schema.sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email            VARCHAR(255) NOT NULL UNIQUE,
    hashed_password  VARCHAR(255) NOT NULL,
    full_name        VARCHAR(255),
    is_active        BOOLEAN      NOT NULL DEFAULT true,
    role             VARCHAR(50)  NOT NULL DEFAULT 'STAFF',
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE items (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id    UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email    ON users(email);
CREATE INDEX idx_items_owner_id ON items(owner_id);
```

**Migration Rules:**
- NEVER use `ddl-auto: create` or `ddl-auto: update` — always `validate`
- Every schema change = new migration file `V{N}__{description}.sql`
- NEVER edit a migration that has been applied to production
- Use `gen_random_uuid()` for UUID primary keys
- Always add indexes for foreign keys and frequently queried columns

---

## LAYER 11 — `pom.xml` — Maven Dependencies

```xml
<!-- pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.0</version>
        <relativePath/>
    </parent>

    <groupId>com.company</groupId>
    <artifactId>app-name</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>app-name</name>

    <properties>
        <java.version>21</java.version>
        <mapstruct.version>1.6.0</mapstruct.version>
        <jjwt.version>0.12.5</jjwt.version>
    </properties>

    <dependencies>
        <!-- Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- JPA + PostgreSQL -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Flyway -->
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-database-postgresql</artifactId>
        </dependency>

        <!-- Validation -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Security -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>

        <!-- JWT -->
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-api</artifactId>
            <version>${jjwt.version}</version>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-impl</artifactId>
            <version>${jjwt.version}</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-jackson</artifactId>
            <version>${jjwt.version}</version>
            <scope>runtime</scope>
        </dependency>

        <!-- MapStruct -->
        <dependency>
            <groupId>org.mapstruct</groupId>
            <artifactId>mapstruct</artifactId>
            <version>${mapstruct.version}</version>
        </dependency>

        <!-- Lombok (optional but common) -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- SpringDoc OpenAPI -->
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>2.5.0</version>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.security</groupId>
            <artifactId>spring-security-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
            <!-- MapStruct annotation processor -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.mapstruct</groupId>
                            <artifactId>mapstruct-processor</artifactId>
                            <version>${mapstruct.version}</version>
                        </path>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## LAYER 12 — `config/SecurityConfig.java` + `security/JwtAuthFilter.java`

```java
// config/SecurityConfig.java
package com.company.appname.config;

import com.company.appname.security.JwtAuthFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthFilter              jwtAuthFilter;
    private final UserDetailsServiceImpl     userDetailsService;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**", "/health", "/actuator/health").permitAll()
                .anyRequest().authenticated()
            )
            .authenticationProvider(authenticationProvider())
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(); }

    @Bean
    public AuthenticationProvider authenticationProvider() {
        var provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService);
        provider.setPasswordEncoder(passwordEncoder());
        return provider;
    }
}
```

```java
// security/JwtAuthFilter.java
package com.company.appname.security;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import lombok.RequiredArgsConstructor;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;

@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtTokenProvider   jwtTokenProvider;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(
        @NonNull HttpServletRequest  request,
        @NonNull HttpServletResponse response,
        @NonNull FilterChain         chain
    ) throws ServletException, IOException {

        final String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }

        final String token  = authHeader.substring(7);
        if (!jwtTokenProvider.isValid(token)) { chain.doFilter(request, response); return; }

        final String userId = jwtTokenProvider.validateAndParseClaims(token).getSubject();
        if (userId != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            var userDetails = userDetailsService.loadUserByUsername(userId);
            var authToken   = new UsernamePasswordAuthenticationToken(
                userDetails, null, userDetails.getAuthorities()
            );
            authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
            SecurityContextHolder.getContext().setAuthentication(authToken);
        }
        chain.doFilter(request, response);
    }
}
```

---

## LAYER 13 — Request Signature Verification Filter

```java
// security/RequestSigningFilter.java
package com.company.appname.security;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.HexFormat;
import java.util.Set;

@Component
public class RequestSigningFilter extends OncePerRequestFilter {

    @Value("${app.security.signing-secret}")
    private String signingSecret;

    private static final Set<String> EXEMPT = Set.of(
        "/api/v1/auth/login", "/api/v1/auth/register", "/health"
    );
    private static final long MAX_AGE_MS = 300_000L; // 5 minutes

    @Override
    protected void doFilterInternal(
        HttpServletRequest request, HttpServletResponse response, FilterChain chain
    ) throws ServletException, IOException {

        String path = request.getRequestURI();
        if (EXEMPT.stream().anyMatch(path::startsWith)) { chain.doFilter(request, response); return; }

        String timestamp = request.getHeader("X-Timestamp");
        String signature = request.getHeader("X-Signature");

        if (timestamp == null || signature == null) {
            response.sendError(401, "Missing signature headers."); return;
        }
        long ts = Long.parseLong(timestamp);
        if (Math.abs(System.currentTimeMillis() - ts) > MAX_AGE_MS) {
            response.sendError(401, "Request expired."); return;
        }

        // Cache body for re-reading
        CachedBodyHttpServletRequest cached = new CachedBodyHttpServletRequest(request);
        String body    = new String(cached.getBody(), StandardCharsets.UTF_8);
        String message = timestamp + request.getMethod().toUpperCase() + path + body;
        String expected = hmacSHA256(signingSecret, message);

        if (!MessageDigest.isEqual(expected.getBytes(), signature.getBytes())) {
            response.sendError(401, "Invalid request signature."); return;
        }
        chain.doFilter(cached, response);
    }

    private String hmacSHA256(String secret, String message) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
        return HexFormat.of().formatHex(mac.doFinal(message.getBytes(StandardCharsets.UTF_8)));
    }
}
```

Add to `application.yml`:
```yaml
app:
  security:
    signing-secret: ${APP_SIGNING_SECRET}
```

Register filter in `SecurityConfig.java` — add before JWT filter:
```java
.addFilterBefore(requestSigningFilter, JwtAuthFilter.class)
```

---

## NAMING CONVENTIONS

| What | Convention | Example |
|------|-----------|---------|
| Classes | `PascalCase` | `UserService`, `ItemController` |
| Methods | `camelCase` | `createUser()`, `getUserById()` |
| Records (DTOs) | `{Resource}{Action}Request` / `{Resource}Response` | `UserCreateRequest`, `UserResponse` |
| Entities | `PascalCase` (singular) | `User`, `Item` |
| Table names | `snake_case` plural | `users`, `item_categories` |
| Column names | `snake_case` | `created_at`, `owner_id` |
| Packages | `lowercase` | `com.company.app.service` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE` |
| Repositories | `{Entity}Repository` | `UserRepository` |
| Services | `{Entity}Service` | `UserService` |
| Controllers | `{Entity}Controller` | `UserController` |
| Mappers | `{Entity}Mapper` | `UserMapper` |
| Request mapping | `/api/v1/{resource}` plural | `/api/v1/users` |

---

## WHEN ADDING A NEW RESOURCE

```
STEP 1   Create Flyway migration: src/main/resources/db/migration/V{N}__{description}.sql
STEP 2   domain/{Resource}.java               → JPA entity extending BaseEntity
STEP 3   dto/{resource}/{Resource}CreateRequest.java
         dto/{resource}/{Resource}UpdateRequest.java
         dto/{resource}/{Resource}Response.java
STEP 4   repository/{Resource}Repository.java → extends JpaRepository<{Resource}, UUID>
STEP 5   mapper/{Resource}Mapper.java         → MapStruct interface
STEP 6   service/{Resource}Service.java       → @Service class with @Transactional methods
STEP 7   controller/{Resource}Controller.java → @RestController with @RequestMapping
STEP 8   exception/GlobalExceptionHandler.java → add any new exception types if needed
```

---

## ABSOLUTE PROHIBITIONS

```
✗  @Transactional on controller methods — services only
✗  Field injection (@Autowired on fields) — constructor injection only
✗  Business logic in controllers — service only
✗  Queries in entities — repositories only
✗  Manual field mapping — always MapStruct
✗  Returning passwords or hashed_password in any response DTO
✗  ddl-auto: create or update — Flyway only
✗  ORDINAL enum persistence — always STRING
✗  Editing applied Flyway migration files
✗  include-message: always in production — never
✗  include-stacktrace: always — never in production
✗  CORS allowedOrigins("*") in production
✗  JWT secret hardcoded — always from ${JWT_SECRET}
✗  swagger-ui enabled in production
✗  Raw SQL strings in service — use @Query or Spring Data methods
```

---

## PRE-COMPLETION CHECKLIST

```
[ ] Flyway migration created for every schema change
[ ] Entity extends BaseEntity (no manual id/timestamp fields)
[ ] DTOs are Java records with validation annotations
[ ] Mapping done via MapStruct — no manual setField() calls
[ ] Service has @Transactional — controller does not
[ ] readOnly = true on all @Transactional read methods
[ ] Passwords hashed in service with passwordEncoder
[ ] Response DTOs never include hashedPassword
[ ] Controller uses @Valid on @RequestBody
[ ] Controller uses @PreAuthorize for access control
[ ] GlobalExceptionHandler covers all custom exceptions
[ ] application-prod.yml has ddl-auto: validate
[ ] application-prod.yml disables springdoc/swagger
[ ] server.error.include-message: never in production
[ ] Constructor injection used — no @Autowired on fields
```

---

*Stack: Spring Boot 3.x · Java 21 · Spring Data JPA · PostgreSQL · Flyway · MapStruct · Spring Security 6 · JWT*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
