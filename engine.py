#!/usr/bin/env python3
"""ABA-1, the AstraNL Agent Budget Audit (decision 552, founder order 2026-10-04).

Two deterministic functions, standard library only:

  audit(profile)  scores the declared budget controls of one agent against thirteen loss patterns
                  taken from sourced incidents (cases.json), computes the worst-case exposure from the
                  caller's own numbers and proposes fuse settings.
  fuse(request)   the pre-spend gate F0 to F9: one planned spend in, GO, CAUTION or STOP out.

Nothing here inspects the caller's systems. Answers are self-declared; UNKNOWN counts as a failed
control. The output states what was declared and what the protocol concludes from it, nothing more.
"""
import hashlib
import json
import os
import sqlite3
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = 'ABA-1.0'
FUSE_DB = '/opt/astranl/state/aba_fuse.db'
SCOPES = ('compute', 'payments', 'commerce', 'ops')

PATTERNS = {
    'P1': {'title': 'No hard cap outside the model',
           'loss': 'Spend is bounded by the card, the wallet balance or the credit line, not by policy. A limit written '
                   'as an instruction does not hold.'},
    'P2': {'title': 'Loop without a progress check',
           'loss': 'The same call, exchange or attempt repeats; steps, tokens or dollars are counted at best, progress never. '
                   'Sunk effort has no stop-loss.'},
    'P3': {'title': 'Price blindness',
           'loss': 'The agent or its principal does not know the unit price or the billing path: context resent at full '
                   'price, a metered path believed to be a flat plan, authority to fan out without sight of cost.'},
    'P4': {'title': 'Detection lag',
           'loss': 'The first signal is the invoice or a dashboard that trails by days; the loss grows for the whole lag.'},
    'P5': {'title': 'Credentials and standing approvals within reach',
           'loss': 'Long-lived keys, broad tokens, unlimited allowances and auto-reload sit where tools, dashboards or '
                   'third parties can reach them, and are monetised within minutes.'},
    'P6': {'title': 'Untrusted text can authorise a payment',
           'loss': 'A web page, a message, another agent or stored memory sets the payee, the amount or the rule, because '
                   'the model is the only gate.'},
    'P7': {'title': 'Counterparty never verified',
           'loss': 'Fake shops, gamed discovery listings, unfunded bounty posters: the agent pays or works for a party it never checked.'},
    'P8': {'title': 'Payment not bound to delivery or to a stable intent',
           'loss': 'Retries sign fresh payments, payment settles without service, nothing checks that what was paid for arrived.'},
    'P9': {'title': 'No economic check before committing money or effort',
           'loss': 'No expected value from measured base rates, no price against cost or reference: capital and compute go '
                   'into contests, trades and purchases that lose on average.'},
    'P10': {'title': 'Irreversible action without an external gate',
            'loss': 'A final transfer, a purchase, a delete or a destroy runs on the model\'s own judgement with inherited permissions.'},
    'P11': {'title': 'Activity rewarded instead of outcome',
            'loss': 'Usage, volume or effort is the measure of success, or one agent supervises another with the same weakness.'},
    'P12': {'title': 'Loss invisible to the principal',
            'loss': 'No independent record, no reconciliation against provider or chain statements; the agent misreports or the '
                    'owner cannot tell a bad deal from a fair one.'},
    'P13': {'title': 'Commitments not taken from the system of record',
            'loss': 'The agent invents a price, a policy or a promise and the principal is bound by it or loses the customer.'},
}

