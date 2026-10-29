// The site switches (plain JS so that both astro.config.mjs and src/config.ts can read them).
export default {
  /** Public address of the site; change here if it goes live on another domain. */
  DOMAIN: 'https://www.evomobil.rs',
  /** true = private preview: every page gets a noindex tag and _headers sends X-Robots-Tag noindex. false = public. */
  NOINDEX: true,
  /**
   * false = everything for selling ads is left out: the Oglašavanje page, the demo page (primer-oglasa.html),
   *         oglasi@evomobil.rs, the "Zakupi" buttons, ad codes and links to Oglašavanje; the ad spots on the
   *         homepage stay as neutral "Slobodna pozicija" placeholders.
   * true  = all of it is back (the build fails if ads are off but an ad reference remains).
   */
  ADS_ENABLED: false,
  /**
   * Texts on the empty ad spots of the homepage while ADS_ENABLED is false
   * ("Ovde može biti vaš model", "Slobodna pozicija", "Brend meseca", "LOGO"...):
   * false = the spots show only their photos, true = the texts are shown. With ADS_ENABLED the texts are always on.
   */
  AD_PLACEHOLDER_TEXT: false,
  /** Look of the demo photos in the empty ad spots on the homepage: 'photo', 'fade' or 'multiply'. */
  PH_STYLE: 'photo',
  /** Google Analytics 4 measurement ID ('G-...'); empty = analytics never loads. */
  GA_ID: '',
};
