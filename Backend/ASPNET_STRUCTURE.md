# AGENT INSTRUCTIONS — ASP.NET Core (C#) Backend

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `ASPNET_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> This file is the single source of truth. No exceptions.

---

## YOUR IDENTITY

You are a senior C# backend engineer building production ASP.NET Core REST APIs.
Every file you generate MUST follow the exact structure, patterns, and rules in this document.
You have creative freedom only over business logic inside the defined boundaries.

---

## TECH STACK — USE EXACTLY THESE

```
Framework       : ASP.NET Core 9          (Minimal API + Controllers)
Language        : C# 13                   (records, pattern matching, nullable refs)
ORM             : Entity Framework Core 9
Database        : PostgreSQL 16
Migrations      : EF Core Migrations
Validation      : FluentValidation 11
Security        : ASP.NET Core JWT Bearer
Mapping         : Mapster 7               (or AutoMapper — project standard)
Testing         : xUnit + Moq + Testcontainers.PostgreSql
API Docs        : Scalar / Swashbuckle    (disabled in production)
```

---

## MANDATORY FOLDER STRUCTURE

```
YourApp/
│
├── src/
│   └── YourApp.Api/
│       │
│       ├── Program.cs                        # App entry + DI registration + middleware
│       ├── appsettings.json                  # Base config
│       ├── appsettings.Development.json      # Dev overrides
│       ├── appsettings.Production.json       # Prod overrides
│       │
│       ├── Controllers/                      # API controllers
│       │   ├── UsersController.cs
│       │   ├── ItemsController.cs
│       │   └── AuthController.cs
│       │
│       ├── Models/                           # EF Core entities — table definitions only
│       │   ├── Common/
│       │   │   └── BaseEntity.cs             # Id, CreatedAt, UpdatedAt
│       │   ├── User.cs
│       │   └── Item.cs
│       │
│       ├── DTOs/                             # Request/Response records
│       │   ├── Common/
│       │   │   ├── PagedResponse.cs          # Generic paginated wrapper
│       │   │   └── ApiError.cs
│       │   ├── Users/
│       │   │   ├── CreateUserRequest.cs
│       │   │   ├── UpdateUserRequest.cs
│       │   │   └── UserResponse.cs
│       │   ├── Items/
│       │   │   ├── CreateItemRequest.cs
│       │   │   ├── UpdateItemRequest.cs
│       │   │   └── ItemResponse.cs
│       │   └── Auth/
│       │       ├── LoginRequest.cs
│       │       └── TokenResponse.cs
│       │
│       ├── Data/                             # EF Core infrastructure
│       │   ├── AppDbContext.cs               # DbContext — entity configs here
│       │   ├── Configurations/               # IEntityTypeConfiguration per entity
│       │   │   ├── UserConfiguration.cs
│       │   │   └── ItemConfiguration.cs
│       │   └── Migrations/                   # EF Core auto-generated (never edit)
│       │
│       ├── Repositories/                     # Data access — repository pattern
│       │   ├── Interfaces/
│       │   │   ├── IUserRepository.cs
│       │   │   └── IItemRepository.cs
│       │   ├── UserRepository.cs
│       │   └── ItemRepository.cs
│       │
│       ├── Services/                         # Business logic
│       │   ├── Interfaces/
│       │   │   ├── IUserService.cs
│       │   │   └── IItemService.cs
│       │   ├── UserService.cs
│       │   └── ItemService.cs
│       │
│       ├── Validators/                       # FluentValidation validators
│       │   ├── CreateUserRequestValidator.cs
│       │   └── UpdateUserRequestValidator.cs
│       │
│       ├── Middleware/                       # Custom middleware
│       │   ├── ExceptionHandlingMiddleware.cs
│       │   └── RequestLoggingMiddleware.cs
│       │
│       ├── Extensions/                       # IServiceCollection extension methods
│       │   ├── DatabaseExtensions.cs
│       │   ├── AuthExtensions.cs
│       │   └── CorsExtensions.cs
│       │
│       └── Common/                           # Shared utilities
│           ├── Exceptions/
│           │   ├── NotFoundException.cs
│           │   ├── ConflictException.cs
│           │   └── ForbiddenException.cs
│           └── Constants.cs
│
├── tests/
│   └── YourApp.Tests/
│       ├── Controllers/
│       ├── Services/
│       └── Repositories/
│
├── YourApp.sln
└── .env
```

---

## ARCHITECTURAL LAYERS

```
Models/         → EF Core entity definitions ONLY. No logic.
DTOs/           → C# records for request/response. FluentValidation validators separately.
Data/           → DbContext + Configurations. No queries in entity config.
Repositories/   → All DB queries. Returns entities. No business rules.
Services/       → Business logic. Calls repositories. Throws custom exceptions.
Controllers/    → HTTP routing. Calls services. Returns ActionResult. No logic.
Validators/     → FluentValidation rules. One file per request DTO.
Middleware/     → Cross-cutting concerns (logging, exception handling).
Extensions/     → DI registration helpers. Keep Program.cs clean.
```

---

## LAYER 1 — `Models/` — EF Core Entities

```csharp
// Models/Common/BaseEntity.cs
namespace YourApp.Api.Models.Common;