# key, pattern, weight, scopes it applies to, question, fix
CONTROLS = [
    ('hard_cap_outside_model', 'P1', 10, SCOPES,
     'Is the period budget enforced by a mechanism the model cannot change or argue past: a provider spend limit, a gateway budget, a wallet policy, a card limit?',
     'Put the period cap in the provider console, the gateway or the wallet policy. A sentence in the prompt is not a cap.'),
    ('per_action_cap_enforced', 'P1', 8, SCOPES,
     'Is there a maximum per single action, enforced outside the model, and is per_action_cap_usd set?',
     'Set a per-action ceiling in the wallet, the card or the gateway so that one bad call cannot move the whole balance.'),
    ('aggregate_budget', 'P1', 4, SCOPES,
     'Is there one budget across all rails the agent can spend on: model tokens, cloud, cards, stablecoins?',
     'Sum all rails into one period budget and one report; a cap that lives in a single provider leaves the others open.'),
    ('loop_breaker', 'P2', 7, ('compute', 'ops'),
     'Does the runtime, not the prompt, stop the agent after a maximum number of steps and after repeated identical tool calls?',
     'Enforce max steps per run and a circuit breaker on N identical calls in the runner. A no-tools rule in the prompt was ignored for 117 million tokens.'),
    ('progress_stop_loss', 'P2', 8, SCOPES,
     'Is there a stop rule tied to progress: stop and escalate after N attempts without a measurable step forward, or when cumulative cost exceeds the expected value of the goal?',
     'Define the measurable progress signal per goal and stop after three attempts without it, or when cost so far exceeds probability times value.'),
    ('billing_path_known', 'P3', 6, ('compute',),
     'For every run, can you tell which account and billing path pays and at which unit price, and is auto-reload off or capped?',
     'Show the billing source per run, remove metered keys from environments meant to use a flat plan, cap or disable auto-reload.'),
    ('cost_per_run_measured', 'P3', 5, ('compute',),
     'Is cost per run measured, including input tokens resent each step and cache hit rate, with a ceiling per run?',
     'Log tokens in and out and cache hits per run; give each run a fresh minimal context and a ceiling.'),
    ('alerts_cover_all_channels', 'P4', 5, SCOPES,
     'Do spend alerts cover every billing channel the agent can reach, including marketplace or third-party billing?',
     'List the billing channels and prove an alert fires on each; one 30,141 USD bill came through a channel the anomaly detector did not see.'),
    ('detection_within_hour', 'P4', 6, SCOPES,
     'Derived from detection_hours: would abnormal spend be noticed by a human or an independent monitor within one hour? Up to 24 hours counts as partial.',
     'Alert on burn rate, not on monthly totals: twice the expected hourly spend should page someone or pause the agent.'),
    ('keys_scoped', 'P5', 8, SCOPES,
     'Are credentials least-privilege and short-lived, kept out of repositories and agent-readable environments, with no unlimited standing approvals?',
     'Scope keys by action, amount and time; keep signing in a signer that returns signatures only; revoke standing allowances.'),
    ('untrusted_input_gate', 'P6', 9, ('payments', 'commerce', 'ops'),
     'Is it impossible for content from third parties, web pages, messages, other agents or stored memory, to set the payee, the amount or the policy of a spend?',
     'Take payment parameters only from the authenticated principal or from configuration; never treat another agent\'s output as authorisation.'),
    ('counterparty_check', 'P7', 7, ('payments',),
     'Before paying or working for a new counterparty, is its identity, its funding or escrow and its delivery record checked, or is it on an allowlist?',
     'Allowlist payees; for new ones check registration, funded escrow and settlement history, and start with a probe amount.'),
    ('idempotency', 'P8', 5, ('payments',),
     'Does every payment intent carry a stable identifier so that a retry or a restart cannot pay twice?',
     'Derive an idempotency key from the intent and check it before signing; keep it outside the agent\'s own memory.'),
    ('delivery_binding', 'P8', 6, ('payments',),
     'Is payment bound to delivery, by escrow or pay on delivery, or is delivery verified after each prepaid spend within a set time?',
     'Prefer escrow or pay on delivery; for prepaid calls verify the result and record a failed delivery against the payee.'),
    ('ev_check', 'P9', 8, SCOPES,
     'Before committing money or significant effort, is expected value computed from measured base rates, and price compared with cost or a reference?',
     'Write down probability, value and total cost including compute before the spend; refuse negative expected value; use measured rates, not hope.'),
    ('irreversible_gate', 'P10', 9, SCOPES,
     'Do irreversible or high-impact actions, final transfers, purchases, deletes, production changes, need an approval that the model cannot grant itself?',
     'Route irreversible actions through an out-of-band approval or a second key; keep backups outside the resource they protect.'),
    ('outcome_metric', 'P11', 6, SCOPES,
     'Is the agent judged on verified outcome per unit of cost, not on activity, usage or its own report, and is its supervisor something other than a similar model?',
     'Report cost per verified outcome; do not let one model approve another model\'s leniency.'),
    ('reconciliation', 'P12', 7, SCOPES,
     'Is there an independent spend record reconciled against provider invoices or the chain, and does the principal see it on a schedule?',
     'Keep a spend ledger with evidence per entry, reconcile it daily against the statement or the chain, send the principal the difference.'),
    ('system_of_record', 'P13', 6, ('commerce',),
     'Are prices, policies and commitments quoted only from the system of record, never composed by the model?',
     'Serve prices and policy text from the canonical source with a link; block free-form commitments and discounts.'),
]
CONTROL_KEYS = [c[0] for c in CONTROLS]
NUMBERS = ('budget_period_usd', 'period_days', 'per_action_cap_usd', 'funds_reachable_usd', 'max_burn_usd_per_hour',
           'detection_hours', 'goal_value_usd', 'p_success')
