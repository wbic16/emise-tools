# Llama Husbandry Fact-Check — Bickford Llama Ranch

Checked: 2026-10-31 (America/Chicago)
Purpose: defaults for the herd app (breeding, spit-off reminders, cria due dates,
vaccination due dates). Sources are veterinary / university-extension first;
breeder-society and vet-practice pages are used only where they corroborate them.

> **Standing caveat for the whole file:** No vaccine is labelled for camelids in
> the US — all use is extra-label and “most vaccination protocols for camelids
> are empirically derived” (Merck/MSD Veterinary Manual, Herd Health). Every
> schedule below is a *common default*, not a prescription. The ranch vet can
> and should override it per animal / region.

## Verdicts at a glance

| App default in the brief | Verdict | Recommended default |
|---|---|---|
| Spit-off reminder 21 days after breeding | **Partly correct — too narrow as the only check** | Keep 21 d, but add an earlier spit-off at **14 d** and a recheck at **~45 d (6 weeks)** |
| (Implied) cria due date from breeding date | Use Merck figure, not the popular “350 d” alone | **Breeding + 342 days**, shown with a **332–352 day window** |
| CD/T: initial series, then annual booster | **Correct** | Cria series 3–4 weeks / ~30 days apart (start age varies — see §3), then **annual** for all adults; plus a dam booster **4–6 weeks before due date** |
| Rabies (if used) | Annual is the camelid default | **Annual**, first at ≥3 months / at weaning. No established 3-year camelid interval — do not borrow the dog/cat 3-year schedule |
| Other “annual” vaccines | **Not universal** | Lepto, West Nile, EEE/WEE/VEE, 7-/8-way clostridial: regional / vet-directed only. Support as custom records, not built-in defaults |

---

## 1. Spit-off test timing after breeding

**21 days is a real checkpoint, but it is not the first or the standard *only* spit-off.**

Why: llamas are induced ovulators. If conception fails, the corpus luteum (CL)
regresses about 10–12 days after breeding and the female becomes receptive again.
If she conceives, progesterone stays high and she keeps refusing (“spitting off”)
the male. That biology produces several distinct checkpoints:

- **~7 days** — behavioural check / progesterone: confirms *ovulation* occurred,
  not pregnancy. Merck: progesterone can confirm ovulation at 6–9 days.
- **14–15 days — the key early spit-off.** Merck: “An indication of pregnancy is
  the female’s rejection of the male if reintroduced **>15 days** after the
  initial breeding.” Breeder/vet guidance converges on 12–14 / 14 days for the
  first pregnancy-indicating spit-off.
- **21 days — progesterone blood test / repeat spit-off.** Merck: progesterone
  >1 ng/mL confirms pregnancy at **>21 days**; transrectal ultrasound is
  “reasonably sure by day 21.” This is where the brief’s 21-day figure most
  cleanly comes from — it is a *confirmation* timing, and a legitimate spit-off
  recheck (optional spit-offs at 21 and 28 days “can catch early losses” —
  Claire Whitehead, specialist in camelid health, quoted in *The ’Paca Post*).
  Caveat: persistent CL causes most false positives on progesterone.
- **~45 days (6 weeks) — second recheck, commonly recommended.** Traditional
  guidance: test after mating at **2–3 weeks, 6 weeks, and at least 12 weeks**.
  45 days also aligns with veterinary confirmation: rectal palpation in llamas
  is practical at **>45 days** (Merck), and transabdominal/transcutaneous
  ultrasound can confirm at **45–60 days** (Merck). A 60-day confirmation is
  often called ideal because losses are less likely after that point
  (Whitehead, above) — **uncertain / vet-dependent** whether the ranch needs a
  separate 60-day reminder.

**App recommendation (keep it simple — three dates, all derived from breeding date):**