public abstract class BaseEntity
{
    public Guid      Id        { get; private set; } = Guid.NewGuid();
    public DateTime  CreatedAt { get; private set; } = DateTime.UtcNow;
    public DateTime  UpdatedAt { get; set; }         = DateTime.UtcNow;
}
```

```csharp
// Models/User.cs
namespace YourApp.Api.Models;

using YourApp.Api.Models.Common;

public class User : BaseEntity
{
    public string  Email          { get; set; } = string.Empty;
    public string  HashedPassword { get; set; } = string.Empty;
    public string? FullName       { get; set; }
    public bool    IsActive       { get; set; } = true;
    public UserRole Role          { get; set; } = UserRole.Staff;

    public ICollection<Item> Items { get; set; } = new List<Item>();
}

public enum UserRole { Admin, Manager, Staff, Viewer }
```

```csharp
// Models/Item.cs
namespace YourApp.Api.Models;

using YourApp.Api.Models.Common;

public class Item : BaseEntity
{
    public string  Title       { get; set; } = string.Empty;
    public string? Description { get; set; }
    public Guid    OwnerId     { get; set; }
    public User    Owner       { get; set; } = null!;
}
```

**Entity Rules:**
- ALWAYS inherit `BaseEntity` — never define `Id`/`CreatedAt`/`UpdatedAt` per-entity
- `Id` setter is `private` — never allow external assignment
- Configuration (indexes, constraints) goes in `Data/Configurations/` — not here
- NEVER add business methods to entities

---

## LAYER 2 — `Data/` — EF Core Context + Configuration

```csharp
// Data/AppDbContext.cs
namespace YourApp.Api.Data;

using Microsoft.EntityFrameworkCore;
using YourApp.Api.Models;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<User> Users { get; set; }
    public DbSet<Item> Items { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
        base.OnModelCreating(modelBuilder);
    }

    public override Task<int> SaveChangesAsync(CancellationToken ct = default)
    {
        // Auto-update UpdatedAt on every save
        foreach (var entry in ChangeTracker.Entries<BaseEntity>()
                 .Where(e => e.State == EntityState.Modified))
        {
            entry.Entity.UpdatedAt = DateTime.UtcNow;
        }
        return base.SaveChangesAsync(ct);
    }
}
```

```csharp
// Data/Configurations/UserConfiguration.cs
namespace YourApp.Api.Data.Configurations;

using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using YourApp.Api.Models;

public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.ToTable("users");

        builder.HasKey(u => u.Id);
        builder.Property(u => u.Id).ValueGeneratedNever();

        builder.Property(u => u.Email)
               .IsRequired().HasMaxLength(255);
        builder.HasIndex(u => u.Email).IsUnique();

        builder.Property(u => u.HashedPassword).IsRequired().HasMaxLength(255);
        builder.Property(u => u.FullName).HasMaxLength(255);
        builder.Property(u => u.Role).HasConversion<string>().HasMaxLength(50);

        builder.Property(u => u.CreatedAt).IsRequired();
        builder.Property(u => u.UpdatedAt).IsRequired();

        builder.HasMany(u => u.Items)
               .WithOne(i => i.Owner)
               .HasForeignKey(i => i.OwnerId)
               .OnDelete(DeleteBehavior.Cascade);
    }
}
```

---

## LAYER 3 — `DTOs/` — C# Records

```csharp
// DTOs/Users/CreateUserRequest.cs
namespace YourApp.Api.DTOs.Users;

