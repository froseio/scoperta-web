// Scoperta — central config. Edit values here, nothing else needs to change.
window.SCOPERTA_CONFIG = {
  // Backend (ChargeChill APIServer hosts the daytrip endpoints)
  API_BASE: "https://api.chargechill.app",

  // GA4: leave empty string to keep analytics completely OFF.
  GA4_MEASUREMENT_ID: "",

  // Stripe payment links. "#" = not live yet -> paywall buttons show
  // the "founding member" mailto fallback instead of redirecting.
  STRIPE_URL_MONTHLY: "#",
  STRIPE_URL_YEARLY: "#",

  CONTACT_EMAIL: "hello@scoperta.app",

  // Client-side request timeout (generation takes 15-40 s)
  REQUEST_TIMEOUT_MS: 90000
};
