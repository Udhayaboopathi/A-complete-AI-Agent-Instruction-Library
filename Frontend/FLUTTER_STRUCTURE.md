# AGENT INSTRUCTIONS — Flutter (Multi-Platform)

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `FLUTTER_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> This file is the single source of truth. No exceptions.

---

## YOUR IDENTITY

You are a senior Flutter engineer building enterprise-grade multi-platform apps.
This app connects to a REST API backend — FastAPI, ASP.NET Core, or Spring Boot.
Targets: **Mobile (iOS + Android) primarily, Desktop (Windows/macOS/Linux), Web when needed.**
Every file you generate MUST follow the exact structure, patterns, and rules in this document.

---

## TECH STACK — USE EXACTLY THESE

```
Framework      : Flutter 3.x           (stable channel)
Language       : Dart 3.x              (records, pattern matching, null safety)
State          : Riverpod 2.x          + riverpod_generator (code gen)
Navigation     : GoRouter 14.x         (web-compatible, deep links, auth guards)
HTTP Client    : Dio 5.x               (interceptors — same pattern as Axios)
Models         : Freezed 2.x           + json_serializable (immutable, copyWith, toJson)
Secure Storage : flutter_secure_storage (tokens — NOT SharedPreferences)
Preferences    : shared_preferences    (non-sensitive UI prefs only)
Forms          : reactive_forms        (FormGroup, FormControl + validators)
Adaptive UI    : flutter_adaptive_scaffold (responsive: mobile/tablet/desktop)
Icons          : lucide_flutter        (consistent with web frontends)
Dates          : intl                  (DateFormat, NumberFormat)
Environment    : flutter_dotenv        (.env file support)
```

---

## MANDATORY FOLDER STRUCTURE

```
lib/
│
├── main.dart                                  # App entry — loads env, runs app
│
├── app/
│   ├── app.dart                               # MaterialApp.router — root widget
│   └── app_theme.dart                         # ThemeData light + dark
│
├── core/                                      # Infrastructure — no UI
│   │
│   ├── api/
│   │   ├── api_client.dart                    # Dio instance + all interceptors
│   │   ├── endpoints.dart                     # ALL backend URL strings
│   │   └── adapters.dart                      # Normalize FastAPI/ASP.NET/Spring responses
│   │
│   ├── auth/
│   │   ├── token_storage.dart                 # flutter_secure_storage wrapper
│   │   └── auth_service.dart                  # login / logout / refresh
│   │
│   ├── router/
│   │   ├── app_router.dart                    # GoRouter config + auth redirect
│   │   └── app_routes.dart                    # Route name constants
│   │
│   ├── env/
│   │   └── app_env.dart                       # Environment variable accessors
│   │
│   ├── providers/
│   │   └── core_providers.dart                # Riverpod providers for core services
│   │
│   └── utils/
│       ├── formatters.dart                    # formatDate, formatCurrency, formatBytes
│       ├── validators.dart                    # Reusable form validators
│       └── constants.dart                     # App-wide constants
│
├── shared/                                    # Reusable UI — zero business logic
│   │
│   ├── widgets/                               # Primitive building blocks
│   │   ├── app_button.dart
│   │   ├── app_text_field.dart
│   │   ├── app_card.dart
│   │   ├── app_badge.dart
│   │   ├── data_table_widget.dart             # Generic reusable table
│   │   ├── loading_widget.dart
│   │   ├── error_view.dart
│   │   ├── empty_state.dart
│   │   └── confirm_dialog.dart
│   │
│   └── layouts/
│       ├── app_shell.dart                     # Navigation shell (adaptive)
│       ├── adaptive_layout.dart               # Mobile/Tablet/Desktop breakpoints
│       ├── page_header.dart
│       └── sidebar.dart                       # Desktop persistent sidebar
│
└── features/                                  # ONE FOLDER PER FEATURE
    └── {feature}/
        │
        ├── data/
        │   ├── {feature}_repository.dart      # All API calls for this feature
        │   └── models/
        │       ├── {feature}.dart             # @freezed model + fromJson/toJson
        │       ├── {feature}.freezed.dart     # GENERATED — never edit
        │       └── {feature}.g.dart           # GENERATED — never edit
        │
        ├── providers/
        │   ├── {feature}_provider.dart        # @riverpod providers
        │   └── {feature}_provider.g.dart      # GENERATED — never edit
        │
        └── screens/
            ├── {feature}_list_screen.dart     # List/index screen
            └── {feature}_detail_screen.dart   # Detail screen
