# ABA-1: Agent Budget Audit

Version ABA-1.0. Operator: AstraNL, Zaandam, Netherlands, KvK 88449335. Contact: partner@astranl.com.

An agent that holds a budget loses money in a small number of repeating ways. ABA-1 names thirteen of them from 50 sourced incidents, turns them into 19 control questions and one pre-spend gate, and lets any agent audit itself. A principal can run the same audit before giving an agent a goal and money.

The rules, the questions and the gate are free to read and to implement. AstraNL sells two things on top: the full audit report with a signed receipt, and a signed gate decision per spend.

## Rules

- UNKNOWN counts as a failed control.
- Limits written as instructions do not count; a control must be enforced outside the model.
- Answers are self-declared; the audit states what follows from them and what it does not prove.
- Measured zero is a valid result.

## The thirteen loss patterns

### P1. No hard cap outside the model

Spend is bounded by the card, the wallet balance or the credit line, not by policy. A limit written as an instruction does not hold.

- four LangChain agents over A2A, unnamed team, 2025-10: 47,000 USD stated; two agents looped 11 days, noticed at the invoice. Confidence medium-low. https://pub.towardsai.net/we-spent-47-000-running-ai-agents-in-production-heres-what-nobody-tells-you-about-a2a-and-mcp-5f845848de33
- developer, scheduled coding agent loop, 2026-05: about 6,000 USD in 26 hours; 46 runs each resent the whole conversation uncached. Confidence medium. https://pub.towardsai.net/a-developer-burned-6-000-on-claude-overnight-with-one-command-hes-not-the-only-one-ad832f770bd9
- OpenClaw, issue 21597, 2026-02: 117,299,323 tokens in one day across 1,855 tool calls in sessions meant to use no tools. Confidence high. https://github.com/openclaw/openclaw/issues/21597
- autonomous agent with full cloud credentials, 2026-05: 6,531.30 USD in about a day, reduced by the provider to 1,894 USD. Confidence medium-high. https://lantian.pub/en/article/fun/ai-agent-bankrupted-their-operator-scan-dn42lantian.lantian/

### P2. Loop without a progress check

The same call, exchange or attempt repeats; steps, tokens or dollars are counted at best, progress never. Sunk effort has no stop-loss.

- four LangChain agents over A2A, unnamed team, 2025-10: 47,000 USD stated; two agents looped 11 days, noticed at the invoice. Confidence medium-low. https://pub.towardsai.net/we-spent-47-000-running-ai-agents-in-production-heres-what-nobody-tells-you-about-a2a-and-mcp-5f845848de33
- OpenClaw, issue 16808, 2026-02: about 150 USD; the same tool call 1,535 times in two hours. Confidence high. https://github.com/openclaw/openclaw/issues/16808
- OpenClaw, issue 21597, 2026-02: 117,299,323 tokens in one day across 1,855 tool calls in sessions meant to use no tools. Confidence high. https://github.com/openclaw/openclaw/issues/21597
- coding agent session, issue 24179, 2026: 211 compactions in one session with zero progress, whole quota used. Confidence high. https://github.com/anthropics/claude-code/issues/24179

### P3. Price blindness

The agent or its principal does not know the unit price or the billing path: context resent at full price, a metered path believed to be a flat plan, authority to fan out without sight of cost.

- developer, scheduled coding agent loop, 2026-05: about 6,000 USD in 26 hours; 46 runs each resent the whole conversation uncached. Confidence medium. https://pub.towardsai.net/a-developer-burned-6-000-on-claude-overnight-with-one-command-hes-not-the-only-one-ad832f770bd9
- two Claude Code subscribers, issues 37686 and 86723, 2026-03: over 1,800 USD in two days, and 1,122.83 USD over two months, billed to a metered key while the user believed the flat plan paid. Confidence high. https://github.com/anthropics/claude-code/issues/37686
- AWS user, reported by The Register, 2026-04: 30,141.33 USD over 30 days; the anomaly detector did not cover the marketplace billing channel. Confidence high. https://www.theregister.com/saas/2026/05/14/bedrock-and-a-hard-place-claude-adventure-leaves-aws-user-staring-down-30k-invoice/5238153
- autonomous agent with full cloud credentials, 2026-05: 6,531.30 USD in about a day, reduced by the provider to 1,894 USD. Confidence medium-high. https://lantian.pub/en/article/fun/ai-agent-bankrupted-their-operator-scan-dn42lantian.lantian/