public record CreateUserRequest(
    string Email,
    string FullName,
    string Password,
    string Role = "Staff"
);
```

```csharp
// DTOs/Users/UpdateUserRequest.cs
namespace YourApp.Api.DTOs.Users;

public record UpdateUserRequest(
    string?  Email     = null,
    string?  FullName  = null,
    string?  Password  = null,
    bool?    IsActive  = null
);
```

```csharp
// DTOs/Users/UserResponse.cs
namespace YourApp.Api.DTOs.Users;

public record UserResponse(
    Guid     Id,
    string   Email,
    string?  FullName,
    bool     IsActive,
    string   Role,
    DateTime CreatedAt,
    DateTime UpdatedAt
    // HashedPassword is NEVER included
);
```

```csharp
// DTOs/Common/PagedResponse.cs
namespace YourApp.Api.DTOs.Common;

public record PagedResponse<T>(
    IEnumerable<T> Items,
    int Total,
    int Page,
    int Size,
    int Pages
)
{
    public static PagedResponse<T> Create(IEnumerable<T> items, int total, int page, int size)
        => new(items, total, page, size, (int)Math.Ceiling((double)total / size));
}
```

```csharp
// DTOs/Common/ApiError.cs
namespace YourApp.Api.DTOs.Common;

public record ApiError(int StatusCode, string Message, DateTime Timestamp);
```

---

## LAYER 4 — `Validators/` — FluentValidation

```csharp
// Validators/CreateUserRequestValidator.cs
namespace YourApp.Api.Validators;

using FluentValidation;
using YourApp.Api.DTOs.Users;

public class CreateUserRequestValidator : AbstractValidator<CreateUserRequest>
{
    public CreateUserRequestValidator()
    {
        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required.")
            .EmailAddress().WithMessage("Invalid email address.");

        RuleFor(x => x.FullName)
            .NotEmpty()
            .MinimumLength(2).WithMessage("Name must be at least 2 characters.")
            .MaximumLength(100);

        RuleFor(x => x.Password)
            .NotEmpty()
            .MinimumLength(8).WithMessage("Password must be at least 8 characters.")
            .MaximumLength(128)
            .Matches("[A-Z]").WithMessage("Must contain an uppercase letter.")
            .Matches("[0-9]").WithMessage("Must contain a number.");

        RuleFor(x => x.Role)
            .Must(r => new[] { "Admin", "Manager", "Staff", "Viewer" }.Contains(r))
            .WithMessage("Invalid role.");
    }
}
```

---

## LAYER 5 — `Repositories/` — Data Access

```csharp
// Repositories/Interfaces/IUserRepository.cs
namespace YourApp.Api.Repositories.Interfaces;

using YourApp.Api.Models;

public interface IUserRepository
{
    Task<User?>           GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<User?>           GetByEmailAsync(string email, CancellationToken ct = default);
    Task<bool>            ExistsByEmailAsync(string email, CancellationToken ct = default);
    Task<(List<User> Items, int Total)> GetPagedAsync(int page, int size, CancellationToken ct = default);
    Task<User>            AddAsync(User user, CancellationToken ct = default);
    Task<User>            UpdateAsync(User user, CancellationToken ct = default);
    Task                  DeleteAsync(User user, CancellationToken ct = default);
}
```

```csharp
// Repositories/UserRepository.cs
namespace YourApp.Api.Repositories;

using Microsoft.EntityFrameworkCore;
using YourApp.Api.Data;
using YourApp.Api.Models;
using YourApp.Api.Repositories.Interfaces;

public class UserRepository(AppDbContext db) : IUserRepository
{
    public Task<User?> GetByIdAsync(Guid id, CancellationToken ct = default)
        => db.Users.FirstOrDefaultAsync(u => u.Id == id, ct);

    public Task<User?> GetByEmailAsync(string email, CancellationToken ct = default)
        => db.Users.FirstOrDefaultAsync(u => u.Email == email, ct);

    public Task<bool> ExistsByEmailAsync(string email, CancellationToken ct = default)
        => db.Users.AnyAsync(u => u.Email == email, ct);

    public async Task<(List<User> Items, int Total)> GetPagedAsync(
        int page, int size, CancellationToken ct = default)
    {
        var query = db.Users.Where(u => u.IsActive).OrderBy(u => u.CreatedAt);
        var total = await query.CountAsync(ct);
        var items = await query.Skip((page - 1) * size).Take(size).ToListAsync(ct);
        return (items, total);
    }