```

---

## COMPONENT VISIBILITY RULES

```
┌─────────────────────────────────────────────────────────────────┐
│  shared/widgets/         usable by: EVERYONE                    │
│  shared/layouts/         usable by: EVERYONE                    │
│  features/{x}/screens/   usable by: ONLY screens inside {x}/   │
│  features/{x}/data/      usable by: ONLY providers inside {x}/ │
└─────────────────────────────────────────────────────────────────┘

One feature CANNOT import another feature's screens, models, or repository.
If a widget is needed in 2+ features → move it to shared/widgets/.
```

---

## THE 3 LAWS

```
LAW 1 — screens/ are UI ONLY
  Screen widgets call providers and render state.
  Zero direct API calls. Zero business logic. Zero repository imports.

LAW 2 — data/ is API ONLY
  Repository classes make HTTP calls. Return domain models.
  No Flutter widgets. No BuildContext. No Riverpod refs.

LAW 3 — core/ is INFRASTRUCTURE ONLY
  No feature-specific logic. No widgets.
  Usable from any feature without circular imports.
```

---

## LAYER 1 — `main.dart`

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app/app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");

  runApp(
    const ProviderScope(     // ← wraps entire app — Riverpod requires this
      child: App(),
    ),
  );
}
```

---

## LAYER 2 — `app/app.dart`

```dart
// lib/app/app.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/router/app_router.dart';
import 'app_theme.dart';

class App extends ConsumerWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title:             'AppName',
      debugShowCheckedModeBanner: false,
      theme:             AppTheme.light(),
      darkTheme:         AppTheme.dark(),
      themeMode:         ThemeMode.system,
      routerConfig:      router,
    );
  }
}
```

---

## LAYER 3 — `core/env/app_env.dart`

```dart
// lib/core/env/app_env.dart
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Single source of truth for all environment variables.
/// Never read dotenv.env[] outside of this class.
abstract class AppEnv {
  static String get apiUrl =>
      dotenv.env['API_URL'] ?? 'http://localhost:8000/api/v1';

  static String get backendType =>
      dotenv.env['BACKEND_TYPE'] ?? 'fastapi';

  static String get signingSecret =>
      dotenv.env['REQUEST_SIGNING_SECRET'] ?? '';

  static bool get isProduction =>
      dotenv.env['ENVIRONMENT'] == 'production';
}
```

```bash
# .env  (never commit)
API_URL=https://api.yourdomain.com/api/v1
BACKEND_TYPE=fastapi
REQUEST_SIGNING_SECRET=same-as-backend-signing-secret
ENVIRONMENT=production

# .env.example  (commit this)
API_URL=
BACKEND_TYPE=fastapi
REQUEST_SIGNING_SECRET=
ENVIRONMENT=development
```

---

## LAYER 3B — `core/providers/core_providers.dart` — Global Riverpod Providers

```dart
// lib/core/providers/core_providers.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:dio/dio.dart';
import '../api/api_client.dart';
import '../auth/auth_service.dart';

part 'core_providers.g.dart';

/// The single Dio instance used across the entire app.
/// All repositories watch this provider — never create Dio manually.
@riverpod
Dio dio(DioRef ref) => createApiClient();

/// The auth service — login, logout, refresh.
@riverpod
AuthService authService(AuthServiceRef ref) {
  return AuthService(ref.watch(dioProvider));
}
```

Run `dart run build_runner build` after adding this file to generate `core_providers.g.dart`.

---

## LAYER 4 — `core/api/api_client.dart` — Dio + Interceptors