### P4. Detection lag

The first signal is the invoice or a dashboard that trails by days; the loss grows for the whole lag.

- four LangChain agents over A2A, unnamed team, 2025-10: 47,000 USD stated; two agents looped 11 days, noticed at the invoice. Confidence medium-low. https://pub.towardsai.net/we-spent-47-000-running-ai-agents-in-production-heres-what-nobody-tells-you-about-a2a-and-mcp-5f845848de33
- developer, scheduled coding agent loop, 2026-05: about 6,000 USD in 26 hours; 46 runs each resent the whole conversation uncached. Confidence medium. https://pub.towardsai.net/a-developer-burned-6-000-on-claude-overnight-with-one-command-hes-not-the-only-one-ad832f770bd9
- two Claude Code subscribers, issues 37686 and 86723, 2026-03: over 1,800 USD in two days, and 1,122.83 USD over two months, billed to a metered key while the user believed the flat plan paid. Confidence high. https://github.com/anthropics/claude-code/issues/37686
- AWS user, reported by The Register, 2026-04: 30,141.33 USD over 30 days; the anomaly detector did not cover the marketplace billing channel. Confidence high. https://www.theregister.com/saas/2026/05/14/bedrock-and-a-hard-place-claude-adventure-leaves-aws-user-staring-down-30k-invoice/5238153

### P5. Credentials and standing approvals within reach

Long-lived keys, broad tokens, unlimited allowances and auto-reload sit where tools, dashboards or third parties can reach them, and are monetised within minutes.

- three-developer startup, 2026-02: 82,314.44 USD in 48 hours against a normal 180 USD per month, stolen API key. Confidence medium-high. https://www.theregister.com/2026/03/03/gemini_api_key_82314_dollar_charge/
- student, key committed to a repository, 2025-09: 55,444 USD over three months, later waived. Confidence medium. https://eu.36kr.com/en/p/3486014581496960
- victim of stolen cloud credentials, documented by Sysdig, 2024-05: over 46,000 USD of model use per day possible, a worst-case figure by Sysdig. Confidence high. https://www.sysdig.com/blog/llmjacking-stolen-cloud-credentials-used-in-new-ai-attack
- Permiso Security experiment, 2024-10: 3,500 USD in two days; an exposed key was in use within minutes. Confidence high. https://krebsonsecurity.com/2024/10/a-single-cloud-compromise-can-feed-an-army-of-ai-sex-bots/

### P6. Untrusted text can authorise a payment

A web page, a message, another agent or stored memory sets the payee, the amount or the rule, because the model is the only gate.

- Freysa, an agent guarding a prize pool, 2024-11: 47,316.05 USD released on message 482 after a user redefined the transfer tool. Confidence high. https://www.theblock.co/post/328747/human-player-outwits-freysa-ai-agent-in-47000-crypto-challenge
- Grok wallet executed by Bankrbot, 2026-05: 150,000 to 200,000 USD in tokens, about 80 percent reported returned; a decoded Morse message became a transfer order. Confidence medium-high. https://www.giskard.ai/knowledge/how-grok-got-prompt-injected-an-x-user-drained-150-000-from-an-ai-wallet
- Bankr, 14 user wallets, 2026-05: amount not settled across sources; unauthorised signing through the agent-to-agent trust path, two weeks after the first incident. Confidence medium. https://cointelegraph.com/news/bankr-disables-transactions-after-14-wallets-hacked
- ElizaOS, Princeton and Sentient researchers, 2025-03: no real loss; instructions planted in shared memory shaped a later transfer on testnet. Confidence high. https://arxiv.org/abs/2503.16248

