#!/usr/bin/env python3
"""
Comprehensive replacement script for dashboard_mockup.html
1. Translate all Greek text to English
2. Replace jargon with plain English
3. Remove all em dashes (— → -)

Rules:
  - Do NOT change CSS class names, IDs, or JS variable names
  - Do NOT change brand name "KickLab AI"
  - Do NOT change team names (already English)
"""

import re

path = '/Users/milton/sports-betting-ai/docs/dashboard_mockup.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# ─────────────────────────────────────────────────────────────────
# HELPER: safe ordered replacement list
# ─────────────────────────────────────────────────────────────────
def batch_replace(text, replacements):
    for old, new in replacements:
        text = text.replace(old, new)
    return text

# ─────────────────────────────────────────────────────────────────
# STEP 1 – LANG ATTRIBUTE
# ─────────────────────────────────────────────────────────────────
content = content.replace('<html lang="el">', '<html lang="en">')

# ─────────────────────────────────────────────────────────────────
# STEP 2 – GREEK TEXT (longest/most-specific first)
# ─────────────────────────────────────────────────────────────────
greek = [
    # Login page subtitle
    ('Τεχνητή Νοημοσύνη που κερδίζει', 'AI that wins'),
    # Toast / Login messages
    ('Σύνδεση επιτυχής 🎉', 'Login successful 🎉'),
    ('Λάθος email ή password', 'Wrong email or password'),
    ('Καλώς ήρθες πίσω', 'Welcome back'),
    ('Καλώς ήρθες!', 'Welcome!'),
    ('Καλώς ήρθες', 'Welcome'),
    # Login form
    ('Να με θυμάσαι', 'Remember me'),
    ('ή συνέχεια με', 'or continue with'),
    ('Ξέχασες τον κωδικό;', 'Forgot password?'),
    ('Δεν έχεις λογαριασμό;', "Don't have an account?"),
    ('Κωδικός', 'Password'),
    ('Είσοδος', 'Sign in'),
    ('Εγγραφή', 'Sign up'),
    # Login button (standalone)
    ('>Σύνδεση<', '>Sign in<'),
    ('Σύνδεση', 'Sign in'),   # remaining instances (e.g. in nav)
    # Nav items  
    ('Σημερινά Picks', "Today's Picks"),
    ('Ιστορία', 'History'),
    ('Ρυθμίσεις Εφαρμογής', 'App Settings'),
    ('Ρυθμίσεις', 'Settings'),
    ('Αναλυτικά', 'Analytics'),
    ('Αρχική', 'Home'),
    ('Στατιστικά', 'Stats'),
    ('Αποσύνδεση', 'Log out'),
    ('Έξοδος', 'Log out'),
    ('Εισαγωγή', 'Log in'),
    ('Κοινότητα', 'Community'),
    ('Ειδοποιήσεις', 'Notifications'),
    ('Λογαριασμός', 'Account'),
    ('🔔 Ειδοποιήσεις', '🔔 Notifications'),
    # Quick stat bar
    ('Σήμερα:', 'Today:'),
    ('Ενεργά:', 'Active:'),
    ('Τελευταία ενημέρωση:', 'Last update:'),
    ('μόλις τώρα', 'just now'),
    # Time strings (in notifications etc.)
    ('5 λεπτά πριν', '5 minutes ago'),
    ('2 ώρες πριν', '2 hours ago'),
    ('1 μέρα πριν', '1 day ago'),
    ('λεπτά πριν', 'minutes ago'),
    ('λεπτό πριν', 'minute ago'),
    ('ώρες πριν', 'hours ago'),
    ('ώρα πριν', 'hour ago'),
    ('μέρες πριν', 'days ago'),
    ('μέρα πριν', 'day ago'),
    ('πριν', 'ago'),
    # Buttons / Actions
    ('Αποθήκευση Αλλαγών', 'Save Changes'),
    ('Αποθήκευση', 'Save'),
    ('Ακύρωση', 'Cancel'),
    ('Επιβεβαίωση', 'Confirm'),
    ('Διαγραφή Λογαριασμού', 'Delete Account'),
    ('Διαγραφή', 'Delete'),
    ('Αποθηκεύτηκε', 'Saved'),
    ('Σφάλμα', 'Error'),
    ('Φόρτωση', 'Loading'),
    ('Δεν βρέθηκαν αποτελέσματα', 'No results found'),
    ('Προβολή', 'View'),
    ('Συνέχεια', 'Continue'),
    ('Ανανέωση', 'Refresh'),
    ('Φίλτρο', 'Filter'),
    ('Αναζήτηση...', 'Search...'),
    ('Αναζήτηση', 'Search'),
    # User
    ('Γιάννης Μ.', 'John M.'),
    ('ΓΜ', 'JM'),
    ('Προφίλ', 'Profile'),
    ('Όνομα', 'Name'),
    # Stats labels
    ('Συνολικό Κέρδος', 'Total Profit'),
    ('Πάνω από μέσο όρο', 'Above average'),
    ('Ενεργό winning streak!', 'Active winning streak!'),
    ('Μέσος Όρος Νίκης', 'Avg. Win'),
    ('Μέσος Όρος Ήττας', 'Avg. Loss'),
    ('Κέρδος/Pick', 'Profit/Pick'),
    ('Μέσες Αποδόσεις', 'Average Odds'),
    ('Μέση απόδοση', 'Average odds'),
    ('Σύνολο', 'Total'),
    ('Νίκες', 'Wins'),
    ('Ήττες', 'Losses'),
    ('Ισοπαλίες', 'Draws'),
    ('Αρχικό', 'Starting'),
    ('Τρέχον', 'Current'),
    ('Κεφάλαιο', 'Bankroll'),
    ('Κέρδη', 'Earnings'),
    ('Κέρδος', 'Profit'),
    ('Ζημία', 'Loss'),
    ('Τζόγος', 'Betting'),
    ('Διαχείριση', 'Management'),
    ('Πληρωμή', 'Payment'),
    ('Συνδρομή', 'Subscription'),
    ('Τελευταίες', 'Latest'),
    ('Ενημερώσεις', 'Updates'),
    ('Αποτελέσματα', 'Results'),
    ('Προβλέψεις', 'Predictions'),
    ('Στοίχημα', 'Bet'),
    ('Γλώσσα', 'Language'),
    # Notifications panel  
    ('Σήμανση ως αναγνωσμένα', 'Mark all as read'),
    # Upcoming picks label
    ('🔴 Επερχόμενα Picks - Feb 18-23, 2026', '🔴 Upcoming Picks - Feb 18-23, 2026'),
    ('Επερχόμενα Picks', 'Upcoming Picks'),
    # Settings
    ('🚪 Αποσύνδεση', '🚪 Log out'),
    ('📋 Προφίλ', '📋 Profile'),
    # Push / SMS notifications settings
    ('Push alerts για νέα picks', 'Push alerts for new picks'),
    ('SMS για picks υψηλής εμπιστοσύνης (>75%)', 'SMS for high-confidence picks (>75%)'),
    # Toast messages (Greek portions)
    ('Αντιγραφή!', 'Copied!'),
    ('Το pick αντιγράφηκε στο clipboard', 'Pick copied to clipboard'),
    ('Λειτουργία κοινοποίησης σύντομα!', 'Sharing coming soon!'),
    ('Δημιουργία αρχείου picks...', 'Creating picks file...'),
    ('Τα picks εξήχθησαν με επιτυχία', 'Picks exported successfully'),
    ('Επιτυχία!', 'Success!'),
    ('Επιτυχία', 'Success'),
    ('Νίκη!', 'Win!'),
    ('Το accumulator αντιγράφηκε στο clipboard', 'Accumulator copied to clipboard'),
    ('Εμφάνιση AI reasoning', 'Showing AI analysis'),
    ('Εμφάνιση AI analysis', 'Showing AI analysis'),
    ('επιλέχθηκε', 'selected'),
    ('Εφαρμογή φίλτρων...', 'Applying filters...'),
    # Chart labels (Greek inside JS strings)
    ("label: 'Κέρδος (€)',", "label: 'Profit (€)',"),
    ('label: "Κέρδος (€)"', "label: 'Profit (€)'"),
    ("'Κέρδος: €'", "'Profit: €'"),
    ('"Κέρδος: €"', "'Profit: €'"),
    # JS switchTab titles
    ("picks: 'Σημερινά Picks',", "picks: \"Today's Picks\","),
    ("history: 'Ιστορία',", "history: 'History',"),
    ("settings: 'Ρυθμίσεις'", "settings: 'Settings'"),
]