```dart
// lib/core/api/api_client.dart
import 'dart:convert';                            // utf8.encode
import 'package:crypto/crypto.dart';              // Hmac, sha256
import 'package:dio/dio.dart';
import '../auth/token_storage.dart';
import '../env/app_env.dart';
import 'adapters.dart';

Dio createApiClient() {
  final dio = Dio(
    BaseOptions(
      baseUrl:         AppEnv.apiUrl,
      connectTimeout:  const Duration(seconds: 15),
      receiveTimeout:  const Duration(seconds: 15),
      sendTimeout:     const Duration(seconds: 15),
      headers: {
        'Content-Type': 'application/json',
        'Accept':       'application/json',
      },
    ),
  );

  dio.interceptors.addAll([
    _AuthInterceptor(),
    _SigningInterceptor(),
    _ErrorInterceptor(),
    if (!AppEnv.isProduction) LogInterceptor(responseBody: true),
  ]);

  return dio;
}

// ── Auth Interceptor ──────────────────────────────────────────────────────────
class _AuthInterceptor extends Interceptor {
  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await TokenStorage.getToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err.response?.statusCode == 401) {
      TokenStorage.clearToken();
      // Navigate to login — handled via GoRouter redirect
    }
    handler.next(err);
  }
}

// ── Request Signing Interceptor (HMAC-SHA256) ─────────────────────────────────
class _SigningInterceptor extends Interceptor {
  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final secret = AppEnv.signingSecret;
    if (secret.isEmpty) { handler.next(options); return; }

    final timestamp = DateTime.now().millisecondsSinceEpoch.toString();
    final method    = options.method.toUpperCase();
    final path      = Uri.parse(options.path).path;
    final body      = options.data != null ? options.data.toString() : '';
    final message   = '$timestamp$method$path$body';

    // HMAC-SHA256 using Dart crypto package
    final hmac = Hmac(sha256, utf8.encode(secret));
    final sig  = hmac.convert(utf8.encode(message)).toString();

    options.headers['X-Timestamp'] = timestamp;
    options.headers['X-Signature'] = sig;

    handler.next(options);
  }
}

// ── Error Interceptor ─────────────────────────────────────────────────────────
class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final message = ApiAdapters.normalizeError(err.response?.data);
    handler.next(
      err.copyWith(
        error: ApiException(message: message, statusCode: err.response?.statusCode),
      ),
    );
  }
}

class ApiException implements Exception {
  final String  message;
  final int?    statusCode;
  const ApiException({required this.message, this.statusCode});

  @override
  String toString() => message;
}
```

---

## LAYER 5 — `core/api/adapters.dart` — Backend-Agnostic

```dart
// lib/core/api/adapters.dart
import '../env/app_env.dart';

class PaginatedResponse<T> {
  final List<T> items;
  final int     total;
  final int     page;
  final int     size;

  const PaginatedResponse({
    required this.items,
    required this.total,
    required this.page,
    required this.size,
  });
}

abstract class ApiAdapters {
  /// Normalize paginated response from any backend.
  static PaginatedResponse<T> normalizePaginated<T>(
    Map<String, dynamic> raw,
    T Function(Map<String, dynamic>) fromJson,
  ) {
    switch (AppEnv.backendType) {
      case 'fastapi':
        return PaginatedResponse(
          items: (raw['items'] as List).map((e) => fromJson(e)).toList(),
          total: raw['total'] as int,
          page:  raw['page']  as int,
          size:  raw['size']  as int,
        );
      case 'aspnet':
        return PaginatedResponse(
          items: (raw['data'] as List).map((e) => fromJson(e)).toList(),
          total: raw['totalCount']  as int,
          page:  raw['pageNumber']  as int,
          size:  raw['pageSize']    as int,
        );
      case 'springboot':
        return PaginatedResponse(
          items: (raw['content'] as List).map((e) => fromJson(e)).toList(),
          total: raw['totalElements'] as int,
          page:  (raw['number'] as int) + 1,
          size:  raw['size']          as int,
        );
      default:
        throw Exception('Unknown backendType: ${AppEnv.backendType}');
    }
  }

  /// Extract error message from any backend error response.
  static String normalizeError(dynamic data) {
    if (data == null) return 'An unexpected error occurred.';
    if (data is Map) {
      if (data['detail'] is String)  return data['detail'] as String;
      if (data['message'] is String) return data['message'] as String;
      if (data['detail'] is List) {
        return (data['detail'] as List).first['msg'] as String? ??
               'Validation error.';
      }
    }
    return 'An unexpected error occurred.';
  }
}
```

---

## LAYER 5B — `core/auth/auth_service.dart` — Login, Logout, Refresh

```dart
// lib/core/auth/auth_service.dart
import 'package:dio/dio.dart';
import '../api/endpoints.dart';
import 'token_storage.dart';

class AuthService {
  final Dio _dio;
  AuthService(this._dio);

  Future<void> login({required String email, required String password}) async {
    final res = await _dio.post(Endpoints.auth.login, data: {
      'email': email, 'password': password,
    });
    final body = res.data as Map<String, dynamic>;
    final token   = body['access_token'] ?? body['accessToken'] ?? body['token'] as String;
    final refresh = body['refresh_token'] ?? body['refreshToken'] as String?;
    await TokenStorage.setToken(token, refresh: refresh);
  }

  Future<void> logout() async {
    await TokenStorage.clearToken();
  }

  /// Silent token refresh — call before token expires or on 401.
  Future<bool> refreshToken() async {
    final refresh = await TokenStorage.getRefresh();
    if (refresh == null) return false;
    try {
      final res = await _dio.post(
        Endpoints.auth.refresh,
        data:    {'refresh_token': refresh},
        options: Options(headers: {'Authorization': null}),   // no auth on refresh
      );
      final body     = res.data as Map<String, dynamic>;
      final newToken = body['access_token'] ?? body['accessToken'] ?? body['token'] as String;
      await TokenStorage.setToken(newToken);
      return true;
    } catch (_) {
      await TokenStorage.clearToken();
      return false;
    }
  }
}
```