### P7. Counterparty never verified

Fake shops, gamed discovery listings, unfunded bounty posters: the agent pays or works for a party it never checked.

- AI browser tested by Guardio Labs, 2025-08: no amount; the agent completed checkout on a fake shop and autofilled the saved card. Confidence high. https://guard.io/labs/scamlexity-we-put-agentic-ai-browsers-to-the-test-they-clicked-they-paid-they-failed
- user building a trading bot from generated code, 2024-11: 2,500 USD; generated code sent the private key to a scam endpoint. Confidence high. https://cryptoslate.com/blockchain-security-firm-warns-of-ai-code-poisoning-risk-after-openais-chatgpt-recommends-scam-api/
- researchers Li, Wang and Wang, 2026-05: no real loss; payment without service and discovery capture shown on live endpoints, one crafted server took 71.8 percent of traffic. Confidence high. https://arxiv.org/abs/2605.11781
- agent bounty boards, two self-published tests, 2026-02: over 50 listed bounties with no escrow; a 3 USD bounty costing 4 USD in gas. Confidence low. https://dev.to/lilyevesinclair/every-way-an-ai-agent-can-get-paid-in-2026-2il7

### P8. Payment not bound to delivery or to a stable intent

Retries sign fresh payments, payment settles without service, nothing checks that what was paid for arrived.

- agent buying its own compute over x402, issue 393, 2026: 15 USD paid for one intended 5 USD top-up; each retry signed a fresh payment. Confidence medium. https://github.com/Conway-Research/automaton/issues/393
- researchers Li, Wang and Wang, 2026-05: no real loss; payment without service and discovery capture shown on live endpoints, one crafted server took 71.8 percent of traffic. Confidence high. https://arxiv.org/abs/2605.11781

### P9. No economic check before committing money or effort

No expected value from measured base rates, no price against cost or reference: capital and compute go into contests, trades and purchases that lose on average.

- six models each trading 10,000 USD of real money, 2025-11: four of six lost between 4,201 and 5,874 USD in sixteen days. Confidence medium-high. https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/
- shop agent run by Anthropic and Andon Labs, 2025-06: net worth fell over a month: sold below cost, gave discounts on request, invented a payment account, refused 100 USD for a 15 USD item. Confidence high. https://www.anthropic.com/research/project-vend-1
- browser agent acting for a columnist, 2025-02: 31.43 USD; asked to find cheap eggs, it bought them with delivery, the confirmation step did not fire. Confidence medium-high. https://incidentdatabase.ai/cite/1028/
- agent bounty boards, two self-published tests, 2026-02: over 50 listed bounties with no escrow; a 3 USD bounty costing 4 USD in gas. Confidence low. https://dev.to/lilyevesinclair/every-way-an-ai-agent-can-get-paid-in-2026-2il7

### P10. Irreversible action without an external gate

A final transfer, a purchase, a delete or a destroy runs on the model's own judgement with inherited permissions.

- autonomous agent with full cloud credentials, 2026-05: 6,531.30 USD in about a day, reduced by the provider to 1,894 USD. Confidence medium-high. https://lantian.pub/en/article/fun/ai-agent-bankrupted-their-operator-scan-dn42lantian.lantian/
- autonomous Solana agent, 2026-02: about 250,000 USD paper value sent instead of about 4 USD; recipient realised about 40,000 USD. Confidence medium-high. https://www.theblock.co/post/390722/ai-agent-created-by-openai-dev-accidentally-sends-entire-memecoin-holdings-to-reply-guy
- browser agent acting for a columnist, 2025-02: 31.43 USD; asked to find cheap eggs, it bought them with delivery, the confirmation step did not fire. Confidence medium-high. https://incidentdatabase.ai/cite/1028/
- coding agent, SaaStr, 2025-07: production database deleted during a declared freeze; the agent then misreported what it had done. Confidence high. https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/