```
spit_off_1   = breeding_date + 14 days   # first pregnancy-indicating spit-off
spit_off_2   = breeding_date + 21 days   # repeat spit-off / progesterone window — the brief's existing reminder
recheck_45   = breeding_date + 45 days   # 6-week recheck / vet ultrasound-or-palpation window
```

Do not present a spit-off at any single date as proof of pregnancy — it is a
screen; ultrasound / palpation / progesterone are the confirmations.

Sources:
- Merck Veterinary Manual — Reproduction of Llamas and Alpacas:
  https://www.merckvetmanual.com/exotic-and-laboratory-animals/llamas-and-alpacas/reproduction-of-llamas-and-alpacas
- Shagbark Ridge / Hamilton Co. Llamas — Llama Breeding & Birthing (7 d, 12–14 d, blood test after 21 d; CL regresses 10–12 d if not pregnant):
  http://www.shagbarkridge.com/breed.html
- Michigan Llama Assoc. — All About Llamas (test at 2–3 weeks, 6 weeks, at least 12 weeks):
  https://michiganllama.org/all-about-llamas
- The ’Paca Post, “Ask A Vet” — Claire E Whitehead BVM&S MS DACVIM (spit-off 7 d, 14 d, optional 21/28 d; ultrasound ~30 d rectal or 45–60 d transabdominal; 60 d ideal):
  https://mailchi.mp/alpacagram/the-paca-post-boost-turnout-for-your-nafd-event?e=a505806032
- British Llama Society — Breeding Llamas (progesterone after 21 d of refusing; ultrasound after 50 d):
  https://www.britishllamasociety.co.uk/breeding-llamas/

## 2. Gestation length — estimated cria due date

**Authoritative figure (Merck): ~342 ± 10 days.**

> “Normal gestation period in camelids is ~342 ± 10 days, with alpacas having
> a somewhat shorter gestation.” — Merck Veterinary Manual, Reproduction

That gives, for llamas:

```
estimated_due_date = breeding_date + 342 days
normal_window      = breeding_date + 332 days  to  breeding_date + 352 days
                     (about 11 to 11.5 months)
```

Notes / uncertainty:

- “About 350 days / 11½ months” is very widely quoted by breeder sources
  (British Llama Society gives an average of 340–345 days; UC Agriculture &
  Natural Resources says “about 350 days”). 350 is **inside** the Merck window’s
  upper half, not a contradiction — but 342 is the better *central* default
  because it comes with the ±10-day range.
- Wider outliers are reported (British Llama Society: range 300–375 days).
  Treat 332–352 as the *normal planning window*, not a guarantee; the app
  should show “due around X (window Y–Z)”, never a single hard date, and
  should not flag a dam as overdue on day 343.
- Use the **last successful breeding date** the breeder records. Hand-breeding
  records give a much tighter estimate than pasture exposure.

Sources:
- Merck Veterinary Manual — Reproduction of Llamas and Alpacas (342 ± 10 d):
  https://www.merckvetmanual.com/exotic-and-laboratory-animals/llamas-and-alpacas/reproduction-of-llamas-and-alpacas
- UC Agriculture and Natural Resources — Llamas and alpacas (gestation about 350 d; nurses 4–6 months):
  https://ucanr.edu/node/140218/printable/print
- British Llama Society — Breeding Llamas (average 340–345 d, range stated 300–375 d):
  https://www.britishllamasociety.co.uk/breeding-llamas/

## 3. Vaccinations and booster intervals

### 3a. CD/T — *Clostridium perfringens* types C & D + tetanus toxoid — CORE

**Confirmed: initial series in crias, then an annual booster for all adults.**
This is the one routine vaccine on which Merck, the veterinary literature,
and vet practices agree.

- *Today’s Veterinary Practice* (General Practitioner’s Guide to Small
  Ruminants and Camelids; author is UF College of Veterinary Medicine small
  ruminant extension specialist): “an initial booster vaccine series as
  lambs/kids/crias, followed by an **annual booster** for protection against
  *Clostridium perfringens* types C and D and *Clostridium tetani* (CD/T).”