Add silent refresh to `_AuthInterceptor` in `api_client.dart`:

```dart
// Inside _AuthInterceptor.onError — retry once after refresh
@override
void onError(DioException err, ErrorInterceptorHandler handler) async {
  if (err.response?.statusCode == 401) {
    // Try to refresh silently before giving up
    // (inject AuthService via a getter to avoid circular dependency)
    final refreshed = await _tryRefresh();
    if (refreshed) {
      // Retry the original request with new token
      final opts = err.requestOptions;
      opts.headers['Authorization'] = 'Bearer ${await TokenStorage.getToken()}';
      try {
        final retryRes = await _dio.fetch(opts);
        return handler.resolve(retryRes);
      } catch (_) {}
    }
    await TokenStorage.clearToken();
  }
  handler.next(err);
}
```

---

## LAYER 6 — `core/auth/token_storage.dart`

```dart
// lib/core/auth/token_storage.dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Stores JWT token in encrypted storage.
/// iOS:     Keychain (most secure)
/// Android: EncryptedSharedPreferences (AES-256 encrypted)
/// Desktop: OS credential store (Windows Credential Locker / macOS Keychain)
/// Web:     localStorage via flutter_secure_storage_web — NOT sessionStorage.
///          Web localStorage is NOT encrypted. For web production:
///          option A) use httpOnly cookies set by the backend (most secure)
///          option B) accept localStorage + rely on HTTPS + CSP headers
///
/// NEVER use plain SharedPreferences for tokens — not encrypted.
abstract class TokenStorage {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock_this_device,
    ),
  );

  static const _tokenKey   = 'access_token';
  static const _refreshKey = 'refresh_token';

  static Future<String?> getToken()   => _storage.read(key: _tokenKey);
  static Future<String?> getRefresh() => _storage.read(key: _refreshKey);

  static Future<void> setToken(String token, {String? refresh}) async {
    await _storage.write(key: _tokenKey, value: token);
    if (refresh != null) {
      await _storage.write(key: _refreshKey, value: refresh);
    }
  }

  static Future<void> clearToken() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _refreshKey);
  }

  static Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
}
```

---

## LAYER 7 — `core/router/app_router.dart` — GoRouter + Auth Guard

```dart
// lib/core/router/app_router.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/dashboard/screens/dashboard_screen.dart';   // ADD per feature
import '../../features/users/screens/users_list_screen.dart';
import '../../features/users/screens/user_detail_screen.dart';
import '../../shared/layouts/app_shell.dart';
import '../auth/token_storage.dart';
import 'app_routes.dart';

part 'app_router.g.dart';

@riverpod
GoRouter appRouter(AppRouterRef ref) {
  return GoRouter(
    initialLocation: AppRoutes.dashboard,
    debugLogDiagnostics: true,

    // ── Auth redirect ──────────────────────────────────────────────────
    redirect: (context, state) async {
      final loggedIn   = await TokenStorage.isLoggedIn();
      final onAuthPage = state.matchedLocation.startsWith('/login') ||
                         state.matchedLocation.startsWith('/register');

      if (!loggedIn && !onAuthPage) {
        return '/login?redirect=${Uri.encodeComponent(state.matchedLocation)}';
      }
      if (loggedIn && onAuthPage) {
        return AppRoutes.dashboard;
      }
      return null;
    },

    routes: [
      GoRoute(
        path:     '/login',
        builder:  (ctx, _) => const LoginScreen(),
      ),

      ShellRoute(
        builder: (ctx, state, child) => AppShell(child: child),
        routes: [
          GoRoute(
            path:    AppRoutes.dashboard,
            builder: (ctx, _) => const DashboardScreen(),
          ),
          GoRoute(
            path:    AppRoutes.users,
            builder: (ctx, _) => const UsersListScreen(),
            routes: [
              GoRoute(
                path:    ':id',
                builder: (ctx, state) =>
                    UserDetailScreen(userId: state.pathParameters['id']!),
              ),
            ],
          ),
          // Add new feature routes here following the same pattern
        ],
      ),
    ],
  );
}
```