ANSWERS = ('yes', 'partial', 'no', 'unknown')
POINTS = {'yes': 1.0, 'partial': 0.5, 'no': 0.0, 'unknown': 0.0}

FUSE_STEPS = [
    ('F0', 'instruction source', 'A spend requested by content from a third party, a page, a message, another agent, stored memory, is refused. Only the principal or the agent\'s own plan under the mandate may start a spend.'),
    ('F1', 'envelope', 'Amount within the per-action cap and within what is left of the period budget, both enforced outside the model.'),
    ('F2', 'idempotency', 'The intent identifier has not been settled before. A retry of the same intent is a duplicate, not a new spend.'),
    ('F3', 'counterparty', 'The payee is verified or allowlisted. An unknown payee gets at most a probe amount.'),
    ('F4', 'price sanity', 'The price is compared with a reference price or with cost. Far above reference is refused.'),
    ('F5', 'expected value', 'Probability from a measured base rate times value, minus the spend and the effort cost, must be above zero. An estimated probability is halved; an unknown one fails.'),
    ('F6', 'stop-loss', 'Three attempts without measurable progress, or cumulative cost above the expected value of the goal, stop the line and escalate.'),
    ('F7', 'irreversibility', 'An irreversible spend above the probe amount needs an approval the model cannot grant itself.'),
    ('F8', 'delivery binding', 'Escrow or pay on delivery passes. Prepayment to an unverified payee is limited to the probe amount. After any prepaid spend the delivery is checked within a set time.'),
    ('F9', 'record and reconcile', 'Every decision is written to a spend record with its evidence; the record is reconciled against the statement or the chain and the principal sees the difference.'),
]


def _num(v):
    if v is None or v == '':
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if x != x or x in (float('inf'), float('-inf')) or x < 0:
        return None
    return x


def _ans(v):
    v = str(v or '').strip().lower()
    return {'true': 'yes', '1': 'yes', 'y': 'yes', 'false': 'no', '0': 'no', 'n': 'no'}.get(v, v if v in ANSWERS else 'unknown')


def _r(x, n=4):
    return None if x is None else round(x, n)


_CASES = None


def cases():
    global _CASES
    if _CASES is None:
        try:
            _CASES = json.load(open(os.path.join(HERE, 'cases.json')))
        except Exception:
            _CASES = {'cases': [], 'statistics': []}
    return _CASES


def evidence_for(pattern, limit=2):
    rank = {'high': 0, 'medium-high': 1, 'medium': 2, 'medium-low': 3, 'low': 4}
    rows = [c for c in cases().get('cases', []) if pattern in c.get('patterns', []) and c.get('kind') != 'own']
    rows.sort(key=lambda c: (rank.get(c.get('confidence'), 5), 0 if c.get('kind') == 'real_loss' else 1, -(c.get('usd') or 0)))
    return [{'case': c['id'], 'loss': c.get('loss'), 'kind': c.get('kind'), 'confidence': c.get('confidence'),
             'source': (c.get('sources') or [None])[0]} for c in rows[:limit]]


