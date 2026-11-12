# DailyDabba

Initial development monorepo. The app entry points are deliberately blank; no
customer-facing UI or business logic has been implemented. Each application owns
its dependencies and can run independently. No global Next.js or NestJS CLI is needed.

## Structure

```text
dailydabba/
  apps/
    web/                 Next.js + TypeScript (port 3000)
    mobile/              Flutter + Dart, Android platform
  services/
    api/                 NestJS + TypeScript + Prisma (port 3001)
  docs/                  Project notes
  infrastructure/docker/ Local infrastructure notes
  .env.example           PostgreSQL development placeholders
  docker-compose.yml     PostgreSQL 17 with persistent storage
```

## Required tools

- Node.js 24 LTS and npm (Node 26 also supported by the project).
- Git.
- Docker Desktop with Docker Compose v2 and Linux containers for local PostgreSQL.
- Flutter 3.50+ stable SDK (includes Dart 3.14+), on your PATH.
- Android Studio, Android SDK/platform tools, a compatible JDK, and an Android
  emulator or physical Android device with USB debugging enabled. `flutter doctor -v`
  reports the SDK/JDK requirements for your Flutter version.

Official setup guides: [Next.js](https://nextjs.org/docs/app/getting-started/installation),
[NestJS](https://docs.nestjs.com/first-steps),
[Prisma configuration](https://www.prisma.io/docs/orm/v7/reference/prisma-config-reference),
[Flutter](https://docs.flutter.dev/install),
[Flutter Android setup](https://docs.flutter.dev/platform-integration/android/setup),
[Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/).

Commands below use PowerShell. On systems where PowerShell blocks npm.ps1, use
`npm.cmd` in place of `npm`. Start in this `dailydabba` directory.

## Environment configuration

```powershell
Copy-Item .env.example .env
Copy-Item services/api/.env.example services/api/.env
```

Copy only if the destination does not exist. Set a local password in `.env`, then
set the same credentials, database name and host port in `services/api/.env`'s
`DATABASE_URL`. URL-encode special characters in the password in the URL. The root
`.env` is read by Compose; the API reads its own `.env` when run from `services/api`.
The examples contain placeholders only. Local `.env` files are ignored by Git.
Neither client app requires environment variables yet. Never put database credentials
in a browser-exposed `NEXT_PUBLIC_*` variable or a Flutter application.

## Install dependencies

From `dailydabba`, install each project separately:

```powershell
cd apps/web
npm ci
cd ../../services/api
npm ci
cd ../../apps/mobile
flutter pub get
cd ../..
```

Commit npm lockfiles and `pubspec.lock` when changing dependencies. Dependency
folders, Prisma generated code and build outputs are ignored.

## Start PostgreSQL

With Docker Desktop running, from `dailydabba`:

```powershell
docker compose up -d --wait postgres
docker compose ps
docker compose exec postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;"'
```

The default database address for apps running on the host is `127.0.0.1:5432`.
If the port is occupied, change `POSTGRES_PORT` and the port in `DATABASE_URL`.
`docker compose down` stops the service while keeping data. The named volume
persists data; `docker compose down -v` deletes that local database. PostgreSQL
initialization credentials only apply when the volume is first created.

## Run the API

From `dailydabba/services/api` after configuring its `.env`:

```powershell
npm run prisma:validate
npm run prisma:generate
npm run start:dev
```

Check in another terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:3001/api/v1/health
```

Expected HTTP 200 JSON: `{"status":"ok"}`. This checks that the backend is
running; it intentionally does not connect to PostgreSQL. PostgreSQL must be
checked separately with the commands above. `HOST` and `PORT` are configurable.

Prisma's schema contains only a PostgreSQL datasource and client generator, with
no business models. Its URL comes from `DATABASE_URL` through `prisma.config.ts`.
No migration or database tables are needed yet. Once models are defined, use
`npm run prisma:migrate -- --name <migration_name>` and regenerate the client.
Prisma Client is not yet wired into a service; add the PostgreSQL driver adapter
when database-backed features are implemented.

Other commands:

```powershell
npm run typecheck
npm run build
npm run start:prod
```

## Run the website

From `dailydabba/apps/web`:

```powershell
npm run dev
```

Open <http://localhost:3000>. A blank page is intentional. There are no fonts,
styles, themes, or customer-facing page content.

```powershell
npm run typecheck
npm run build
npm start
```

Run the production start command after building, with the development server stopped.

## Run Android

Install Flutter and Android Studio, then verify the Android toolchain:

```powershell
flutter doctor -v
flutter doctor --android-licenses
```

Review and accept any licenses required by your local Android toolchain. Start an
emulator in Android Studio's Device Manager, or connect an Android device with
USB debugging enabled. Then, from `dailydabba/apps/mobile`:

```powershell
flutter pub get
flutter devices
flutter run -d <android_device_id>
```

Replace `<android_device_id>` with the Android device ID shown by `flutter devices`.
The Flutter entry point intentionally renders nothing. The Android application ID
uses the development placeholder `com.example.dailydabba_mobile`.

```powershell
flutter analyze
flutter build apk --debug
```

Android debug builds require the SDK/JDK configured by `flutter doctor`. Android
is the only native platform scaffolded at this stage. Machine-specific SDK paths,
Gradle caches, debug signing keys and APKs are not committed. A temporary SDK used
during setup is not a permanent Flutter installation; install Flutter on your PATH
for ongoing development.