```dart
// lib/core/router/app_routes.dart
abstract class AppRoutes {
  static const dashboard = '/dashboard';
  static const users     = '/users';
  static const items     = '/items';
  // Add new routes here — always add as a constant
}
```

---

## LAYER 8 — Feature Model with Freezed

```dart
// lib/features/users/data/models/user.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

enum UserRole { admin, manager, staff, viewer }

@freezed
class User with _$User {
  const factory User({
    required String   id,
    required String   email,
    String?           fullName,
    @Default(true)    bool     isActive,
    @Default(UserRole.staff) UserRole role,
    required DateTime createdAt,
    required DateTime updatedAt,
    // hashedPassword is NEVER in the model — backend never sends it
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

@freezed
class UserCreate with _$UserCreate {
  const factory UserCreate({
    required String email,
    required String fullName,
    required String password,
    @Default(UserRole.staff) UserRole role,
  }) = _UserCreate;

  Map<String, dynamic> toJson() => _$UserCreateToJson(this);
}

@freezed
class UserListParams with _$UserListParams {
  const factory UserListParams({
    @Default(0)  int    skip,
    @Default(20) int    limit,
    String?            search,
    UserRole?          role,
  }) = _UserListParams;
}
```

**Freezed Rules:**
- ALWAYS use `@freezed` for all data models — never plain Dart classes
- NEVER add `hashed_password` or any password field to models
- Run `dart run build_runner build` after every model change
- NEVER manually edit `.freezed.dart` or `.g.dart` files

---

## LAYER 9 — Feature Repository

```dart
// lib/features/users/data/users_repository.dart
import 'package:dio/dio.dart';
import '../../../core/api/adapters.dart';
import '../../../core/providers/core_providers.dart';
import 'models/user.dart';
import '../../../core/api/endpoints.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'users_repository.g.dart';

@riverpod
UsersRepository usersRepository(UsersRepositoryRef ref) {
  return UsersRepository(ref.watch(dioProvider));
}

class UsersRepository {
  final Dio _dio;
  UsersRepository(this._dio);

  Future<PaginatedResponse<User>> getUsers(UserListParams params) async {
    final res = await _dio.get(
      Endpoints.users.list,
      queryParameters: {
        if (params.skip  != 0)    'skip':   params.skip,
        if (params.limit != 20)   'limit':  params.limit,
        if (params.search != null)'search': params.search,
        if (params.role   != null)'role':   params.role!.name,
      },
    );
    return ApiAdapters.normalizePaginated<User>(
      res.data as Map<String, dynamic>,
      User.fromJson,
    );
  }

  Future<User> getUserById(String id) async {
    final res = await _dio.get(Endpoints.users.detail(id));
    return User.fromJson(res.data as Map<String, dynamic>);
  }

  Future<User> createUser(UserCreate data) async {
    final res = await _dio.post(Endpoints.users.create, data: data.toJson());
    return User.fromJson(res.data as Map<String, dynamic>);
  }

  Future<User> updateUser(String id, Map<String, dynamic> data) async {
    final res = await _dio.patch(Endpoints.users.update(id), data: data);
    return User.fromJson(res.data as Map<String, dynamic>);
  }

  Future<void> deleteUser(String id) async {
    await _dio.delete(Endpoints.users.delete(id));
  }
}
```

---

## LAYER 10 — Riverpod Providers

```dart
// lib/features/users/providers/users_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../data/users_repository.dart';
import '../data/models/user.dart';
import '../../../core/api/adapters.dart';

part 'users_provider.g.dart';

// ── List Provider ─────────────────────────────────────────────────────────────
@riverpod
Future<PaginatedResponse<User>> usersList(
  UsersListRef ref, {
  UserListParams params = const UserListParams(),
}) {
  return ref.watch(usersRepositoryProvider).getUsers(params);
}

// ── Detail Provider ───────────────────────────────────────────────────────────
@riverpod
Future<User> userDetail(UserDetailRef ref, String id) {
  return ref.watch(usersRepositoryProvider).getUserById(id);
}

// ── Mutation: Create ──────────────────────────────────────────────────────────
@riverpod
class CreateUserNotifier extends _$CreateUserNotifier {
  @override
  AsyncValue<User?> build() => const AsyncValue.data(null);

  Future<void> create(UserCreate data) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(
      () => ref.read(usersRepositoryProvider).createUser(data),
    );
    if (state.hasValue) {
      // Invalidate the list so it re-fetches with the new user
      ref.invalidate(usersListProvider);
    }
  }
}

// ── Mutation: Delete ──────────────────────────────────────────────────────────
@riverpod
class DeleteUserNotifier extends _$DeleteUserNotifier {
  @override
  AsyncValue<void> build() => const AsyncValue.data(null);

  Future<void> delete(String id) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(
      () => ref.read(usersRepositoryProvider).deleteUser(id),
    );
    if (!state.hasError) {
      ref.invalidate(usersListProvider);
    }
  }
}
```