content = batch_replace(content, greek)

# ─────────────────────────────────────────────────────────────────
# STEP 3 – JARGON REPLACEMENTS
# Most specific → least specific order
# ─────────────────────────────────────────────────────────────────

# ---- Variance banner ----
content = content.replace(
    "You're running below EV — that's normal",
    "Rough patch? That's betting."
)
# In case em dashes already replaced (just in case order matters):
content = content.replace(
    "You're running below EV - that's normal",
    "Rough patch? That's betting."
)
content = content.replace(
    "Your last <span id=\"varianceLosses\">3</span> picks went against you. With a 77% win rate, streaks like this happen in <span id=\"variancePct\">18</span>% of samples. The model's edge is intact — stay the course.",
    "Your last <span id=\"varianceLosses\">3</span> picks didn't go your way. Even top tipsters hit bad runs. Your overall record is still strong at 77%. Keep going."
)
content = content.replace(
    "Your last <span id=\"varianceLosses\">3</span> picks went against you. With a 77% win rate, streaks like this happen in <span id=\"variancePct\">18</span>% of samples. The model's edge is intact - stay the course.",
    "Your last <span id=\"varianceLosses\">3</span> picks didn't go your way. Even top tipsters hit bad runs. Your overall record is still strong at 77%. Keep going."
)

