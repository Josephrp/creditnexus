# Frontend Consistency Audit

This document tracks the current design inconsistencies in the CreditNexus frontend and the remediation plan. Each issue links back to the file(s) where it appears so individual fixes can be tracked and reviewed.

## Inconsistency Log

| # | Summary | Example Location(s) |
|---|---------|---------------------|
| 1 | Hard-coded slate gradients override theme tokens, preventing dark/light schemes from applying. | `bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900` in [Individual Landing](../client/src/sites/individuals/IndividualLanding.tsx) and [Business Landing](../client/src/sites/businesses/BusinessLanding.tsx). |
| 2 | Raw Tailwind color utilities (e.g. `bg-emerald-600`, `text-slate-300`) instead of CSS variables, causing hue drift. | CTA buttons across [Individual Flow](../client/src/sites/individuals/IndividualApplicationFlow.tsx) and [App shell](../client/src/App.tsx). |
| 3 | Buttons mix shared `<Button>` component and ad-hoc `<button>` markup, leading to inconsistent focus/spacing. | [Business Application Flow](../client/src/sites/businesses/BusinessApplicationFlow.tsx) vs. [MainNavigation](../client/src/components/MainNavigation.tsx). |
| 4 | Card padding overrides (`p-12`, `p-8`) diverge from design-system rhythm. | [IndividualApplicationFlow intro card](../client/src/sites/individuals/IndividualApplicationFlow.tsx). |
| 5 | Nested Cards with different backgrounds/borders result in double outlines. | [BusinessApplicationFlow selection cards](../client/src/sites/businesses/BusinessApplicationFlow.tsx). |
| 6 | Typography scale (hero 5xl vs. 4xl) is inconsistent between parallel sections. | [Individual Landing](../client/src/sites/individuals/IndividualLanding.tsx) vs. [Individual Application Flow](../client/src/sites/individuals/IndividualApplicationFlow.tsx). |
| 7 | Icon treatments (gradient badges vs. flat monochrome) vary with no semantic meaning. | Step indicators in [IndividualApplicationFlow](../client/src/sites/individuals/IndividualApplicationFlow.tsx) vs. header icons in [App](../client/src/App.tsx). |
| 8 | CTA button groups differ in layout/gap logic between intro and success states. | [IndividualApplicationFlow](../client/src/sites/individuals/IndividualApplicationFlow.tsx). |
| 9 | Success cards (Individual vs Business) use different spacing, messaging layout, and icon sizes. | [IndividualApplicationFlow success](../client/src/sites/individuals/IndividualApplicationFlow.tsx) vs. [BusinessApplicationFlow success](../client/src/sites/businesses/BusinessApplicationFlow.tsx). |
| 10 | Light-mode overrides in `index.css` target Tailwind utilities, but many components bypass them with hard-coded colors, breaking light theme. | [index.css overrides](../client/src/index.css) vs. [LoginForm](../client/src/components/LoginForm.tsx). |
| 11 | App shell variants (`App.tsx` vs `DesktopAppLayout.tsx`) have different headers/sidebars, so route changes feel like app switches. | [App.tsx](../client/src/App.tsx) and [DesktopAppLayout.tsx](../client/src/components/DesktopAppLayout.tsx). |
| 12 | Navigation hover/active styles duplicated with bespoke Tailwind strings instead of theme tokens. | [MainNavigation](../client/src/components/MainNavigation.tsx). |
| 13 | Tabs expect theme colors but consuming pages set conflicting backgrounds. | [DocumentParser Tabs](../client/src/apps/docu-digitizer/DocumentParser.tsx). |
| 14 | Forms mix shared `<Input>` with manual `<input>` markup, producing inconsistent focus rings and heights. | [LoginForm](../client/src/components/LoginForm.tsx) vs. [Input component](../client/src/components/ui/input.tsx). |
| 15 | Section padding (`py-12`, `py-20`) not standardized, causing uneven scrolling rhythm. | [Individual Landing](../client/src/sites/individuals/IndividualLanding.tsx) vs. [Business Landing](../client/src/sites/businesses/BusinessLanding.tsx). |
| 16 | Card border colors vary (`border-slate-600`, `border-emerald-500/30`) making hierarchy unclear. | [BusinessApplicationFlow cards](../client/src/sites/businesses/BusinessApplicationFlow.tsx) vs. [Dashboard metric cards](../client/src/components/Dashboard.tsx). |
| 17 | Numbered step badges alternate between rounded-full and rounded-lg with different palettes. | [Individual Landing](../client/src/sites/individuals/IndividualLanding.tsx). |
| 18 | Error/success notifications implemented ad-hoc rather than via shared alert/toast component. | [DisbursementPage](../client/src/sites/payments/DisbursementPage.tsx), [LoginForm](../client/src/components/LoginForm.tsx), [SignupFlow](../client/src/components/SignupFlow.tsx). |
| 19 | Action button sizes (`px-8 py-3` vs default `h-10`) vary widely even for similar CTAs. | [IndividualApplicationFlow](../client/src/sites/individuals/IndividualApplicationFlow.tsx) vs. [ReceiptPage actions](../client/src/sites/payments/ReceiptPage.tsx). |
| 20 | Icon colors reused inconsistently (e.g., `CheckCircle` for multiple semantics). | [BusinessApplicationFlow feature lists](../client/src/sites/businesses/BusinessApplicationFlow.tsx). |
| 21 | Wallet/MetaMask flows present inconsistent messaging layouts/backgrounds. | [MetaMaskLogin](../client/src/sites/metamask/MetaMaskLogin.tsx) vs. [DisbursementPage wallet card](../client/src/sites/payments/DisbursementPage.tsx). |
| 22 | Tables lack a shared component, so borders/striping differ per page. | [ReceiptPage repayment table](../client/src/sites/payments/ReceiptPage.tsx). |
| 23 | Card corner radii vary (rounded-2xl vs rounded-lg) without reason. | [LoginForm](../client/src/components/LoginForm.tsx) vs. [Card component defaults](../client/src/components/ui/card.tsx). |
| 24 | Progress/stepper patterns are bespoke per flow. | [SignupFlow](../client/src/components/SignupFlow.tsx) vs. [Application flows](../client/src/sites/individuals/IndividualApplicationFlow.tsx). |
| 25 | Secondary actions alternate between outline buttons and plain text links with inconsistent styling. | [MetaMaskLogin](../client/src/sites/metamask/MetaMaskLogin.tsx) vs. [Individual Landing CTA](../client/src/sites/individuals/IndividualLanding.tsx). |
| 26 | Vertical spacing inside cards uses mixed primitives (`space-y-2`, `mb-4`, `gap-6`). | [BusinessLanding CTA lists](../client/src/sites/businesses/BusinessLanding.tsx). |
| 27 | Brand/iconography treatment differs between shell header and other sections. | Gradient badge in [App.tsx](../client/src/App.tsx) vs static headers elsewhere. |
| 28 | Icon-and-text button ordering/margins differ across CTAs. | [Individual Landing CTAs](../client/src/sites/individuals/IndividualLanding.tsx) vs. [Business Landing CTAs](../client/src/sites/businesses/BusinessLanding.tsx). |
| 29 | Table/list typography mixes `text-sm`, `text-lg` arbitrarily. | [ReceiptPage](../client/src/sites/payments/ReceiptPage.tsx) vs. [DisbursementPage loan details](../client/src/sites/payments/DisbursementPage.tsx). |
| 30 | Form labels alternate between `text-slate-300`, `text-slate-400`, and `text-white`. | [LoginForm](../client/src/components/LoginForm.tsx), [SignupFlow](../client/src/components/SignupFlow.tsx). |
| 31 | Accessibility attributes inconsistent—icon-only buttons often lack `aria-label`. | Copy buttons in [DisbursementPage](../client/src/sites/payments/DisbursementPage.tsx). |
| 32 | Dashboard spacing stacks `space-y-6` with additional `mt-*` margins, causing uneven gutters. | [Dashboard](../client/src/components/Dashboard.tsx). |
| 33 | State/action badges reuse same color palette for different semantics. | `workflowStateColors` vs `actionColors` in [Dashboard](../client/src/components/Dashboard.tsx). |
| 34 | Success icon containers (`rounded-full` size, border) inconsistent across flows. | [MetaMaskLogin success](../client/src/sites/metamask/MetaMaskLogin.tsx) vs. [ReceiptPage success header](../client/src/sites/payments/ReceiptPage.tsx). |
| 35 | Receipt action buttons mix icon spacing conventions (`mr-2` vs flex gap). | [ReceiptPage actions](../client/src/sites/payments/ReceiptPage.tsx). |
| 36 | Desktop vs mobile nav backgrounds/colors dont match, creating visual jumps. | [MainNavigation mobile drawer](../client/src/components/MainNavigation.tsx). |
| 37 | Alerts/toasts implemented as plain DIVs with custom classes instead of shared component. | [DocumentParser warnings](../client/src/apps/docu-digitizer/DocumentParser.tsx). |
| 38 | Loading states use different icon placement/margins. | [DocumentParser](../client/src/apps/docu-digitizer/DocumentParser.tsx) vs. [LoginForm](../client/src/components/LoginForm.tsx). |
| 39 | Section dividers use different border colors/opacities. | [LoginForm](../client/src/components/LoginForm.tsx) vs. [SignupFlow](../client/src/components/SignupFlow.tsx). |
| 40 | Inline links vs buttons have inconsistent hover/underline behavior. | [SignupFlow](../client/src/components/SignupFlow.tsx) vs. [Landing CTAs](../client/src/sites/individuals/IndividualLanding.tsx). |