    public async Task<User> AddAsync(User user, CancellationToken ct = default)
    {
        db.Users.Add(user);
        await db.SaveChangesAsync(ct);
        return user;
    }

    public async Task<User> UpdateAsync(User user, CancellationToken ct = default)
    {
        db.Users.Update(user);
        await db.SaveChangesAsync(ct);
        return user;
    }

    public async Task DeleteAsync(User user, CancellationToken ct = default)
    {
        db.Users.Remove(user);
        await db.SaveChangesAsync(ct);
    }
}
```

**Repository Rules:**
- ALWAYS define interface + implementation — controllers and services use the interface
- NEVER put business logic in repositories — only queries
- Use `CancellationToken` on every async method
- NEVER call `SaveChangesAsync` in service — repositories own persistence

---

## LAYER 6 — `Services/` — Business Logic

```csharp
// Services/UserService.cs
namespace YourApp.Api.Services;

using Mapster;
using Microsoft.AspNetCore.Identity;
using YourApp.Api.Common.Exceptions;
using YourApp.Api.DTOs.Common;
using YourApp.Api.DTOs.Users;
using YourApp.Api.Models;
using YourApp.Api.Repositories.Interfaces;
using YourApp.Api.Services.Interfaces;

public class UserService(IUserRepository userRepository, IPasswordHasher<User> passwordHasher)
    : IUserService
{
    public async Task<UserResponse> CreateUserAsync(
        CreateUserRequest request, CancellationToken ct = default)
    {
        if (await userRepository.ExistsByEmailAsync(request.Email, ct))
            throw new ConflictException("A user with this email already exists.");

        var user = request.Adapt<User>();
        user.HashedPassword = passwordHasher.HashPassword(user, request.Password);

        return (await userRepository.AddAsync(user, ct)).Adapt<UserResponse>();
    }

    public async Task<PagedResponse<UserResponse>> GetUsersAsync(
        int page, int size, CancellationToken ct = default)
    {
        var (items, total) = await userRepository.GetPagedAsync(page, size, ct);
        return PagedResponse<UserResponse>.Create(
            items.Adapt<List<UserResponse>>(), total, page, size);
    }

    public async Task<UserResponse> GetUserByIdAsync(Guid id, CancellationToken ct = default)
    {
        var user = await userRepository.GetByIdAsync(id, ct)
            ?? throw new NotFoundException($"User {id} not found.");
        return user.Adapt<UserResponse>();
    }

    public async Task<UserResponse> UpdateUserAsync(
        Guid id, UpdateUserRequest request, CancellationToken ct = default)
    {
        var user = await userRepository.GetByIdAsync(id, ct)
            ?? throw new NotFoundException($"User {id} not found.");

        if (request.Email is not null)     user.Email    = request.Email;
        if (request.FullName is not null)  user.FullName = request.FullName;
        if (request.IsActive is not null)  user.IsActive = request.IsActive.Value;
        if (request.Password is not null)
            user.HashedPassword = passwordHasher.HashPassword(user, request.Password);

        return (await userRepository.UpdateAsync(user, ct)).Adapt<UserResponse>();
    }

    public async Task DeleteUserAsync(Guid id, CancellationToken ct = default)
    {
        var user = await userRepository.GetByIdAsync(id, ct)
            ?? throw new NotFoundException($"User {id} not found.");
        await userRepository.DeleteAsync(user, ct);
    }
}
```

---

## LAYER 7 — `Controllers/` — REST Endpoints

```csharp
// Controllers/UsersController.cs
namespace YourApp.Api.Controllers;

using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using YourApp.Api.DTOs.Common;
using YourApp.Api.DTOs.Users;
using YourApp.Api.Services.Interfaces;

[ApiController]
[Route("api/v1/users")]
[Authorize]
public class UsersController(IUserService userService) : ControllerBase
{
    [HttpPost]
    [Authorize(Roles = "Admin")]
    [ProducesResponseType(typeof(UserResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ApiError), StatusCodes.Status409Conflict)]
    public async Task<ActionResult<UserResponse>> CreateUser(
        CreateUserRequest request,
        CancellationToken ct)
    {
        var result = await userService.CreateUserAsync(request, ct);
        return CreatedAtAction(nameof(GetUserById), new { id = result.Id }, result);
    }