---

## LAYER 11 — Feature Screen

```dart
// lib/features/users/screens/users_list_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../shared/widgets/loading_widget.dart';
import '../../../shared/widgets/error_view.dart';
import '../../../shared/widgets/empty_state.dart';
import '../../../shared/layouts/page_header.dart';
import '../providers/users_provider.dart';
import '../data/models/user.dart';

class UsersListScreen extends ConsumerWidget {
  const UsersListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersAsync = ref.watch(usersListProvider());

    return Scaffold(
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          PageHeader(
            title:       'Users',
            description: 'Manage system users.',
            action: FilledButton.icon(
              onPressed: () => context.push('/users/create'),
              icon:  const Icon(Icons.add),
              label: const Text('Add User'),
            ),
          ),
          Expanded(
            child: usersAsync.when(
              loading: () => const LoadingWidget(),
              error:   (err, _) => ErrorView(
                message: err.toString(),
                onRetry: () => ref.invalidate(usersListProvider),
              ),
              data: (response) => response.items.isEmpty
                ? const EmptyState(message: 'No users found.')
                : _UsersList(users: response.items),
            ),
          ),
        ],
      ),
    );
  }
}

class _UsersList extends StatelessWidget {
  final List<User> users;
  const _UsersList({required this.users});

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding:    const EdgeInsets.all(16),
      itemCount:  users.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final user = users[index];
        return ListTile(
          title:    Text(user.fullName ?? user.email),
          subtitle: Text(user.email),
          trailing: Chip(label: Text(user.role.name)),
          onTap:    () => context.push('/users/${user.id}'),
        );
      },
    );
  }
}
```

---

## LAYER 12 — Adaptive Layout (Mobile + Desktop)

```dart
// lib/shared/layouts/app_shell.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'sidebar.dart';

/// Adaptive shell:
/// Mobile  (<600px)  → BottomNavigationBar
/// Tablet  (<1200px) → NavigationRail
/// Desktop (≥1200px) → Persistent Sidebar
class AppShell extends StatelessWidget {
  final Widget child;
  const AppShell({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;

    if (width >= 1200) return _DesktopShell(child: child);
    if (width >= 600)  return _TabletShell(child: child);
    return _MobileShell(child: child);
  }
}

class _DesktopShell extends StatelessWidget {
  final Widget child;
  const _DesktopShell({required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          const Sidebar(),                          // persistent 260px sidebar
          const VerticalDivider(width: 1),
          Expanded(child: child),
        ],
      ),
    );
  }
}

class _TabletShell extends StatelessWidget {
  final Widget child;
  const _TabletShell({required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            destinations: _navDestinations,
            selectedIndex: _selectedIndex(context),
            onDestinationSelected: (i) => _navigate(context, i),
          ),
          const VerticalDivider(width: 1),
          Expanded(child: child),
        ],
      ),
    );
  }
}

class _MobileShell extends StatelessWidget {
  final Widget child;
  const _MobileShell({required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        destinations:    _navDestinations.map((d) => d.toNavigationDestination()).toList(),
        selectedIndex:   _selectedIndex(context),
        onDestinationSelected: (i) => _navigate(context, i),
      ),
    );
  }
}

// Navigation destinations — extend this list as you add features
const _navItems = [
  (label: 'Dashboard', icon: Icons.dashboard_outlined, selectedIcon: Icons.dashboard, path: '/dashboard'),
  (label: 'Users',     icon: Icons.people_outlined,   selectedIcon: Icons.people,    path: '/users'),
];

final _navDestinations = _navItems.map((item) =>
  NavigationDestination(icon: Icon(item.icon), selectedIcon: Icon(item.selectedIcon), label: item.label)
).toList();

int _selectedIndex(BuildContext context) {
  final location = GoRouterState.of(context).matchedLocation;
  if (location.startsWith('/users')) return 1;
  return 0;
}

void _navigate(BuildContext context, int index) {
  switch (index) {
    case 0: context.go('/dashboard'); break;
    case 1: context.go('/users');     break;
  }
}
```

