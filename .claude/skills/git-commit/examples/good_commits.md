# 良いコミットメッセージの例

このドキュメントでは、Conventional Commits形式の優れたコミットメッセージの実例を紹介します。

## 目次
- [新機能追加 (feat)](#新機能追加-feat)
- [バグ修正 (fix)](#バグ修正-fix)
- [ドキュメント (docs)](#ドキュメント-docs)
- [リファクタリング (refactor)](#リファクタリング-refactor)
- [パフォーマンス (perf)](#パフォーマンス-perf)
- [テスト (test)](#テスト-test)
- [ビルド (build)](#ビルド-build)
- [CI/CD (ci)](#cicd-ci)
- [Breaking Changes](#breaking-changes)
- [マルチコミット推奨ケース](#マルチコミット推奨ケース)

---

## 新機能追加 (feat)

### 例1: 基本的な新機能
```
feat(auth): add OAuth2 login support

Implement OAuth2 authentication flow with Google and GitHub providers.
Includes token refresh mechanism and session management.

Closes #123
```

### 例2: スコープなし新機能
```
feat: add dark mode toggle

Allow users to switch between light and dark themes.
Theme preference is saved to localStorage.
```

### 例3: 複雑な新機能
```
feat(api): add GraphQL subscription support

Implement real-time data updates using WebSocket connections.
- Add GraphQL subscription schema definitions
- Implement PubSub mechanism with Redis
- Add client-side subscription hooks

Performance: 1000 concurrent connections tested successfully.

Closes #456
Refs #457
```

---

## バグ修正 (fix)

### 例1: クリティカルバグ
```
fix(api): handle null response in user endpoint

Previously, the endpoint would crash when receiving a null user object
from the database. Now returns a 404 status with appropriate error message.

Fixes #789
```

### 例2: エッジケース対応
```
fix(ui): prevent double form submission

Add debouncing to submit button to prevent duplicate API calls.
Includes loading state indicator during submission.
```

### 例3: セキュリティ修正
```
fix(auth): patch XSS vulnerability in comment system

Sanitize user input before rendering to prevent script injection.
All user-generated content is now escaped properly.

Security: CVE-2024-12345
```

---

## ドキュメント (docs)

### 例1: 基本的なドキュメント更新
```
docs: update installation guide for Python 3.11

Add instructions for installing with uv and pip.
Remove outdated Python 3.8 references.
```

### 例2: API ドキュメント
```
docs(api): add OpenAPI specification

Generate OpenAPI 3.0 spec from code annotations.
Includes interactive Swagger UI at /api/docs.
```

### 例3: チュートリアル追加
```
docs: add getting started tutorial

Create step-by-step guide for new users covering:
- Installation
- Basic configuration
- First API call
- Common troubleshooting
```

---

## リファクタリング (refactor)

### 例1: コード整理
```
refactor(core): extract common utility functions

Move repeated validation logic to shared utils module.
No behavior changes, purely organizational.
```

### 例2: アーキテクチャ改善
```
refactor(db): migrate from ORM to query builder

Improve query performance by using direct SQL queries.
- Replace 20 ORM calls with 3 optimized queries
- Reduce average response time from 500ms to 50ms

Breaking: Database schema migration required.
```

### 例3: ファイル構造変更
```
refactor: reorganize project structure

Move components to feature-based folders instead of type-based.
Update all import statements accordingly.
```

---

## パフォーマンス (perf)

### 例1: データベース最適化
```
perf(db): add indexes to user queries

Add composite index on (email, created_at) columns.
Reduces query time from 2s to 50ms for user lookup.
```

### 例2: フロントエンド最適化
```
perf(ui): implement virtual scrolling for large lists

Replace naive rendering with react-window.
Can now handle 10,000+ items without performance degradation.
```

### 例3: バンドルサイズ削減
```
perf(build): reduce bundle size by 40%

- Replace moment.js with date-fns
- Enable tree shaking for lodash
- Lazy load admin panel components

Before: 450KB, After: 270KB (minified + gzipped)
```

---

## テスト (test)

### 例1: ユニットテスト追加
```
test(auth): add unit tests for JWT validation

Cover success, expiration, and invalid signature cases.
Increase auth module coverage from 60% to 95%.
```

### 例2: 統合テスト
```
test(api): add end-to-end API tests

Test complete user registration and login flow.
Includes database setup and teardown for isolation.
```

### 例3: フレイキーテスト修正
```
test: fix flaky timeout in async tests

Replace hardcoded delays with proper async/await.
All tests now pass consistently in CI.
```

---

## ビルド (build)

### 例1: 依存関係更新
```
build: upgrade dependencies to latest versions

- React 17 → 18
- TypeScript 4.5 → 5.0
- Webpack 5.70 → 5.88

All tests passing, no breaking changes detected.
```

### 例2: ビルド設定変更
```
build(webpack): optimize production build

- Enable code splitting for vendor libraries
- Add content hash to filenames for caching
- Configure compression plugin
```

### 例3: パッケージ管理
```
build: migrate from npm to pnpm

Reduce node_modules size by 50% using pnpm workspaces.
Update CI scripts accordingly.
```

---

## CI/CD (ci)

### 例1: GitHub Actions 追加
```
ci: add automated testing workflow

Run tests on every PR and push to main.
Includes linting, type checking, and unit tests.
```

### 例2: デプロイ自動化
```
ci: automate production deployment

Deploy to production on tagged releases.
Includes smoke tests and rollback on failure.
```

### 例3: カバレッジレポート
```
ci: add test coverage reporting to PR comments

Automatically comment on PRs with coverage changes.
Fail build if coverage drops below 80%.
```

---

## Breaking Changes

### 例1: API 変更
```
feat(api)!: change user endpoint response format

BREAKING CHANGE: User API now returns ISO 8601 timestamps instead of
Unix timestamps.

Before:
{
  "created": 1234567890
}

After:
{
  "created": "2024-01-15T10:30:00Z"
}

Migration guide: https://docs.example.com/migration/v2
Refs #999
```

### 例2: 設定ファイル変更
```
refactor(config)!: migrate to new configuration format

BREAKING CHANGE: Configuration file format changed from JSON to YAML.

Migration:
1. Rename config.json to config.yml
2. Convert to YAML format using provided script:
   python scripts/migrate_config.py

Closes #1234
```

### 例3: 依存関係のメジャーバージョンアップ
```
build!: upgrade Node.js requirement to v18+

BREAKING CHANGE: Node.js 16 is no longer supported.
Minimum required version is now 18.0.0.

Reason: Utilize native fetch API and improved performance.
```

---

## マルチコミット推奨ケース

### ❌ 悪い例: 複数の関心事を1つのコミットに
```
feat: add dark mode, fix login bug, update docs

- Implement dark mode toggle
- Fix null pointer in login
- Update README with new features
```

### ✅ 良い例: 3つの独立したコミット

**コミット1:**
```
feat(ui): add dark mode toggle

Allow users to switch between light and dark themes.
Theme preference is saved to localStorage.
```

**コミット2:**
```
fix(auth): handle null response in login endpoint

Prevent crash when user object is null.
Returns proper 404 error instead.

Fixes #789
```

**コミット3:**
```
docs: update README with dark mode feature

Add dark mode toggle documentation.
Include screenshot of theme switcher.
```

---

## よくある間違いと修正例

### 間違い1: 曖昧なメッセージ
❌ `fix: fix bug`
✅ `fix(auth): prevent session timeout on page reload`

### 間違い2: 過去形の使用
❌ `feat: added new feature`
✅ `feat: add new feature`

### 間違い3: 大文字開始
❌ `feat: Add new feature`
✅ `feat: add new feature`

### 間違い4: 末尾のピリオド
❌ `fix: resolve issue.`
✅ `fix: resolve issue`

### 間違い5: スコープの誤用
❌ `feat(everything): update whole codebase`
✅ 複数のコミットに分割（auth, api, ui等）

### 間違い6: 詳細すぎるsubject
❌ `fix: fix the bug where users couldn't login when their email address contained special characters like + or . in the local part`
✅ `fix(auth): handle special characters in email validation` + Bodyに詳細記述

---

## チェックリスト

コミット前に以下を確認：

- [ ] Type は正しいか？ (feat/fix/docs等)
- [ ] Scope は適切か？（または省略が妥当か）
- [ ] Subject は72文字以内か？
- [ ] Subject は命令形・小文字開始・末尾ピリオドなしか？
- [ ] Breaking Changes がある場合、フッターに明記したか？
- [ ] Issue番号を参照したか？（該当する場合）
- [ ] 複数の関心事が混在していないか？

---

## 参考資料

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