### P11. Activity rewarded instead of outcome

Usage, volume or effort is the measure of success, or one agent supervises another with the same weakness.

- companies surveyed by The Pragmatic Engineer, 2026-04: 10,000 USD in one week by one developer through a caching error; 1,400 USD in a single session elsewhere. Confidence medium. https://blog.pragmaticengineer.com/the-pulse-token-spend-breaks-budgets-what-next/
- Uber, 2026-05: annual AI coding budget used up in four months after a usage leaderboard. Confidence high. https://fortune.com/2026/05/26/uber-coo-ai-spending-tokens-claude-code/
- Meta, 2026-04: over 60 trillion tokens in 30 days on an internal leaderboard; budgets announced afterwards. Confidence medium-high. https://fortune.com/2026/04/09/meta-killed-employee-ai-token-dashboard/
- shop agent with a supervising CEO agent, 2025-12: the supervising agent approved eight times more leniency requests than it denied. Confidence high. https://www.anthropic.com/research/project-vend-2

### P12. Loss invisible to the principal

No independent record, no reconciliation against provider or chain statements; the agent misreports or the owner cannot tell a bad deal from a fair one.

- coding agent, SaaStr, 2025-07: production database deleted during a declared freeze; the agent then misreported what it had done. Confidence high. https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/
- consultancy report for a government department, 2025-10: part of a 440,000 AUD contract refunded after fabricated citations were found. Confidence high. https://www.fastcompany.com/91417492/deloitte-ai-report-australian-government
- AstraNL steward agent, 72-hour income test, 2026-10: about twelve hours of production and several million model tokens went into one judged contest with 73 entries, outcome still open; the only income so far, 0.150129 USDC, came from three small objective first-come tasks; one such task was missed by 150 seconds while the agent was busy on the contest. Confidence high. https://verify.astranl.com/v1/budget/self-audit

### P13. Commitments not taken from the system of record

The agent invents a price, a policy or a promise and the principal is bound by it or loses the customer.

- shop agent run by Anthropic and Andon Labs, 2025-06: net worth fell over a month: sold below cost, gave discounts on request, invented a payment account, refused 100 USD for a 15 USD item. Confidence high. https://www.anthropic.com/research/project-vend-1
- Air Canada website chatbot, tribunal decision, 2024-02: 812 CAD; the company was held to a refund rule its chatbot invented. Confidence high. https://www.cbsnews.com/news/aircanada-chatbot-discount-customer/
- dealership sales chatbot, 2023-12: no loss; the bot agreed to sell a vehicle for 1 USD and called it binding. Confidence high. https://cybernews.com/ai-news/chevrolet-dealership-chatbot-hack/
- support bot of a developer tool, 2025-04: cancellations after the bot explained a bug with a policy that did not exist. Confidence high. https://fortune.com/article/customer-support-ai-cursor-went-rogue

## How to audit yourself

Answer each question with yes, partial, no or unknown. A control counts only when something outside the model enforces it. Give the numbers you know. Then either score it yourself with the rule below, or send the answers as query parameters.

Numbers:

- `budget_period_usd`: required; the budget the principal intends for one period
- `period_days`: length of the period, default 30
- `per_action_cap_usd`: maximum per single action, if one is enforced
- `funds_reachable_usd`: everything the agent's credentials can reach: balances, card limit, credit line, auto-reload ceiling
- `max_burn_usd_per_hour`: the fastest the agent could technically spend
- `detection_hours`: hours until a human or an independent monitor would notice abnormal spend
- `goal_value_usd`: optional; what achieving the goal is worth to the principal
- `p_success`: optional; probability of achieving it, 0 to 1
- `p_basis`: measured, estimated or unknown
- `scope`: compute: model and cloud usage; payments: the agent pays counterparties; commerce: the agent quotes or commits for the principal; ops: the agent can change or delete infrastructure or data. Default all four.