- Merck (Herd Health): “Most animals should receive *Clostridium perfringens*
  type C and D vaccinations and tetanus toxoid.”

**Initial series — timing VARIES by protocol and dam history. Mark uncertain;
do not hard-code one cria schedule as fact:**

| Protocol | First dose | Booster(s) | Then |
|---|---|---|---|
| Merck “one successful approach” | 3 months of age | 30 days later | Annual |
| Merck neonatal alternative (immunocompetent at birth) | First week of life | Two boosters at 3-week intervals | Annual |
| TVP, dam with unknown / no vaccine history | 2–3 days of age (vaccine or antitoxin) | 3–4 weeks later; a third 3–4 weeks after that “can also be considered” | Annual |
| Example vet practice (Bourbon Vet, KY) | 3–4 months | 4–6 weeks after initial | Annual |

Practical app default that covers most herds without inventing precision:
**dose 1 → dose 2 at +3 to +4 weeks (~30 days) → annual booster (+365 days
from last dose).** Let the user set the cria start age; offer the 2–3-day
start only when the dam’s status is unknown/unvaccinated.

**Pregnant females — a second, derivable CD/T date (important, see §4):**
Merck (Herd Health): “Pregnant animals should receive vaccine boosters
**4 to 6 weeks before parturition** to maximize antibody transfer to the
neonate.” Some practices use 6–8 weeks pre-due — use Merck’s 4–6 weeks as the
default window and note the variation.

### 3b. Rabies — commonly used, ANNUAL if used

- Merck: “In rabies endemic areas, a rabies vaccine should be administered.”
  Merck does **not** state an interval in the camelid herd-health section.
- Tufts Cummings School, Veterinary Field Service: rabies + CD/T are core for
  small ruminants incl. llamas/alpacas; rabies protection is “an **annual
  vaccine**”, given over 12 weeks of age.
- Vet-practice / sanctuary guidance converges on annual: vaccinate at
  weaning / from 3–6 months, then **booster annually**; in many states only a
  licensed veterinarian may administer it, and because use is off-label a
  vaccinated camelid may still be treated as unvaccinated after an exposure.

**App default: `next_rabies = last_rabies + 365 days`, first dose at ≥3 months.**
**Uncertain:** no camelid-specific licensed duration exists, so do **not**
default to a 3-year interval.

### 3c. Others — regional / vet-directed only, NOT built-in annual defaults

- **Leptospirosis:** where abortions from *Leptospira* spp are a regional
  problem — initial vaccination, then **boosters 2 times a year** (Merck).
- **West Nile virus + equine encephalitides (EEE/WEE/VEE):** “may be needed in
  some areas” (Merck). Schedules vary widely in practice — **uncertain**, do
  not set a default interval.
- **Polyvalent clostridial (7-/8-way, incl. *C. novyi, C. septicum,
  C. sordellii, C. chauvoei*):** used where liver fluke or snake envenomation
  is a problem (Merck). Optional alternative to plain CD/T for some herds,
  not an additional annual shot by default.
- Only killed vaccines should be used for other viral diseases (Merck).

**App implication:** build exactly two vaccine types with built-in intervals
— CD/T (annual) and Rabies (annual, optional per animal/herd) — plus a
free-form “other vaccine” record with a user-set next-due date. That keeps the
“absolutely simple” model honest.

Sources:
- MSD/Merck Veterinary Manual — Herd Health of Llamas and Alpacas, Vaccination section:
  https://www.msdvetmanual.com/exotic-and-laboratory-animals/llamas-and-alpacas/herd-health-of-llamas-and-alpacas?disableGlobalInfoCollect=false#Vaccination_v3303705
- Today’s Veterinary Practice — The General Practitioner’s Guide to Small Ruminants and Camelids (2024):
  https://todaysveterinarypractice.com/preventive-medicine/the-general-practitioners-guide-to-small-ruminants-and-camelids/