    [HttpGet]
    [Authorize(Roles = "Admin,Manager")]
    [ProducesResponseType(typeof(PagedResponse<UserResponse>), StatusCodes.Status200OK)]
    public async Task<ActionResult<PagedResponse<UserResponse>>> GetUsers(
        [FromQuery] int page = 1,
        [FromQuery] int size = 20,
        CancellationToken ct = default)
        => Ok(await userService.GetUsersAsync(page, size, ct));

    [HttpGet("{id:guid}")]
    [ProducesResponseType(typeof(UserResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ApiError), StatusCodes.Status404NotFound)]
    public async Task<ActionResult<UserResponse>> GetUserById(Guid id, CancellationToken ct)
        => Ok(await userService.GetUserByIdAsync(id, ct));

    [HttpPatch("{id:guid}")]
    [ProducesResponseType(typeof(UserResponse), StatusCodes.Status200OK)]
    public async Task<ActionResult<UserResponse>> UpdateUser(
        Guid id, UpdateUserRequest request, CancellationToken ct)
        => Ok(await userService.UpdateUserAsync(id, request, ct));

    [HttpDelete("{id:guid}")]
    [Authorize(Roles = "Admin")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    public async Task<IActionResult> DeleteUser(Guid id, CancellationToken ct)
    {
        await userService.DeleteUserAsync(id, ct);
        return NoContent();
    }
}
```

---

## LAYER 8 — `Middleware/` — Exception Handling

```csharp
// Middleware/ExceptionHandlingMiddleware.cs
namespace YourApp.Api.Middleware;

using System.Text.Json;
using YourApp.Api.Common.Exceptions;
using YourApp.Api.DTOs.Common;

public class ExceptionHandlingMiddleware(RequestDelegate next, ILogger<ExceptionHandlingMiddleware> logger)
{
    public async Task InvokeAsync(HttpContext context)
    {
        try { await next(context); }
        catch (Exception ex)
        {
            logger.LogError(ex, "Unhandled exception for {Method} {Path}",
                context.Request.Method, context.Request.Path);
            await HandleExceptionAsync(context, ex);
        }
    }

    private static Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        var (statusCode, message) = exception switch
        {
            NotFoundException  e => (StatusCodes.Status404NotFound,    e.Message),
            ConflictException  e => (StatusCodes.Status409Conflict,    e.Message),
            ForbiddenException e => (StatusCodes.Status403Forbidden,   e.Message),
            _                    => (StatusCodes.Status500InternalServerError,
                                    "An internal error occurred.")     // never expose details
        };

        context.Response.StatusCode  = statusCode;
        context.Response.ContentType = "application/json";

        var error = new ApiError(statusCode, message, DateTime.UtcNow);
        return context.Response.WriteAsync(JsonSerializer.Serialize(error,
            new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase }));
    }
}
```

---

## LAYER 9 — `Program.cs`

```csharp
// Program.cs
using YourApp.Api.Data;
using YourApp.Api.Extensions;
using YourApp.Api.Middleware;
using YourApp.Api.Repositories;
using YourApp.Api.Repositories.Interfaces;
using YourApp.Api.Services;
using YourApp.Api.Services.Interfaces;
using FluentValidation;
using FluentValidation.AspNetCore;
using Microsoft.EntityFrameworkCore;
using Mapster;

var builder = WebApplication.CreateBuilder(args);

// ── Database ──────────────────────────────────────────────────────────
builder.Services.AddDbContext<AppDbContext>(opts =>
    opts.UseNpgsql(builder.Configuration.GetConnectionString("Default"))
        .UseSnakeCaseNamingConvention());

// ── Repositories ──────────────────────────────────────────────────────
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IItemRepository, ItemRepository>();

// ── Services ──────────────────────────────────────────────────────────
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IItemService, ItemService>();

// ── Validation ────────────────────────────────────────────────────────
builder.Services.AddFluentValidationAutoValidation();
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

// ── Auth + CORS ────────────────────────────────────────────────────────
builder.Services.AddAuthExtensions(builder.Configuration);
builder.Services.AddCorsExtensions(builder.Configuration);

// ── Controllers ────────────────────────────────────────────────────────
builder.Services.AddControllers();

// ── Swagger (dev only) ─────────────────────────────────────────────────
if (builder.Environment.IsDevelopment())
{
    builder.Services.AddEndpointsApiExplorer();
    builder.Services.AddSwaggerGen();
}