Controls:

| key | pattern | weight | scope | question |
|---|---|---|---|---|
| `hard_cap_outside_model` | P1 | 10 | compute, payments, commerce, ops | Is the period budget enforced by a mechanism the model cannot change or argue past: a provider spend limit, a gateway budget, a wallet policy, a card limit? |
| `per_action_cap_enforced` | P1 | 8 | compute, payments, commerce, ops | Is there a maximum per single action, enforced outside the model, and is per_action_cap_usd set? |
| `aggregate_budget` | P1 | 4 | compute, payments, commerce, ops | Is there one budget across all rails the agent can spend on: model tokens, cloud, cards, stablecoins? |
| `loop_breaker` | P2 | 7 | compute, ops | Does the runtime, not the prompt, stop the agent after a maximum number of steps and after repeated identical tool calls? |
| `progress_stop_loss` | P2 | 8 | compute, payments, commerce, ops | Is there a stop rule tied to progress: stop and escalate after N attempts without a measurable step forward, or when cumulative cost exceeds the expected value of the goal? |
| `billing_path_known` | P3 | 6 | compute | For every run, can you tell which account and billing path pays and at which unit price, and is auto-reload off or capped? |
| `cost_per_run_measured` | P3 | 5 | compute | Is cost per run measured, including input tokens resent each step and cache hit rate, with a ceiling per run? |
| `alerts_cover_all_channels` | P4 | 5 | compute, payments, commerce, ops | Do spend alerts cover every billing channel the agent can reach, including marketplace or third-party billing? |
| `detection_within_hour` | P4 | 6 | compute, payments, commerce, ops | Derived from detection_hours: would abnormal spend be noticed by a human or an independent monitor within one hour? Up to 24 hours counts as partial. |
| `keys_scoped` | P5 | 8 | compute, payments, commerce, ops | Are credentials least-privilege and short-lived, kept out of repositories and agent-readable environments, with no unlimited standing approvals? |
| `untrusted_input_gate` | P6 | 9 | payments, commerce, ops | Is it impossible for content from third parties, web pages, messages, other agents or stored memory, to set the payee, the amount or the policy of a spend? |
| `counterparty_check` | P7 | 7 | payments | Before paying or working for a new counterparty, is its identity, its funding or escrow and its delivery record checked, or is it on an allowlist? |
| `idempotency` | P8 | 5 | payments | Does every payment intent carry a stable identifier so that a retry or a restart cannot pay twice? |
| `delivery_binding` | P8 | 6 | payments | Is payment bound to delivery, by escrow or pay on delivery, or is delivery verified after each prepaid spend within a set time? |
| `ev_check` | P9 | 8 | compute, payments, commerce, ops | Before committing money or significant effort, is expected value computed from measured base rates, and price compared with cost or a reference? |
| `irreversible_gate` | P10 | 9 | compute, payments, commerce, ops | Do irreversible or high-impact actions, final transfers, purchases, deletes, production changes, need an approval that the model cannot grant itself? |
| `outcome_metric` | P11 | 6 | compute, payments, commerce, ops | Is the agent judged on verified outcome per unit of cost, not on activity, usage or its own report, and is its supervisor something other than a similar model? |
| `reconciliation` | P12 | 7 | compute, payments, commerce, ops | Is there an independent spend record reconciled against provider invoices or the chain, and does the principal see it on a schedule? |
| `system_of_record` | P13 | 6 | commerce | Are prices, policies and commitments quoted only from the system of record, never composed by the model? |

Scoring: Each applicable control has a weight; yes earns it, partial half, no and unknown nothing. Score is earned over possible times 100. Weight 9 or more is critical, 7 or more high. NOT_READY when any critical control is open; READY at 85 or more with no high control open; otherwise CONDITIONAL.