---

## LAYER 13 — `core/api/endpoints.dart`

```dart
// lib/core/api/endpoints.dart
import '../env/app_env.dart';

abstract class Endpoints {
  static final auth = _AuthEndpoints();
  static final users = _CrudEndpoints('users');
  static final items = _CrudEndpoints('items');
  // Add: static final {feature} = _CrudEndpoints('{feature}');
}

class _AuthEndpoints {
  String get login   => '${AppEnv.apiUrl}/auth/login';
  String get me      => '${AppEnv.apiUrl}/auth/me';
  String get logout  => '${AppEnv.apiUrl}/auth/logout';
  String get refresh => '${AppEnv.apiUrl}/auth/refresh';
}

class _CrudEndpoints {
  final String _resource;
  _CrudEndpoints(this._resource);

  String get list   => '${AppEnv.apiUrl}/$_resource';
  String get create => '${AppEnv.apiUrl}/$_resource';
  String detail(String id) => '${AppEnv.apiUrl}/$_resource/$id';
  String update(String id) => '${AppEnv.apiUrl}/$_resource/$id';
  String delete(String id) => '${AppEnv.apiUrl}/$_resource/$id';
}
```

---

## LAYER 14 — `pubspec.yaml` Dependencies

```yaml
# pubspec.yaml
name: your_app_name
description: Enterprise Flutter app
publish_to: none

environment:
  sdk: ">=3.0.0 <4.0.0"
  flutter: ">=3.16.0"

dependencies:
  flutter:
    sdk: flutter

  # State management
  flutter_riverpod:        ^2.5.0
  riverpod_annotation:     ^2.3.0

  # Navigation
  go_router:               ^14.0.0

  # HTTP
  dio:                     ^5.4.0
  crypto:                  ^3.0.0     # HMAC-SHA256 signing

  # Models
  freezed_annotation:      ^2.4.0
  json_annotation:         ^4.9.0

  # Secure storage
  flutter_secure_storage:  ^9.0.0

  # Preferences (non-sensitive only)
  shared_preferences:      ^2.2.0

  # Forms
  reactive_forms:          ^17.0.0

  # Environment
  flutter_dotenv:          ^5.1.0

  # Utilities
  intl:                    ^0.19.0    # DateFormat, NumberFormat

dev_dependencies:
  flutter_test:
    sdk: flutter
  riverpod_generator:      ^2.4.0    # @riverpod code gen
  build_runner:            ^2.4.0
  freezed:                 ^2.5.0    # @freezed code gen
  json_serializable:       ^6.7.0    # fromJson/toJson code gen
  flutter_lints:           ^4.0.0
```

---

## NAMING CONVENTIONS

| What | Convention | Example |
|------|-----------|---------|
| Files | `snake_case.dart` | `users_repository.dart` |
| Classes | `PascalCase` | `UsersRepository`, `UserListScreen` |
| Freezed models | `PascalCase` | `User`, `UserCreate` |
| Providers | `camelCase` + `Provider` suffix | `usersListProvider` |
| Notifiers | `PascalCase` + `Notifier` | `CreateUserNotifier` |
| Screens | `{Feature}Screen` | `UsersListScreen` |
| Repositories | `{Feature}Repository` | `UsersRepository` |
| Route constants | `UPPER_SNAKE` in class | `AppRoutes.users` |
| Env vars | `UPPER_SNAKE_CASE` | `API_URL`, `BACKEND_TYPE` |
| Enum values | `camelCase` | `UserRole.admin` |

---

## WHEN ADDING A NEW FEATURE

```
STEP 1   lib/features/{feature}/data/models/{feature}.dart
         → @freezed model + fromJson + field comments
         → Run: dart run build_runner build

STEP 2   lib/core/api/endpoints.dart
         → add: static final {feature} = _CrudEndpoints('{feature}');

STEP 3   lib/features/{feature}/data/{feature}_repository.dart
         → @riverpod class using Dio + ApiAdapters.normalizePaginated

STEP 4   lib/features/{feature}/providers/{feature}_provider.dart
         → @riverpod list/detail queries + Notifier mutations
         → Run: dart run build_runner build

STEP 5   lib/features/{feature}/screens/{feature}_list_screen.dart
         → ConsumerWidget using ref.watch(provider)

STEP 6   lib/core/router/app_router.dart
         → add GoRoute for new feature

STEP 7   lib/core/router/app_routes.dart
         → add static const {feature} = '/{feature}';

STEP 8   lib/shared/layouts/app_shell.dart
         → add navigation item to _navDestinations

STEP 9   lib/core/env/app_env.dart
         → add new env vars if needed
```