# ---- CLV patterns (Posted @ X · Closed @ Y · CLV +Z%) ----
def replace_clv_pattern(m):
    posted = m.group(1)
    closed = m.group(2)
    sign = m.group(3)
    pct = m.group(4)
    if sign == '+':
        return f'Got in early · Odds dropped to {closed} · Beat market by {pct}%'
    else:
        return f'Got in early · Odds moved to {closed} · Missed market by {pct}%'

content = re.sub(
    r'Posted @ ([\d.]+) · Closed @ ([\d.]+) · CLV ([+-])([\d.]+)%',
    replace_clv_pattern,
    content
)

# ---- Average CLV / Closing Line Value ----
content = content.replace('Average CLV', 'Avg. Market Beat')
content = content.replace('Closing Line Value', 'Beat the Market')

# ---- CLV +/- as badge/label ----
def replace_clv_label(m):
    sign = m.group(1)
    pct = m.group(2)
    if sign == '+':
        return f'Beat market by {pct}%'
    else:
        return f'Missed market by {pct}%'
content = re.sub(r'CLV ([+-])([\d.]+)%', replace_clv_label, content)

# ---- Remaining CLV as standalone label ----
content = content.replace('CLV', 'Market Beat')

# ---- Kelly ----
# Specific patterns first
content = re.sub(r'\(¼ Kelly · €[\d,]+ bank\)', '(based on your bankroll)', content)
content = content.replace('Kelly stake:', 'Suggested bet:')
content = content.replace('¼ Kelly', 'Safe bet size')
content = content.replace('Kelly Criterion Calculator', 'Bet Size Calculator')
content = content.replace('Kelly Criterion', 'optimal bet sizing formula')
content = content.replace('Full Kelly', 'Full bet sizing')
content = content.replace('full Kelly', 'full bet sizing')
content = content.replace('Kelly %', 'Stake %')
content = content.replace('Optimal Kelly Stake', 'Suggested Bet Size')
content = content.replace('Kelly Stake', 'Suggested Bet')
# "Kelly" in stake comparison table (stake-method-name)
content = content.replace('>Kelly<', '>Suggested<')