var app = builder.Build();

// ── Middleware pipeline (ORDER MATTERS) ────────────────────────────────
app.UseMiddleware<ExceptionHandlingMiddleware>();   // outermost
app.UseMiddleware<RequestLoggingMiddleware>();
app.UseCors("AllowFrontend");
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapControllers();

// ── Run migrations on startup (optional — or use CLI) ─────────────────
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    await db.Database.MigrateAsync();
}

app.Run();
```

---

## LAYER 10 — `appsettings.json`

```json
{
  "ConnectionStrings": {
    "Default": "Host=127.0.0.1;Database=myapp;Username=appuser;Password=changeme"
  },
  "Jwt": {
    "Secret":            "REPLACE_IN_ENV",
    "Issuer":            "YourApp",
    "Audience":          "YourApp",
    "ExpirationMinutes": 30
  },
  "Cors": {
    "AllowedOrigins": ["http://localhost:3000"]
  },
  "Logging": {
    "LogLevel": {
      "Default":                           "Warning",
      "Microsoft.EntityFrameworkCore":     "Warning"
    }
  }
}
```

> **IMPORTANT — How to override with real secrets in production:**
> ASP.NET Core does NOT support `${ENV_VAR}` syntax in JSON files.
> Use environment variables with the double-underscore (`__`) separator instead:
>
> ```bash
> # Linux / Docker environment variables
> ConnectionStrings__Default="Host=db;Database=prod;Username=user;Password=secret"
> Jwt__Secret="your-long-random-jwt-secret"
> Cors__AllowedOrigins__0="https://app.yourdomain.com"
> ```
>
> Or use `.env` file + `DotNetEnv` package, or ASP.NET User Secrets in development:
> ```bash
> dotnet user-secrets set "Jwt:Secret" "your-dev-secret"
> dotnet user-secrets set "ConnectionStrings:Default" "Host=127.0.0.1;..."
> ```

```json
// appsettings.Production.json
{
  "Logging": {
    "LogLevel": { "Default": "Error" }
  },
  "DetailedErrors": false,
  "ShowSwagger":    false
}
```

---

## LAYER 11 — Request Signature Verification Middleware

```csharp
// Middleware/RequestSigningMiddleware.cs
using System.Security.Cryptography;
using System.Text;
using YourApp.Api.DTOs.Common;
using System.Text.Json;

public class RequestSigningMiddleware(RequestDelegate next, IConfiguration config)
{
    private static readonly HashSet<string> _exempt = new() { "/api/v1/auth/login", "/api/v1/auth/register", "/health" };
    private const int MaxAgeSeconds = 300;

    public async Task InvokeAsync(HttpContext context)
    {
        var path = context.Request.Path.Value ?? "";
        if (_exempt.Any(e => path.StartsWith(e))) { await next(context); return; }

        var timestamp = context.Request.Headers["X-Timestamp"].FirstOrDefault();
        var signature = context.Request.Headers["X-Signature"].FirstOrDefault();

        if (string.IsNullOrEmpty(timestamp) || string.IsNullOrEmpty(signature))
        {
            context.Response.StatusCode  = 401;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsync(JsonSerializer.Serialize(
                new ApiError(401, "Missing signature headers.", DateTime.UtcNow)));
            return;
        }

        if (!long.TryParse(timestamp, out var ts) ||
            Math.Abs(DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() - ts) > MaxAgeSeconds * 1000)
        {
            context.Response.StatusCode = 401;
            await context.Response.WriteAsync(JsonSerializer.Serialize(
                new ApiError(401, "Request expired.", DateTime.UtcNow)));
            return;
        }

        // Read body for signing
        context.Request.EnableBuffering();
        var body = await new StreamReader(context.Request.Body, leaveOpen: true).ReadToEndAsync();
        context.Request.Body.Position = 0;

        var secret  = config["Security:SigningSecret"] ?? "";
        var message = $"{timestamp}{context.Request.Method.ToUpper()}{path}{body}";
        var expected = ComputeHmac(secret, message);

        if (!CryptographicOperations.FixedTimeEquals(
                Encoding.UTF8.GetBytes(expected),
                Encoding.UTF8.GetBytes(signature)))
        {
            context.Response.StatusCode = 401;
            await context.Response.WriteAsync(JsonSerializer.Serialize(
                new ApiError(401, "Invalid request signature.", DateTime.UtcNow)));
            return;
        }

        await next(context);
    }