---

## CODE GENERATION — RUN THESE AFTER EVERY MODEL CHANGE

```bash
# Generate all: freezed models + riverpod providers + json serializers
dart run build_runner build --delete-conflicting-outputs

# Watch mode during development (auto-regenerates on save)
dart run build_runner watch --delete-conflicting-outputs
```

**Generated files to NEVER edit:**
- `*.freezed.dart`
- `*.g.dart`

---

## BACKEND COMPATIBILITY

| | FastAPI | ASP.NET Core | Spring Boot |
|-|---------|-------------|-------------|
| `BACKEND_TYPE` | `fastapi` | `aspnet` | `springboot` |
| Token field | `access_token` | `token`/`accessToken` | `accessToken` |
| Paginated list | `items/total/page/size` | `data/totalCount/pageNumber/pageSize` | `content/totalElements/number/size` |
| Error field | `detail` | `message` | `message` |

**To switch backends:** change `BACKEND_TYPE` in `.env`. Only `adapters.dart` changes behavior.

---

## ABSOLUTE PROHIBITIONS

```
✗  Direct Dio calls in screen widgets — always through repository
✗  Token in SharedPreferences — always flutter_secure_storage
✗  Business logic in screens — providers and repositories only
✗  One feature importing another feature's models or repositories
✗  Hardcoded backend URLs — always use Endpoints.*
✗  Reading dotenv.env[] directly — always use AppEnv.*
✗  Editing *.freezed.dart or *.g.dart files manually
✗  Class-based state without Riverpod (setState for server state)
✗  Using SharedPreferences for access tokens
✗  Committing .env file — always .env.example only
✗  Navigator.push() — always context.go() (GoRouter)
✗  StatefulWidget for server state — ConsumerWidget + Riverpod
✗  Platform checks (if Platform.isAndroid) in feature code — use adaptive_layout
✗  401 handling in individual screens — interceptor handles it globally
✗  Multiple Dio instances — one instance via dioProvider
```

---

## PRE-COMPLETION CHECKLIST

```
[ ] dart run build_runner build run after model changes
[ ] No *.freezed.dart or *.g.dart edited manually
[ ] Token stored via TokenStorage — never SharedPreferences
[ ] New endpoints added to Endpoints class in endpoints.dart
[ ] New GoRoute added to app_router.dart
[ ] New nav item added to app_shell.dart
[ ] All URLs via Endpoints.* — no hardcoded strings
[ ] All env vars via AppEnv.* — no direct dotenv.env[] reads
[ ] ConsumerWidget used for screens that need Riverpod state
[ ] ref.invalidate() called after successful mutations
[ ] Adaptive layout handles mobile/tablet/desktop breakpoints
[ ] Error states handled with ErrorView widget
[ ] Loading states handled with LoadingWidget
[ ] Screen imports no other feature's files
```

---

## DATA FLOW

```
User taps "Create User"
  → UsersListScreen calls context.push('/users/create')
  → UserCreateScreen submits form
  → ref.read(createUserNotifierProvider.notifier).create(data)
  → CreateUserNotifier calls usersRepository.createUser(data)
  → Dio sends POST with auth token + HMAC signature
  → _AuthInterceptor injects Authorization header
  → _SigningInterceptor injects X-Timestamp + X-Signature
  → backend responds → _ErrorInterceptor normalizes on failure
  → notifier sets state = AsyncValue.data(newUser)
  → ref.invalidate(usersListProvider) → list re-fetches
  → SnackBar shown via state listener

User opens /users screen
  → GoRouter → auth redirect → TokenStorage.isLoggedIn()
  → Not logged in → redirect to /login
  → Logged in → UsersListScreen builds
  → ref.watch(usersListProvider()) fires
  → ApiAdapters.normalizePaginated → PaginatedResponse<User>
  → ListView renders users
```

---

*Flutter 3.x · Dart 3.x · Riverpod 2.x · GoRouter 14.x · Dio 5.x · Freezed 2.x*
*Targets: iOS · Android · Windows · macOS · Linux · Web*
*Works with: FastAPI · ASP.NET Core · Spring Boot*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