# ---- Expected Value / EV ----
# Very specific patterns first
content = content.replace('Profit vs Expected Value', 'Your Results vs Math Prediction')
content = content.replace('Profit vs EV', 'Your Results vs Math Prediction')
content = content.replace('EV benchmark', 'Math Prediction')
content = content.replace('EV Academy', 'Value Betting Academy')
content = content.replace('EV advantage', 'model advantage')
content = content.replace('+EV', 'good value')
# In academy body text
content = content.replace('Expected Value (EV)', 'Math Prediction')
content = content.replace('What is Expected Value (EV)?', 'What is a Math Prediction?')
content = content.replace('Expected Value', 'What the math expects')
content = content.replace('Expected value', 'What the math expects')
# Chart dataset labels
content = content.replace("label: 'Expected Value (€)'", "label: 'Math Prediction (€)'")
content = content.replace('label: "Expected Value (€)"', "label: 'Math Prediction (€)'")
# In academy text
content = content.replace('EV is the long-term signal', 'your expected results are the long-term signal')
content = content.replace('track EV, not results', 'track your expected results, not just wins')
content = content.replace('P/L vs EV curve', 'P/L vs Math Prediction curve')
# Canvas element / chart
content = content.replace('profitVsEVChart', 'profitVsMathChart')
# Remaining EV as label (be careful not to hit CSS/JS vars)
# In JS comment lines it's OK to translate
content = content.replace('// EV per bet', '// Math Prediction per bet')
content = content.replace('// Wins: avg odds', '// Wins: avg odds')  # no-op
content = content.replace('avg edge +', 'avg AI Advantage +')

# ---- ROI ----
content = content.replace('Flat ROI', 'Flat return')
content = content.replace('+75% ROI', '+75% Return')
content = content.replace('2.5% ROI', '2.5% Return')
content = content.replace('ROI', 'Return')

# ---- Hit rate / Win rate ----
content = content.replace('Hit rate', 'Win rate')
content = content.replace('hit rate', 'win rate')

# ---- Think Mode ----
content = content.replace(
    "showToast('info', 'Think Mode ON', 'Εμφάνιση AI reasoning')",
    "showToast('info', 'AI Analysis Mode ON', 'Showing AI analysis')"
)
content = content.replace(
    "showToast('info', 'AI Analysis Mode ON', 'Εμφάνιση AI analysis')",
    "showToast('info', 'AI Analysis Mode ON', 'Showing AI analysis')"
)
content = content.replace('Think Mode ON', 'AI Analysis Mode ON')
content = content.replace('Think Mode', 'AI Analysis Mode')
content = content.replace('think mode', 'AI Analysis Mode')
content = content.replace('🧠 Think', '🧠 AI Analysis')

# ---- AI reasoning → AI analysis ----
content = content.replace('AI reasoning', 'AI analysis')
# Note: do NOT rename CSS class ai-reasoning-header

# ---- Min Edge Filter label ----
content = content.replace('Min Edge:', 'AI Advantage:')
content = content.replace('Min Edge Filter', 'Minimum AI Advantage Filter')
content = content.replace('Minimum Edge Filter', 'Minimum AI Advantage Filter')
# The aria-label
content = content.replace('aria-label="Minimum Edge Filter"', 'aria-label="Minimum AI Advantage Filter"')