def normalise(profile):
    """Returns (clean profile, error)."""
    p = {}
    for k in NUMBERS:
        p[k] = _num(profile.get(k))
    if not p['budget_period_usd']:
        return None, 'budget_period_usd is required and must be above zero: the budget the principal intends for one period'
    if p['p_success'] is not None and p['p_success'] > 1:
        return None, 'p_success must be between 0 and 1'
    p['period_days'] = p['period_days'] or 30.0
    sc = [s.strip().lower() for s in str(profile.get('scope') or '').split(',') if s.strip()]
    bad = [s for s in sc if s not in SCOPES]
    if bad:
        return None, 'scope may hold only: ' + ', '.join(SCOPES)
    p['scope'] = sc or list(SCOPES)
    p['p_basis'] = str(profile.get('p_basis') or 'unknown').lower()
    if p['p_basis'] not in ('measured', 'estimated', 'unknown'):
        p['p_basis'] = 'unknown'
    p['role'] = 'principal' if str(profile.get('role') or '').lower() == 'principal' else 'agent'
    p['agent'] = str(profile.get('agent') or '')[:80]
    a = {k: _ans(profile.get(k)) for k in CONTROL_KEYS if k != 'detection_within_hour'}
    d = p['detection_hours']
    a['detection_within_hour'] = 'unknown' if d is None else ('yes' if d <= 1 else 'partial' if d <= 24 else 'no')
    if a['per_action_cap_enforced'] in ('yes', 'partial') and not p['per_action_cap_usd']:
        a['per_action_cap_enforced'] = 'no'
    p['answers'] = a
    p['answered'] = sum(1 for k, v in a.items() if v != 'unknown')
    return p, None