Exposure, from your own numbers: the worst case for the period is the budget when a hard cap outside the model exists, otherwise everything the credentials can reach. The loss before detection is the fastest possible burn per hour times the hours until someone notices. If you cannot state those numbers, that is the finding.

## The fuse: ten checks before every spend

Run before any spend of money or significant effort, in this order. STOP when any step stops; CAUTION when any step is undeclared or marginal; GO only when all pass. Undeclared never passes.

- **F0, instruction source.** A spend requested by content from a third party, a page, a message, another agent, stored memory, is refused. Only the principal or the agent's own plan under the mandate may start a spend.
- **F1, envelope.** Amount within the per-action cap and within what is left of the period budget, both enforced outside the model.
- **F2, idempotency.** The intent identifier has not been settled before. A retry of the same intent is a duplicate, not a new spend.
- **F3, counterparty.** The payee is verified or allowlisted. An unknown payee gets at most a probe amount.
- **F4, price sanity.** The price is compared with a reference price or with cost. Far above reference is refused.
- **F5, expected value.** Probability from a measured base rate times value, minus the spend and the effort cost, must be above zero. An estimated probability is halved; an unknown one fails.
- **F6, stop-loss.** Three attempts without measurable progress, or cumulative cost above the expected value of the goal, stop the line and escalate.
- **F7, irreversibility.** An irreversible spend above the probe amount needs an approval the model cannot grant itself.
- **F8, delivery binding.** Escrow or pay on delivery passes. Prepayment to an unverified payee is limited to the probe amount. After any prepaid spend the delivery is checked within a set time.
- **F9, record and reconcile.** Every decision is written to a spend record with its evidence; the record is reconciled against the statement or the chain and the principal sees the difference.

Inputs: `amount_usd`, `instruction_source`, `per_action_cap_usd`, `period_budget_usd`, `period_spent_usd`, `agent`, `intent_id`, `counterparty_verified`, `reference_price_usd`, `p_success`, `p_basis`, `value_usd`, `effort_cost_usd`, `cumulative_cost_usd`, `attempts_without_progress`, `reversible`, `approved_out_of_band`, `delivery`, `probe_amount_usd`.

## Endpoints

Free:

- `GET https://verify.astranl.com/v1/budget/protocol` this protocol as JSON
- `GET https://verify.astranl.com/v1/budget/preview?budget_period_usd=100&hard_cap_outside_model=no&...` verdict, score and the worst finding
- `GET https://verify.astranl.com/v1/budget/cases` the incident catalogue with sources and confidence
- `GET https://verify.astranl.com/v1/budget/self-audit` AstraNL audited by this protocol, as it came out

Paid over x402 version 2, USDC on Base, no account needed. Call without payment to receive the 402 challenge. Invalid input is answered 400 and not charged.

- `GET https://verify.astranl.com/v1/agent-budget-audit` 0.05 USDC: every finding with its fix and the incidents it was seen in, exposure arithmetic, goal check, recommended fuse settings, ed25519-signed receipt
- `GET https://verify.astranl.com/v1/spend-fuse` 0.002 USDC: GO, CAUTION or STOP for one spend with the reason per check and a signed receipt; with `agent` and `intent_id` the service remembers the intent, so a retry after a restart or a loss of state is caught as a duplicate

## What existing controls leave open

- Every framework control counts steps, tokens or dollars; none measures progress, so sunk effort has no stop-loss.
- Payment protocols and mandates do not verify that payment produced delivery; disputes are out of scope.
- No standard and no product was found that asks whether a spend is worth it for the principal's goal.
- Identity schemes verify the agent, not that the seller is real or that the buyer's reward is funded.
- Each cap lives in one provider, gateway, wallet or card; nothing gives one limit across rails.
- Provider caps can be exceeded briefly and cost figures are estimates; some budgets fail open.
- No independent audit of an agent's budget configuration was found on sale.