# ---- EDGE as displayed value ----
# "EDGE: " (all caps, in value-meter-stats spans)
content = content.replace('EDGE: ', 'AI Advantage: ')
# Edge: +/-  (title case label)
content = content.replace('Edge: +', 'AI Advantage: +')
content = content.replace('Edge: -', 'AI Advantage: -')
# "Edge vs market" label in reasoning stats
content = content.replace('📈 Edge vs market', '📈 AI Advantage vs market')
content = content.replace('Edge vs market', 'AI Advantage vs market')
# "Edge quality" label
content = content.replace('📊 Edge quality', '📊 AI Advantage quality')
content = content.replace('Edge quality', 'AI Advantage quality')
# "edge >" (in filter label/text, not in class names)
content = content.replace('edge >', 'AI Advantage >')
# Specific narrative phrases containing "edge" (text, not CSS)
content = content.replace('-9.7% negative edge', '-9.7% negative AI Advantage')
content = content.replace('negative edge of -', 'negative AI Advantage of -')
content = content.replace('negative edge', 'negative AI Advantage')
content = content.replace('+19.9% edge', '+19.9% AI Advantage')
content = content.replace('+29.1% edge', '+29.1% AI Advantage')
content = content.replace('+11% edge', '+11% AI Advantage')
content = content.replace('+8.9% edge', '+8.9% AI Advantage')
content = content.replace('+7.2% edge', '+7.2% AI Advantage')
content = content.replace('+6.3% edge', '+6.3% AI Advantage')
content = content.replace('+1.9% edge', '+1.9% AI Advantage')
content = content.replace('+0.4% edge', '+0.4% AI Advantage')
content = content.replace("model's edge", "model's AI Advantage")
content = content.replace('The edge is real but thin', 'The AI Advantage is real but thin')
content = content.replace('the edge is genuine', 'the AI Advantage is genuine')
content = content.replace('is a real edge', 'is a real AI Advantage')
content = content.replace('real edge', 'real AI Advantage')
content = content.replace('genuine edge', 'genuine AI Advantage')
content = content.replace('calculated edge', 'calculated AI Advantage')
content = content.replace('edge is exceptional', 'AI Advantage is exceptional')
content = content.replace('edge before you bet', 'AI Advantage before you bet')
content = content.replace('has real edge', 'has a real AI Advantage')
content = content.replace('has edge', 'has an AI Advantage')
content = content.replace('your edge', 'your AI Advantage')
content = content.replace('their edge', 'their AI Advantage')
content = content.replace('compounding your edge', 'compounding your AI Advantage')
content = content.replace('know the edge', 'know the AI Advantage')
content = content.replace('every pick has a calculated', 'every pick has a calculated')  # no-op (no edge here)
content = content.replace('verifiable via Market Beat', 'verifiable via Market Beat')  # already done
# "The +X.X% edge" / "a +X.X% edge" (regex)
content = re.sub(r'\bThe \+([\d.]+)% edge\b', r'The +\1% AI Advantage', content)
content = re.sub(r'\ba \+([\d.]+)% edge\b', r'a +\1% AI Advantage', content)
content = re.sub(r'\bthe \+([\d.]+)% edge\b', r'the +\1% AI Advantage', content)
# "(+X.X% edge)"
content = re.sub(r'\(\+([\d.]+)% edge\)', r'(+\1% AI Advantage)', content)
# "Thin +1.9% — marginal" → keep as "Thin +1.9% - marginal" (em dash handled separately)
# "edge%" in JS comments
content = content.replace('edge% * stake', 'AI advantage% * stake')
content = content.replace('edge% * €100', 'AI advantage% * €100')
content = content.replace('// avg edge', '// avg AI Advantage')
content = content.replace('avg edge', 'avg AI Advantage')
# "works over large samples" - has "edge" in context? Let me check...
# "compilers" – no issue
# Academy text: "proving your model has real edge"
content = content.replace('proving your model has real AI Advantage', 'proving your model has a real AI Advantage')  # fix double-replace
# "has a real AI Advantage" - OK
# "edge" in JS variable (edgeFilterLabel etc.) — we must NOT touch those
# Verify: these are in id="edgeFilterLabel" id="edgeFilterValue" id="edgeFilterCount" etc.
# Our replacements above only targeted text content not attribute values
# The `edge >` replacement might catch `oninput="filterByEdge(this.value)"` — let's check
# "filterByEdge(this.value)" — the word "edge" here is part of a function name, NOT standalone
# Our `.replace('edge >', ...)` won't match "filterByEdge" since there's no space-edge-space pattern
# But we need to double-check the label oninput line:
# <label id="edgeFilterLabel">Min AI Advantage: <span ...