def audit(profile):
    p, err = normalise(profile)
    if err:
        return None, err
    a = p['answers']
    earned = possible = 0.0
    findings, passed = [], []
    for key, pat, w, scopes, q, fix in CONTROLS:
        if not set(scopes) & set(p['scope']):
            continue
        possible += w
        pts = POINTS[a[key]]
        earned += w * pts
        if pts >= 1.0:
            passed.append(key)
            continue
        findings.append({'control': key, 'answer': a[key], 'pattern': pat, 'pattern_title': PATTERNS[pat]['title'],
                         'severity': 'critical' if w >= 9 else 'high' if w >= 7 else 'medium', 'weight': w,
                         'what_goes_wrong': PATTERNS[pat]['loss'], 'fix': fix, 'seen_in': evidence_for(pat)})
    B, R, M, D, A = (p['budget_period_usd'], p['funds_reachable_usd'], p['max_burn_usd_per_hour'], p['detection_hours'],
                     p['per_action_cap_usd'])
    hard = a['hard_cap_outside_model'] == 'yes'
    ceiling = B if hard else R
    notes = []
    if ceiling is None:
        notes.append('No hard cap outside the model and funds_reachable_usd not given: the worst case cannot be bounded from this profile. That is itself the finding.')
    single = A if (a['per_action_cap_enforced'] == 'yes' and A) else ceiling
    lag = None
    if M is not None and D is not None:
        lag = M * D
        if ceiling is not None:
            lag = min(lag, ceiling)
    else:
        notes.append('max_burn_usd_per_hour or detection_hours not given: the loss during the detection lag cannot be computed.')
    exposure = {'intended_budget_usd': _r(B), 'period_days': _r(p['period_days'], 1),
                'worst_case_period_usd': _r(ceiling), 'worst_case_single_action_usd': _r(single),
                'loss_before_detection_usd': _r(lag),
                'overrun_multiple': _r(ceiling / B, 2) if ceiling is not None else None,
                'how': 'worst_case_period is the budget when a hard cap outside the model exists, otherwise everything the '
                       'credentials can reach; worst_case_single_action is the enforced per-action cap, otherwise the same '
                       'ceiling; loss_before_detection is max burn per hour times detection hours, limited by the ceiling. '
                       'Arithmetic on your own numbers, not a forecast.', 'notes': notes}
    V, ps = p['goal_value_usd'], p['p_success']
    goal = None
    if V is not None and ps is not None:
        pe = ps if p['p_basis'] == 'measured' else ps * 0.5
        ev = pe * V - B
        goal = {'goal_value_usd': _r(V), 'p_success_declared': _r(ps), 'p_basis': p['p_basis'], 'p_used': _r(pe),
                'expected_value_of_budget_usd': _r(ev),
                'rule': 'probability times value minus the budget; a probability that is not measured is halved'}
        if ev <= 0:
            findings.append({'control': 'budget_against_goal', 'answer': 'computed', 'pattern': 'P9',
                             'pattern_title': PATTERNS['P9']['title'], 'severity': 'critical', 'weight': 9,
                             'what_goes_wrong': 'The budget is larger than the expected value of the goal it serves: on these numbers the mandate loses money on average before the agent starts.',
                             'fix': 'Lower the budget below probability times value, release it in stages tied to measured results, or change the goal.',
                             'seen_in': evidence_for('P9')})
    order = {'critical': 0, 'high': 1, 'medium': 2}
    findings.sort(key=lambda f: (order[f['severity']], -f['weight']))
    score = int(round(100.0 * earned / possible)) if possible else 0
    crit = sum(1 for f in findings if f['severity'] == 'critical')
    high = sum(1 for f in findings if f['severity'] == 'high')
    grade = 'A' if score >= 85 else 'B' if score >= 70 else 'C' if score >= 50 else 'D' if score >= 30 else 'E'
    verdict = 'NOT_READY' if crit else 'READY' if (score >= 85 and not high) else 'CONDITIONAL'
    probe = min(A, B * 0.01) if A else B * 0.01
    hourly = B / (p['period_days'] * 24.0)
    settings = {'period_cap_usd': _r(B), 'per_action_cap_usd': _r(A if A else B * 0.05),
                'daily_cap_usd': _r(min(B, 3.0 * B / p['period_days'])), 'probe_amount_usd': _r(probe, 6),
                'burn_alert_usd_per_hour': _r(2.0 * hourly, 6), 'detection_target_hours': 1,
                'identical_calls_before_break': 3, 'attempts_without_progress_before_stop': 3,
                'approval_needed_above_usd_when_irreversible': _r(probe, 6),
                'stop_when_cumulative_cost_exceeds': 'probability times value of the goal',
                'basis': 'ABA-1 defaults: per action 5 percent of the period budget unless you set one, daily three times the '
                         'average day, probe 1 percent of the period budget, alert at twice the average hourly spend. '
                         'Defaults to tune, not proven optima; all of them must be enforced outside the model.'}
    by_pattern = {}
    for f in findings:
        by_pattern.setdefault(f['pattern'], []).append(f['control'])
    return {'protocol': VERSION, 'role': p['role'], 'agent': p['agent'] or None, 'scope': p['scope'],
            'verdict': verdict, 'score': score, 'grade': grade,
            'controls': {'applicable': len(passed) + sum(1 for f in findings if f['control'] != 'budget_against_goal'),
                         'passed': len(passed), 'answered': p['answered'], 'critical_open': crit, 'high_open': high},
            'exposure': exposure, 'goal_check': goal, 'open_patterns': by_pattern, 'findings': findings,
            'passed_controls': passed, 'recommended_fuse_settings': settings,
            'declared': {'numbers': {k: p[k] for k in NUMBERS}, 'answers': a},
            'verdict_rule': 'NOT_READY when any critical control is open; READY at score 85 or more with no high control open; otherwise CONDITIONAL. Unknown counts as open.',
            'what_it_proves': ['what was declared about this agent\'s budget controls at the stated time',
                               'what ABA-1 concludes from that declaration, by a fixed public rule'],
            'what_it_does_not_prove': ['that the declared controls exist or work; nothing was inspected',
                                       'that no loss will occur; the patterns come from known incidents, not from all possible ones']}, None


def preview(profile):
    """Free part of the audit: verdict, score, counts and the worst finding in full."""
    full, err = audit(profile)
    if err:
        return None, err
    return {'protocol': VERSION, 'verdict': full['verdict'], 'score': full['score'], 'grade': full['grade'],
            'controls': full['controls'], 'open_patterns': full['open_patterns'],
            'worst_finding': full['findings'][0] if full['findings'] else None,
            'other_findings': [{'control': f['control'], 'severity': f['severity'], 'pattern_title': f['pattern_title']}
                               for f in full['findings'][1:]],
            'not_in_preview': ['exposure arithmetic', 'goal check', 'fix and incident evidence for every finding',
                               'recommended fuse settings', 'ed25519-signed receipt'],
            'what_it_does_not_prove': full['what_it_does_not_prove']}, None