    private static string ComputeHmac(string secret, string message)
    {
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret));
        return Convert.ToHexString(hmac.ComputeHash(Encoding.UTF8.GetBytes(message))).ToLower();
    }
}
```

Add to `Program.cs` middleware pipeline after `RequestLoggingMiddleware`:
```csharp
app.UseMiddleware<RequestSigningMiddleware>();
```

Add to `appsettings.json`:
```json
"Security": { "SigningSecret": "REPLACE_IN_ENV" }
```

---

## NAMING CONVENTIONS

| What | Convention | Example |
|------|-----------|---------|
| Classes / Records | `PascalCase` | `UserService`, `CreateUserRequest` |
| Methods | `PascalCase` + `Async` suffix | `CreateUserAsync()` |
| Properties | `PascalCase` | `HashedPassword`, `CreatedAt` |
| Private fields | `_camelCase` | `_userRepository` |
| Interfaces | `I` prefix | `IUserService`, `IUserRepository` |
| DTOs | `{Action}{Resource}Request` / `{Resource}Response` | `CreateUserRequest`, `UserResponse` |
| Entities | `PascalCase` singular | `User`, `Item` |
| Table names | `snake_case` plural (via EF config) | `users`, `items` |
| Routes | `/api/v1/{resource}` lowercase | `/api/v1/users` |
| Enums | `PascalCase` | `UserRole.Admin` |

---

## WHEN ADDING A NEW RESOURCE

```
STEP 1   Models/{Resource}.cs                    → EF Core entity extending BaseEntity
STEP 2   Data/Configurations/{Resource}Configuration.cs → IEntityTypeConfiguration
STEP 3   Data/AppDbContext.cs                    → add DbSet<{Resource}>
STEP 4   DTOs/{Resources}/Create{Resource}Request.cs
         DTOs/{Resources}/Update{Resource}Request.cs
         DTOs/{Resources}/{Resource}Response.cs
STEP 5   Validators/Create{Resource}RequestValidator.cs
STEP 6   Repositories/Interfaces/I{Resource}Repository.cs
         Repositories/{Resource}Repository.cs
STEP 7   Services/Interfaces/I{Resource}Service.cs
         Services/{Resource}Service.cs
STEP 8   Controllers/{Resources}Controller.cs
STEP 9   Program.cs                              → register new repository + service
STEP 10  dotnet ef migrations add Add{Resource}Table
         dotnet ef database update
```

---

## ABSOLUTE PROHIBITIONS

```
✗  Business logic in controllers — service only
✗  DbContext injected directly in controllers or services — repositories only
✗  SaveChangesAsync called in services — repositories own persistence
✗  HashedPassword in any Response DTO
✗  No interface for service or repository — always define the interface
✗  CancellationToken omitted from async methods
✗  CORS AllowAnyOrigin() in production
✗  JWT secret hardcoded — always from configuration
✗  Swagger/OpenAPI enabled in production
✗  Exception details exposed in production error responses
✗  Manual field mapping — always Mapster/AutoMapper
✗  Synchronous EF Core calls (ToList(), First(), etc.) — always async
✗  EnsureCreated() or Database.EnsureDeleted() in production — migrations only
```

---

## PRE-COMPLETION CHECKLIST

```
[ ] Entity inherits BaseEntity — no manual Id/timestamps
[ ] Entity configuration in IEntityTypeConfiguration — not in OnModelCreating directly
[ ] DTOs are C# records — no classes with properties
[ ] FluentValidation validator created for every Create/Update request
[ ] Repository interface defined + registered in Program.cs
[ ] Service interface defined + registered in Program.cs
[ ] CancellationToken passed through all async methods
[ ] HashedPassword never in any Response DTO
[ ] Passwords hashed in service — never in controller or repository
[ ] ExceptionHandlingMiddleware returns generic message in production
[ ] CORS AllowedOrigins set to specific list — never AllowAnyOrigin()
[ ] EF Core migration created: dotnet ef migrations add
[ ] appsettings.Production.json hides Swagger
[ ] All async methods use await — no .Result or .Wait()
```

---

*Stack: ASP.NET Core 9 · C# 13 · Entity Framework Core 9 · PostgreSQL · FluentValidation · Mapster · JWT Bearer*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