# ---- Variance ----
content = content.replace('statistically normal', 'completely normal')
# "Variance is the short-term noise"
content = content.replace('Variance is the short-term noise', 'Rough patches are the short-term noise')
# "high variance" → keep as "high variance" (it's natural in context of derbies)
# "derbies defy form — high variance"
# Replace all Variance/variance but then restore specific exceptions
content = content.replace('Variance', 'Rough patch')
content = content.replace('variance', 'rough patch')
# Restore "high rough patch" (from "high variance" in derby context)
content = content.replace('high rough patch', 'high variance')

# ─────────────────────────────────────────────────────────────────
# STEP 4 – EM DASH REMOVAL  (— → -)
# ─────────────────────────────────────────────────────────────────
content = content.replace('—', '-')
# Also handle en-dash (" – ") in some contexts if present
# (The instructions only mention em dash, so leave en-dash alone)

# ─────────────────────────────────────────────────────────────────
# STEP 5 – MISCELLANEOUS FIXES
# ─────────────────────────────────────────────────────────────────

# Fix chart canvas ID reference (we renamed it above)
# profitVsMathChart in canvas element but the JS must also reference it
# Actually the canvas id is referenced in JS as getElementById('profitVsEVChart')
# Instructions say don't change variable names / IDs - let's revert this
content = content.replace('profitVsMathChart', 'profitVsEVChart')

# Fix "Profit vs EV" chart title that may have become double-replaced
content = content.replace('Your Results vs Math Prediction', 'Your Results vs Math Prediction')  # no-op

# Fix the kelly-note class text 
# The kelly-note span gets generated in JS:
# (¼ Kelly · €${bankroll.toLocaleString()} bank) → (based on your bankroll)
# Already handled by the regex above. But let's make sure the JS template literal is covered:
content = content.replace(
    '`<div class="kelly-rec">💰 Kelly stake: <strong>€${stakeRounded}</strong> <span class="kelly-note">(¼ Kelly · €${bankroll.toLocaleString()} bank)</span>',
    '`<div class="kelly-rec">💰 Suggested bet: <strong>€${stakeRounded}</strong> <span class="kelly-note">(based on your bankroll)</span>'
)

# Fix verdictText in JS that still says "edge"
content = content.replace(
    'verdictText = `<strong>Exceptional value (+${edge}%):</strong> Our AI gives ${p.prediction} a ${conf}% probability — market implies only ${impliedPct}% at odds ${p.odds.toFixed(2)}. Strong mispricing detected.`;',
    'verdictText = `<strong>Exceptional value (+${edge}%):</strong> Our AI gives ${p.prediction} a ${conf}% probability - market implies only ${impliedPct}% at odds ${p.odds.toFixed(2)}. Strong mispricing detected.`;'
)
content = content.replace(
    'verdictText = `<strong>Marginal value (+${edge}%):</strong> AI and market are close — ${conf}% vs ${impliedPct}%. Thin edge, size stakes conservatively.`;',
    'verdictText = `<strong>Marginal value (+${edge}%):</strong> AI and market are close - ${conf}% vs ${impliedPct}%. Thin AI Advantage, size stakes conservatively.`;'
)
content = content.replace(
    'verdictText = `<strong>Skip:</strong> ${p.prediction} confidence is ${conf}% but market prices ${impliedPct}% at odds ${p.odds.toFixed(2)}. Negative edge of ${edge}% — no value here.`;',
    'verdictText = `<strong>Skip:</strong> ${p.prediction} confidence is ${conf}% but market prices ${impliedPct}% at odds ${p.odds.toFixed(2)}. Negative AI Advantage of ${edge}% - no value here.`;'
)