- Tufts Cummings School — Individual Animal Care for Small Ruminants (rabies annual, >12 weeks; CD/T core):
  https://vet.tufts.edu/tufts-veterinary-field-service/services-species/sheep-and-goats/individual-animal-care
- Bourbon Veterinary — Camelid Vaccinations (CD/T 3–4 mo, booster 4–6 wks later, annually; breeding females 6–8 wks pre-due):
  https://www.bourbonvet.com/camelid-vaccines

## 4. Other dates the app should derive automatically

Short list only — each is a direct derivation breeders already track. Anything
else (shearing, toenails, deworming/fecals) is herd-level or condition-based,
not a clean per-animal computed date, so it is deliberately **excluded** below.

1. **Dam’s pre-birthing CD/T booster — due date − 6 weeks to − 4 weeks**
   (window: `due_date - 42 days` … `due_date - 28 days`). This is the highest-value
   extra derivation: it protects the cria via colostrum and is easy to miss
   if it is only tied to the herd’s annual round. Source: Merck Herd Health (§3a).

2. **Pregnancy-confirmation vet check — breeding + 45 days**
   Already covered as the 45-day recheck in §1 (palpation >45 d, transabdominal
   ultrasound 45–60 d — Merck). One reminder can serve both the spit-off recheck
   and the vet check; don’t create two.

3. **Cria weaning — birth + ~6 months**
   UC ANR: cria “nurses for about 4–6 months until weaning.” Ohio State
   camelid guidance (Anderson): wean “no earlier than 4 months, but preferably
   at 6 months”, often around ~100 lb for llamas. App default: `birth + 180 days`
   as a *reminder to assess*, labelled “~6 months — assess cria + dam condition”,
   not an automatic separation order.

4. **(Optional, off by default) Cria CD/T series from birth date**
   Only if the ranch picks one protocol in §3a — e.g. the Merck 3-month
   protocol gives `birth + ~90 days`, booster `+30 days`. Because start age
   legitimately varies (first week vs 3–4 months, and depends on the dam’s
   status), ship this **disabled / vet-configured**, not as a fixed default.

5. **(Optional) Re-breeding earliest window — birth + 14 to 21 days**
   Merck: “most females can conceive within 14–21 days after delivery.”
   Some breeders deliberately wait longer (e.g. 19–27 days). If included at
   all, show it as an informational earliest window, not a “breed now” reminder.

**Deliberately not derived:** annual shearing (spring, herd-level, once a
year), toenail trimming (every ~6–12 weeks to a few times a year, highly
individual/terrain-dependent), deworming (modern guidance is fecal-test-driven;
Merck suggests fecal flotations four times a year — a herd calendar item, not
a per-animal due date, and meningeal-worm prevention is regional). Adding any
of these as per-animal computed due dates would be invented precision.

Sources (in addition to §1–§3):
- Ohio State University Camelid Health Program, via Shagbark Ridge — Birthing in Llamas / Neonatal Period (weaning preferably 6 months, not before 4):
  http://www.shagbarkridge.com/info/birth2.html
- UC Agriculture and Natural Resources — Llamas and alpacas (nursing / weaning 4–6 months):
  https://ucanr.edu/node/140218/printable/print

---

## Suggested constants for the app

```text
SPIT_OFF_1_DAYS        = 14
SPIT_OFF_2_DAYS        = 21    # the brief's original reminder — keep it, as the second check
PREGNANCY_RECHECK_DAYS = 45
GESTATION_DAYS         = 342
GESTATION_WINDOW_DAYS  = ±10   # display 332–352
PREBIRTH_CDT_WINDOW    = due_date - 42d  to  due_date - 28d
CDT_BOOSTER_INTERVAL   = 365 days (annual, after initial 2-dose series ~30 days apart)
RABIES_INTERVAL        = 365 days (annual, if the herd vaccinates for rabies)
WEANING_REMINDER       = birth + 180 days (assess, don't auto-separate)
```
