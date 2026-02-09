import * as Sentry from "@sentry/nextjs";

Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    integrations: [
        Sentry.consoleLoggingIntegration({ levels: ["log", "warn", "error"] }),
    ],
});