# Fix "📈 Edge vs market" span label in JS-generated pick HTML
content = content.replace(
    '<span class="rsLabel">📈 Edge vs market</span>',
    '<span class="rsLabel">📈 AI Advantage vs market</span>'
)

# Fix "Thin +1.9% — marginal" in reasoning-stat
content = content.replace('Thin +1.9% — marginal', 'Thin +1.9% - marginal')

# Fix "Razor-thin edge:" verdict text
content = content.replace('Razor-thin edge:', 'Razor-thin AI Advantage:')
# Fix "minimal edge" in narrative
content = content.replace('minimal edge', 'minimal AI Advantage')
content = content.replace('thin — only bet', 'thin - only bet')

# Fix "KickLab tracks your average CLV" → already translated CLV to Market Beat
# "KickLab tracks your average Market Beat in the Analytics tab" - OK

# Fix "KickLab uses ¼ Kelly" in academy
content = content.replace('KickLab uses ¼ Kelly for all stake recommendations', 
                           'KickLab uses Safe bet size for all stake recommendations')

# Fix "¼ Kelly (2.5% here = €250)" in academy body
content = re.sub(r'¼ Kelly \(([\d.]+)% here = €([\d,]+)\)', 
                 r'Safe bet size (\1% here = €\2)', content)

# Fix "Formula: Kelly % = Edge / (Odds − 1)"
content = content.replace('Formula: Kelly % = Edge / (Odds − 1)', 
                           'Formula: Stake % = AI Advantage / (Odds - 1)')
# Also handle en-dash version  
content = content.replace('Formula: Kelly % = Edge / (Odds - 1)', 
                           'Formula: Stake % = AI Advantage / (Odds - 1)')

# Fix "10% / (2.00 − 1)" 
content = content.replace('10% / (2.00 − 1)', '10% / (2.00 - 1)')
content = content.replace('10% / (2.00 - 1)', '10% / (2.00 - 1)')  # no-op

# Fix "Full Kelly is aggressive"
content = content.replace('full bet sizing is aggressive', 'betting full size is aggressive')

# ---- Remaining textual "edge" occurrences we may have missed ----
# In academy text
content = content.replace('proving your model has a real AI Advantage', 
                           'proving your model has a real AI Advantage')  # no-op
# "industry gold standard for proving your model has real AI Advantage"  
content = content.replace('has real AI Advantage', 'has a real AI Advantage')
# "value to bet" - no change needed
# "no value here" - no change needed
# "verifiable via Market Beat" - already handled
# "works over large samples" - no "edge" here

# Also fix "Edge" alone at the top of the lpr table (column header)
content = content.replace('<span style="text-align:right;">Edge</span>', 
                           '<span style="text-align:right;">AI Advantage</span>')

# Fix "Thin +1.9% — marginal" in pick reasoning stat value
content = content.replace('Thin +1.9%', 'Thin +1.9%')  # no-op, already fine
# Fix "Near-even — minimal edge" (already got this)
content = content.replace('Near-even — minimal AI Advantage', 'Near-even - minimal AI Advantage')

# Fix "• 22:00" separator bullets in pick titles - keep as-is

# Fix remaining greek in graph labels
content = content.replace("label: 'Κέρδος (€)'", "label: 'Profit (€)'")

# ─────────────────────────────────────────────────────────────────
# STEP 6 – Write output
# ─────────────────────────────────────────────────────────────────
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Count changed lines
orig_lines = original.splitlines()
new_lines = content.splitlines()
changed = sum(1 for a, b in zip(orig_lines, new_lines) if a != b)
print(f"Done!")
print(f"Lines changed: {changed} / {len(orig_lines)}")
print(f"File length: {len(new_lines)} lines")