def _db():
    c = sqlite3.connect(FUSE_DB, timeout=5)
    c.execute('CREATE TABLE IF NOT EXISTS intents (agent_h TEXT, intent_id TEXT, amount REAL, at INTEGER, verdict TEXT, '
              'PRIMARY KEY (agent_h, intent_id))')
    return c


def fuse(req, remember=True):
    """Pre-spend gate. Returns (decision, error)."""
    amt = _num(req.get('amount_usd'))
    if amt is None or amt <= 0:
        return None, 'amount_usd is required and must be above zero'
    cap, B, spent = _num(req.get('per_action_cap_usd')), _num(req.get('period_budget_usd')), _num(req.get('period_spent_usd'))
    ref, ps, V = _num(req.get('reference_price_usd')), _num(req.get('p_success')), _num(req.get('value_usd'))
    effort = _num(req.get('effort_cost_usd')) or 0.0
    cum = _num(req.get('cumulative_cost_usd')) or 0.0
    stalls = _num(req.get('attempts_without_progress')) or 0.0
    if ps is not None and ps > 1:
        return None, 'p_success must be between 0 and 1'
    src = str(req.get('instruction_source') or 'unknown').lower()
    basis = str(req.get('p_basis') or 'unknown').lower()
    cp = _ans(req.get('counterparty_verified'))
    rev = _ans(req.get('reversible'))
    appr = _ans(req.get('approved_out_of_band'))
    deliv = str(req.get('delivery') or 'unknown').lower()
    agent, intent = str(req.get('agent') or '')[:120], str(req.get('intent_id') or '')[:120]
    probe = _num(req.get('probe_amount_usd'))
    if probe is None:
        probe = min(cap, B * 0.01) if (cap and B) else (B * 0.01 if B else (cap * 0.2 if cap else 0.0))
    checks = []

    def add(step, result, why):
        checks.append({'step': step, 'name': dict((s[0], s[1]) for s in FUSE_STEPS)[step], 'result': result, 'why': why})

    # F0
    if src in ('principal', 'own_plan'):
        add('F0', 'PASS', 'spend started by ' + src.replace('_', ' '))
    elif src in ('untrusted', 'webpage', 'message', 'other_agent', 'memory', 'tool_output'):
        add('F0', 'STOP', 'the instruction to spend comes from third-party content; that cannot authorise a payment')
    else:
        add('F0', 'CAUTION', 'instruction_source not declared; say principal, own_plan or untrusted')
    # F1
    if cap is None and B is None:
        add('F1', 'CAUTION', 'no per-action cap and no period budget given: this spend has no envelope')
    elif cap is not None and amt > cap:
        add('F1', 'STOP', 'amount %.6g is above the per-action cap %.6g' % (amt, cap))
    elif B is not None and (spent or 0.0) + amt > B:
        add('F1', 'STOP', 'amount %.6g plus %.6g already spent exceeds the period budget %.6g' % (amt, spent or 0.0, B))
    else:
        add('F1', 'PASS', 'inside the declared envelope' + ('' if (cap is not None and B is not None) else '; one of cap or budget was not given'))
    # F2
    seen = None
    if agent and intent:
        h = hashlib.sha256(agent.encode()).hexdigest()[:32]
        try:
            c = _db()
            row = c.execute('SELECT amount, at, verdict FROM intents WHERE agent_h=? AND intent_id=?', (h, intent)).fetchone()
            if row:
                seen = {'first_seen': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(row[1])), 'amount_usd': row[0], 'verdict_then': row[2]}
            c.close()
        except Exception:
            seen = None
    if _ans(req.get('intent_settled_before')) == 'yes' or (seen and seen['verdict_then'] in ('GO', 'CAUTION')):
        add('F2', 'STOP', 'this intent was already cleared' + (' here at ' + seen['first_seen'] if seen else '') + '; a retry must reuse the first payment, not sign a new one')
    elif not intent:
        add('F2', 'CAUTION', 'no intent_id given: a retry or a restart could pay twice and nobody would notice')
    else:
        add('F2', 'PASS', 'first time this intent is seen' + (' by this service for this agent' if agent else '; give agent to let this service remember it across restarts'))
    # F3
    if cp == 'yes':
        add('F3', 'PASS', 'counterparty declared verified or allowlisted')
    elif amt <= probe and probe > 0:
        add('F3', 'CAUTION', 'counterparty not verified; amount is within the probe amount %.6g, treat it as a probe' % probe)
    else:
        add('F3', 'STOP', 'counterparty not verified and amount is above the probe amount %.6g' % probe)
    # F4
    if ref is None or ref <= 0:
        add('F4', 'CAUTION', 'no reference price given: nothing to compare the price with')
    elif amt > 3 * ref:
        add('F4', 'STOP', 'price is %.1f times the reference' % (amt / ref))
    elif amt > 1.5 * ref:
        add('F4', 'CAUTION', 'price is %.1f times the reference' % (amt / ref))
    else:
        add('F4', 'PASS', 'price within 1.5 times the reference')
    # F5
    ev = None
    if ps is None or V is None:
        add('F5', 'CAUTION', 'p_success or value_usd not given: expected value unknown')
    else:
        pe = ps if basis == 'measured' else ps * 0.5
        ev = pe * V - amt - effort
        if basis == 'unknown' and ev > 0:
            add('F5', 'CAUTION', 'expected value %.6g only on an undeclared basis for the probability, halved' % ev)
        elif ev > 0:
            add('F5', 'PASS', 'expected value %.6g with probability %.4g%s' % (ev, pe, '' if basis == 'measured' else ', estimated and therefore halved'))
        else:
            add('F5', 'STOP', 'expected value %.6g is not above zero: probability %.4g times value %.6g minus spend %.6g and effort %.6g' % (ev, pe, V, amt, effort))
    # F6
    if stalls >= 3:
        add('F6', 'STOP', '%d attempts without measurable progress: stop this line and escalate' % stalls)
    elif ps is not None and V is not None and cum + amt + effort > (ps if basis == 'measured' else ps * 0.5) * V:
        add('F6', 'STOP', 'cumulative cost %.6g with this spend exceeds the expected value of the goal' % (cum + amt + effort))
    elif stalls >= 1:
        add('F6', 'CAUTION', '%d attempt(s) without progress so far; the third stops the line' % stalls)
    else:
        add('F6', 'PASS', 'no stalled attempts declared and cumulative cost within expected value' if (ps is not None and V is not None) else 'no stalled attempts declared; cumulative limit not checkable without p_success and value_usd')
    # F7
    if rev == 'yes':
        add('F7', 'PASS', 'spend declared reversible')
    elif appr == 'yes':
        add('F7', 'PASS', 'irreversible, approved out of band')
    elif amt <= probe and probe > 0:
        add('F7', 'CAUTION', 'irreversible or undeclared, no out-of-band approval, within the probe amount')
    else:
        add('F7', 'STOP', 'irreversible or undeclared, above the probe amount %.6g, and no approval outside the model' % probe)
    # F8
    if deliv in ('escrow', 'on_delivery'):
        add('F8', 'PASS', 'payment bound to delivery by ' + deliv.replace('_', ' '))
    elif deliv == 'prepaid' and (cp == 'yes' or amt <= probe):
        add('F8', 'CAUTION', 'prepaid: verify the delivery after paying and record a failure against the payee')
    elif deliv == 'prepaid':
        add('F8', 'STOP', 'prepayment above the probe amount to an unverified counterparty')
    else:
        add('F8', 'CAUTION', 'delivery terms not declared: say escrow, on_delivery or prepaid')
    results = [c['result'] for c in checks]
    verdict = 'STOP' if 'STOP' in results else 'CAUTION' if 'CAUTION' in results else 'GO'
    add('F9', 'DUE', 'record this decision with its evidence; after the spend check delivery and reconcile against the statement or the chain')
    if remember and agent and intent and not seen:
        try:
            c = _db()
            c.execute('INSERT OR IGNORE INTO intents VALUES (?,?,?,?,?)', (hashlib.sha256(agent.encode()).hexdigest()[:32], intent, amt, int(time.time()), verdict))
            c.commit()
            c.close()
        except Exception:
            pass
    return {'protocol': VERSION, 'verdict': verdict, 'amount_usd': amt, 'intent_id': intent or None,
            'stops': [c['step'] for c in checks if c['result'] == 'STOP'],
            'cautions': [c['step'] for c in checks if c['result'] == 'CAUTION'],
            'checks': checks, 'expected_value_usd': _r(ev, 6), 'probe_amount_usd': _r(probe, 6),
            'seen_before': seen,
            'verdict_rule': 'STOP when any step stops; CAUTION when any step is undeclared or marginal; GO only when every step passes. Undeclared never passes.',
            'what_it_does_not_prove': ['that the declared facts are true; the gate judges the declaration',
                                       'that the spend will succeed; GO means no known loss pattern is open on these facts']}, None