## Remediation TODOs

- [ ] Standardize background tokens across public-facing pages (replace hard-coded gradients/colors with CSS variables).
- [ ] Update CTA buttons to use shared `<Button>` component variants and theme tokens.
- [ ] Normalize Card padding/spacing (introduce layout utility or props on Card).
- [ ] Create shared alert/notice component for errors/success states.
- [ ] Introduce shared stepper/progress component for multi-step flows.
- [ ] Extract shared table styles (or component) for financial tables.
- [ ] Audit and align typography scale for hero/section headings.
- [ ] Consolidate icon badge styles (size, color, semantic mapping).
- [ ] Normalize form input/label styling by reusing `<Input>` and shared label classes.
- [ ] Add accessibility labels to icon-only buttons and actions.
- [ ] Harmonize navigation/header treatments between `App` and `DesktopAppLayout`.
- [ ] Document button/icon spacing conventions and update CTA layouts accordingly.
- [ ] Define consistent border/radius tokens for Card-like components.
- [ ] Establish loading state pattern (icon placement, text) and refactor to use it.

## Light Mode Testing Results

### Components Verified

- **Buttons**: All variants work correctly in light mode
- **Inputs**: Proper styling in both modes
- **Cards**: Consistent panel styling
- **Tables**: Added missing variables, now working
- **Alerts**: All variants adapt correctly
- **Dashboard**: Updated to use theme variables
- **MetaMaskLogin**: Fixed gradient and card styling

### Issues Resolved

1. Removed hardcoded dark colors from Dashboard
2. Added table-specific CSS variables
3. Fixed wallet connection component gradients
4. Standardized panel hover states

### Remaining Tasks

- Verify all form components
- Test complex data displays
- Check modal overlays

## Status Tracking

- **Document created:** 
- **First fixes in progress:** 

Updates to this document should include checked TODO boxes and references to associated pull requests or commits.
