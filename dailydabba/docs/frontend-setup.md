# DailyDabba frontend prototype

Both apps use local sample data, with no API requests. The current active backend
is FastAPI in `backend`; Phase 5 adds auth/profile APIs, but this prototype does
not connect to them. `services/api` is historical. No backend changes are needed.

## Web (PowerShell)

Use Node 24–26 as specified by the existing package engines. This laptop currently
has Node 22; typecheck and production build pass, but npm reports an engine warning.

```powershell
Set-Location W:\startup-project-with-sriram\food_startup\dailydabba\apps\web
npm.cmd ci
npm.cmd run dev
```

Open http://localhost:3000. If port 3000 is already occupied by this preview,
open the existing page instead of launching a second server. An alternate port:

```powershell
npm.cmd exec next dev -- --port 3002
```

Validation / production:

```powershell
npm.cmd run typecheck
npm.cmd run build
# Stop the development server with Ctrl+C before using the same port.
npm.cmd start
```

## Android (PowerShell)

Install Flutter 3.50+ (Dart 3.14+) and Android Studio with the Android SDK and JDK.
The temporary SDK used for this task is not a permanent PATH installation.

```powershell
Set-Location W:\startup-project-with-sriram\food_startup\dailydabba\apps\mobile
flutter doctor -v
flutter pub get
flutter analyze
flutter test
flutter devices
# Replace the value with an Android device ID reported above.
$androidDeviceId = 'emulator-5554'
flutter run -d $androidDeviceId
flutter build apk --debug
```

For this laptop's temporary validation SDK, if it still exists:

```powershell
$flutterSdk = 'C:\Users\svsiv\AppData\Local\Temp\dailydabba-flutter\bin\flutter.bat'
& $flutterSdk analyze
& $flutterSdk test
& $flutterSdk run -d $androidDeviceId
```

Start an emulator in Android Studio Device Manager, or connect an authorized USB
debugging device. No emulator ID is assumed by the app. Application ID remains
the existing development placeholder.

## Prototype behaviour

- Compact greeting, specials/plans switch, meal-time filters, short banner,
  food cards, additional meal suggestions and bottom navigation on small screens.
- Desktop retains a content grid and convenient cart summary.
- Plans show photo strips and a selectable illustrative meal-week calendar.
- Meal details, quantity changes, removal, empty carts, checkout address/slot
  selection, sample order details and account addresses are available.
- Cart state lasts for the current session, not across reloads or app restarts.
- Login, profile/address editing, order placement, payment and subscriptions are
  unavailable. Checkout never submits anything. Calendar choices do not book meals.
- Taxes, delivery charges, credits, skips, pauses and refund rules remain pending.
- No calorie, protein or other nutrition claims are included.

Data boundaries: `apps/web/app/demo.ts` and `apps/mobile/lib/data/demo.dart`.
Flutter state: `lib/cart.dart`; reusable widgets: `lib/widgets/common.dart`.
Food photographs are bundled locally under each app's image directory. They are
illustrative Unsplash images, not verified depictions of individual demo meals.
Source image IDs: `photo-1546833999-b9f581a1996d`,
`photo-1631452180519-c014fe946bc7`, `photo-1639024471283-03518883512d`.

## Validation of the structural redesign

Web typecheck and production build passed. The running local server returned
HTTP 200 with the revised layout. Flutter cart and navigation widget tests passed;
analysis reports no errors or warnings and three informational deprecations for
`package:flutter/material.dart`. `flutter analyze --no-fatal-infos` succeeds.
No Android device or configured emulator was available for a native UI preview.

## Customer-facing copy update — 14 November 2026

The interface now uses production-style wording without demo labels. Fictional
order history, profile identity and saved addresses have been replaced with guest
and empty states. Checkout clearly reports that ordering is not yet available;
no order, payment or subscription is submitted. The catalog remains local fixture
data and integration boundaries remain unchanged. Earlier descriptions of sample
customer records and selectable checkout addresses above describe the prior UI.