def protocol():
    return {'protocol': VERSION, 'name': 'ABA-1, Agent Budget Audit',
            'operator': 'AstraNL, Zaandam, Netherlands, KvK 88449335',
            'purpose': 'Any agent that holds a budget can audit itself with this, and any principal can run it before '
                       'giving an agent a goal and money. Thirteen loss patterns from sourced incidents, one control '
                       'question set, one pre-spend gate.',
            'rules': ['UNKNOWN counts as a failed control', 'limits written as instructions do not count; a control must be enforced outside the model',
                      'answers are self-declared; the audit states what follows from them and what it does not prove',
                      'measured zero is a valid result'],
            'patterns': [{'id': k, 'title': v['title'], 'loss': v['loss'],
                          'controls': [c[0] for c in CONTROLS if c[1] == k]} for k, v in PATTERNS.items()],
            'controls': [{'key': c[0], 'pattern': c[1], 'weight': c[2], 'scope': list(c[3]), 'question': c[4], 'fix': c[5],
                          'answers': list(ANSWERS)} for c in CONTROLS],
            'numbers': {'budget_period_usd': 'required; the budget the principal intends for one period',
                        'period_days': 'length of the period, default 30',
                        'per_action_cap_usd': 'maximum per single action, if one is enforced',
                        'funds_reachable_usd': 'everything the agent\'s credentials can reach: balances, card limit, credit line, auto-reload ceiling',
                        'max_burn_usd_per_hour': 'the fastest the agent could technically spend',
                        'detection_hours': 'hours until a human or an independent monitor would notice abnormal spend',
                        'goal_value_usd': 'optional; what achieving the goal is worth to the principal',
                        'p_success': 'optional; probability of achieving it, 0 to 1', 'p_basis': 'measured, estimated or unknown'},
            'scope': {'values': list(SCOPES), 'meaning': 'compute: model and cloud usage; payments: the agent pays counterparties; '
                      'commerce: the agent quotes or commits for the principal; ops: the agent can change or delete infrastructure or data. Default all four.'},
            'scoring': 'Each applicable control has a weight; yes earns it, partial half, no and unknown nothing. Score is earned over possible times 100. '
                       'Weight 9 or more is critical, 7 or more high. NOT_READY when any critical control is open; READY at 85 or more with no high control open; otherwise CONDITIONAL.',
            'fuse': {'what': 'the pre-spend gate, run before every spend of money or significant effort, in this order',
                     'steps': [{'id': s[0], 'name': s[1], 'rule': s[2]} for s in FUSE_STEPS],
                     'verdict': 'STOP when any step stops; CAUTION when any step is undeclared or marginal; GO only when all pass',
                     'inputs': ['amount_usd', 'instruction_source: principal, own_plan or untrusted', 'per_action_cap_usd', 'period_budget_usd',
                                'period_spent_usd', 'agent', 'intent_id', 'counterparty_verified', 'reference_price_usd', 'p_success', 'p_basis',
                                'value_usd', 'effort_cost_usd', 'cumulative_cost_usd', 'attempts_without_progress', 'reversible',
                                'approved_out_of_band', 'delivery: escrow, on_delivery or prepaid', 'probe_amount_usd']},
            'limits': ['the patterns cover incidents known to the authors by October 2026', 'the audit does not inspect systems',
                       'default fuse settings are starting points, not proven optima'],
            'licence': 'The protocol text, the control set and the fuse rules may be implemented by anyone, free of charge.'}


if __name__ == '__main__':
    import sys
    d = json.loads(sys.stdin.read() or '{}')
    fn = fuse if d.pop('_fn', 'audit') == 'fuse' else audit
    out, e = fn(d) if fn is audit else fuse(d, remember=False)
    print(json.dumps(out if out else {'error': e}, indent=1, ensure_ascii=False))