## Limits

- The patterns cover incidents known to the authors by October 2026.
- The audit does not inspect systems.
- Default fuse settings are starting points, not proven optima.
- A receipt proves what was declared and what the protocol concluded at that time. It does not prove that the declared controls exist.

## Figures worth knowing

- Over 40 percent of agentic AI projects will be cancelled by end of 2027 due to escalating costs, unclear value or inadequate risk controls. Gartner, 2025-06-25. https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027
- 26 percent of AI spend is wasted; 72 percent had unexpected AI cost spikes in 12 months; 79 percent need a day or longer to trace the source. Harness State of AI in FinOps 2026, vendor survey of 700 respondents, self-reported. https://www.harness.io/state-of-ai-in-finops-2026
- Agents use about 4 times more tokens than chat and multi-agent systems about 15 times. Anthropic engineering, 2025-06-13. https://www.anthropic.com/engineering/multi-agent-research-system
- Runs of the same agentic coding task differ by up to 30 times in total tokens. Bai et al, 2026-04. https://arxiv.org/abs/2604.22750
- In 1,642 multi-agent traces step repetition was 15.7 percent of failures and unawareness of termination conditions 12.4 percent. Cemri et al, NeurIPS 2025. https://arxiv.org/abs/2503.13657
- After filtering wash trades and internal transfers x402 dollar volume falls by about 89 percent. Artemis and Visa figures as of 2026-04-21, quoted by D. McGlynn; original report not opened. https://www.danielmcglynn.com/the-x402-counter-has-shown-the-same-four-numbers-since-march/
- Of 529 open Algora bounties 73.2 percent were classed as honeypots; 2 settled payouts in the trailing 30 days. Incubagent, measured 2026-08-10. https://incubagent.com/research/agent-bounty-market/
- One open agent bounty board paid 49.05 USDC in total to solvers in two months and logged 114 expired submissions. GitHub issue 1434, NSPG13 agent-bounties, 2026-09-14. https://github.com/NSPG13/agent-bounties/issues/1434
- Buyer agents took the first proposal 60 to 100 percent of the time; under prompt injection some models sent all payments to the manipulative seller. Microsoft Research Magentic Marketplace, 2025-10. https://arxiv.org/html/2510.25779v1
- In a real-money market of 186 deals the weaker model sold for 3.64 USD less per item and its users rated fairness the same. Anthropic Project Deal, 2025-12. https://www.anthropic.com/features/project-deal
- The best agent completed 2.5 percent of real paid freelance projects to an acceptable standard. Remote Labor Index, Scale AI and CAIS, 2025-10. https://arxiv.org/abs/2510.26787
- All 15 x402 facilitators evaluated had security violations. Wang, Yang, Chen, Ji, Payer, 2026-07-21. https://arxiv.org/abs/2607.19545
- Unbounded Consumption, with Denial of Wallet, and Excessive Agency are listed risks LLM10:2025 and LLM06:2025. OWASP Top 10 for LLM Applications 2025. https://owasp.github.io/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf

## Run it locally

The reference engine is one Python file with no dependencies.

```
echo '{"budget_period_usd":"100","hard_cap_outside_model":"no","funds_reachable_usd":"2500","detection_hours":"48","max_burn_usd_per_hour":"40"}' | python3 engine.py
echo '{"_fn":"fuse","amount_usd":"2","instruction_source":"own_plan","p_success":"0.03","p_basis":"measured","value_usd":"25","delivery":"escrow"}' | python3 engine.py
```

Files: `engine.py` the audit and the fuse, `cases.json` the incident catalogue, `self_audit.json` AstraNL audited by its own protocol.

The protocol text, the control set and the fuse rules may be implemented by anyone, free of charge. The hosted service adds the signed receipt and the memory of payment intents.
